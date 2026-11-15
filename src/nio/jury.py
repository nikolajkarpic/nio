"""Jury gates (#27): collect lens outputs into a findings ledger, ground and dedup them, apply the refuter's
results and the dispositions, and compose the gate outcome. The ledger's data is .nio/specs/<slug>/jury/<gate>.json;
<gate>.md next to it is regenerated from it on every change, for people to read. Both are committed."""
import collections
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path

from nio import agents, evidence, records, spec

# the plan gate judges its four files against the spec and architecture.md: a change to either withdraws its approval
GATES = {"spec": ["spec.md"], "plan": ["plan.md", "contracts.md", "tests.md", "quickstart.md", "spec.md", "architecture.md"],
         # the tasks gate judges the planned tasks against the plan and the spec; `#### Fixes` sections are left out
         "tasks": ["tasks.md", "plan.md", "contracts.md", "tests.md", "quickstart.md", "spec.md"]}
KINDS = {"contradiction", "gap", "ambiguity", "untestable", "risk", "scope", "inconsistency"}
SEVERITY = ["minor", "major", "blocker"]  # ascending
CONTEXT = {"sufficient", "limited", "needs-more"}
EVIDENCE = {"observed", "inferred"}
DISPOSITIONS = {"spec-fix", "plan-fix", "spec-change", "open-question", "accepted-risk", "out-of-scope", "overruled", "fix-task",
                "held"}  # held: under auto, a fix the fix agent may not make alone (a [human] line, a scope cut, risk:)
FIXES = {"spec-fix", "plan-fix", "spec-change", "open-question", "fix-task"}  # settled by changing the judged artefact; a lens checks each
PLAN_ONLY = {"plan-fix", "spec-change"}  # spec-change: a plan finding rooted in the spec, sent to a change request
HUMAN_ONLY = {"accepted-risk", "out-of-scope", "overruled"}  # overruled: a final-check `not fixed` the human overrides (#58)
BY = {"agent", "grill", "human", "auto"}  # grill: the human answered a grill question; auto: the driver, under the human's grant
MAX_FINDINGS = 5
FIELDS = ["cites", "kind", "severity", "evidence", "quote", "situation", "fix"]
GAPS = ["missing", "partial", "contradicts", "unrequested"]  # the implementation gate's `gap` (CT-12); it also needs `where`
CLOSED = {"refuted", "dropped", "merged", "overruled", "noted"}  # never need a disposition
VERDICT = re.compile(r"^- (J-\d+):\s*(fixed|not fixed)\b\s*[—–:-]*\s*(.*)$")  # a fix verdict in a re-review (#52 FR-8)
CORE = {"spec": ["testability", "logic"], "plan": ["test-proof", "architecture-fit"], "tasks": ["executability"]}  # #47
HIGH_RISK = {"auth", "money", "data-deletion", "migration"}
PLAN_LENSES = {"security": {"auth", "pii"}, "risk-rollback": {"migration", "data-deletion"}}  # the plan gate's own triggers (#57 FR-5, FR-6)
# the implementation gate's trigger table, row for row (CT-8); consistency comes from the epic's diff, not a flag
IMPL_LENSES = {"adversary": {"external-input", "multi-party", "public-api"}, "security": {"auth", "pii", "secrets"},
               "risk-rollback": {"migration", "data-deletion"}}
MAX_RUNS = 6  # lens runs per gate, each juror counted; `jury.max_runs` in config overrides it (#47)
PR_RUNS = 8  # the pr gate's own default: its six core lenses and both risk lenses run without asking (2026-11-14-effort-jury)
PR_CORE = ["correctness", "conformance", "adversary", "consistency", "integration", "test-proof"]  # FR-4; test-proof: 2026-11-15 FR-41
MAX_ROUNDS = 2  # rounds per gate before the human rules what is open; `jury.max_rounds` in config overrides it (#129)
SKIPPED = "minor, skipped at the round cap"


def max_rounds(root):
    """`jury.max_rounds` from config, 2 when unset; anything but a whole number of at least 1 stops (#129 FR-3, FR-7)."""
    n = records.config(root).get("jury", {}).get("max_rounds", MAX_ROUNDS)
    if type(n) is not int or n < 1:
        raise ValueError(f"jury.max_rounds must be a whole number of at least 1, not {n!r}")
    return n


def impl_gate(gate):
    """An implementation gate: an epic's old `implementation-E-n`, or `pr`, the one on the whole effort diff."""
    return gate == "pr" or gate.startswith("implementation")


def lens_of(stem, gate):
    """The lens a juror's file stem names: `<gate>-<lens>`, with an epic part (`~E1`, `~rest`) at the pr gate over the
    split limit, and `-<n>` for an escalation juror."""
    return re.sub(r"(~\w+)?(-\d+)?$", "", stem[len(gate) + 1:])


def gates(root):
    """{gate: (files, core lenses)}: `GATES` and `CORE`, plus each extension step that declares a jury gate, as
    `<ext>.<step>` with its output and spec.md, the step's lenses as core (2026-11-15-extensions CT-9)."""
    from nio import extensions
    out = {g: (f, CORE[g]) for g, f in GATES.items()}
    for m in extensions.active(root, guard=False):
        for st in m.get("steps", []):
            if st.get("gate"):
                out[f"{m['name']}.{st['name']}"] = ([st["output"], "spec.md"], st["gate"]["lenses"])
    return out


def gate_arg(name):
    """argparse type: a known gate, `pr`, or an implementation name that `epic_gate` then accepts or refuses."""
    import argparse
    from nio import records
    try:
        known = gates(records.repo_root())
    except Exception:  # not in a repo: the built-in gates
        known = GATES
    if name in known or impl_gate(name):
        return name
    raise argparse.ArgumentTypeError(f"invalid choice: {name!r} (choose from {', '.join(sorted(known))}, implementation-E-n)")


def epic_gate(root, slug, gate, finished=True):
    """The epic `implementation-E-n` names, when every task in it, fix tasks included, is done; else ValueError (CT-1).
    `finished` False checks the name only: a finding can be ruled on while its fix tasks wait. `pr` is the whole effort:
    every task of it done."""
    from nio import implement
    if gate == "pr":
        left = undone(root, slug, "pr") if finished else []
        if left:
            raise ValueError(f"the effort is not finished: {', '.join(left)} not done")
        return "pr"
    m = re.fullmatch(r"implementation-(E-\d+)", gate)
    if not (m and any(t["epic"] == m.group(1) for t in implement.tasks_of(root, slug))):
        raise ValueError(f"the subject of the implementation gate must be an epic from tasks.md as implementation-E-n, not {gate!r}")
    left = undone(root, slug, m.group(1)) if finished else []
    if left:
        raise ValueError(f"epic {m.group(1)} is not finished: {', '.join(left)} not done")
    return m.group(1)


def undone(root, slug, epic):
    """The epic's tasks, fix tasks included, that aren't done."""
    from nio import flow, implement
    states = implement.status(root, slug, flow.read(root, slug)[1])
    return [t["id"] for t in implement.tasks_of(root, slug) if epic in ("pr", t["epic"]) and states.get(t["id"]) != "done"]


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
        elif out and (m := re.match(r"^- ([A-Za-z-]+):\s*(.*)$", line.strip())):
            # a guidance comment after two spaces, as in the template; a value's own "#22" stays
            out[-1][1].setdefault(m[1].lower(), []).append(re.sub(r"\s{2,}#\s.*$", "", m[2]).strip())
    return out


def unquote(q):
    """A quote's text: the outer marks off, and the escapes a juror puts inside (`\\"`, `\\\\`) undone. A source note after
    the closing mark, as `"..." (tasks.md, T-11)`, is no part of the quote (2026-11-15 FR-23)."""
    q = re.sub(r'(")\s*\([^()]*,\s*[A-Z]+-\d+\)$', r"\1", q.strip())
    q = q[1:-1] if len(q) > 1 and q[0] == q[-1] == '"' else q.strip('"')
    return re.sub(r'\\(["\\])', r"\1", q)


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
    findings, impl = [], impl_gate(gate)
    for head, f in blocks(lines):
        m = re.match(r"^(F\d+)\s+(.+)$", head)
        missing = [k for k in FIELDS + ["gap", "where"] * impl if not f.get(k)]
        if not m or missing:
            errs.append(f"finding `{head}`: needs `### F<n> <title>` and {missing or 'all fields'}")
            continue
        one = {k: f[k][0] for k in FIELDS if k != "quote"}
        one.update(ref=m[1], title=m[2], quotes=[unquote(q) for q in f["quote"]],
                   cites=[c.strip() for c in one["cites"].split(",") if c.strip()])
        checks = [("kind", KINDS), ("severity", SEVERITY), ("evidence", EVIDENCE)]
        if impl:  # a finding traces to an AC, FR or CT, and says what is wrong (gap) and where (CT-12)
            one.update(gap=f["gap"][0], where=f["where"][0], tampering=f.get("tampering", [""])[0] == "yes")
            checks.append(("gap", GAPS))
            if f.get("right"):
                one["right"] = f["right"][0]
                checks.append(("right", ["spec", "code"]))
        bad = [f"{k} `{one[k]}` must be one of {', '.join(sorted(allowed))}" for k, allowed in checks if one[k] not in allowed]
        if impl and not any(re.fullmatch(r"(AC|FR|CT)-\d+", c) for c in one["cites"]):
            bad.append("cites must hold an AC, FR or CT ID")
        if bad:
            errs.append(f"{m[1]}: " + "; ".join(bad))
            continue
        if f.get("run"):  # joined: two `run:` lines aren't a TC, so the human hears of them, where keeping one would lose one
            one["run"] = ", ".join(f["run"])
        if one["evidence"] == "inferred" and one["severity"] == "blocker":
            one["severity"] = "major"  # an inferred finding can't block on its own
        findings.append(one)
    if findings and re.match(r"none\W*$", (secs.get("Findings", "").strip().splitlines() or [""])[0].strip(), re.I):
        errs.append("`## Findings` holds none and findings")
    if not findings and secs.get("Findings", "").strip().rstrip(".!").lower() != "none" and not errs:
        errs.append("`## Findings` must hold findings or the single line `none`")
    if len(findings) > MAX_FINDINGS:
        errs.append(f"{len(findings)} findings; a lens returns at most {MAX_FINDINGS}")
    # fix verdicts, one per finding in a re-review's fix-check pack; merge checks them against the pack
    meta["verdicts"] = {}
    for line in secs.get("Verdicts", "").splitlines():
        if not line.startswith("- "):
            continue
        m = VERDICT.match(line.strip())
        if not m or not m[3].strip():
            errs.append(f"verdict `{line.strip()}`: write `- J-<n>: fixed | not fixed — <reason>`")
        elif m[1] in meta["verdicts"]:
            errs.append(f"{m[1]} has more than one verdict")
        else:
            meta["verdicts"][m[1]] = (m[2], m[3].strip())
    return meta, findings, errs


ID = re.compile(r"^[A-Z][A-Z0-9]*-\d+$")  # FR-1, AC-12, SC-3; anything else in `cites` is a label, e.g. a table row


def undefined(finding, text):
    """The IDs the finding cites that `text` doesn't hold."""
    return [c for c in finding["cites"] if ID.match(c) and not re.search(rf"(?<![\w-]){re.escape(c)}(?![\w-])", text)]


def grounded(finding, text, human="", quotes=True):
    """Every cited ID is in the gate's artefacts, and every quote is in them or in the human's own words (the intake and
    their grill answers, which the scope lens quotes). Whitespace-insensitive for quotes. Labels aren't checked: the
    quotes ground them, and every finding has at least one. At the implementation gate (`quotes` off) a quote is code,
    often abbreviated, so only the IDs count (CT-12, FR-23)."""
    flat = " ".join(text.split()) + "\n" + " ".join(human.split())
    return not undefined(finding, text) and (not quotes or all(" ".join(q.split()) in flat for q in finding["quotes"]))


def planned(name, text, keep=()):
    """A file as its gate judges it: tasks.md without its `#### Fixes` sections, except the fix tasks in `keep`, and
    without retired fix-task IDs; any other file as it is. Work added under Fixes after approval, or a fix task retired,
    doesn't withdraw it (#42 FR-27, FR-50; #126)."""
    if name == "quickstart.md":  # the `Read first` line finish adds is not an edit to the plan
        from nio import explain
        return explain.unread_first(text)
    if name != "tasks.md":
        return text
    kept = []
    if keep:  # fix tasks the caller still judges as planned: an edit to one reopens the gate (#126 FR-10)
        from nio import tasks
        found = tasks.parse(text)["tasks"]
        kept = [line for t in keep for line in found[t]["block"]]
    text = re.sub(r"^#### Fixes$.*?(?=^## |\Z)", "", text, flags=re.M | re.S)
    text = re.sub(r"^## E-\d+ PR fixes[ \t]*(?:\r?\n- (?:Tier|Effort):.*)*$", "", text, flags=re.M)  # the pr gate's closing epic: fix tasks, and its own rating
    return re.sub(r"\n\s*\n+", "\n\n", "\n".join([unretire(text), *kept])).rstrip() + "\n"  # the blank lines a Fixes section leaves don't count


def unretire(text):
    """`text` without retired fix-task IDs: an ID above every planned task's; retiring one doesn't count (#126 FR-9)."""
    top = max(map(int, re.findall(r"^### T-(\d+)\b", re.sub(r"<!--.*?-->", "", text, flags=re.S), re.M)), default=0)

    def unfix(m):
        ids = [x.strip() for x in m[2].split(",") if x.strip()]
        left = [x for x in ids if not (re.fullmatch(r"T-\d+", x) and int(x[2:]) > top)]
        return m[0] if left == ids else f"{m[1]}{', '.join(left)}]"
    return re.sub(r"^(retired:\s*\[)([^\]\n]*)\]", unfix, text, count=1, flags=re.M)


def artefact(root, slug, gate):
    """The gate's artefacts as one text, in a fixed order; empty when none exists. At the tasks gate, tasks.md as
    `planned` reads it."""
    text = lambda p: planned(p.name, p.read_text())
    return "\n".join(text(p) for p in (root / ".nio/specs" / slug / n for n in gates(root)[gate][0]) if p.exists())


LIKE = re.compile(r"^- (?:Binding|Like):\s*`([^`:]+)", re.M)


def sources(root, slug, gate, lens=""):
    """The files a juror at this gate is given, which are also the only files its quotes may come from (#57 FR-42,
    FR-43). The plan gate adds CLAUDE.md and every file a contract binds or a `Like:` line names."""
    folder = root / ".nio/specs" / slug
    if gate not in gates(root):  # an implementation gate: the spec and tasks, and what the epic's commits changed
        from nio import evidence
        changed = evidence.code_diff(root, *evidence.span(root, slug, epic_gate(root, slug, gate, finished=False)), "--name-only", "--diff-filter=d")
        return [p for p in [folder / n for n in ("spec.md", "contracts.md", "tasks.md")] + [root / n for n in changed] if p.is_file()]
    files = [folder / n for n in gates(root)[gate][0]]
    if gate == "plan":
        contracts = folder / "contracts.md"
        named = LIKE.findall(contracts.read_text()) if contracts.exists() else []
        files += [root / "CLAUDE.md"] + [root / n for n in dict.fromkeys(named)]
    reader = {("spec", "scope"): "scope", ("plan", "architecture-fit"): "architecture-fit"}.get((gate, lens))
    if reader:
        from nio import onboard
        files += onboard.doc_paths(root, reader, slug)
    return [p for p in dict.fromkeys(files) if p.is_file() and p.resolve().is_relative_to(root.resolve())]


def grounding(root, slug, gate, lens=""):
    """What a quote is checked against: the gate's artefact, plus at the plan gate the other files the lens reads."""
    return "\n".join(p.read_text() for p in sources(root, slug, gate, lens))


def blob(root, text, write=False):
    """The git blob hash of `text`, stored in git's objects when `write` (the version a round judged, #27 FR-23)."""
    args = ["git", "hash-object", "--stdin"] + ["-w"] * write
    try:
        r = subprocess.run(args, cwd=root, input=text, capture_output=True, text=True)
    except FileNotFoundError:
        raise ValueError("git is not installed (the jury needs a git repo)") from None
    if r.returncode or not r.stdout.strip():  # without a version no round can ever be approved: say so, don't hide it
        raise ValueError(f"git hash-object failed (the jury needs a git repo): {r.stderr.strip()}")
    return r.stdout.strip()


def human_words(root, slug):
    """The intake and the human's grill answers (questions and answers only: no headers, options or calls)."""
    intake = root / ".nio/specs" / slug / "intake.md"
    lines = [line for line in answers(root, slug) if line.startswith(("Question: ", "Answer: "))]
    return (intake.read_text() if intake.exists() else "") + "\n" + "\n".join(lines)


def version(led, rnd):
    return led.get("versions", {}).get(str(rnd))


def raised_round(f):
    """The last round a finding was raised in by a juror of its own: an escalation juror's (`<lens>-<n>`) is a vote,
    so a fix made while that round ran is checked against the version before it (2026-11-15 FR-29)."""
    return max((s["round"] for s in f["sources"] if s.get("round") and not re.search(r"-\d+$", s["juror"])), default=f["first_round"])


def worst(*levels):
    return max(levels, key=SEVERITY.index)


def rung(risk):
    """The gate's risk tier from the spec's risk flags (#27 FR-3): none low, any medium, the costly ones high."""
    return "low" if not risk else "high" if set(risk) & HIGH_RISK else "medium"


class Lines(list):
    lenses = ()


def plan(root, slug, gate, extra=(), pick=None):
    """(lines, ok): the lens runs this gate needs, why each runs, the tier, and the run budget. Not ok when the gate's
    own check fails or a lens has no card; over the cap is reported for the human to choose, not refused."""
    impl = impl_gate(gate)
    if impl:
        epic = epic_gate(root, slug, gate)
    elif gate not in gates(root):
        raise ValueError(f"only the {', '.join(CORE)} gates are built so far")
    ext = "." in gate
    if impl:
        notes = [""]
    elif ext:
        out = gates(root)[gate][0][0]
        if not (root / ".nio/specs" / slug / out).exists():
            return [f"no {out} yet: run {gate} first"], False
        notes = [""]
    elif gate == "plan":
        from nio import plan as plans  # plan.py reads the jury's ledger for `approved`
        errors, notes = plans.check(root, slug, gate=True)
        if errors:
            return [f"`nio check plan {slug} --gate` fails ({len(errors)} errors): finish the plan first"], False
    elif gate == "tasks":  # #42 FR-32, FR-42: the check first, then executability alone
        from nio import tasks
        errors, notes = tasks.check(root, slug)
        if errors:
            return [f"`nio check tasks {slug}` fails ({len(errors)} errors): the check must pass first"], False
    else:
        errors, notes = spec.check(root, slug, gate=True)
        if errors:
            return [f"`nio check spec {slug} --gate` fails ({len(errors)} errors): finish the grill first"], False
    meta, _ = records.parse(spec.path(root, slug)) if spec.path(root, slug).exists() else ({}, "")
    risk = [r for r in meta.get("risk") or [] if r in spec.RISKS]
    lenses = {lens: "core" for lens in (PR_CORE if gate == "pr" else ["conformance", "correctness"] if impl else gates(root)[gate][1])}
    table = IMPL_LENSES if impl else PLAN_LENSES if gate == "plan" else {k: v for k, v in spec.LENSES.items() if "(plan gate)" not in k}
    for lens, flags in table.items() if gate != "tasks" and not ext else []:
        if flags & set(risk):
            lenses.setdefault(lens, "risk: " + ", ".join(sorted(flags & set(risk))))
    if impl and gate != "pr":  # a module that existed before the epic is changed: a file modified from the parent of its first commit
        try:
            commits = evidence.commits_of(root, slug, epic)
        except ValueError:  # no commits, no diff
            commits = []
        old = commits and records.git(root, "diff", "--name-only", "--diff-filter=M", evidence.parent_of(root, commits[-1]), commits[0])
        if old:
            lenses.setdefault("consistency", f"changes {', '.join(old[:3])}" + (" ..." if len(old) > 3 else ""))
    if gate == "plan":
        contracts = (root / ".nio/specs" / slug / "contracts.md").read_text()
        stateful = [m[1] for m in re.finditer(r"^### (CT-\d+)\b(?:(?!^### ).)*?^- State:", contracts, re.M | re.S)]
        if stateful:
            lenses.setdefault("logic", f"state: {', '.join(stateful)}")
        if re.search(r"^## Data model\s*$", contracts, re.M):
            lenses.setdefault("risk-rollback", "data model")
    elif gate == "spec" and spec.SCOPE_NOTE in notes[0]:  # the check's own count, so the two never disagree
        lenses.setdefault("scope", f"more than {spec.SCOPE_FRS} FRs")
    for item in extra:  # the skill's own triggers (#27 FR-27), each with its reason
        lens, _, why = item.partition(":")
        if not why.strip():
            raise ValueError(f"--add {item}: give the reason, as lens:reason")
        lenses.setdefault(lens.strip(), why.strip())
    cards = agents.load(root)
    missing = [lens for lens in lenses if lens not in cards]
    cap = records.config(root).get("jury", {}).get("max_runs", PR_RUNS if gate == "pr" else MAX_RUNS)
    tier = rung(risk)
    over = len(lenses) > cap
    if pick is not None:  # the human's choice over the cap: the core lenses always run, the rest may be dropped (CT-8)
        picked = [x.strip() for x in pick.split(",") if x.strip()]
        core = [lens for lens, why in lenses.items() if why == "core"]
        unknown = [x for x in picked if x not in lenses]
        if unknown or [c for c in core if c not in picked]:
            raise ValueError(f"--pick {pick}: " + (f"not planned: {', '.join(unknown)}" if unknown else
                             f"cannot drop {', '.join(c for c in core if c not in picked)} (a core lens always runs)"))
        if not over:
            raise ValueError(f"--pick {pick}: the plan is {len(lenses)} runs, within the cap of {cap}; nothing to pick")
        led = load(root, slug, gate)
        held = [x for x in lenses if x not in picked and any(k.endswith(f"{gate}-{x}.md") for k in led.get("collected", {}))]
        if held:
            raise ValueError(f"--pick {pick}: cannot drop {', '.join(held)} (its output is already collected)")
        led.update(picked=picked, dropped=[x for x in lenses if x not in picked])
        save(root, led)
    out = Lines([f"tier: {tier}" + (f" ({', '.join(sorted(set(risk) & HIGH_RISK) or risk)})" if risk else ""),
           "lenses: " + ", ".join(f"{lens} ({why})" for lens, why in lenses.items()),
           f"runs: {len(lenses)} of {cap}" + (" — over the cap: the human chooses what runs" if len(lenses) > cap else "")])
    out.lenses = list(lenses)  # the names, so no caller parses them out of the display line (a `--add` reason can hold " (")
    if over:
        cfg = records.config(root)
        out += [f"run: {lens} ({why}) — {agents.resolve(cfg, lens, cards[lens][0], 'claude')[0]}" for lens, why in lenses.items() if lens in cards]
        out.append("choices: run all, or pick a set with --pick (no hit rates recorded yet)")
    if missing:
        out.append(f"missing cards: {', '.join(missing)} — the gate is blocked until they exist")
    return out, not missing


def phase(led):
    """first | re-review | final-owed | final (#52 FR-19, FR-24). The first review runs up to the first round the ledger
    recorded `rejected`; later rounds re-review. Once the human's one list is recorded and settled with a fix, one final
    fix check is owed, and it starts with the next collected round."""
    rejected = [r for r, o in led["recorded"] if o == "rejected"]
    if not rejected or led["round"] <= rejected[0]:
        return "first"
    lst = led.get("list")
    if lst and lst.get("final") and led["round"] >= lst["final"]:
        return "final"
    return "final-owed" if fixes(led) else "re-review"


def fixes(led):
    """IDs on the human's list fixed as a spec-fix, once every listed finding is settled: what the final check covers."""
    lst = led.get("list") or {}
    listed = [f for f in led["findings"] if f["id"] in lst.get("ids", [])]
    if not listed or any(f["status"] == "open" for f in listed):
        return []
    return [f["id"] for f in listed if f["disposition"] in FIXES and not (impl_gate(led["gate"]) and f["severity"] == "minor")]


def pack_ids(led, lens):
    """The findings a lens gives a fix verdict on in a re-review (#52 FR-7, FR-9): its own, disposed as fixed."""
    return [f["id"] for f in led["findings"] if f["status"] == "disposed" and f["disposition"] in FIXES
            and any(s["lens"] == lens for s in f["sources"])]


CITED = re.compile(r"(?<![\w-])([A-Z]+-\d+)(?![\w-])")


def parts(text):
    """({id: its whole block}, {section: the text outside any item}): an item's continuation lines (an AC's Observable)
    belong to it; tables, notes and prose belong to their section (#52 FR-14)."""
    items, secs, cur, sec, whole = {}, collections.defaultdict(list), None, "(front matter)", False
    for line in text.splitlines():
        if line.startswith("## "):
            sec, cur = line[3:].strip(), None
        elif m := spec.DEF.match(line):
            cur = m[1] or m[2]
            items[cur], whole = [line], line.startswith("### ")
        elif cur and (whole and not line.startswith("#") or line.startswith(" ") and line.strip()):  # a `### ID` item: to the next heading
            items[cur].append(line)
        else:
            cur = None
            if line.strip():
                secs[sec].append(line)
    return {k: "\n".join(v) for k, v in items.items()}, {k: "\n".join(v) for k, v in secs.items()}


def diff(root, slug, gate):
    """(led, (items before, sections before), (items after, sections after), changed IDs, changed sections, neighbours)
    since the version the last round judged. At the implementation gate a version is a commit: the changed IDs are the
    files changed since it, and the items are the spec's and contracts', as they read now."""
    led = load(root, slug, gate)
    versions = led.get("versions", {})
    if not versions:
        raise ValueError(f"no round of the {gate} jury has been collected for {slug}")
    if impl_gate(gate):
        judged = versions[max(versions, key=int)]
        if records.git(root, "cat-file", "-e", judged, full=True)[0]:
            raise ValueError(f"the judged {gate} commit isn't in this clone's git objects; re-run every lens")
        head = evidence.span(root, slug, gate.removeprefix("implementation-"))[1]
        items = evidence.items(root, slug)[0], {}
        return led, items, items, evidence.code_diff(root, judged, head, "--name-only"), [], []
    old = "\n".join(records.git(root, "cat-file", "-p", versions[max(versions, key=int)]))
    if not old:
        raise ValueError(f"the judged {gate} version isn't in this clone's git objects; re-run every lens")
    before, after = parts(old), parts(artefact(root, slug, gate))
    flat = lambda t: " ".join(t.split())
    ids = sorted(i for i in before[0].keys() | after[0].keys() if flat(before[0].get(i, "")) != flat(after[0].get(i, "")))
    secs = [s for s in dict.fromkeys([*before[1], *after[1]]) if flat(before[1].get(s, "")) != flat(after[1].get(s, ""))]
    near = {c for i in ids for c in CITED.findall(after[0].get(i, ""))}  # what a changed item cites...
    near |= {i for i, t in after[0].items() if set(CITED.findall(t)) & set(ids)}  # ...and what cites it
    near |= {c for s in secs for c in CITED.findall(after[1].get(s, ""))}  # a changed table's or note's cites
    neighbours = sorted(near & after[0].keys() - set(ids))
    return led, before, after, ids, secs, neighbours


def fix_ids(root, slug):
    """IDs of the tasks under `#### Fixes` in tasks.md now."""
    from nio import tasks
    p = tasks.path(root, slug)
    return [i for i, t in tasks.parse("\n".join(records.parse(p)[1]))["tasks"].items() if t["fix"]] if p.exists() else []


def fixes_added(root, slug, gate):
    """Fix tasks added since the last collected round (CT-4); they never re-run a lens. `[]` outside the tasks gate."""
    if gate != "tasks":
        return []
    led = load(root, slug, gate)
    seen = led.get("fixes", {}).get(str(led["round"]), [])
    return [i for i in fix_ids(root, slug) if i not in seen]


def awaits_fix_verdict(f):
    return f["status"] == "disposed" and f["disposition"] == "fix-task"


def changed(root, slug, gate):
    """(changed IDs, lenses to re-run, neighbour IDs, changed sections) since the version the last round judged
    (#27 FR-19, FR-23; #52 FR-14). In the first review the lenses to re-run are every lens that blocked, plus any lens
    with a finding citing a changed ID; after it, every lens with a fix to check. Once the gate was approved or closed,
    every lens that judged it re-checks the change. At the implementation gate conformance also re-runs for a CLI finding
    with a fix to judge, since it drives `join`, and when nothing else would start the round the fixes need (CT-20)."""
    led, _, _, ids, secs, neighbours = diff(root, slug, gate)
    lenses = {s["lens"] for f in led["findings"] for s in f["sources"] if s["lens"] not in ("deferred", "cli")}
    if any(o == "rejected" for _, o in led["recorded"]):  # a re-review or the final check is next
        rerun = {lens for lens in lenses if pack_ids(led, lens)}
    else:
        rerun = {lens for lens, js in votes(led).items() if any(v == "block" for _, v in js)}
        rerun |= {s["lens"] for f in led["findings"] if set(f["cites"]) & set(ids) for s in f["sources"] if s["lens"] not in ("deferred", "cli")}
    if not rerun and (ids or secs) and led["recorded"] and (
            led["recorded"][-1][1] in ("approved", "human", "closed") or (gate in gates(root) and any(o == "rejected" for _, o in led["recorded"]))):
        # an approved or closed gate whose artefact changed since (a change request, #57 FR-35, FR-47): every lens that
        # judged it re-checks only what changed, from its fix-check pack
        rerun = set(votes(led))
    if impl_gate(gate) and any(o == "rejected" for _, o in led["recorded"]):
        if (ids and not rerun) or any(awaits_fix_verdict(f) and any(s["lens"] == "cli" for s in f["sources"]) for f in led["findings"]):
            rerun.add("conformance")
    return ids, sorted(rerun), neighbours, secs


def fixcheck(root, slug, gate, lens, blocker=None):
    """The fix-check pack for one lens in a re-review or the final fix check (#52 FR-7, FR-13, FR-15): its fixed findings,
    the changed text before and after, the neighbours, and the findings the human ruled on. With `blocker`, the pack for
    an escalation juror, who judges only that blocker. collect checks verdicts against the same `pack_ids`."""
    led, before, after, ids, secs, neighbours = diff(root, slug, gate)
    by_id = {f["id"]: f for f in led["findings"]}
    mine = [by_id[i] for i in pack_ids(led, lens)]
    impl = impl_gate(gate)
    if blocker and blocker not in by_id:
        raise ValueError(f"no finding {blocker} in the {gate} ledger of {slug}")
    out = [f"# Fix-check pack: {lens}, {gate} gate of {slug}", "",
           "This is a fix check, not a review. You get your own findings from the last round and the code's diff since the "
           "commit you judged. You may open any file of the project to read it." if impl else
           "This is a fix check, not a review. You get your own findings from the last round, what changed since you judged "
           "it, and the items around the changes; nothing else of the artefact. Don't open the artefact itself.", ""]
    if blocker:
        f = by_id[blocker]
        out += ["You are an extra juror for one new blocker. Judge only whether it holds, from the text here. If it holds, "
                "raise it as F1 with the same cites; if not, `## Findings` is `none`. Give no verdicts.", "",
                "## The blocker to judge", f"### {f['id']} {f['title']}", f"- cites: {', '.join(f['cites'])}",
                *[f'- quote: "{q}"' for q in f["quotes"]], *[f"- situation: {s['situation']}" for s in f["sources"][:1]], ""]
    else:
        out += ["Give exactly one verdict per finding below, in a `## Verdicts` section before `## Findings`: "
                "`- J-<n>: fixed | not fixed — <reason>`. Raise a new finding only if it is a blocker you can show from the "
                "text here (observed); a new major or minor is kept only as a note. Stop once every finding has a verdict.", "",
                "## Your findings to check", *(["None: give no verdicts.", ""] if not mine else [])]
        for f in mine:
            out += [f"### {f['id']} {f['title']}", f"- cites: {', '.join(f['cites'])}", *[f'- quote: "{q}"' for q in f["quotes"]],
                    *[f"- situation: {s['situation']}" for s in f["sources"] if s["lens"] == lens][:1],
                    f"- fix asked: {f['fix']}", f"- what was done: {f['note']}",
                    # what it cites, as it reads now: a fix made rounds ago isn't among the changed items (#58)
                    *(["- what it cites, now:", *[after[0][c] for c in f["cites"] if c in after[0]]] if any(c in after[0] for c in f["cites"]) else []), ""]
    ruled = [f for f in led["findings"] if f["disposition"] in HUMAN_ONLY]
    out += ["## Settled by the human: don't raise these again", *([f"- {f['id']} {f['title']} ({f['disposition']}: {f['note']})" for f in ruled] or ["None."]), ""]
    if impl:
        judged = version(led, led["round"])
        return out + [f"## Diff since {judged[:8]}", "", *evidence.code_diff(root, judged, evidence.span(root, slug, gate.removeprefix("implementation-"))[1])]
    out += ["## Changed items, before and after", ""]
    for i in ids:
        out += [f"### {i}", "Before:", before[0].get(i, "(new)"), "After:", after[0].get(i, "(removed)"), ""]
    for s in secs:
        out += [f"### Section {s}: text outside its items", "Before:", before[1].get(s, "(new)"), "After:", after[1].get(s, "(removed)"), ""]
    out += ["## Neighbours: items that cite a changed item or that it cites (current text)", "",
            *([after[0][i] for i in neighbours] or ["None."])]
    if added := fixes_added(root, slug, gate):
        from nio import tasks
        out += ["", "## Tasks added under Fixes (current text)", ""]
        for t in added:
            out += [*tasks.show(root, slug, t), ""]
    return out


def option_labels(raw):
    """{number: text} from an Options block. One option per line is read line by line (a wrapped line continues the
    option above it); options run together on one line split only at the next number in sequence, so "Cap at 5. Then"
    stays whole.
    ponytail: on one line, an option that itself contains " 2. " still splits early; the grill logs one per line."""
    lines = [line.strip() for line in raw.splitlines() if line.strip()]
    if lines and lines[0].startswith("1. "):
        labels = {}
        for line in lines:
            if line.startswith(f"{len(labels) + 1}. "):
                labels[str(len(labels) + 1)] = line[len(f"{len(labels) + 1}. "):]
            else:
                labels[str(len(labels))] += " " + line
        if len(labels) > 1:  # else the options run together on a line: split them below
            return labels
    text = " ".join(raw.split())
    labels, n = {}, 1
    first = re.search(r"(?:^|\s)1\. ", text)  # "(pick one) 1. A 2. B" too
    if not first:
        return labels
    start = first.end()
    while True:
        nxt = text.find(f" {n + 1}. ", start)
        labels[str(n)] = text[start:nxt if nxt >= 0 else None].strip()
        if nxt < 0:
            return labels
        start, n = nxt + len(f" {n + 1}. "), n + 1


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
        opts = re.search(r"^Options[^:]*:[ \t]*(.*(?:\n(?!Answer:|Patched:).*)*)", entry, re.M)
        labels = option_labels(opts[1]) if opts else {}
        if re.fullmatch(r"[\d,\s]+|\d+(?:, \d+)* and \d+", given):  # "1", "1, 2 and 4": options picked by number
            given = "; ".join(re.sub(r" \(recommended\)", "", labels.get(n, n), flags=re.I) for n in re.findall(r"\d+", given))
        out += [entry.splitlines()[0], q[0], f"Answer: {given} [human]", ""]
    return out


def moved(root, slug, gate, run, led):
    """CT-3: new lens outputs in a run whose judged version changed since its packs were written are refused."""
    sj = root / ".nio/runs" / run / "jury/packs/step.json"
    if not sj.exists() or json.loads(sj.read_text())["version"] == version_now(root, slug, gate):
        return
    for path in (root / ".nio/runs" / run / "jury").glob(f"{gate}-*.md"):
        if not re.fullmatch(rf"{gate}-refuter(-\d+)?", path.stem) and led["collected"].get(f"{run}/{path.name}") != hashlib.sha256(path.read_bytes()).hexdigest():
            raise ValueError(f"the {gate} changed after {run}'s packs were written: restore it, or start a new run (nio jury next without --run)")


def ask_refuter(root, slug, gate, run, ids):
    """Record the findings the refuter is asked about in `run`; a batch asked after the last was answered is the run's
    next one, with its own pack and output file (2026-11-15 FR-27)."""
    led = load(root, slug, gate)
    if not led.get("asked", {}).get(run):
        led.setdefault("batches", {})[run] = led.get("batches", {}).get(run, 0) + 1
    led.setdefault("asked", {})[run] = sorted(set(led.get("asked", {}).get(run, [])) | set(ids))
    save(root, led)


def collect(root, slug, gate, run, expect=(), tier=None, ask=True):
    """Merge the run's new lens outputs into the ledger, then apply the refuter's output if present.
    Returns lines to print, ending with the refuter batch when blocker or major findings still need validating."""
    impl = impl_gate(gate)
    if impl:
        epic = epic_gate(root, slug, gate)
        led = load(root, slug, gate)
        if "picked" not in led and any("over the cap" in x for x in plan(root, slug, gate)[0]):
            raise ValueError(f"{gate} plans more runs than the cap: record the human's pick first (nio jury plan {slug} {gate} --pick <lens,lens>)")
        for path in sorted((root / ".nio/runs" / run / "jury").glob(f"{gate}-*.md")):  # T-20: a lens the human didn't pick is refused (FR-16)
            lens = lens_of(path.stem, gate)  # an escalation juror (-2, -3) counts as its lens
            if "picked" in led and lens != "refuter" and lens not in led["picked"]:
                raise ValueError(f"{path.name}: lens {lens} was not picked for {gate} (picked: {', '.join(led['picked'])})")
        # a round judges the epic's last commit; the cites are checked against the spec and contracts (CT-12)
        commit = evidence.span(root, slug, epic)[1]
        moved(root, slug, gate, run, led)
        evidence.current(root, slug, epic, evidence.load(root, run))  # before the ledger marks anything collected: a retry must still join
        text = ground = "\n".join(p.read_text() for p in (root / ".nio/specs" / slug / n for n in ("spec.md", "contracts.md")) if p.exists())
        human = ""
        planned = plan(root, slug, gate)[0].lenses
        expect = set(expect) | {x for x in planned if x not in led.get("dropped", [])}
    elif gate not in gates(root):
        raise ValueError(f"gate must be one of {sorted(gates(root))}")
    else:
        led = load(root, slug, gate)
        text = artefact(root, slug, gate)
        if not text:
            raise ValueError(f"no {gate} artefact under .nio/specs/{slug}/ ({', '.join(gates(root)[gate][0])})")
        moved(root, slug, gate, run, led)
        human = human_words(root, slug)
        ground = lambda lens="": grounding(root, slug, gate, lens)
    led["expect"] = sorted(set(led["expect"]) | set(expect))
    led["tier"] = tier or led["tier"]
    judged = lambda write=False: commit if impl else blob(root, text, write)
    jury = root / ".nio/runs" / run / "jury"
    out, new = [], []
    for path in sorted(jury.glob(f"{gate}-*.md")):
        key, sha = f"{run}/{path.name}", hashlib.sha256(path.read_bytes()).hexdigest()
        if not re.fullmatch(rf"{gate}-refuter(-\d+)?", path.stem) and led["collected"].get(key) != sha:
            led["collected"][key] = sha
            new.append(path)
    if new and gate == "plan" and (st := state(root, slug, led))[0] in ("with-human", "waiting-on-spec"):
        raise ValueError(st[1])  # no round runs until the human rules, or the spec change is settled (#57 FR-50)
    # a retry: every new file re-runs a juror that failed (invalid, or asked for more context) in this round, on this
    # same version. It joins the round its juror failed in instead of starting one (#55).
    # An escalation juror (`<gate>-<lens>-2`, #105) joins the round its lens judged too (#129 FR-4).
    jj = led["jurors"]
    base = lambda p: re.sub(r"-\d+$", "", p.stem)
    retry = new and all(p.stem in jj and jj[p.stem]["round"] == led["round"] and jj[p.stem]["version"] == judged()
                        and (not jj[p.stem]["valid"] or jj[p.stem]["context"] == "needs-more")
                        or base(p) != p.stem and jj.get(base(p), {}).get("round") == led["round"] and jj[base(p)]["version"] == judged()
                        for p in new)
    if new and retry:
        out += merge(led, new, gate, slug, ground, human)
    elif new:
        led["round"] += 1
        # the artefact this round judges, kept in git's object store so a later round can tell what changed (FR-23)
        led.setdefault("versions", {})[str(led["round"])] = judged(write=True)
        if gate == "tasks":
            led.setdefault("fixes", {})[str(led["round"])] = fix_ids(root, slug)
        if fixes(led) and not led["list"].get("final"):  # the round that starts the one final fix check (#52 FR-24)
            led["list"]["final"] = led["round"]
        out += merge(led, new, gate, slug, ground, human)
    review = phase(led) in ("re-review", "final")
    for f in led["findings"]:  # what the grounding sources now hold may ground a finding dropped earlier
        if f["status"] == "dropped" and any(grounded(f, ground(s["lens"]) if callable(ground) else ground, human, not impl) for s in f["sources"]):
            f.update(status="open", reason="", validation="pending" if f["severity"] != "minor" else "grounded")
            if review and f["severity"] != "blocker":  # after the first review, a note (#52 FR-12)
                f.update(status="noted", validation="grounded")
            out.append(f"revived {f['id']} {f['title']} (now grounded)")
    if gate == "spec":
        out += deferred(led, root, slug)
    refuter = jury / f"{gate}-refuter-{led.get('batches', {}).get(run, 1)}.md"  # the batch asked; an older driver's plain name too
    refuter = refuter if refuter.exists() else jury / f"{gate}-refuter.md"
    if refuter.exists():
        sha = hashlib.sha256(refuter.read_bytes()).hexdigest()
        if led["collected"].get(f"{run}/{refuter.name}") != sha:
            asked = led.get("asked", {}).get(run)
            if not asked:
                raise ValueError(f"refuter output before its batch: {refuter} was not asked for; delete it and call again")
            led["collected"][f"{run}/{refuter.name}"] = sha
            out += refute(led, refuter, asked)
            led["asked"].pop(run)  # answered: a later change to the file has no batch until the next one prints
    save(root, led)
    if impl:  # the conformance lens's matches are joined to the results (CT-21); each review round re-judges them on its results
        # at the pr gate over the split limit each part's conformance juror matches its own ACs: join them all
        outs = [p for p in new if lens_of(p.stem, gate) == "conformance" and not re.search(r"-\d+$", p.stem)]
        usable = [p for p in outs if (j := led["jurors"].get(p.stem) or {}).get("valid") and j.get("context") != "needs-more"]
        results = evidence.load(root, run)
        if usable or (review and led.get("matched")):
            found = [m[1] for p in usable if (m := re.search(r"^## Matches[ \t]*\n(.*?)(?=^## |\Z)", p.read_text(), re.M | re.S))]
            evidence.join(root, slug, epic, "\n".join(found).splitlines(), results)
            evidence.save(root, run, results)
    led = load(root, slug, gate) if impl else led
    pending = [f for f in led["findings"] if f["validation"] == "pending" and f["status"] in ("open", "disposed")]
    if pending:
        out += ["", f"## Refuter batch: confirm or refute each, in .nio/runs/{run}/jury/{gate}-refuter.md", ""]
        for f in pending:
            out += [f"### {f['id']} {f['title']}", f"- kind: {f['kind']}, severity: {f['severity']}, cites: {', '.join(f['cites'])}"]
            out += [f'- quote: "{q}"' for q in f["quotes"]]
            out += [f"- situation ({s['lens']}): {s['situation']}" for s in f["sources"]] + [f"- fix: {f['fix']}", ""]
        if ask:
            ask_refuter(root, slug, gate, run, [f["id"] for f in pending])
    if impl:  # the runs the findings asked for are made now; the ones that weren't are the human's to see (CT-11)
        out += [f"listed for the human: {r['request']} (finding {r['finding']}): {r['why']}"
                for r in evidence.requested(root, led, run)[1] if r["round"] == led["round"]]
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
    out, rnd = [], led["round"]
    review = phase(led) in ("re-review", "final")
    packs, verdicts = {}, collections.defaultdict(list)
    for path in paths:
        meta, findings, errs = parse_lens(path, gate, slug)
        lens = lens_of(path.stem, gate)  # the file name gives the lens; `-2` marks an escalation juror
        if meta.get("lens") and meta["lens"] != lens:
            out.append(f"lens    {path.name}: front matter says {meta['lens']}; filed under {lens}")
        # after the first review a lens answers a fix verdict per finding in its pack; an escalation juror
        # (`<gate>-<lens>-2`) judges only the new blocker, and a lens asking for more context is re-run anyway
        if review and not errs and not re.search(r"-\d+$", path.stem) and meta.get("context") != "needs-more":
            want = packs.setdefault(lens, set(pack_ids(led, lens)))
            # the lens's own findings another lens's verdict fixed earlier this round were in the pack it was handed (#55)
            handed = want | {f["id"] for f in led["findings"] if f.get("fixed_in") == rnd and any(s["lens"] == lens for s in f["sources"])}
            errs += [f"no verdict for {i}, which is in the fix-check pack" for i in sorted(want - set(meta["verdicts"]))]
            errs += [f"{i} is not in the fix-check pack" for i in sorted(set(meta["verdicts"]) - handed)]
            if not errs:
                for i, (v, why) in meta["verdicts"].items():
                    verdicts[i].append((path.stem, v, why))
        juror = led["jurors"].setdefault(path.stem, {"attempts": 0})
        if juror.get("version") != version(led, rnd):  # attempts count per version: a new version earns a fresh retry
            juror["attempts"] = 0
        juror.update(lens=lens, by=meta.get("by", ""), context=meta.get("context", ""),
                     valid=not errs, errors=errs, round=rnd, attempts=juror["attempts"] + 1, version=version(led, rnd))
        if errs:
            out += [f"INVALID {path.name}: {e}" for e in errs]
            continue
        if juror["context"] != "needs-more":  # the last round this juror actually judged
            juror["judged"] = rnd
        said = [add(led, f, path.stem, juror["lens"], rnd, text(juror["lens"]) if callable(text) else text, human, review) for f in findings]
        out += said
        if said and all(x.startswith("dropped") for x in said):  # FR-24: a juror whose every finding is ungrounded is re-run
            juror.update(valid=False, errors=["every finding is ungrounded"])
            out.append(f"INVALID {path.name}: every finding is ungrounded")
    if review:
        return out + apply_verdicts(led, verdicts, rnd)
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


def apply_verdicts(led, verdicts, rnd):
    """After the first review only a verdict settles a fix (#52 FR-10, FR-11, FR-25): silence never marks a finding fixed.
    One `not fixed` among a finding's verdicts reopens it, with one failed round at most per round; a blocker found not
    fixed goes back to the refuter before it can start another round."""
    out, by_id = [], {f["id"]: f for f in led["findings"]}
    for i, given in sorted(verdicts.items()):
        f = by_id[i]
        if f["status"] == "open" and f["last_round"] == rnd:  # raised again in this very round: a `fixed` can't close it
            out.append(f"not fixed {i} {f['title']} (raised again this round)")
            continue
        if any(v == "not fixed" for _, v, _ in given):
            if f["last_round"] < rnd:
                f["rounds"] += 1
            f.update(status="open", baseline="unchanged", disposition="", by="", note="", last_round=rnd,
                     reason="; ".join(f"{j}: {why}" for j, v, why in given if v == "not fixed"))
            if f["severity"] == "blocker":
                f["validation"] = "pending"
            out.append(f"not fixed {i} {f['title']}")
        elif f["status"] != "fixed":
            f.update(status="fixed", baseline="absent", fixed_in=rnd)
            out.append(f"fixed   {i} {f['title']}")
    return out


def key(f):
    ids = frozenset(c for c in f["cites"] if ID.match(c))
    return f["kind"], ids or frozenset(f["cites"])


def same(g, f):
    """Same kind and cited IDs, and labels that don't point elsewhere: `state table row asking` and `the non-goal …`
    are two problems even when both cite FR-3. A side without labels matches either way."""
    labels = lambda x: {c.lower() for c in x["cites"] if not ID.match(c)}
    return key(g) == key(f) and (not labels(g) or not labels(f) or bool(labels(g) & labels(f)))


def add(led, f, juror, lens, rnd, text, human="", review=False):
    impl = impl_gate(led["gate"])
    source = {"juror": juror, "lens": lens, "situation": f["situation"], "severity": f["severity"], "round": rnd}
    if f.get("run"):  # on the source: two jurors on one finding may each ask for a run, and each round has its own (CT-11)
        source["run"] = f["run"]
    # same kind and the same cited IDs; near-duplicates are the refuter's `same-as`. One juror's findings in one round
    # are distinct problems by construction, so they never merge with each other.
    match = next((g for g in led["findings"] if g["status"] != "merged" and same(g, f)
                  and not any(s["juror"] == juror and s.get("round") == rnd for s in g["sources"])), None)
    if not match and re.search(r"-\d+$", juror) and any(g["severity"] == "blocker" and g["validation"] == "confirmed" and g["status"] == "open"
                                                         and any(s["lens"] == lens for s in g["sources"]) for g in led["findings"]):
        led.setdefault("notes", []).append({"juror": juror, "title": f["title"], "round": rnd})  # FR-26: a vote, not a finding
        return f"note    {juror}: {f['title']} (an escalation juror's; no finding)"
    if not match:
        ok = grounded(f, text, human, not impl)
        g = {"id": f"J-{len(led['findings']) + 1}", **{k: f[k] for k in ("title", "kind", "severity", "cites", "evidence", "quotes", "fix")},
             "sources": [source], "validation": ("pending" if f["severity"] != "minor" else "grounded") if ok else "ungrounded",
             "reason": "" if ok else f"{', '.join(undefined(f, text))} not defined by the spec or contracts" if impl else "a cited ID or quote is not in the artefact", "status": "open" if ok else "dropped",
             "disposition": "", "by": "", "note": "", "baseline": "new", "rounds": 0, "first_round": rnd, "last_round": rnd}
        g.update({k: f[k] for k in ("gap", "where", "tampering", "right") if k in f})  # the implementation gate's (CT-12)
        if ok and review and f["severity"] != "blocker":  # after the first review only a blocker counts (#52 FR-12)
            g.update(status="noted", validation="grounded", reason="raised in a re-review below blocker: a note only")
        led["findings"].append(g)
        label = "new    " if g["status"] == "open" else g["status"]
        return f"{label} {g['id']} [{g['severity']}/{g['kind']}] {g['title']}" + (" (ungrounded)" if not ok else " (a note only)" * (g["status"] == "noted"))
    if match["status"] == "dropped":  # reported again: it stays dropped unless the artefact now grounds it
        if not grounded(f, text, human, not impl):
            match["last_round"] = rnd
            return f"dropped {match['id']} {match['title']} (still ungrounded)"
        match.update({k: f[k] for k in ("cites", "quotes")}, status="open", reason="",
                     validation="pending" if f["severity"] != "minor" else "grounded")
        if review and f["severity"] != "blocker":  # revived after the first review: a note, like a new one (#52 FR-12)
            match.update(status="noted", validation="grounded")
    # reported again on a newer version than it was last raised on: the fix didn't take, a failed round
    if match["last_round"] < rnd and version(led, match["last_round"]) not in (None, version(led, rnd)):
        match["baseline"] = "unchanged"
        if match["status"] in ("fixed", "open", "overruled") or match["disposition"] in FIXES:
            match.update(status="open", rounds=match["rounds"] + 1, disposition="", by="", note="")
    elif match["status"] == "fixed":  # raised again on the very version it was marked fixed on: it isn't fixed
        match.update(status="open", baseline="unchanged")
    match["last_round"] = rnd
    match["sources"] = [s for s in match["sources"] if s["juror"] != juror] + [source]
    if f.get("tampering"):
        match["tampering"] = True
    cli = any(s["lens"] == "cli" for s in match["sources"])  # CT-20: a CLI finding stays confirmed, no refuter
    raised = worst(match["severity"], f["severity"])
    if cli:
        pass
    elif raised != match["severity"] and (match["validation"] == "grounded" or raised == "blocker"):
        match["validation"] = "pending"  # a blocker claim is the refuter's to judge, whatever validated the lesser one
    match["severity"] = raised
    if review and raised == "blocker" and not cli and match["status"] in ("open", "noted"):  # #52 FR-11, FR-13: a blocker
        match.update(status="open", validation="pending")  # raised again after the first review goes back to the refuter
    return f"{match['baseline']:<7} {match['id']} [{match['severity']}/{match['kind']}] {match['title']} (+{lens})"


def record_cli(root, slug, gate, findings, origin=None):
    """Put the CLI's own findings in the ledger as confirmed (CT-20, FR-24): no refuter and no vote, since they are observed
    and no juror raised them. A repeat with the same title adds none. The new entries' IDs. `origin` is the caller,
    `checks` or `join`, which gives the fix verdict no juror can on its own entries only: the other reports different
    findings, so its silence says nothing. Gone from `findings` is fixed; still there is not fixed, the same J-n."""
    led = load(root, slug, gate)
    out = []
    reported, judged = {f["title"] for f in findings}, False
    for g in led["findings"] if origin else []:
        if g.get("origin") != origin:
            continue
        if g["title"] in reported and (awaits_fix_verdict(g) or g["status"] == "fixed"):  # a fix that came undone counts too
            g.update(status="open", baseline="unchanged", disposition="", by="", note="", rounds=g["rounds"] + 1, last_round=led["round"],
                     reason="the CLI still reports it after its fix task")
            judged = True
        elif g["title"] not in reported and (awaits_fix_verdict(g) or g["status"] in ("open", "noted")):  # gone after a good re-run too
            g.update(status="fixed", baseline="absent", fixed_in=led["round"])
            judged = True
    for f in findings:
        if any(g["title"] == f["title"] and any(s["lens"] == "cli" for s in g["sources"]) for g in led["findings"]):
            continue
        out.append(f"J-{len(led['findings']) + 1}")
        led["findings"].append({
            "id": out[-1], "title": f["title"], "kind": "gap", "severity": f["severity"], "cites": [c.strip() for c in f["cite"].split(",") if c.strip()],
            "evidence": "observed", "quotes": [], "fix": f.get("fix", ""), "gap": f["gap"], "where": f["where"], "tampering": bool(f.get("tampering")), "origin": origin,
            "sources": [{"juror": "cli", "lens": "cli", "situation": f.get("situation", f["gap"]), "severity": f["severity"], "round": led["round"]}],
            "validation": "confirmed", "reason": "the CLI's own check; no refuter", "status": "open", "disposition": "", "by": "", "note": "",
            "baseline": "new", "rounds": 0, "first_round": led["round"], "last_round": led["round"]})
    if out or judged:
        save(root, led)
    return out


def refute(led, path, asked):
    out, by_id = [], {f["id"]: f for f in led["findings"]}
    for head, f in blocks(path.read_text().splitlines()):
        fid = head.split()[0] if head else ""
        g = by_id.get(fid)
        if not g or fid not in asked or g["validation"] != "pending":
            continue
        target = by_id.get((f.get("same-as") or [""])[0])
        if target and target is not g and target["status"] in ("open", "disposed"):  # never into a closed finding
            target["sources"] += [s for s in g["sources"] if s["juror"] not in {t["juror"] for t in target["sources"]}]
            raised = worst(target["severity"], g["severity"])
            if raised != target["severity"] and target["validation"] == "grounded":  # a confirmed one stays confirmed (FR-28)
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
            out.append(f"INVALID refuter block {fid}: needs `- result: confirmed | refuted` and `- reason:`"
                       + (f" (same-as {target['id']} is {target['status']}: only an open or disposed finding takes a merge)" if target else ""))
    return out


def dispose(root, slug, gate, fid, disposition, by, note, change="", routed=False, ruled=False):
    """`fid` one ID or comma-separated IDs, `note` a string or a list (one, or one per ID); all checks pass before the one save."""
    ids = fid.split(",")
    notes = [note] if isinstance(note, str) else list(note)
    if "" in ids or len(set(ids)) != len(ids):
        raise ValueError(f"IDs must be distinct and non-empty: {fid}")
    if len(notes) not in (1, len(ids)):
        raise ValueError(f"{len(notes)} notes for {len(ids)} findings; give one note, or one per finding in order")
    led = load(root, slug, gate)
    if by == "auto":  # 2026-11-15 FR-47: the driver acts for the human only on an effort whose auto flag the human granted
        from nio import flow
        if not flow.load(root, slug)[0]["auto"]:
            raise ValueError(f"--by auto needs {slug}'s auto flag on")
    bad = []
    for i, n in zip(ids, notes * len(ids) if len(notes) == 1 else notes):
        try:
            _dispose_one(root, slug, gate, led, i, disposition, by, n, change, routed, ruled)
        except ValueError as e:
            if len(ids) == 1:
                raise
            bad.append(f"{i}: {e}")
    if bad:
        raise ValueError("\n".join(bad))
    save(root, led)
    return ids


def _dispose_one(root, slug, gate, led, fid, disposition, by, note, change, routed, ruled=False):
    f = next((g for g in led["findings"] if g["id"] == fid), None)
    if not f:
        raise ValueError(f"no finding {fid} in the {gate} ledger of {slug}")
    if disposition == "reopen":  # 2026-11-15 FR-25: the human's ruling on a finding dropped as ungrounded
        if by != "human":
            raise ValueError("reopen is the human's call (--by human)")
        if f["status"] != "dropped":
            raise ValueError(f"{fid} is {f['status']}; reopen takes a dropped finding")
        f.update(status="open", validation="pending", reason="", ruling=note)
        return
    if disposition not in DISPOSITIONS or by not in BY or not note.strip():
        raise ValueError(f"disposition must be one of {sorted(DISPOSITIONS)}, --by one of {sorted(BY)}, and --note is required")
    if fid in batch_open(led) and by not in ("human", "auto") and not routed:  # #129: the capped batch is the human's to rule
        raise ValueError(f"{fid} is in the capped batch; only the human rules it (nio jury rule, or --by human)")
    if f.get("tampering") and by != "human" and not routed:  # only the human disposes of it; `tasks.append_fix` alone routes it to its fix task (FR-26)
        raise ValueError(f"{fid} is test tampering; only the human disposes of it (--by human)")
    if disposition in PLAN_ONLY and gate != "plan" and not (disposition == "spec-change" and gate == "pr"):  # FR-39 at pr
        raise ValueError(f"`{disposition}` belongs to the plan gate")
    if disposition == "fix-task":
        from nio import tasks
        if not impl_gate(gate):
            raise ValueError("`fix-task` belongs to the implementation gate")
        if not tasks.fixes_of(root, slug, gate, fid):
            raise ValueError(f"`fix-task` needs a task whose `From:` names {fid}; the rejected outcome appends it")
    if disposition == "spec-change":  # #57 FR-34, FR-41: the change record the finding waits on
        path, meta = change_record(root, change)
        if not path:
            raise ValueError(f"spec-change needs --change naming a change record; `{change}` isn't one")
        note = f"{change}: {note}"
    if disposition in HUMAN_ONLY and by not in ("human", "auto"):
        raise ValueError(f"{disposition} is the human's call (--by human)")
    if by == "auto" and not ruled:  # FR-19, FR-47: the driver accepts minors as risk; a capped batch only through `rule`
        if fid in batch_open(led):
            raise ValueError(f"{fid} is in the capped batch; under auto the driver rules it with nio jury rule")
        if disposition in HUMAN_ONLY and (disposition != "accepted-risk" or f["severity"] != "minor"):
            raise ValueError(f"{disposition} on a {f['severity']} is the human's call; under auto only a minor is accepted as risk")
    if any(s["lens"] == "deferred" for s in f["sources"]) and by == "agent":
        raise ValueError(f"{fid} was deferred by the grill; only the human closes it (--by human, or --by grill once a session settles it)")
    if any(s["lens"] == "deferred" for s in f["sources"]) and disposition == "spec-fix":
        still = dict(spec.items(spec.sections(spec.path(root, slug).read_text().splitlines()).get("Deferred", [])))
        if f["cites"][0] in still:
            raise ValueError(f"{f['cites'][0]} is still in `## Deferred`; a spec-fix settles it there first")
    if f["status"] == "disposed" and f["disposition"] == "spec-change" and state(root, slug, led)[0] == "waiting-on-spec":
        raise ValueError(f"{fid} is disposed and waits on {(CHANGE.findall(f['note']) or ['its change request'])[0]}")
    if disposition == "overruled" and fid not in (led.get("list") or {}).get("flagged", []):
        raise ValueError(f"only a finding the final fix check flagged can be overruled; {fid} isn't one")
    noted_major = f["status"] == "noted" and f["severity"] == "major" and impl_gate(gate)
    if f["status"] != "open" and not (by == "human" and (f["status"] == "disposed" or noted_major)):
        raise ValueError(f"{fid} is {f['status']}; only open findings take a disposition")
    f.update(status="overruled" if disposition == "overruled" else "disposed", disposition=disposition, by=by, note=note)
    if disposition == "overruled":
        f["reason"] = f"overruled by the human: {note}"


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


def compose(led, current):
    """(outcome, reasons, listed). Fail-closed: rerun | pending | human | rejected | approved, in that order. `current`
    is the artefact's version now: a version no juror has judged is never approved, whatever the dispositions say, with
    one exception (#52 FR-23): what the final fix check sent to the human, once they settle it, is never checked again.
    `listed` holds the IDs a `human` outcome hands over as one list (#52 FR-2, FR-21)."""
    lenses, ph = votes(led), phase(led)
    judged = version(led, led["round"])
    if not judged:
        return "rerun", ["no lens output has been collected yet: run the lenses"], []
    if ph == "final-owed":  # the human settled the list with a fix: one final fix check before anything else (#52 FR-22)
        return "rerun", [f"run the final fix check on the fixes from the human's list: {', '.join(fixes(led))} (`nio jury fixcheck`)"], []
    flagged = [f for f in led["findings"] if f["id"] in (led.get("list") or {}).get("flagged", [])]
    if current != judged:
        if ph == "final" and flagged:
            still = [f["id"] for f in flagged if f["status"] == "open"]
            if still:
                return "human", [f"the final fix check flagged these; fix or accept each as risk: {', '.join(still)}"], still
            done = [f["id"] for f in flagged if f["disposition"] in FIXES]
            return "approved", [f"fixed after the final fix check, judged by no lens: {', '.join(done)}"] * bool(done), []
        if ph == "final":  # passed, then edited: approved, saying no lens judged the edit (#52 FR-5)
            return "approved", [f"the {led['gate']} changed after the final fix check; no lens judged that change"], []
        return "rerun", [f"the {led['gate']} changed since round {led['round']} judged it: re-review what changed (`nio jury changed`)"], []
    retry = [f"{n}: {v}" for js in lenses.values() for n, v in js if v in ("invalid", "needs-more") and led["jurors"][n]["attempts"] < 2]
    stuck = [f"{n}: {v} after {led['jurors'][n]['attempts']} attempts" for js in lenses.values() for n, v in js
             if v in ("invalid", "needs-more") and led["jurors"][n]["attempts"] >= 2]
    missing = [lens for lens in led["expect"] if lens not in lenses]
    if retry or missing:
        return "rerun", retry + [f"{lens}: no output" for lens in missing], []
    if any(v == "pending" for js in lenses.values() for _, v in js) or any(
            f["validation"] == "pending" and f["status"] == "open" for f in led["findings"]):  # a not-fixed blocker too
        return "pending", ["blocker or major findings wait for the refuter"], []
    split = []
    # one group per juror and its escalation jurors: the pr gate's per-epic jurors of a lens judge different diffs
    groups = collections.defaultdict(list)
    for lens, js in lenses.items():
        for n, v in js:
            groups[(lens, re.sub(r"-\d+$", "", n))].append((n, v))
    for (lens, _), js in groups.items():
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
    blocker = any(f["severity"] == "blocker" and f["validation"] == "confirmed" and f["status"] == "open" for f in led["findings"])
    # failed twice: the human decides instead of another re-review, so only where one would start (#52 FR-16)
    impl = impl_gate(led["gate"])  # CT-13: minors never reject or hand over; they are listed in the verdict
    live = [f for f in led["findings"] if not (impl and f["severity"] == "minor")]
    stale = [f"{f['id']} failed {f['rounds']} rounds" for f in live
             if f["status"] == "open" and f["rounds"] >= 2 and (ph == "first" or (ph == "re-review" and blocker))]
    # disposed as a spec-fix, yet the artefact (== judged, see above) reads as it did when the finding was raised: the
    # fix never landed, or was undone; a fix judged in a later round that skipped the finding's lens counts
    unapplied = [f["id"] for f in led["findings"] if f["status"] == "disposed" and f["disposition"] in ("spec-fix", "plan-fix")
                 and version(led, raised_round(f)) == judged]  # the version it was raised on (2026-11-15 FR-29)
    if unapplied:
        return "human" if ph == "final" else "rejected", [f"{'plan' if led['gate'] == 'plan' else 'spec'}-fix without a change to the {led['gate']}: {', '.join(unapplied)}"], []
    if stuck or split or stale:
        return "human", stuck + split + stale, []
    ids = [f["id"] for f in live if f["status"] == "open"]
    noted = [f["id"] for f in live if impl and f["status"] == "noted" and f["severity"] == "major"]  # no later ruling yet
    if noted and not ids:
        return "human", [f"noted majors wait for the human: {', '.join(noted)}"], noted
    if ids and (ph == "first" or (ph == "re-review" and blocker)):  # #52 FR-1, FR-6
        return "rejected", [f"unresolved: {', '.join(ids)}"], []
    if ids and ph == "final":  # #52 FR-21
        return "human", [f"the final fix check flagged these; fix or accept each as risk: {', '.join(ids)}"], ids
    if ids:  # #52 FR-2: no confirmed blocker after the first review, so one list instead of another round
        return "human", [f"one list for the human; fix or accept each as risk: {', '.join(ids)}"], ids
    return "approved", [], []


def later_epic(root, slug, gate, led):
    """An open finding whose cited ACs tasks.md serves only in later epics not built yet is the system's `out-of-scope`,
    before any fix task is made (#126 FR-12); any other finding is left as it is."""
    from nio import implement
    if gate == "pr":  # every epic is built by the pr gate
        return
    ts = implement.tasks_of(root, slug)
    order = list(dict.fromkeys(t["epic"] for t in ts))
    here = order.index(gate.removeprefix("implementation-"))
    built = lambda e: (l := load(root, slug, f"implementation-{e}"))["outcome"] == "approved" or l.get("closed")
    for f in led["findings"]:
        serving = {c: [t for t in ts if c in t["serves"]] for c in f["cites"] if c.startswith("AC-")}
        if f["status"] == "open" and serving and all(s and all(order.index(t["epic"]) > here and not built(t["epic"]) for t in s)
                                                     for s in serving.values()):
            ac, t = next((c, s[0]) for c, s in serving.items())
            f.update(status="disposed", disposition="out-of-scope", by="system",
                     note=f"{ac} is served by {t['id']} in {t['epic']}, a later epic not built yet")


def code_right(f):
    return f.get("gap") == "contradicts" and f.get("right") == "code"


def to_task(f, rejected=()):
    """Does the decision table send this finding to a fix task (FR-26, FR-30, FR-43)? Code that is right goes to a change
    request, and to a task only once the human has rejected that request (`rejected` holds those findings' IDs, FR-44)."""
    return f["status"] == "open" and f["severity"] != "minor" and f["validation"] == "confirmed" and (not code_right(f) or f["id"] in rejected)


def version_now(root, slug, gate):
    """The version the gate would judge now: the epic's last commit, as `collect` judges, or the artefact's blob."""
    if impl_gate(gate):
        return evidence.span(root, slug, gate.removeprefix("implementation-"))[1]
    text = artefact(root, slug, gate)
    now = blob(root, text)  # an emptied or deleted artefact is a version too
    if gate == "tasks":  # a ledger judged before #126 kept retired fix-task IDs in its text: the same tasks, so its version
        led = load(root, slug, gate)
        last = version(led, led["round"])
        if last and last != now:
            code, old, _ = records.git(root, "cat-file", "-p", last, full=True)
            if code == 0 and unretire(old).rstrip() == text.rstrip():
                return last
    return now


def cuts(root, slug, gate, led):
    """CT-38: what the fixes since the last round changed that the fix agent may not change alone: a `[human]` item
    changed or gone, an item removed, a non-goal added, the risk flags changed. [] when nothing was judged yet."""
    judged = version(led, led["round"])
    old = "\n".join(records.git(root, "cat-file", "-p", judged)) if judged else ""
    if not old:
        return []
    new = artefact(root, slug, gate)
    (was, was_secs), (now, now_secs) = parts(old), parts(new)
    flat = lambda s: " ".join(s.split())
    out = [(f"[human] line gone: {i}" if i not in now else f"[human] line changed: {i}") if "[human]" in text else f"removed: {i}"
           for i, text in was.items() if i not in now or "[human]" in text and flat(now[i]) != flat(text)]
    goals = lambda secs: [x.strip() for x in secs.get("Non-goals", "").splitlines() if x.strip()]
    out += [f"non-goal added: {x}" for x in goals(now_secs) if x not in goals(was_secs)]
    risk = lambda text: (re.search(r"^risk:\s*(\[[^\]]*\])", text, re.M) or [None, ""])[1]
    out += [f"risk changed: {risk(old)} → {risk(new)}"] * (risk(old) != risk(new))
    return out


def composed(root, slug, gate, led, current, rejected=()):
    """`compose`, and at the implementation gate: never approved while a task of the epic, a fix task above all, isn't done
    or a fix has no verdict yet (FR-26); and human, not a dead end, when rejected has no new work to send back, since a
    finding `not fixed` with its task done can't get a second one (FR-26). Under auto (2026-11-15 CT-37, CT-38), at the
    spec, plan and tasks gates: a fix the round check flags, or a finding held, goes to the human; a minor is accepted as
    the gate's risk."""
    from nio import flow
    if gate in gates(root) and flow.load(root, slug)[0]["auto"]:
        if hits := cuts(root, slug, gate, led):
            return "human", hits, []
        for f in led["findings"]:
            if f["status"] == "open" and f["severity"] == "minor":
                f.update(status="disposed", disposition="accepted-risk", by="auto", note="a minor, accepted as the gate's risk under auto")
    held = [f["id"] for f in led["findings"] if f["status"] == "disposed" and f["disposition"] == "held"]
    if held:
        return "human", [f"held for the human: {', '.join(held)}"], held
    outcome, reasons, listed = compose(led, current)
    if outcome not in ("approved", "rejected") or not impl_gate(gate):
        return outcome, reasons, listed
    left = undone(root, slug, gate.removeprefix("implementation-"))
    if outcome == "approved":
        if left:
            return "rejected", [f"tasks not done: {', '.join(left)}"], []
        waiting = [f["id"] for f in led["findings"] if awaits_fix_verdict(f)]
        if waiting and phase(led) != "final":  # the final check's flagged fixes are never checked again (#52 FR-23)
            return "rerun", [f"no fix verdict yet on {', '.join(waiting)}: run `nio jury evidence`, then the lenses `nio jury changed` names"], []
    elif not left:
        from nio import tasks
        routed = [f["id"] for f in led["findings"] if to_task(f, rejected)]
        if routed and all(tasks.fixes_of(root, slug, gate, i) for i in routed):
            return "human", [f"not fixed, with its fix task done and no second task allowed; fix or accept each as risk: {', '.join(routed)}"], routed
    return outcome, reasons, listed


def check(root, slug, gate, record=False, human=""):
    """Compose the outcome, save it, and with `record` write the verdict record once per round and outcome.
    `human` is the human closing the gate themselves, with their reason: the outcome is `human`, never `approved`.
    Returns (outcome, lines to print)."""
    led = load(root, slug, gate)
    reopened = reopen_dropped(root, led) if gate == "plan" else []
    if impl_gate(gate):
        later_epic(root, slug, gate, led)
    current = version_now(root, slug, gate)
    held, rejected, raised = settle(root, slug, gate, led, record and not human.strip() and not led.get("closed")) \
        if impl_gate(gate) else ([], [], [])
    outcome, reasons, listed = composed(root, slug, gate, led, current, [] if held else rejected)
    if human.strip():
        if record:  # only a recorded closure sticks; an unrecorded --human counts for this call alone
            led["closed"] = [led["round"], current, human.strip()]
    elif outcome == "approved" or led.get("closed", [])[:2] != [led["round"], current]:
        led.pop("closed", None)  # approval, a new round or a changed artefact ends a closure for good
    closed = led.get("closed") or (human.strip() and [led["round"], current, human.strip()])
    if closed:
        outcome, reasons = "human", [f"the human closed the gate: {closed[2]}"] + [f"(the jury said {outcome}: {r})" for r in reasons]
    appended, asked = [], []
    if record and outcome == "rejected" and not closed and impl_gate(gate):
        from nio import tasks
        save(root, led)  # append_fix disposes through the saved ledger
        if gate == "pr":  # FR-39: a finding rooted in the spec or plan asks for a change to that file, not a code fix
            for f in led["findings"]:
                if to_task(f, [] if held else rejected) and (name := plan_rooted(slug, f)):
                    cid = raise_change(root, slug, gate, f, name)
                    dispose(root, slug, gate, f["id"], "spec-change", "agent", f"change asked against {name}", change=cid, routed=True)
                    asked.append(f["id"])
            led = load(root, slug, gate)
        appended = [(f["id"], tasks.append_fix(root, slug, gate.removeprefix("implementation-"), f)) for f in led["findings"] if to_task(f, [] if held else rejected)]  # a pending request holds its own finding and the rejected ones
        led = load(root, slug, gate)
    led["outcome"] = outcome
    unresolved = sum(f["status"] == "open" for f in led["findings"])
    lines = [f"outcome: {outcome}", f"round: {led['round']}", f"unresolved: {unresolved}", *[f"- {r}" for r in reasons], *reopened]
    if held or rejected and outcome == "rejected":  # CT-15: the epic waits on the human, or goes back to the implement stage
        lines.insert(1, "state: waiting-on-change" if held else "state: implementing")
        lines += [f"- {fid} waits on the change request {cid}" for fid, cid in held if cid] + [f"- {x}" for x in raised]
    lines += [f"fix task {tid} for {fid}" for fid, tid in appended if tid] + [f"change asked: {fid}" for fid in asked]
    lines += [f"vote {lens}: {', '.join(f'{n}={v}' for n, v in js)}" for lens, js in votes(led).items()]
    notes = [f for f in led["findings"] if f["status"] == "noted"]  # raised below blocker after the first review (#52 FR-12)
    lines += ["notes (no ruling needed):"] * bool(notes) + [f"- {f['id']} [{f['severity']}/{f['kind']}] {f['title']}" for f in notes]
    review = [f for f in led["findings"] if f["by"] == "agent"]  # still listed once a re-run marks it fixed
    lines += ["for the human to review (set by the agent):"] * bool(review)
    lines += [f"- {f['id']} {f['disposition']}: {f['note']}" for f in review]
    system = [f for f in led["findings"] if f["by"] == "system"]  # the gate summary (#129 FR-12, FR-15)
    lines += ["closed by the system:"] * bool(system) + [f"- {f['id']} [{f['severity']}] {f['title']}: {f['disposition']} ({f['note']})" for f in system]
    # the human's closure is its own record, even in a round that already recorded `human` from the jury (#55)
    entry = [led["round"], "closed" if closed else outcome]
    if record and outcome in ("approved", "rejected", "human") and entry not in led["recorded"]:
        lines.append(f"recorded {verdict(root, led, outcome, reasons).relative_to(root)}")
        led["recorded"].append(entry)
    if gate == "plan":
        save(root, led)
        lines.insert(1, "state: {} ({})".format(*state(root, slug)))
    if record and listed and not closed:  # the list the human settles, or what the final check flagged (#52 FR-24)
        if phase(led) == "final":
            led["list"]["flagged"] = sorted(set(led["list"]["flagged"]) | set(listed), key=lambda i: int(i[2:]))
        elif not led.get("list"):
            led["list"] = {"round": led["round"], "ids": listed, "final": None, "flagged": []}
    save(root, led)
    if record and outcome != "approved" and impl_gate(gate):  # approved: `nio flow done` makes its commit (CT-17)
        from nio import flow
        with flow.lock(root, slug):
            if flow.uncommitted(root, slug, gate):
                lines += flow.commit_gate(root, slug, "implementing", [], None, None, [], gate, f"nio: jury {gate} round {led['round']}")[1]
    if record and gate == "pr" and outcome in ("approved", "rejected", "human"):  # FR-11, FR-16: the human's one message
        text = outcome_text(led, outcome, bool(closed))
        lines += ["outcome for the human:", *text, *post(root, slug, led, "\n".join(text))]
    return outcome, lines


def post(root, slug, led, body):
    """Publish the pr gate's verdict comment; until it is on the pull request it waits in the ledger as `unposted`, which
    keeps the gate from approval and which the next `nio jury next <slug> pr` posts again (FR-16)."""
    led["unposted"] = body
    save(root, led)
    out = publish(root, slug, body)
    led.pop("unposted")
    save(root, led)
    return out


def outcome_text(led, outcome, closed=False):
    """The pr gate's verdict (FR-11, FR-16): `APPROVED` or `REQUEST_CHANGES` and the head commit judged, the verdict, then
    the findings fixed, still open, ruled by the human and closed by the system. A gate the human closed through their
    rulings has nothing left to change: APPROVED."""
    fs = led["findings"]
    row = lambda f: f"- {f['id']} [{f['severity']}] {f['title']}" + (f": {f['disposition']} by {f['by']} ({f['note']})" if f["disposition"] else "")
    groups = (("fixed", [f for f in fs if f["status"] == "fixed"]),
              ("open", [f for f in fs if f["status"] == "open" or f["status"] == "disposed" and f["disposition"] == "fix-task"]),
              ("ruled by the human", [f for f in fs if f["status"] in ("disposed", "overruled") and f["by"] == "human" and f["disposition"] != "fix-task"]),
              ("closed by the system", [f for f in fs if f["by"] == "system"]))
    return [f"{'APPROVED' if outcome == 'approved' or closed else 'REQUEST_CHANGES'} {version(led, led['round']) or ''}",
            f"verdict: {'closed by the human' if closed else outcome}, round {led['round']}"] + \
        [x for name, g in groups if g for x in [f"{name}:", *map(row, g)]]


def hub(root, *args):
    """Run one `git` or `gh` command: every GitHub call of the pr gate goes through here (tests fake it). (code, out, err)."""
    try:
        r = subprocess.run(args, cwd=root, capture_output=True, text=True)
    except FileNotFoundError:
        return 127, "", f"{args[0]} is not installed"
    return r.returncode, r.stdout, r.stderr


VERDICT_MARK = "<!-- nio: pr gate verdict -->"  # finds the one verdict comment to edit; nothing else is kept


def publish(root, slug, body=None):
    """Push `nio/<slug>`, open its pull request against the default branch or reuse the open one, and with `body` post
    the verdict comment, or edit the one posted before (FR-16, FR-17). Never merges. A failed step raises ValueError
    naming it: push, pull request or comment; the gate stays open."""
    from nio import implement
    branch = implement.branch(slug)

    def call(step, *args):
        code, out, err = hub(root, *args)
        if code:
            raise ValueError(f"{step} failed, the pr gate stays open: {(err or out).strip()}")
        return out.strip()
    from nio import flow
    call("push", "git", "push", "-u", "origin", branch)
    find = ("gh", "pr", "list", "--head", branch, "--state", "open", "--json", "number", "--jq", ".[0].number // empty")
    num = call("pull request", *find)
    described = ["--body", f"Effort `{slug}`. The pr gate's verdict is the comment below; only the human approves it."]
    if flow.load(root, slug)[0]["auto"]:  # CT-40: under auto the run report is the pull request's body
        path = root / ".nio/runs" / f"report-{slug}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(flow.report(root, slug))
        described = ["--body-file", str(path)]
        if num:
            call("pull request", "gh", "pr", "edit", num, *described)
    if not num:
        sp = spec.path(root, slug)
        title = next((x[2:] for x in (sp.read_text().splitlines() if sp.exists() else []) if x.startswith("# ")), slug)
        call("pull request", "gh", "pr", "create", "--head", branch, "--base", evidence.default_branch(root).removeprefix("origin/"),
             "--title", title, *described)
        num = call("pull request", *find)
    out = [f"pull request: #{num} on {branch}"]
    if body is None:
        return out
    api = "repos/{owner}/{repo}/issues"
    ids = call("comment", "gh", "api", "--paginate", f"{api}/{num}/comments", "--jq",
               f'.[] | select(.body | contains("{VERDICT_MARK}")) | .id').split()
    text = f"body={body}\n\n{VERDICT_MARK}"
    if ids:
        call("comment", "gh", "api", "-X", "PATCH", f"{api}/comments/{ids[0]}", "-f", text)
    else:
        call("comment", "gh", "api", f"{api}/{num}/comments", "-f", text)
    return out + [f"verdict comment {'edited' if ids else 'posted'}: {body.splitlines()[0]}"]


CHANGE = re.compile(r"\bC-\d{6}-[a-z2-7]{4}\b")


def change_record(root, cid):
    """(path, meta) of the change record `cid`, or (None, {}) when there is none."""
    for path in (root / ".nio/memory").rglob(f"{cid}-*.md"):
        meta, _ = records.parse(path)
        if meta.get("type") == "change":
            return path, meta
    return None, {}


def change_for(root, slug, gate, fid):
    """(path, meta) of the change request that names finding `fid` at `gate` of `slug`, or (None, {})."""
    named = lambda text, name, end: re.search(rf"(?<![\w-]){name}(?!{end})", text)
    for path in sorted((root / ".nio/memory").rglob("C-*.md")):
        meta, _ = records.parse(path)
        text = re.sub(r"^- situation \(.*$", "", path.read_text(), flags=re.M)  # a juror's words name other findings
        if meta.get("type") == "change" and f"/{slug}/" in str(meta.get("against")) and named(text, fid, r"\d") and named(text, gate, r"[\w-]"):
            return path, meta
    return None, {}


def gate_changes(root, slug, gate):
    """The change requests against `slug`'s spec that name this epic gate, as paths from the root; [] at any other gate."""
    if not impl_gate(gate):
        return []
    named = re.compile(rf"(?<![\w-]){gate}(?![\w-])")
    return [str(p.relative_to(root)) for p in sorted((root / ".nio/memory").rglob("C-*.md"))
            if f"/{slug}/spec.md" in str(records.parse(p)[0].get("against")) and named.search(p.read_text())]


def plan_rooted(slug, f):
    """The spec or plan file of the effort a finding's `where` names, or None (2026-11-15 FR-39)."""
    m = re.search(rf"\.nio/specs/{re.escape(slug)}/((?:spec|plan|contracts|tests|quickstart|architecture)\.md)", f.get("where") or "")
    return m and m[1]


def raise_change(root, slug, gate, finding, against="spec.md"):
    """The pending change request against the spec for a contradicts finding whose code is right, or against the spec or
    plan file `against` a pr finding is rooted in: the existing one when a request already names the finding and the
    gate, so a repeat or a stop before the ledger save raises no second (CT-15, FR-30). The file is never touched."""
    path = change_for(root, slug, gate, finding["id"])[0]
    if not path and against != "spec.md":
        areas = records.areas(root)
        path = records.new(root, "change", "project" if "project" in areas else areas[0],
                           f"Plan change asked: {finding['id']} at {gate}", by="jury")
        head = re.sub(r"^against: .*$", f'against: ".nio/specs/{slug}/{against}"', path.read_text().partition("\n---\n")[0], flags=re.M)
        path.write_text(f"{head}\n---\n## What is wrong\n{finding['id']} at {gate}, rooted in {against}: {finding['title']}.\n"
                        + "".join(f"- situation ({s['lens']}): {s['situation']}\n" for s in finding["sources"])
                        + f"## Proposed change\nChange {against}: {finding.get('fix') or finding['title']}\n## Human decision\nPending.\n")
    if not path:
        areas = records.areas(root)
        path = records.new(root, "change", "project" if "project" in areas else areas[0],
                           f"Code is right, spec is stale: {finding['id']} at {gate}", by="jury")
        head = path.read_text().partition("\n---\n")[0]
        head = re.sub(r"^against: .*$", f'against: ".nio/specs/{slug}/spec.md"', head, flags=re.M)
        cites = ", ".join(finding["cites"])
        wrong = f"{finding['id']} at {gate} says the code contradicts {cites}, and the code is the right side: {finding['title']}."
        path.write_text(f"{head}\n---\n## What is wrong\n{wrong}\n" + "".join(f"- situation ({s['lens']}): {s['situation']}\n" for s in finding["sources"])
                        + f"## Proposed change\nChange {cites} in spec.md to match the code. Reject it and a fix task changes the code instead.\n"
                        + f"## Human decision\nPending.\n")
    return path.name[:13]


def settle(root, slug, gate, led, raising=False):
    """Walk the gate's confirmed code-is-right blockers and majors against their change requests (CT-15, FR-44), raising the
    missing ones when `raising`. Returns (held [(finding, request or None)], rejected [finding IDs], what was raised). A
    pending or missing request holds the epic; an accepted one settles its finding (`accepted-risk`: the spec changes, the
    code stays); a rejected one sends its finding to a fix task."""
    held, rejected, raised = [], [], []
    for f in led["findings"]:
        if not (code_right(f) and f["severity"] != "minor" and f["validation"] == "confirmed" and (f["status"] == "open" or f["disposition"] == "fix-task")):
            continue
        path, meta = change_for(root, slug, gate, f["id"])
        cid = path.name[:13] if path else None
        if not path and raising and f["status"] == "open":
            cid = raise_change(root, slug, gate, f)
            raised.append(f"raised {cid} for {f['id']}")
            meta = {"outcome": "pending"}
        outcome = meta.get("outcome")
        if outcome == "rejected":
            rejected.append(f["id"])
        elif outcome == "accepted" and f["status"] == "open":
            f.update(status="disposed", disposition="accepted-risk", by="human", note=f"{cid}: the human accepted the change request")
        elif outcome != "accepted" and f["status"] == "open":
            held.append((f["id"], cid))
    return held, rejected, raised


def standing(root, slug, gate):
    """The gate's outcome on its current artefact, as `check` would print it, without saving anything."""
    led = load(root, slug, gate)
    current = version_now(root, slug, gate)
    outcome = composed(root, slug, gate, led, current)[0]
    closed = led.get("closed") or []
    return "closed" if closed[:2] == [led["round"], current] and outcome != "approved" else outcome


def state(root, slug, led=None):
    """(state, reason) of the plan gate, from its ledger, the change records its spec-rooted findings name, and the spec
    gate (#57 FR-35, FR-47, FR-49, FR-50; the spec's state table "plan gate")."""
    led = led or load(root, slug, "plan")
    for f in led["findings"]:
        if f["status"] == "disposed" and f["disposition"] == "spec-change":
            cid = (CHANGE.findall(f["note"]) or [""])[0]
            outcome = change_record(root, cid)[1].get("outcome")
            if outcome == "pending" or outcome == "accepted" and standing(root, slug, "spec") not in ("approved", "closed"):
                return "waiting-on-spec", f"the plan jury is paused until the spec change is settled ({cid}, for {f['id']})"
    now = standing(root, slug, "plan")
    if now == "closed":
        return "closed-by-human", "the human closed the plan gate"
    if now == "approved":
        return "approved", "the plan jury approved the plan"
    if now == "human":
        return "with-human", "the plan gate waits on the human's ruling"
    return "open", f"the plan jury's outcome is {now}"


def reopen_dropped(root, led):
    """A spec-rooted finding whose change request the human rejected goes back to them, open (#57 FR-49)."""
    out = []
    for f in led["findings"]:
        if f["status"] == "disposed" and f["disposition"] == "spec-change":
            cid = (CHANGE.findall(f["note"]) or [""])[0]
            if change_record(root, cid)[1].get("outcome") == "rejected":
                f.update(status="open", disposition="", by="", note=f"{cid} was dropped; fix it in the plan or accept the risk")
                out.append(f"reopened {f['id']}: {cid} was dropped")
    return out


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
    for lens, js in votes(led).items():  # one row per lens, host, model and vote: a split pr gate has dozens of jurors
        rows = collections.Counter(tuple(([p.strip() for p in led["jurors"][name]["by"].split("/")] + ["", "", ""])[1:3]) + (vote,) for name, vote in js)
        body += [f"| {lens} | {h} | {m} | {v}{f' ×{n}' if n > 1 else ''} |" for (h, m, v), n in rows.items()]
    body += ["## Reasons", *[f"- {r}" for r in reasons[:6]]]  # the record body stays under 40 lines
    body += [f"- {f['id']} [{f['severity']}/{f['kind']}] {f['title']}: {f['status']} {f['disposition']}".rstrip() for f in [f for f in open_ if f['severity'] != 'minor'][:8] + [f for f in open_ if f['severity'] == 'minor']]  # never cut a minor (FR-31, FR-33)
    if not reasons and not open_:
        body.append("- Every lens approved and no finding is open.")
    body += [f"- Dropped lenses (the human's pick): {', '.join(led['dropped'])}."] if led.get("dropped") else []
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


def _out_line(gate, lens, run, name=None):
    return ("## Your output\n\nWrite your whole output, front matter first, to "
            f".nio/runs/{run}/jury/{gate}-{name or lens}.md and to no other file. Set lens: {lens}, gate: {gate}, "
            f'subject: {{slug}}, by: "juror / <your host> / <your model>".\n')


def _pack_text(root, slug, gate, run, lens, fix, part=None):
    """What the skill gives a lens today, then the lens output format and where its output goes (CT-2)."""
    from importlib import resources
    from nio import plan as plans, pack as memory, query, tasks
    if gate not in gates(root):
        body = evidence.pack(root, slug, gate, lens, run, part)
    elif fix:
        body = "\n".join(fixcheck(root, slug, gate, lens)) + "\n"
    else:
        errors, notes = {"spec": spec, "plan": plans, "tasks": tasks}[gate].check(root, slug, True, "HEAD")
        body = "\n".join([f"# Pack: {lens}, {gate} gate of {slug}", "", "Files to read (quotes may come only from these):",
                          *[str(p.relative_to(root)) for p in sources(root, slug, gate, lens)], "", f"## nio check {gate} {slug}", "",
                          *[f"ERROR {e}" for e in errors], *notes, f"{len(errors)} errors", ""])
        reader = {("spec", "scope"): "scope", ("plan", "architecture-fit"): "architecture-fit"}.get((gate, lens))
        if reader:
            from nio import onboard
            body += "\n" + onboard.docs_for(root, reader, slug)
        if lens == "scope":
            body += "\n".join(["## Intake and the human's answers", f".nio/specs/{slug}/intake.md", "", *answers(root, slug), ""])
        if lens == "consistency":
            m = re.search(r"^## Summary\n(.*?)(?=^## |\Z)", artefact(root, slug, "spec"), re.M | re.S)
            asked = " ".join(m[1].split()) if m else slug
            text, ids = memory.build(root, asked, worker=False)
            memory.save(root, run, f"{lens}-memory", text)
            query.log(root, "pack", f"{lens}-memory", ids, text)
            body += "\n" + text + "\n"
    tail = resources.files("nio").joinpath("templates/lens-output.md").read_text()
    name = f"{lens}~{part}" if part else lens
    return body.rstrip("\n") + "\n\n" + tail.rstrip("\n") + "\n\n" + _out_line(gate, lens, run, name).replace("{slug}", slug)


def packs(root, slug, gate, run, lenses, fix=False):
    """Write `packs/<lens>.md` per lens (never over an existing one) and `packs/step.json`; the `run <lens>:` lines (CT-2)."""
    root = Path(root)
    folder = root / ".nio/runs" / run / "jury/packs"
    folder.mkdir(parents=True, exist_ok=True)
    led = load(root, slug, gate)
    parts = list(evidence.split(root, slug)) if gate == "pr" and not fix else []  # FR-13: one juror per epic, plus the rest
    jurors = [(lens, p) for lens in lenses for p in (parts if parts and lens != "integration" else [None])]
    sj = folder / "step.json"
    if not sj.exists() or not json.loads(sj.read_text())["lenses"]:  # a run started before its evidence has no lenses yet
        sj.write_text(json.dumps({"gate": gate, "round": led["round"], "version": version_now(root, slug, gate),
                                                      "lenses": [f"{lens}~{p}" if p else lens for lens, p in jurors]}))
    lines = []
    for lens, part in jurors:
        name = f"{lens}~{part}" if part else lens
        p = folder / f"{name}.md"
        if not p.exists():
            p.write_text(_pack_text(root, slug, gate, run, lens, fix, part))
        lines.append(f"run {name}: card nio-{lens}, pack {p.relative_to(root)}, output .nio/runs/{run}/jury/{gate}-{name}.md")
    return lines


def refuter_pack(root, slug, gate, run, batch):
    """The n-th refuter batch of the run, written to `packs/refuter-<n>.md`; its output is `<gate>-refuter-<n>.md`."""
    root = Path(root)
    text = ["# Pack: refuter, " + f"{gate} gate of {slug}", "", *batch, "## Files to read (quotes may come only from these)",
            *[str(f.relative_to(root)) for f in sources(root, slug, gate)], "", f"Ledger: .nio/specs/{slug}/jury/{gate}.md", ""]
    if gate == "spec":
        text += ["## The human's grill answers", *answers(root, slug), ""]
    ask_refuter(root, slug, gate, run, re.findall(r"^### (J-\d+)", "\n".join(batch), re.M))
    n = load(root, slug, gate).get("batches", {}).get(run, 1)
    p = root / ".nio/runs" / run / f"jury/packs/refuter-{n}.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("\n".join(text) + "\n" + _out_line(gate, f"refuter-{n}", run).replace("{slug}", slug).split("Set lens:")[0].rstrip() + "\n")
    return p


def _begin(root, slug, gate, run, lenses, fix):
    """CT-1 case 2: the run's packs and the lines that start its jurors; no lenses, no run (CT-6)."""
    if not lenses:
        return [f"next: show the human: the {gate} changed but no lens has a fix to check"]
    pushed = publish(root, slug) if gate == "pr" and not run else []  # each pr round starts on the pushed branch (FR-16, FR-17)
    run = run or _reusable(root, slug, gate) or records.new_run(root)
    if gate not in gates(root) and not evidence.path(root, run).exists():
        sj = root / ".nio/runs" / run / "jury/packs/step.json"
        sj.parent.mkdir(parents=True, exist_ok=True)
        led = load(root, slug, gate)
        sj.write_text(json.dumps({"gate": gate, "round": led["round"], "version": version_now(root, slug, gate), "lenses": []}))
        return [*pushed, f"run: {run}", f"next: nio jury evidence {slug} {gate.removeprefix('implementation-')} --run {run}, "
                f"then nio jury next {slug} {gate} --run {run}"]
    lines = packs(root, slug, gate, run, lenses, fix)
    return [*pushed, f"run: {run}", *lines, f"next: run each juror above in parallel, then nio jury next {slug} {gate} --run {run}"]


def _reusable(root, slug, gate):
    led, now = load(root, slug, gate), version_now(root, slug, gate)
    for p in sorted((root / ".nio/runs").glob("R-*/jury/packs/step.json")):
        s = json.loads(p.read_text())
        if (s["gate"], s["round"], s["version"]) == (gate, led["round"], now) and not list(p.parent.parent.glob(f"{gate}-*.md")):
            return p.parts[-4]


def step(root, slug, gate, run="", add=(), pick=None):
    """One gate step (CT-1): collect, check and write the next packs; every line it returns ends in `next: <action>`."""
    root = Path(root)
    max_rounds(root)  # a bad setting starts no round (#129 FR-7)
    lines, ok = plan(root, slug, gate, add, pick)
    if not ok:
        return lines + [f"next: {lines[-1]}"]
    if run and not (root / ".nio/runs" / run).is_dir():
        raise ValueError(f"no run {run} under .nio/runs/")
    led = load(root, slug, gate)
    if gate == "pr" and not run and led.get("unposted"):  # a verdict comment that failed: post it before anything else
        return post(root, slug, led, led["unposted"]) + [{
            "rejected": f"next: nio flow next {slug}",
            "human": "next: show the human the listed findings and wait for their ruling"}.get(
            "closed" if led.get("closed") else led.get("outcome"), APPROVE.format(slug=slug))]
    if pick is None and "picked" not in led and any(x.startswith("choices:") for x in lines):
        return lines + [f"next: show the human the planned runs and let them choose, then nio jury next {slug} {gate} --pick <lens,lens>"]
    names = lines.lenses
    names = [x for x in names if x not in led.get("dropped", [])]
    tier = lines[0].split()[1]
    again = f"nio jury next {slug} {gate} --run {{}}"
    outputs = list((root / ".nio/runs" / run / "jury").glob(f"{gate}-*.md")) if run else []
    if not outputs:
        errors = agents.sync(root)[1]
        if errors:
            raise ValueError("; ".join(errors))
        other = os.environ.get("CLAUDE_PROJECT_DIR")  # FR-33: the host loads the agents of the checkout it started in
        warn = [f"warning: agents were rendered into {root}, but this session loads them from {other}; start the session in {root}"] \
            if other and Path(other).resolve() != root.resolve() else []
        if (cl := capped(root, slug, gate, led, names)) is not None:
            return warn + cl
        fix = bool(led["round"])
        return warn + _begin(root, slug, gate, run, next_lenses(root, slug, gate) if fix else names, fix)
    for p in outputs:
        lens = lens_of(p.stem, gate)
        if lens != "refuter" and lens not in names:
            raise ValueError(f"{p.name}: {lens} is not planned for {gate} (planned: {', '.join(names)}); rename or remove it")
    got = collect(root, slug, gate, run, names, tier, ask=False)
    cut = next((i for i, x in enumerate(got) if x.startswith("## Refuter batch")), len(got))
    end = next((i for i, x in enumerate(got) if i > cut and x.startswith("listed for the human")), len(got))
    batch = got[cut:end]
    lines = [x for x in got[:cut] + got[end:] if x]
    led = load(root, slug, gate)
    sj = root / ".nio/runs" / run / "jury/packs/step.json"
    packed = json.loads(sj.read_text())["lenses"] if sj.exists() else []
    redo = [l for l in packed if not (root / f".nio/runs/{run}/jury/{gate}-{l}.md").exists()]
    redo += [k[len(gate) + 1:] for k, j in led["jurors"].items() if not re.search(r"-\d+$", k) and j["round"] == led["round"]
             and (not j["valid"] or j["context"] == "needs-more") and j["attempts"] < 2 and k[len(gate) + 1:] not in redo]
    if redo:
        return lines + [f"next: re-run {l} on .nio/runs/{run}/jury/packs/{l}.md, adding the INVALID lines above to it "
                        f"(output .nio/runs/{run}/jury/{gate}-{l}.md), then {again.format(run)}" for l in redo]
    if batch:
        p = refuter_pack(root, slug, gate, run, batch)
        return lines + [f"next: run nio-refuter on {p.relative_to(root)} (output .nio/runs/{run}/jury/{gate}-{p.stem}.md), then {again.format(run)}"]
    for f in led["findings"]:  # escalation jurors land in a later round than the blocker: count every round since it was raised
        for l in dict.fromkeys(s["lens"] for s in f["sources"] if s["lens"] in names):
            if f["severity"] == "blocker" and f["validation"] == "confirmed" and f["status"] == "open" and escalation(led, f, l) < 3:
                j = re.sub(r"-\d+$", "", next(s["juror"] for s in f["sources"] if s["lens"] == l))  # its part's juror at a split pr gate
                return lines + [f"next: escalate {l}: run 2 more jurors on copies of its pack whose ## Your output line names "
                                f"{j}-2.md and {j}-3.md (in the first review the copies are of packs/{j[len(gate) + 1:]}.md; after it, of "
                                f"nio jury fixcheck {slug} {gate} --lens {l} --blocker {f['id']} plus the lens output format), then {again.format(run)}"]
    if (cl := capped(root, slug, gate, led, names)) is not None:
        return lines + cl
    outcome, cl = check(root, slug, gate, record=True)
    lines += cl
    impl = gate not in gates(root)
    if outcome == "rerun":
        return lines + _begin(root, slug, gate, "", next_lenses(root, slug, gate), True)
    return lines + [{
        "rejected": f"next: nio flow next {slug}" if impl else f"next: dispose of each open finding in one nio jury dispose {slug} {gate} J-a,J-b <disposition> --by <by> --note <note> call per disposition, fix the artefact, then {again.format(run)}",
        "human": "next: show the human the listed findings and wait for their ruling",
        "approved": APPROVE.format(slug=slug) if gate == "pr" else f'next: nio flow done {gate} {slug} --by "<role> / <host> / <model>"' if impl else f"next: tell the human the outcome, then nio flow next {slug}",
    }.get(outcome, f"next: {again.format(run)}")]


APPROVE = "next: stop and tell the human the outcome above; only they approve the pr gate, at a terminal: nio flow approve {slug}"


def escalation(led, f, lens):
    """The jurors of `lens` that judged blocker `f`: every one since the round it was raised, escalation jurors of an
    earlier round included, so a later round never asks for them again (#105, #129 FR-4)."""
    if any(re.search(r"-\d+$", s["juror"]) for s in f["sources"] if s["lens"] == lens):
        return 3  # raised by escalation jurors: it was escalated already, or each escalation raises another blocker forever
    raised = {re.sub(r"-\d+$", "", s["juror"]) for s in f["sources"] if s["lens"] == lens}  # a split pr juror's part only
    return sum(j["lens"] == lens and j["round"] >= f.get("first_round", led["round"]) and (re.sub(r"-\d+$", "", n) in raised or "~" not in n)
               for n, j in led["jurors"].items())


def next_lenses(root, slug, gate):
    """The lenses the next round re-runs: an automatic or human-asked round's own (#129 FR-5, FR-13), else `changed`'s."""
    led = load(root, slug, gate)
    cap = led.get("cap") or {}
    return cap.get("lenses") or changed(root, slug, gate)[1] if cap.get("allow", 0) > led["round"] else changed(root, slug, gate)[1]


def lenses_of(f, gate):
    """The lenses that re-check finding `f`, as `changed` maps them: a CLI finding's is conformance at the implementation
    gate; a point the grill deferred has none, only the human closes it."""
    impl = impl_gate(gate)
    return {"conformance" if s["lens"] == "cli" else s["lens"] for s in f["sources"]
            if s["lens"] != "deferred" and (impl or s["lens"] != "cli")}


def batch_open(led):
    """The IDs of the capped batch the human hasn't ruled yet: none before the round cap stops the gate, or once a round
    runs (#129). A finding disposed by anyone but the human is still theirs to rule."""
    cap, by_id = led.get("cap") or {}, {f["id"]: f for f in led["findings"]}
    return [i for i in cap.get("batch", []) if cap.get("round") == led["round"] and (by_id[i]["status"] == "open" or by_id[i]["by"] != "human")]


def capped(root, slug, gate, led, names):
    """None while the gate goes on as today; else the step's lines at the round cap (#129, the state table "gate rounds").
    A finished round at or over `jury.max_rounds` decides once: 2+ open blockers start one automatic round on their
    lenses, once per gate; else open minors are skipped, and open majors and blockers go to the human in one batch.
    Once the human ruled every finding of it, the gate closes, unless they asked for one more round."""
    cap, impl = led.get("cap") or {}, gate not in gates(root)
    if cap.get("round") != led["round"]:
        if led["round"] < max(max_rounds(root), cap.get("allow", 0)):
            return None
        open_ = [f for f in led["findings"] if f["status"] == "open"]
        if gate not in gates(root):  # a later epic's finding is the system's out-of-scope before the cap counts it (#126 FR-12)
            later_epic(root, slug, gate, led)
            open_ = [f for f in open_ if f["status"] == "open"]
        if not open_:
            save(root, led)
            return None
        blockers = [f for f in open_ if f["severity"] == "blocker" and f["validation"] == "confirmed"]
        cap = led["cap"] = {"round": led["round"], "auto": cap.get("auto", False)}
        lenses = sorted({x for f in blockers for x in lenses_of(f, gate) if x in names})
        if len(blockers) >= 2 and not cap["auto"] and lenses:  # FR-13: its round starts once the blockers' fixes are in
            cap.update(auto=True, allow=led["round"] + 1, lenses=lenses)
            save(root, led)
            return None
        for f in open_:  # FR-15
            if f["severity"] == "minor":
                f.update(status="disposed", disposition="accepted-risk", by="system", note=SKIPPED)
        cap["batch"] = [f["id"] for f in open_ if f["severity"] != "minor"]
        if not impl:  # the version judged: a `fix` ruling waits until it changes
            cap["version"] = version_now(root, slug, gate)
        save(root, led)
    left = batch_open(led)
    if left:
        by_id = {f["id"]: f for f in led["findings"]}
        how = (f"a fix or again appends a fix task: build it through the implement stage, nio flow next {slug}" if impl else
               f"a fix: edit the {gate} first")
        return [f"capped: round {led['round']} is at the round cap; the human rules each finding: accept (as risk), fix "
                f"(no juror re-checks it), or again (one more round on its lenses)",
                *[f"- {i} [{by_id[i]['severity']}/{by_id[i]['kind']}] {by_id[i]['title']}" for i in left],
                f'next: show the human the capped batch, then record each ruling with nio jury rule {slug} {gate} J-a,J-b '
                f'accept|fix|again --note "<their words>" ({how}), then nio jury next {slug} {gate}']
    if not cap.get("batch") or cap.get("allow", 0) > led["round"] and not impl:  # only minors were open (FR-18), or one more round
        return None
    if cap.get("allow", 0) > led["round"]:
        return None
    if owed := owed_fixes(root, slug, gate, led):
        return [f"waiting: edit the {gate} for {', '.join(owed)} (ruled fix by the human), then call the step again",
                f"next: edit the {gate} for {', '.join(owed)}, then nio jury next {slug} {gate}"]
    lines = check(root, slug, gate, record=True, human="the human ruled every finding of the capped batch")[1]
    return lines + [APPROVE.format(slug=slug) if gate == "pr" else f'next: nio flow done {gate} {slug} --by "<role> / <host> / <model>"' if impl else
                    f"next: tell the human the gate is closed by their rulings, then nio flow next {slug}"]


def owed_fixes(root, slug, gate, led):
    """The capped batch's findings the human ruled `fix` at a spec, plan or tasks gate while the artefact is still the
    version the capped round judged: the edit is owed before the gate closes."""
    cap = led.get("cap") or {}
    if gate not in gates(root) or cap.get("round") != led["round"] or "version" not in cap:
        return []
    return cap.get("fix", []) if version_now(root, slug, gate) == cap["version"] else []


RULINGS = ("accept", "fix", "again")


def rule(root, slug, gate, fid, ruling, note, by="human"):
    """The human's ruling on findings of a capped batch (#129 FR-5, FR-6, FR-16, FR-20): accept as risk; fix, which no
    juror re-checks; or again, a fix one more round re-checks on those findings' lenses. Refused, recording nothing,
    unless every ID is open in the batch. Under auto the driver rules for the human: `by: auto` in the ledger and a
    `ruling` history line naming the grant (2026-11-15 FR-47); refused for an agent with auto off."""
    from nio import flow
    ids = fid.split(",")
    w = flow.who(by, root, slug)
    if w["role"] != "human" and not w.get("auto"):
        raise ValueError(f"a ruling on the capped batch is the human's (--by human), or the driver's under auto")
    actor = "human" if w["role"] == "human" else "auto"
    led = load(root, slug, gate)
    bad = [i for i in ids if i not in batch_open(led)]
    if bad:
        raise ValueError(f"{', '.join(bad)} not open in a capped batch of the {gate} gate (a round is running, or the gate "
                         f"hasn't reached its round cap)")
    none = [i for i in ids if ruling == "again" and not lenses_of(next(f for f in led["findings"] if f["id"] == i), gate)]
    if none:
        raise ValueError(f"no lens re-checks {', '.join(none)} (deferred by the grill): rule accept or fix")
    if actor == "auto":
        with flow.lock(root, slug):
            state, lines = flow.load(root, slug)
            stage = lines[-1]["to"] if lines else None
            flow.write(root, slug, [{"kind": "ruling", "from": stage, "to": stage, "evidence": {"gate": gate, "ids": ids, "auto": w["auto"]}}],
                       state, w, stage)
    if ruling == "accept":
        return dispose(root, slug, gate, fid, "accepted-risk", actor, note, ruled=True)
    if impl_gate(gate):
        from nio import tasks
        for f in [f for f in led["findings"] if f["id"] in ids]:
            tasks.append_fix(root, slug, gate.removeprefix("implementation-"), f)
    dispose(root, slug, gate, fid, {"plan": "plan-fix"}.get(gate, "fix-task" if gate not in gates(root) else "spec-fix"), actor, note, ruled=True)
    if ruling == "fix" and gate in gates(root):
        led = load(root, slug, gate)
        led["cap"]["fix"] = sorted(set(led["cap"].get("fix", [])) | set(ids), key=lambda i: int(i[2:]))
        save(root, led)
    if ruling == "again":
        led = load(root, slug, gate)
        cap = led["cap"]
        lenses = {x for f in led["findings"] if f["id"] in ids for x in lenses_of(f, gate)}
        cap.update(auto=True, lenses=sorted(lenses | set(cap.get("lenses", []) if cap.get("allow", 0) > led["round"] else [])),
                   allow=led["round"] + 1)
        save(root, led)
    return ids
