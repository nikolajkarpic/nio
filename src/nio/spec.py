"""Specs (#20): create .nio/specs/<slug>/spec.md (slug = <YYYY-MM-DD>-<name>, the day it was written) from a template, and run the mechanical checks of #21 on it:
structure, permanent IDs, provenance, AC coverage, SHALL statements, and complete state and decision tables."""
import datetime
import itertools
import re
from importlib import resources

from nio import onboard, records

ROUTES = {
    "full": {"mandatory": ["Summary", "Actors and journeys", "User stories", "Functional requirements", "Non-goals"],
             "ids": {"A", "UJ", "US", "AC", "FR", "NFR", "SC"}, "template": "spec"},
    "lite": {"mandatory": ["Summary", "Current behaviour", "Expected behaviour", "Unchanged behaviour", "Acceptance criteria"],
             "ids": {"CB", "EB", "UB", "AC"}, "template": "spec-bugfix"},
    "epic": {"mandatory": ["Summary", "Actors and journeys", "Roadmap", "Non-goals"], "ids": {"A", "UJ", "R"}, "template": "spec-epic"},
}
OPTIONAL = ["Rules", "Key entities", "Non-functional requirements", "Success criteria", "Glossary", "Risks and evidence against",
            "Decisions", "Open points", "Deferred"]
RISKS = {"auth", "secrets", "pii", "money", "external-input", "data-deletion", "migration", "multi-party", "public-api"}
# #47's triggers; `money` isn't in its mapping, so it brings in the adversary (abuse of payments)
LENSES = {"adversary": {"external-input", "multi-party", "public-api", "money"}, "security": {"auth", "pii", "secrets"},
          "risk-rollback (plan gate)": {"migration", "data-deletion"}}
SCOPE_FRS = 8  # more FRs than this triggers the scope lens (#47)
SCOPE_NOTE = f"scope (more than {SCOPE_FRS} FRs)"  # `nio jury plan` reads this from the check's notes
TAGGED = {"A", "UJ", "US", "AC", "FR", "NFR", "SC", "CB", "EB", "UB"}  # items that must carry provenance
SHALL = {"FR", "EB", "UB"}
# where each kind of item lives; one placed elsewhere is easy to miss for readers and lenses alike
HOME = {"A": ["Actors and journeys"], "UJ": ["Actors and journeys"], "US": ["User stories"],
        "AC": ["User stories", "Acceptance criteria"], "FR": ["Functional requirements"], "NFR": ["Non-functional requirements"],
        "SC": ["Success criteria"], "CB": ["Current behaviour"], "EB": ["Expected behaviour"], "UB": ["Unchanged behaviour"],
        "R": ["Roadmap"]}  # OP and DF say where they belong themselves
LEVELS = {"unit", "integration", "e2e"}
# provenance (#20, #22): the human said it; the agent proposed it; an agent decided it (delegated, or below the grill's
# bar); research backs it; it follows from other items; or the grill deferred it
TAG = re.compile(r"\[(human|default|agent|auto|research: RF-\d+|derived: [A-Z]+-\d+(?:,\s*[A-Z]+-\d+)*|deferred: DF-\d+)\]\s*$")
TAGS = "[human], [default], [agent], [auto], [research: RF-n], [derived: <IDs>] or [deferred: DF-n]"
# a spec ID is not followed by another dash, so a memory record ID like **D-261025-k2m4** isn't read as one
DEF = re.compile(r"^(?:- )?\*\*([A-Z]+-\d+)(?![-\w])[^*]*\*\*|^### ([A-Z]+-\d+)(?![-\w])")
CITE = re.compile(r"^\(([A-Z]+-\d+(?:,\s*[A-Z]+-\d+)*)\)")


def path(root, slug):
    return root / ".nio/specs" / slug / "spec.md"


def new(root, name, route="full", epic="", today=None):
    """Create the spec from its route's template in .nio/specs/<YYYY-MM-DD>-<name>/ and return the path.
    The dated folder name is the spec's slug."""
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name):
        raise ValueError("name must be lowercase words joined by dashes")
    if epic and not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*/R-\d+", epic):
        raise ValueError("--epic must look like <epic slug>/R-<n>")
    state = onboard.progress(root)["state"] if route != "lite" else "done"
    if state not in ("done", "skipped"):
        raise ValueError(f'onboarding is {state}: run @nio:onboard first, or skip it on purpose with nio onboard skip "<reason>"')
    taken = sorted((root / ".nio/specs").glob(f"[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]-{name}/spec.md"))
    if taken or path(root, name).exists():
        raise ValueError(f"{(taken or [path(root, name)])[0].relative_to(root)} already exists")
    slug = f"{today or datetime.date.today().isoformat()}-{name}"
    out = path(root, slug)
    text = resources.files("nio").joinpath(f"templates/{ROUTES[route]['template']}.md").read_text()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text.replace("<slug>", slug).replace('epic: ""', f'epic: "{epic}"'))
    return out


def sections(body):
    """{## heading: [lines]} in order."""
    out, name = {}, None
    for line in body:
        if line.startswith("## "):
            name = line[3:].strip()
            out[name] = []
        elif name:
            out[name].append(line)
    return out


def items(lines):
    """[(id, [lines])]: each definition (`**FR-1**`, `### US-1`) with the lines up to the next one or a subheading."""
    out = []
    for line in lines:
        m = DEF.match(line)
        if m:
            out.append((m[1] or m[2], [line]))
        elif out and line.startswith("#"):
            out.append((None, []))  # a subheading ends the item
        elif out and out[-1][0]:
            out[-1][1].append(line)
    return [(i, ls) for i, ls in out if i]


def table(lines):
    """Rows of the first markdown table in `lines`, header first, separator dropped."""
    rows = [[c.strip() for c in line.strip().strip("|").split("|")] for line in lines if line.strip().startswith("|")]
    return [r for r in rows if not all(re.fullmatch(r":?-{3,}:?", c) for c in r)]


def subsections(lines):
    """[(### heading, [lines])] inside one section."""
    out = []
    for line in lines:
        if line.startswith("### "):
            out.append((line[4:].strip(), []))
        elif out:
            out[-1][1].append(line)
    return out


def check_state(name, rows):
    errs, m = [], re.match(r"^(.+?)\s*\(start:\s*([^;]+);\s*final:\s*([^)]+)\)$", name)
    if not m:
        return [f"state table `{name}`: heading must be `State table: <name> (start: <state>; final: <state>, …)`"]
    title, start, finals = m[1], m[2].strip(), {f.strip() for f in m[3].split(",")}
    if len(rows) < 2 or rows[0][0].lower() != "state" or rows[0][-1] != "Src":
        return [f"state table {title}: the first column is `State` and the last is `Src`"]
    events, states = rows[0][1:-1], {r[0] for r in rows[1:]}
    errs += [f"state table {title}: `{s}` has more than one row" for s in sorted(states) if [r[0] for r in rows[1:]].count(s) > 1]
    errs += [f"state table {title}: `{s}` is not a row" for s in {start} | finals if s not in states]
    edges = {}
    for r in rows[1:]:
        if len(r) != len(rows[0]):
            errs.append(f"state table {title} row {r[0]}: {len(r)} cells, the header has {len(rows[0])}")
            continue
        if not TAG.search(r[-1]):
            errs.append(f"state table {title} row {r[0]}: `Src` must be {TAGS}")
        for event, cell in zip(events, r[1:-1]):
            go = re.fullmatch(r"(?:→|->)\s*(.+)", cell)
            if go:
                if go[1].strip() not in states:
                    errs.append(f"state table {title}: {r[0]} × {event} goes to `{go[1].strip()}`, which is not a row")
                edges.setdefault(r[0], set()).add(go[1].strip())
            elif cell != "ignore" and not re.fullmatch(r"reject:\s*\S.*", cell):
                errs.append(f"state table {title}: {r[0]} × {event} must be `→ <state>`, `ignore` or `reject: <why>`, got `{cell}`")
    seen, todo = {start}, [start]
    while todo:
        for nxt in edges.get(todo.pop(), ()):
            if nxt not in seen:
                seen.add(nxt)
                todo.append(nxt)
    errs += [f"state table {title}: `{s}` can't be reached from `{start}`" for s in sorted(states - seen)]
    errs += [f"state table {title}: `{s}` has no way out and isn't final" for s in sorted(states - finals) if not edges.get(s)]
    return errs


def check_decision(title, rows):
    if len(rows) < 2 or rows[0][-1] != "Src":
        return [f"decision table {title}: needs a header and rows, and the last column is `Src`"]
    errs, conds, outs = [], [], []
    for i, h in enumerate(rows[0][:-1]):
        if h.startswith("→") or h.startswith("->"):
            outs.append(i)
        elif m := re.fullmatch(r"(.+?)\s*\(([^()]+)\)", h):  # the values are in the last parentheses
            conds.append((i, m[1], [v.strip() for v in m[2].split(",")]))
        else:
            errs.append(f"decision table {title}: condition `{h}` must list its values, e.g. `{h} (a, b)`")
    if not outs:
        errs.append(f"decision table {title}: needs at least one `→ <output>` column")
    if errs:
        return errs
    good = []
    for r in rows[1:]:
        label = " / ".join(r[i] for i, _, _ in conds)
        if len(r) != len(rows[0]):
            errs.append(f"decision table {title} row {label}: {len(r)} cells, the header has {len(rows[0])}")
            continue
        bad = [f"`{r[i]}` is not a value of {name}" for i, name, vals in conds if r[i] != "-" and r[i] not in vals]
        bad += [f"output `{rows[0][i]}` is empty" for i in outs if not r[i]]
        bad += [f"`Src` must be {TAGS}"] * (not TAG.search(r[-1]))
        errs += [f"decision table {title} row {label}: {b}" for b in bad]
        good.append(r)
    for combo in itertools.product(*[vals for _, _, vals in conds]):
        hits = [r for r in good if all(r[i] in ("-", v) for (i, _, _), v in zip(conds, combo))]
        case = ", ".join(f"{name}={v}" for (_, name, _), v in zip(conds, combo))
        if not hits:
            errs.append(f"decision table {title}: gap, no row covers {case}")
        elif len(hits) > 1:
            errs.append(f"decision table {title}: overlap, {len(hits)} rows match {case} (the hit policy is Unique)")
    return errs


def defined(text):
    """{id: normalised text} for every item defined in a spec's text, for the renumbering check."""
    out = {}
    for line in text.splitlines():
        if m := DEF.match(line):
            words = re.sub(r"\*\*|\[[^\]]*\]\s*$|[A-Z]+-\d+", "", line)
            out[m[1] or m[2]] = " ".join(words.split()).lower()
        elif m := re.match(r"^\|\s*(R-\d+)\s*\|", line):
            out[m[1]] = " ".join(line.split("|")[2].split()).lower()
    return out


def check(root, slug, gate=False, base="HEAD"):
    """(errors, notes) for one spec. Notes list the lenses its risk flags and size trigger."""
    p = path(root, slug)
    if not p.exists():
        raise ValueError(f"no spec at {p.relative_to(root)}")
    rel = p.relative_to(root)
    try:
        meta, body = records.parse(p)
    except ValueError as e:
        return [f"{rel}: {e}"], []
    # guidance comments are not content: they neither fill a section nor count as a [default] or a placeholder
    body = re.sub(r"<!--.*?-->", "", "\n".join(body), flags=re.S).splitlines()
    errs = []
    route = meta.get("route")
    if not isinstance(route, str) or route not in ROUTES:
        return [f"{rel}: `route` must be one of {sorted(ROUTES)}"], []
    if meta.get("slug") != slug:
        errs.append(f"`slug` must be `{slug}`, the folder name")
    risk = meta.get("risk")
    if not isinstance(risk, list) or any(not isinstance(r, str) or r not in RISKS for r in risk):
        errs.append(f"`risk` must be a list from {sorted(RISKS)}, or []")
        risk = [r for r in risk if isinstance(r, str) and r in RISKS] if isinstance(risk, list) else []
    have = sorted(onboard.progress(root).get("apps") or {})
    if have and "apps" in meta:
        named = meta["apps"] if isinstance(meta["apps"], list) else []
        if not named:
            errs.append(f"spec names no app; the project has apps: {', '.join(have)}")
        errs += [f"app {a} has no project docs (.nio/project/{a}/)" for a in named if str(a) not in have or not (root / ".nio/project" / str(a)).is_dir()]
    retired = meta.get("retired") or []
    if not isinstance(retired, list) or any(not isinstance(r, str) or not re.fullmatch(r"[A-Z]+-\d+", r) for r in retired):
        errs.append("`retired` must be a list of IDs, e.g. [FR-3, OP-1]")
        retired = [r for r in retired if isinstance(r, str)] if isinstance(retired, list) else []
    secs = sections(body)
    allowed = ROUTES[route]["mandatory"] + OPTIONAL
    errs += [f"section `## {s}` is not part of a {route} spec" for s in secs if s not in allowed]
    # a fresh draft has no decisions yet; after the grill it always has some (#40)
    for s in ROUTES[route]["mandatory"] + ["Decisions"] * (gate and route == "full"):
        if not "\n".join(secs.get(s, [])).strip():
            errs.append(f"section `## {s}` is missing or empty"
                        + (": a bug fix needs at least one unchanged-behaviour item, its regression test" if s == "Unchanged behaviour" and route == "lite" else ""))
    for s, lines in secs.items():
        if re.fullmatch(r"(n/?a|none|tbd|-)\.?", "\n".join(lines).strip().lower()):
            errs.append(f"section `## {s}` says N/A; remove a section that doesn't apply")
        # `<slug>` inside a code span is content (a command, a path), not a template placeholder
        if any(re.search(r"<[a-z][^>]*>", re.sub(r"`[^`]*`", "", line)) for line in lines):
            errs.append(f"section `## {s}` still has template `<placeholders>`")

    found = {}
    for s, lines in secs.items():
        for iid, block in items(lines):
            found.setdefault(iid, []).append((s, block))
        if s == "Roadmap":
            for r in table(lines)[1:]:
                found.setdefault(r[0], []).append((s, [" | ".join(r)]))
    for iid, defs in found.items():
        prefix = iid.split("-")[0]
        if len(defs) > 1:
            errs.append(f"{iid} is defined {len(defs)} times")
        if prefix not in ROUTES[route]["ids"] | {"OP", "DF"}:
            errs.append(f"{iid}: `{prefix}` IDs don't belong in a {route} spec ({', '.join(sorted(ROUTES[route]['ids']))})")
        if iid in retired:
            errs.append(f"{iid} is retired and can't be used again")
        s, block = defs[0]
        if prefix in HOME and s not in HOME[prefix]:
            errs.append(f"{iid} is under `## {s}`; {prefix} items belong in `## {' or '.join(HOME[prefix])}`")
        if prefix in TAGGED and not TAG.search(block[0]):
            errs.append(f"{iid}: its line must end with {TAGS}")
        if prefix in SHALL and "SHALL" not in block[0]:
            errs.append(f"{iid}: state it with SHALL (EARS: THE SYSTEM SHALL, WHEN … THE SYSTEM SHALL, IF … THEN …)")
        if prefix == "US":
            text = "\n".join(block)
            if not re.search(r"\(P\d+\)", block[0]):
                errs.append(f"{iid}: the heading needs a priority, e.g. `(P1)`")
            errs += [f"{iid}: needs `{k}`" for k in ("Why this priority", "Independent test") if k not in text]
        if prefix == "AC":
            errs += check_ac(iid, block, found, route)
        if prefix == "OP":
            errs += check_op(iid, block[0], s, found, allowed)
        if prefix == "DF":
            errs += check_df(iid, block[0], s, found, retired, allowed)
    research = p.parent / "research.md"
    rfs = set(re.findall(r"\*\*(RF-\d+)\*\*", research.read_text())) if research.exists() else set()
    errs += check_tags(body, found, rfs)
    for goal in joined(secs.get("Non-goals", [])):
        if not TAG.search(goal):
            errs.append(f"non-goal `{goal[2:40]}…` must end with {TAGS}")
    targets = {"full": ["FR"], "lite": ["EB", "UB"]}.get(route, [])
    cited = {c for iid, defs in found.items() if iid.startswith("AC-") for c in cites(defs[0][1][0])}
    errs += [f"{iid} has no AC" for iid in found if iid.split("-")[0] in targets and iid not in cited]

    errs += check_glossary(secs)

    for name, lines in subsections(secs.get("Rules", [])):
        rows = table(lines)
        if name.startswith("State table:"):
            errs += check_state(name[len("State table:"):].strip(), rows)
        elif name.startswith("Decision table:"):
            errs += check_decision(name[len("Decision table:"):].strip(), rows)
        else:
            errs.append(f"`### {name}` in Rules must be a `State table:` or a `Decision table:`")

    if gate:
        for line in body:  # name each one, so the grill can ask about it
            # the tag at the end of a line or in a table's `Src` cell; prose that mentions `[default]` in a code span is not one
            if re.search(r"\[default\]\s*\|?\s*$", re.sub(r"`[^`]*`", "", line)):
                m = DEF.match(line)
                what = (m[1] or m[2]) if m else f"`{line.strip()[:50]}`"
                errs.append(f"{what} is still [default]; the grill must confirm it ([human]) or research must back it")
        if "\n".join(secs.get("Open points", [])).strip():
            errs.append("`## Open points` must be empty at the gate")
    errs += history(root, rel, found, retired, base)

    lenses = ["testability", "logic"] + [lens for lens, flags in LENSES.items() if flags & set(risk)]
    if sum(i.startswith("FR-") for i in found) > SCOPE_FRS:
        lenses.append(SCOPE_NOTE)
    notes = [f"lenses: {', '.join(lenses)}"]
    # what the grill's finish gate shows the human: calls nobody asked them, consequences, and what was deferred
    for label, kind in (("agent calls", "agent"), ("derived", "derived"), ("deferred", "deferred")):
        ids = [i for i, defs in found.items() if (m := TAG.search(defs[0][1][0])) and m[1].startswith(kind)]
        # table rows and lines without an ID carry the tag too; count them so the human knows they exist
        loose = sum(1 for line in body if re.search(rf"\[{kind}\b", re.sub(r"`[^`]*`", "", line)) and not DEF.match(line))
        more = [f"{loose} line{'s' * (loose > 1)} without an ID"] * bool(loose)
        notes += [f"{label}: {', '.join(ids + more)}"] * bool(ids or loose)
    dfs = [f"{i} (contradiction)" if "; contradiction)" in defs[0][1][0] else i for i, defs in found.items() if i.startswith("DF-")]
    notes += [f"deferred points: {', '.join(dfs)}"] * bool(dfs)
    return [f"{rel}: {e}" for e in errs], notes


def cites(line):
    rest = DEF.sub("", line, count=1).strip()
    m = CITE.match(rest)
    return [c.strip() for c in m[1].split(",")] if m else []


def check_op(iid, line, section, found, sections_allowed):
    """`**OP-1** (fact|decision; <ID or section>) <question>` in Open points: research takes facts, the grill decisions."""
    rest = DEF.sub("", line, count=1).strip()
    m = re.match(r"^\((fact|decision);\s*([^)]+)\)\s*\S", rest)
    if section != "Open points":
        return [f"{iid}: open points belong in `## Open points`"]
    if not m:
        return [f"{iid}: write it as `**{iid}** (fact|decision; <ID or section>) <question>`"]
    target = m[2].strip()
    # a section that isn't written yet is a fine target: "(decision; Rules)" before any table exists
    return [] if target in found or target in sections_allowed else [f"{iid}: its target `{target}` is neither an ID nor a section"]


def joined(lines):
    """`- ` bullets with their indented wrapped lines joined, one string per bullet."""
    out = []
    for line in lines:
        if line.startswith("- "):
            out.append(line)
        elif out and line.startswith("  "):
            out[-1] += " " + line.strip()
    return out


def check_glossary(secs):
    """A glossary entry `- **Term**: … Never "x", "y".` bans its synonyms everywhere else in the spec, so the words
    don't drift. Code spans are skipped; the glossary may name the words it bans, and Decisions may record a rename."""
    banned, terms = {}, []
    for entry in joined(secs.get("Glossary", [])):
        m = re.match(r"^- \*\*([^*]+)\*\*:", entry)
        terms += [m[1]] if m else []
        if m and "Never" in entry:
            for word in re.findall(r'"([^"]+)"', entry.split("Never", 1)[1]):
                banned[word] = m[1]
    errs = []
    whole = lambda w: rf"(?<![\w-]){re.escape(w)}(?![\w-])"
    # a glossary term that contains a banned word ("Refund request", never "request") is vocabulary, not the synonym:
    # skip its uses, but never the banned phrase itself, so "Refund", never "refund request" still catches it
    own = {w: [whole(t) for t in terms if t.lower() != w.lower() and re.search(whole(w), t, re.I)] for w in banned}
    for s, lines in secs.items():
        if s in ("Glossary", "Decisions"):
            continue
        for line in lines:
            text = re.sub(r"`[^`]*`", "", line)
            for word, term in banned.items():
                rest = text
                for t in own[word]:
                    rest = re.sub(t, "", rest, flags=re.I)
                if re.search(whole(word), rest, re.I):
                    errs.append(f"`## {s}` says \"{word}\"; the glossary says {term}: `{line.strip()[:50]}`")
    return errs


def check_tags(body, found, rfs):
    """Wherever `[derived: …]` appears (an item, a table's Src cell, any line), its sources exist and are settled:
    answered, researched or decided by an agent, never a proposal, a deferred point or another derived item.
    `[deferred: DF-n]` names a point in `## Deferred`."""
    errs = []
    for line in body:
        text = re.sub(r"`[^`]*`", "", line)
        m = DEF.match(line)
        where = (m[1] or m[2]) if m else f"`{line.strip()[:40]}`"
        for tag in re.findall(r"\[derived: ([^\]]*)\]", text):
            for src in [s.strip() for s in tag.split(",")]:
                if src.startswith("RF-"):
                    if src not in rfs:
                        errs.append(f"{where} is derived from {src}, which isn't in research.md")
                    continue
                t = TAG.search(found[src][0][1][0]) if src in found else None
                if src not in found:
                    errs.append(f"{where} is derived from {src}, which isn't defined")
                elif not t or not t[1].startswith(("human", "agent", "auto", "research")):
                    errs.append(f"{where} is derived from {src}, which is {t[1] if t else 'untagged'}; derive only from answers and research")
        for did in re.findall(r"\[deferred: (DF-\d+)\]", text):
            if did not in found:
                errs.append(f"{where} points at {did}, which isn't in `## Deferred`")
    return errs


def check_df(iid, line, section, found, retired, sections_allowed):
    """`**DF-1** (from OP-4[; contradiction]) <what is unsettled>`: a point the grill deferred when it ended early.
    The source is an open point, an item, or the section of a line without an ID (a table row, a non-goal)."""
    if section != "Deferred":
        return [f"{iid}: deferred points belong in `## Deferred`"]
    m = re.match(r"^\(from ([^;)]+?)(;\s*contradiction)?\)\s*\S", DEF.sub("", line, count=1).strip())
    if not m:
        return [f"{iid}: write it as `**{iid}** (from <OP, item ID or section>[; contradiction]) <what is unsettled>`"]
    src = m[1].strip()
    if not re.fullmatch(r"[A-Z]+-\d+", src):
        return [] if src in sections_allowed else [f"{iid} comes from `{src}`, which is neither an ID nor a section"]
    if src.startswith("OP-"):
        return [] if src in retired else [f"{iid} comes from {src}, which must move to `retired:` once deferred"]
    tag = TAG.search(found[src][0][1][0]) if src in found else None
    return [] if tag and tag[1] == f"deferred: {iid}" else [f"{iid} comes from {src}, whose line must end with [deferred: {iid}]"]


def check_ac(iid, block, found, route):
    errs, text, refs = [], "\n".join(block), cites(block[0])
    want = {"full": {"FR"}, "lite": {"EB", "UB"}}.get(route, set())
    if not refs:
        errs.append(f"{iid}: cite what it tests right after the ID, e.g. `**{iid}** ({'FR-1' if route == 'full' else 'EB-1'})`")
    for r in refs:
        if r not in found:
            errs.append(f"{iid} cites {r}, which isn't defined")
        elif r.split("-")[0] not in want:
            errs.append(f"{iid} cites {r}; an AC cites {' or '.join(sorted(want))}")
    if not re.search(r"\bGiven\b.*\bwhen\b.*\bthen\b", text, re.I | re.S):
        errs.append(f"{iid}: needs Given / when / then")
    if not re.search(r"Observable:\s*\S", text):
        errs.append(f"{iid}: needs `Observable:` (what the test asserts)")
    level = re.search(r"Level:\s*([a-z0-9]+)", text)
    if not level or level[1] not in LEVELS:
        errs.append(f"{iid}: needs `Level:` {' | '.join(sorted(LEVELS))}")
    return errs


def history(root, rel, found, retired, base):
    """IDs are permanent: one defined at `base` must still be defined or be retired, and its text can't move to another ID."""
    old_text = "\n".join(records.git(root, "show", f"{base}:{rel}"))
    if not old_text:
        return []
    try:
        old_meta, _ = records.parse(rel, old_text + "\n")
    except ValueError:
        return []
    old, now = defined(old_text), defined((root / rel).read_text())
    errs = [f"{iid} was removed without being retired; add it to `retired:` (IDs are never reused)"
            for iid in old if iid not in now and iid not in retired]
    errs += [f"{iid} was retired at {base} and can't be brought back" for iid in old_meta.get("retired") or []
             if iid in now and iid not in retired]  # still listed: the current-file check already says so
    errs += [f"{other} now has {iid}'s text from {base}: renumbered? IDs are permanent" for iid, text in old.items()
             for other, t in now.items() if other != iid and text and t == text and now.get(iid) != text]
    return errs
