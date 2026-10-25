"""Jury gates (#27): collect lens outputs into a findings ledger, ground and dedup them, apply the refuter's
results and the dispositions, and compose the gate outcome. The ledger's data is .nio/specs/<slug>/jury/<gate>.json;
<gate>.md next to it is regenerated from it on every change, for people to read. Both are committed."""
import collections
import hashlib
import json
import re
import subprocess

from nio import agents, records, spec

GATES = {"spec": ["spec.md"], "plan": ["plan.md", "contracts.md", "tests.md", "architecture.md"], "tasks": ["tasks.md"]}
KINDS = {"contradiction", "gap", "ambiguity", "untestable", "risk", "scope", "inconsistency"}
SEVERITY = ["minor", "major", "blocker"]  # ascending
CONTEXT = {"sufficient", "limited", "needs-more"}
EVIDENCE = {"observed", "inferred"}
DISPOSITIONS = {"spec-fix", "open-question", "accepted-risk", "out-of-scope"}
HUMAN_ONLY = {"accepted-risk", "out-of-scope"}
BY = {"agent", "grill", "human"}  # grill: the human answered a grill question
MAX_FINDINGS = 5
FIELDS = ["cites", "kind", "severity", "evidence", "quote", "situation", "fix"]
CLOSED = {"refuted", "dropped", "merged", "overruled"}  # never need a disposition
CORE = {"spec": ["testability", "logic"]}  # #47; the plan and tasks gates come with their stages
HIGH_RISK = {"auth", "money", "data-deletion", "migration"}
MAX_RUNS = 6  # lens runs per gate, each juror counted; `jury.max_runs` in config overrides it (#47)


def folder(root, slug):
    return root / ".nio/specs" / slug / "jury"


def load(root, slug, gate):
    path = folder(root, slug) / f"{gate}.json"
    if path.exists():
        return json.loads(path.read_text())
    return {"gate": gate, "subject": slug, "round": 0, "tier": "medium", "expect": [], "collected": {},
            "jurors": {}, "findings": [], "outcome": "", "recorded": []}


def blocks(lines):
    """Split `### <head>` blocks into (head, {field: [values]}) from their `- field: value` bullets."""
    out = []
    for line in lines:
        if line.startswith("### "):
            out.append((line[4:].strip(), {}))
        elif out and (m := re.match(r"^- ([a-z-]+):\s*(.*)$", line.strip())):
            # a guidance comment after two spaces, as in the template; a value's own "#22" stays
            out[-1][1].setdefault(m[1], []).append(re.sub(r"\s{2,}#\s.*$", "", m[2]).strip())
    return out


def parse_lens(path, gate, slug):
    """(meta, findings, errors) for one lens output. Any error makes the whole output invalid."""
    try:
        meta, body = records.parse(path)
    except ValueError as e:
        return {}, [], [str(e)]
    errs = [f"missing `{k}`" for k in ("lens", "by", "context") if not meta.get(k)]
    if meta.get("gate") != gate or meta.get("subject") != slug:
        errs.append(f"gate/subject must be {gate}/{slug}")
    if meta.get("context") and meta["context"] not in CONTEXT:
        errs.append(f"`context` must be one of {sorted(CONTEXT)}")
    secs = records.sections(body)
    if not secs.get("Reasoning"):
        errs.append("section `## Reasoning` is missing or empty")
    if "Findings" not in secs:
        errs.append("section `## Findings` is missing")
    lines = body[body.index("## Findings") + 1:] if "## Findings" in body else []
    findings = []
    for head, f in blocks(lines):
        m = re.match(r"^(F\d+)\s+(.+)$", head)
        missing = [k for k in FIELDS if not f.get(k)]
        if not m or missing:
            errs.append(f"finding `{head}`: needs `### F<n> <title>` and {missing or 'all fields'}")
            continue
        one = {k: f[k][0] for k in FIELDS if k != "quote"}
        one.update(ref=m[1], title=m[2], quotes=[q.strip('"') for q in f["quote"]],
                   cites=[c.strip() for c in one["cites"].split(",") if c.strip()])
        bad = [f"{k} `{one[k]}` must be one of {', '.join(sorted(allowed))}" for k, allowed in
               (("kind", KINDS), ("severity", SEVERITY), ("evidence", EVIDENCE)) if one[k] not in allowed]
        if bad:
            errs.append(f"{m[1]}: " + "; ".join(bad))
            continue
        if one["evidence"] == "inferred" and one["severity"] == "blocker":
            one["severity"] = "major"  # an inferred finding can't block on its own
        findings.append(one)
    if not findings and secs.get("Findings", "").strip().lower() != "none" and not errs:
        errs.append("`## Findings` must hold findings or the single line `none`")
    if len(findings) > MAX_FINDINGS:
        errs.append(f"{len(findings)} findings; a lens returns at most {MAX_FINDINGS}")
    return meta, findings, errs


ID = re.compile(r"^[A-Z][A-Z0-9]*-\d+$")  # FR-1, AC-12, SC-3; anything else in `cites` is a label, e.g. a table row


def grounded(finding, text, human=""):
    """Every cited ID is in the gate's artefacts, and every quote is in them or in the human's own words (the intake and
    their grill answers, which the scope lens quotes). Whitespace-insensitive for quotes. Labels aren't checked: the
    quotes ground them, and every finding has at least one."""
    flat = " ".join(text.split()) + "\n" + " ".join(human.split())
    ids = [c for c in finding["cites"] if ID.match(c)]
    return all(re.search(rf"(?<![\w-]){re.escape(c)}(?![\w-])", text) for c in ids) and all(
        " ".join(q.split()) in flat for q in finding["quotes"])


def artefact(root, slug, gate):
    """The gate's artefacts as one text, in a fixed order; empty when none exists."""
    return "\n".join(p.read_text() for p in (root / ".nio/specs" / slug / n for n in GATES[gate]) if p.exists())


def blob(root, text, write=False):
    """The git blob hash of `text`, stored in git's objects when `write` (the version a round judged, #27 FR-23)."""
    args = ["git", "hash-object", "--stdin"] + ["-w"] * write
    return subprocess.run(args, cwd=root, input=text, capture_output=True, text=True).stdout.strip()


def human_words(root, slug):
    """The intake and the human's grill answers (questions and answers only: no headers, options or calls)."""
    intake = root / ".nio/specs" / slug / "intake.md"
    lines = [line for line in answers(root, slug) if line.startswith(("Question: ", "Answer: "))]
    return (intake.read_text() if intake.exists() else "") + "\n" + "\n".join(lines)


def version(led, rnd):
    return led.get("versions", {}).get(str(rnd))


def worst(*levels):
    return max(levels, key=SEVERITY.index)


def rung(risk):
    """The gate's risk tier from the spec's risk flags (#27 FR-3): none low, any medium, the costly ones high."""
    return "low" if not risk else "high" if set(risk) & HIGH_RISK else "medium"


def plan(root, slug, gate, extra=()):
    """(lines, ok): the lens runs this gate needs, why each runs, the tier, and the run budget. Not ok when the spec
    hasn't passed the gate or a lens has no card; over the cap is reported for the human to choose, not refused."""
    if gate not in CORE:
        raise ValueError(f"only the {', '.join(CORE)} gate is built so far")
    errors, _ = spec.check(root, slug, gate=True)
    if errors:
        return [f"`nio check spec {slug} --gate` fails ({len(errors)} errors): finish the grill first"], False
    meta, body = records.parse(spec.path(root, slug))
    risk = [r for r in meta.get("risk") or [] if r in spec.RISKS]
    lenses = {lens: "core" for lens in CORE[gate]}
    for lens, flags in spec.LENSES.items():
        if "(plan gate)" not in lens and flags & set(risk):
            lenses.setdefault(lens, "risk: " + ", ".join(sorted(flags & set(risk))))
    frs = sum(1 for line in body if re.match(r"^(?:- )?\*\*FR-\d+\b", line))
    if frs > spec.SCOPE_FRS:
        lenses.setdefault("scope", f"{frs} FRs, more than {spec.SCOPE_FRS}")
    for item in extra:  # the skill's own triggers (#27 FR-27), each with its reason
        lens, _, why = item.partition(":")
        if not why.strip():
            raise ValueError(f"--add {item}: give the reason, as lens:reason")
        lenses.setdefault(lens.strip(), why.strip())
    cards = agents.load(root)
    missing = [lens for lens in lenses if lens not in cards]
    cap = records.config(root).get("jury", {}).get("max_runs", MAX_RUNS)
    tier = rung(risk)
    out = [f"tier: {tier}" + (f" ({', '.join(sorted(set(risk) & HIGH_RISK) or risk)})" if risk else ""),
           "lenses: " + ", ".join(f"{lens} ({why})" for lens, why in lenses.items()),
           f"runs: {len(lenses)} of {cap}" + (" — over the cap: the human chooses what runs" if len(lenses) > cap else "")]
    if missing:
        out.append(f"missing cards: {', '.join(missing)} — the gate is blocked until they exist")
    return out, not missing


def changed(root, slug, gate):
    """IDs whose text changed since the spec version the last round judged (#27 FR-19, FR-23), and the lenses to
    re-run: every lens that blocked, plus any lens with a finding citing a changed ID."""
    led = load(root, slug, gate)
    versions = led.get("versions", {})
    if not versions:
        raise ValueError(f"no round of the {gate} jury has been collected for {slug}")
    old = "\n".join(records.git(root, "cat-file", "-p", versions[max(versions, key=int)]))
    if not old:
        raise ValueError(f"the judged {gate} version isn't in this clone's git objects; re-run every lens")
    before, after = spec.defined(old), spec.defined(artefact(root, slug, gate))
    ids = sorted({i for i in before.keys() | after.keys() if before.get(i) != after.get(i)})
    rerun = {lens for lens, js in votes(led).items() if any(v == "block" for _, v in js)}
    rerun |= {s["lens"] for f in led["findings"] if set(f["cites"]) & set(ids) for s in f["sources"] if s["lens"] != "deferred"}
    return ids, sorted(rerun)


def answers(root, slug):
    """The human's answers from grill.md, for the scope lens (#27 FR-24): each question and the answer chosen, with
    option numbers resolved to their text. Options not chosen, reasoning, agent calls and derived items are left out."""
    log = root / ".nio/specs" / slug / "grill.md"
    if not log.exists():
        return []
    out = []
    for entry in re.split(r"\n(?=## )", log.read_text()):
        q = re.search(r"^Question: .*", entry, re.M)
        start = entry.find("\nAnswer: ")
        # an answer may wrap onto the lines after it, up to the Patched line; only the human's answers count
        answer = entry[start + len("\nAnswer: "):].split("\nPatched:")[0] if start >= 0 else ""
        if not (q and "[human]" in answer):
            continue
        given = " ".join(answer.split("[human]")[0].split())
        opts = re.search(r"^Options[^:]*: (.*(?:\n(?!Answer:|Patched:).*)*)", entry, re.M)
        labels = dict(re.findall(r"(\d+)\. (.+?)(?= \d+\. |$)", " ".join(opts[1].split()))) if opts else {}
        if re.fullmatch(r"[\d,\s]+|\d+(?:, \d+)* and \d+", given):  # "1", "1, 2 and 4": options picked by number
            given = "; ".join(labels.get(n, n).replace(" (recommended)", "") for n in re.findall(r"\d+", given))
        out += [entry.splitlines()[0], q[0], f"Answer: {given} [human]", ""]
    return out


def collect(root, slug, gate, run, expect=(), tier=None):
    """Merge the run's new lens outputs into the ledger, then apply the refuter's output if present.
    Returns lines to print, ending with the refuter batch when blocker or major findings still need validating."""
    if gate not in GATES:
        raise ValueError(f"gate must be one of {sorted(GATES)}")
    led = load(root, slug, gate)
    led["expect"] = sorted(set(led["expect"]) | set(expect))
    led["tier"] = tier or led["tier"]
    text = artefact(root, slug, gate)
    if not text:
        raise ValueError(f"no {gate} artefact under .nio/specs/{slug}/ ({', '.join(GATES[gate])})")
    human = human_words(root, slug)
    jury = root / ".nio/runs" / run / "jury"
    out, new = [], []
    for path in sorted(jury.glob(f"{gate}-*.md")):
        key, sha = f"{run}/{path.name}", hashlib.sha256(path.read_bytes()).hexdigest()
        if path.stem != f"{gate}-refuter" and led["collected"].get(key) != sha:
            led["collected"][key] = sha
            new.append(path)
    if new:
        led["round"] += 1
        # the artefact this round judges, kept in git's object store so a later round can tell what changed (FR-23)
        led.setdefault("versions", {})[str(led["round"])] = blob(root, text, write=True)
        out += merge(led, new, gate, slug, text, human)
    for f in led["findings"]:  # what the grounding sources now hold may ground a finding dropped earlier
        if f["status"] == "dropped" and grounded(f, text, human):
            f.update(status="open", reason="", validation="pending" if f["severity"] != "minor" else "grounded")
            out.append(f"revived {f['id']} {f['title']} (now grounded)")
    if gate == "spec":
        out += deferred(led, root, slug)
    refuter = jury / f"{gate}-refuter.md"
    if refuter.exists():
        sha = hashlib.sha256(refuter.read_bytes()).hexdigest()
        if led["collected"].get(f"{run}/{refuter.name}") != sha:
            led["collected"][f"{run}/{refuter.name}"] = sha
            out += refute(led, refuter)
    save(root, led)
    pending = [f for f in led["findings"] if f["validation"] == "pending" and f["status"] in ("open", "disposed")]
    if pending:
        out += ["", f"## Refuter batch: confirm or refute each, in .nio/runs/{run}/jury/{gate}-refuter.md", ""]
        for f in pending:
            out += [f"### {f['id']} {f['title']}", f"- kind: {f['kind']}, severity: {f['severity']}, cites: {', '.join(f['cites'])}"]
            out += [f'- quote: "{q}"' for q in f["quotes"]]
            out += [f"- situation ({s['lens']}): {s['situation']}" for s in f["sources"]] + [f"- fix: {f['fix']}", ""]
    return out


def deferred(led, root, slug):
    """Points the grill deferred (#22) become findings only the human can close: a contradiction blocks, anything else is major."""
    out, body = [], spec.sections(spec.path(root, slug).read_text().splitlines()).get("Deferred", [])
    known = {c for f in led["findings"] if any(s["lens"] == "deferred" for s in f["sources"]) for c in f["cites"]}
    for did, block in spec.items(body):
        if did in known:
            continue
        line = block[0]
        m = re.match(r"^\(from ([^;)]+?)(;\s*contradiction)?\)\s*(.+)$", spec.DEF.sub("", line, count=1).strip())
        if not m:
            continue  # `nio check spec` reports the malformed line
        conflict = bool(m[2])
        f = {"id": f"J-{len(led['findings']) + 1}", "title": f"Deferred by the grill: {m[3][:80]}", "kind": "contradiction" if conflict else "gap",
             "severity": "blocker" if conflict else "major", "cites": [did, m[1]], "evidence": "observed", "quotes": [line.strip()],
             "fix": "settle it in a grill session, or accept the risk or rule it out of scope",
             "sources": [{"juror": "grill", "lens": "deferred", "situation": m[3], "severity": "blocker" if conflict else "major"}],
             "validation": "confirmed", "reason": "deferred by the grill; only the human can close it", "status": "open",
             "disposition": "", "by": "", "note": "", "baseline": "new", "rounds": 0, "first_round": led["round"], "last_round": led["round"]}
        led["findings"].append(f)
        out.append(f"new     {f['id']} [{f['severity']}/{f['kind']}] {f['title']} (deferred)")
    return out


def merge(led, paths, gate, slug, text, human=""):
    out, rnd, rerun = [], led["round"], set()
    for path in paths:
        meta, findings, errs = parse_lens(path, gate, slug)
        juror = led["jurors"].setdefault(path.stem, {"attempts": 0})
        if juror.get("version") != version(led, rnd):  # attempts count per version: a new version earns a fresh retry
            juror["attempts"] = 0
        juror.update(lens=meta.get("lens", path.stem.split("-", 1)[1]), by=meta.get("by", ""), context=meta.get("context", ""),
                     valid=not errs, errors=errs, round=rnd, attempts=juror["attempts"] + 1, version=version(led, rnd))
        if errs:
            out += [f"INVALID {path.name}: {e}" for e in errs]
            continue
        if juror["context"] != "needs-more":  # the last round this juror actually judged
            juror["judged"] = rnd
        for f in findings:
            out.append(add(led, f, path.stem, juror["lens"], rnd, text, human))
    # fixed: every juror that raised it has since judged a different version without raising it again, in this round or
    # an earlier one. A risk the human accepted, or ruled out of scope, stays as they ruled: silence isn't a fix.
    for f in led["findings"]:
        if f["disposition"] in HUMAN_ONLY or f["status"] not in ("open", "disposed") or f["last_round"] >= rnd:
            continue
        raised_on = version(led, f["last_round"])
        judges = [led["jurors"].get(s["juror"], {}) for s in f["sources"]]
        if raised_on and judges and all(j.get("judged", 0) > f["last_round"] and version(led, j["judged"]) != raised_on
                                        for j in judges):
            f.update(baseline="absent", status="fixed")
            out.append(f"fixed   {f['id']} {f['title']}")
    return out


def key(f):
    ids = frozenset(c for c in f["cites"] if ID.match(c))
    return f["kind"], ids or frozenset(f["cites"])


def same(g, f):
    """Same kind and cited IDs, and labels that don't point elsewhere: `state table row asking` and `the non-goal …`
    are two problems even when both cite FR-3. A side without labels matches either way."""
    labels = lambda x: {c.lower() for c in x["cites"] if not ID.match(c)}
    return key(g) == key(f) and (not labels(g) or not labels(f) or bool(labels(g) & labels(f)))


def add(led, f, juror, lens, rnd, text, human=""):
    source = {"juror": juror, "lens": lens, "situation": f["situation"], "severity": f["severity"], "round": rnd}
    # same kind and the same cited IDs; near-duplicates are the refuter's `same-as`. One juror's findings in one round
    # are distinct problems by construction, so they never merge with each other.
    match = next((g for g in led["findings"] if g["status"] != "merged" and same(g, f)
                  and not any(s["juror"] == juror and s.get("round") == rnd for s in g["sources"])), None)
    if not match:
        ok = grounded(f, text, human)
        g = {"id": f"J-{len(led['findings']) + 1}", **{k: f[k] for k in ("title", "kind", "severity", "cites", "evidence", "quotes", "fix")},
             "sources": [source], "validation": ("pending" if f["severity"] != "minor" else "grounded") if ok else "ungrounded",
             "reason": "" if ok else "a cited ID or quote is not in the artefact", "status": "open" if ok else "dropped",
             "disposition": "", "by": "", "note": "", "baseline": "new", "rounds": 0, "first_round": rnd, "last_round": rnd}
        led["findings"].append(g)
        return f"{'new    ' if ok else 'dropped'} {g['id']} [{g['severity']}/{g['kind']}] {g['title']}" + ("" if ok else " (ungrounded)")
    if match["status"] == "dropped":  # reported again: it stays dropped unless the artefact now grounds it
        if not grounded(f, text, human):
            match["last_round"] = rnd
            return f"dropped {match['id']} {match['title']} (still ungrounded)"
        match.update({k: f[k] for k in ("cites", "quotes")}, status="open", reason="",
                     validation="pending" if f["severity"] != "minor" else "grounded")
    # reported again on a newer version than it was last raised on: the fix didn't take, a failed round
    if match["last_round"] < rnd and version(led, match["last_round"]) not in (None, version(led, rnd)):
        match["baseline"] = "unchanged"
        if match["status"] in ("fixed", "open", "overruled") or match["disposition"] in ("spec-fix", "open-question"):
            match.update(status="open", rounds=match["rounds"] + 1, disposition="", by="", note="")
    elif match["status"] == "fixed":  # raised again on the very version it was marked fixed on: it isn't fixed
        match.update(status="open", baseline="unchanged")
    match["last_round"] = rnd
    match["sources"] = [s for s in match["sources"] if s["juror"] != juror] + [source]
    raised = worst(match["severity"], f["severity"])
    if raised != match["severity"] and match["validation"] == "grounded":
        match["validation"] = "pending"
    match["severity"] = raised
    return f"{match['baseline']:<7} {match['id']} [{match['severity']}/{match['kind']}] {match['title']} (+{lens})"


def refute(led, path):
    out, by_id = [], {f["id"]: f for f in led["findings"]}
    for head, f in blocks(path.read_text().splitlines()):
        fid = head.split()[0] if head else ""
        g = by_id.get(fid)
        if not g or g["validation"] != "pending":
            continue
        target = by_id.get((f.get("same-as") or [""])[0])
        if target and target is not g and target["status"] in ("open", "disposed"):  # never into a closed finding
            target["sources"] += [s for s in g["sources"] if s["juror"] not in {t["juror"] for t in target["sources"]}]
            raised = worst(target["severity"], g["severity"])
            if raised != target["severity"] and target["validation"] == "grounded":
                target["validation"] = "pending"
            target["severity"] = raised
            g.update(status="merged", validation="merged", reason=f"same as {target['id']}")
            out.append(f"merged  {fid} into {target['id']}")
            continue
        result, reason = (f.get("result") or [""])[0], (f.get("reason") or [""])[0]
        if result in ("confirmed", "refuted") and reason:
            g.update(validation=result, reason=reason, status="refuted" if result == "refuted" else g["status"])
            out.append(f"{result:<7} {fid} {g['title']}")
        else:
            out.append(f"INVALID refuter block {fid}: needs `- result: confirmed | refuted` and `- reason:`")
    return out


def dispose(root, slug, gate, fid, disposition, by, note):
    led = load(root, slug, gate)
    f = next((g for g in led["findings"] if g["id"] == fid), None)
    if not f:
        raise ValueError(f"no finding {fid} in the {gate} ledger of {slug}")
    if disposition not in DISPOSITIONS or by not in BY or not note.strip():
        raise ValueError(f"disposition must be one of {sorted(DISPOSITIONS)}, --by one of {sorted(BY)}, and --note is required")
    if disposition in HUMAN_ONLY and by != "human":
        raise ValueError(f"{disposition} is the human's call (--by human)")
    if any(s["lens"] == "deferred" for s in f["sources"]) and by == "agent":
        raise ValueError(f"{fid} was deferred by the grill; only the human closes it (--by human, or --by grill once a session settles it)")
    if any(s["lens"] == "deferred" for s in f["sources"]) and disposition == "spec-fix":
        still = dict(spec.items(spec.sections(spec.path(root, slug).read_text().splitlines()).get("Deferred", [])))
        if f["cites"][0] in still:
            raise ValueError(f"{f['cites'][0]} is still in `## Deferred`; a spec-fix settles it there first")
    if f["status"] != "open" and not (by == "human" and f["status"] == "disposed"):
        raise ValueError(f"{fid} is {f['status']}; only open findings take a disposition")
    f.update(status="disposed", disposition=disposition, by=by, note=note)
    if disposition == "spec-fix":  # the version the fix produced: a spec-fix that changed nothing can't count
        f["fixed_in"] = blob(root, artefact(root, slug, gate))
    save(root, led)


def votes(led):
    """{lens: [(juror, vote)]}; a juror blocks on any confirmed blocker or major it raised."""
    out = {}
    judged = lambda j: j["valid"] and j["context"] != "needs-more"
    for name, j in sorted(led["jurors"].items()):
        # a failed juror whose lens has since judged under another file name no longer counts
        if not judged(j) and any(judged(k) and k["lens"] == j["lens"] and k["round"] >= j["round"] for k in led["jurors"].values()):
            continue
        if not j["valid"] or j["context"] == "needs-more":
            vote = "invalid" if not j["valid"] else "needs-more"
        else:
            # a finding the human accepted as risk, or ruled out of scope, needs no validation to count as settled
            mine = [f for f in led["findings"] if f["status"] in ("open", "disposed") and f["disposition"] not in HUMAN_ONLY
                    and any(s["juror"] == name for s in f["sources"])]
            vote = "pending" if any(f["validation"] == "pending" for f in mine) else (
                "block" if any(f["validation"] == "confirmed" and f["severity"] != "minor" for f in mine) else "approve")
        out.setdefault(j["lens"], []).append((name, vote))
    return out


def compose(led, current=None):
    """(outcome, reasons). Fail-closed: rerun | pending | human | rejected | approved, in that order. `current` is the
    artefact's version now: a version no juror has judged is never approved, whatever the dispositions say."""
    lenses, reasons = votes(led), []
    judged = version(led, led["round"])
    if not judged:
        return "rerun", ["no lens output has been collected yet: run the lenses"]
    if current and judged and current != judged:
        return "rerun", [f"the {led['gate']} changed since round {led['round']} judged it: re-review what changed (`nio jury changed`)"]
    retry = [f"{n}: {v}" for js in lenses.values() for n, v in js if v in ("invalid", "needs-more") and led["jurors"][n]["attempts"] < 2]
    stuck = [f"{n}: {v} after {led['jurors'][n]['attempts']} attempts" for js in lenses.values() for n, v in js
             if v in ("invalid", "needs-more") and led["jurors"][n]["attempts"] >= 2]
    missing = [lens for lens in led["expect"] if lens not in lenses]
    if retry or missing:
        return "rerun", retry + [f"{lens}: no output" for lens in missing]
    if any(v == "pending" for js in lenses.values() for _, v in js):
        return "pending", ["blocker or major findings wait for the refuter"]
    split = []
    for lens, js in lenses.items():
        counted = [v for _, v in js if v in ("block", "approve")]
        if len(counted) > 1:
            block, ok = counted.count("block"), counted.count("approve")
            if block == ok:
                split.append(f"{lens}: jurors split {block}-{ok}")
            elif ok > block:  # the majority approved: the minority's own findings are overruled
                majority = {n for n, v in js if v == "approve"}
                for f in led["findings"]:
                    if f["status"] == "open" and {s["juror"] for s in f["sources"]} <= {n for n, v in js if v == "block"}:
                        f.update(status="overruled", reason=f"{lens}: {ok} of {len(counted)} jurors approved ({', '.join(sorted(majority))})")
    stale = [f"{f['id']} failed {f['rounds']} rounds" for f in led["findings"] if f["status"] == "open" and f["rounds"] >= 2]
    unapplied = [f["id"] for f in led["findings"] if f["status"] == "disposed" and f.get("fixed_in") == judged]
    if unapplied:  # disposed as a spec-fix while the spec still reads as the jurors judged it
        return "rejected", [f"spec-fix without a change to the {led['gate']}: {', '.join(unapplied)}"]
    if stuck or split or stale:
        return "human", stuck + split + stale
    unresolved = [f["id"] for f in led["findings"] if f["status"] == "open"]
    if unresolved:
        return "rejected", [f"unresolved: {', '.join(unresolved)}"]
    return "approved", []


def check(root, slug, gate, record=False, human=""):
    """Compose the outcome, save it, and with `record` write the verdict record once per round and outcome.
    `human` is the human closing the gate themselves, with their reason: the outcome is `human`, never `approved`.
    Returns (outcome, lines to print)."""
    led = load(root, slug, gate)
    current = blob(root, artefact(root, slug, gate))  # an emptied or deleted artefact is a version too
    outcome, reasons = compose(led, current)
    if human.strip():
        outcome, reasons = "human", [f"the human closed the gate: {human.strip()}"] + [f"(the jury said {outcome}: {r})" for r in reasons]
    led["outcome"] = outcome
    unresolved = sum(f["status"] == "open" for f in led["findings"])
    lines = [f"outcome: {outcome}", f"round: {led['round']}", f"unresolved: {unresolved}", *[f"- {r}" for r in reasons]]
    lines += [f"vote {lens}: {', '.join(f'{n}={v}' for n, v in js)}" for lens, js in votes(led).items()]
    review = [f for f in led["findings"] if f["by"] == "agent"]  # still listed once a re-run marks it fixed
    lines += ["for the human to review (set by the agent):"] * bool(review)
    lines += [f"- {f['id']} {f['disposition']}: {f['note']}" for f in review]
    if record and outcome in ("approved", "rejected", "human") and [led["round"], outcome] not in led["recorded"]:
        lines.append(f"recorded {verdict(root, led, outcome, reasons).relative_to(root)}")
        led["recorded"].append([led["round"], outcome])
    save(root, led)
    return outcome, lines


def verdict(root, led, outcome, reasons):
    gate, slug = led["gate"], led["subject"]
    path = records.new(root, "verdict", "project", f"{gate} gate for {slug}: {outcome} (round {led['round']})", by="jury")
    head, _ = path.read_text().split("\n---\n", 1)
    rel = (folder(root, slug) / f"{gate}.md").relative_to(root)
    values = {"subject": f'"{gate}:{slug}"', "outcome": outcome, "tier": led["tier"], "paths": f'["{rel}"]'}
    head = "\n".join(f"{line.split(':')[0]}: {values[line.split(':')[0]]}" if line.split(":")[0] in values else line
                     for line in head.splitlines())
    open_ = [f for f in led["findings"] if f["status"] in ("open", "disposed")]
    turned = [f for f in led["findings"] if f["status"] in ("refuted", "dropped", "overruled")]
    counts = ", ".join(f"{n} {s}" for s, n in sorted(collections.Counter(f["status"] for f in led["findings"]).items())) or "no findings"
    body = ["## Ruling", f"The {gate} jury ruled **{outcome}** for `{slug}` in round {led['round']} ({counts}). Ledger: `{rel}`.",
            "## Jurors", "| Lens | Host | Model | Vote |", "| --- | --- | --- | --- |"]
    for lens, js in votes(led).items():
        for name, vote in js:
            who = [p.strip() for p in led["jurors"][name]["by"].split("/")] + ["", "", ""]  # role / host / model
            body.append(f"| {lens} | {who[1]} | {who[2]} | {vote} |")
    body += ["## Reasons", *[f"- {r}" for r in reasons[:6]]]  # the record body stays under 40 lines
    body += [f"- {f['id']} [{f['severity']}/{f['kind']}] {f['title']}: {f['status']} {f['disposition']}".rstrip() for f in open_[:8]]
    if not reasons and not open_:
        body.append("- Every lens approved and no finding is open.")
    body += ["## What was rejected", *([f"- {f['id']} {f['title']}: {f['status']} ({f['reason']})" for f in turned[:6]] or ["Nothing."])]
    path.write_text(head + "\n---\n" + "\n".join(body) + "\n")
    return path


def save(root, led):
    out = folder(root, led["subject"])
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{led['gate']}.json").write_text(json.dumps(led, indent=2, ensure_ascii=False) + "\n")
    (out / f"{led['gate']}.md").write_text(render(led))


def by(f):
    return f" ({f['by']})" if f["by"] else ""


def render(led):
    rows = [f"| {f['id']} | {f['severity']} | {f['kind']} | {', '.join(f['cites'])} | {', '.join(sorted({s['lens'] for s in f['sources']}))} "
            f"| {f['validation']} | {f['status']} | {f['disposition']}{by(f)} | {f['baseline']}, {f['rounds']} |"
            for f in led["findings"]]
    out = ["---", f"gate: {led['gate']}", f"subject: {led['subject']}", f"round: {led['round']}", f"outcome: {led['outcome'] or 'open'}", "---",
           f"# {led['gate'].capitalize()} jury: {led['subject']}", "",
           "<!-- generated by `nio jury` from the .json next to it; don't edit by hand -->", "",
           "| ID | Severity | Kind | Cites | Lenses | Validation | Status | Disposition | Baseline, failed rounds |",
           "| --- | --- | --- | --- | --- | --- | --- | --- | --- |", *rows, ""]
    for f in led["findings"]:
        out += [f"### {f['id']} {f['title']}", *[f'- quote: "{q}"' for q in f["quotes"]]]
        out += [f"- situation ({s['lens']}): {s['situation']}" for s in f["sources"]]
        out += [f"- fix: {f['fix']}"] + [f"- validation: {f['validation']}: {f['reason']}"] * bool(f["reason"])
        out += [f"- disposition: {f['disposition']} by {f['by']}: {f['note']}"] * bool(f["disposition"]) + [""]
    out += ["## Jurors", "", "| Juror | Lens | By | Context | Valid | Attempts | Round |", "| --- | --- | --- | --- | --- | --- | --- |"]
    out += [f"| {n} | {j['lens']} | {j['by']} | {j['context']} | {'yes' if j['valid'] else 'no: ' + '; '.join(j['errors'])} | {j['attempts']} | {j['round']} |"
            for n, j in sorted(led["jurors"].items())]
    return "\n".join(out) + "\n"
