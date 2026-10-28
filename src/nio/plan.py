"""Plans (#41, #48): create the plan files next to an approved spec, and run their mechanical checks: structure,
permanent IDs, provenance, bindings, and coverage of every FR, AC and journey."""
import re
from importlib import resources
from pathlib import Path

from nio import records, spec

FILES = {  # file: (its ID prefix, mandatory sections, optional sections); plan.md first, the others read its frontmatter
    "plan.md": ("OP", ["Build order", "Coverage"], ["Complexity tracking", "Decisions", "Open points"]),
    "contracts.md": ("CT", ["Contracts"], ["Data model"]),
    "tests.md": ("TC", ["Acceptance tests"], ["Quality tests", "Misuse tests"]),
    "quickstart.md": ("QS", ["Scenarios"], ["Prerequisites"]),
}
HEAD = re.compile(r"\(([^()]*)\)\s*\[[^\]]*\]\s*$")  # the last parentheses before the provenance tag
BIND = re.compile(r"`([^`:]+)(?::([^`]+))?`\s*\((new|existing)\)")
ID = re.compile(r"\b[A-Z]+-\d+\b")


def new(root, slug):
    """Write the plan files that don't exist yet from their templates next to the spec, never overwriting one;
    return their paths."""
    folder = spec.path(root, slug).parent
    full_spec(root, slug)
    missing = [f for f in FILES if not (folder / f).exists()]
    if not missing:
        raise ValueError(f"the plan files already exist in {folder.relative_to(root)}")
    out = []
    for f in missing:
        (folder / f).write_text(resources.files("nio").joinpath(f"templates/{f}").read_text().replace("<slug>", slug))
        out.append(folder / f)
    return out


def full_spec(root, slug):
    """The spec's body; only a full spec has a plan stage."""
    if not spec.path(root, slug).exists():
        raise ValueError(f"no spec at {spec.path(root, slug).relative_to(root)}")
    meta, body = records.parse(spec.path(root, slug))
    if meta.get("route") != "full":
        raise ValueError(f"only a full spec has a plan stage; `{slug}` is route `{meta.get('route')}`")
    return body


def head(line):
    m = HEAD.search(line)
    return [p.strip() for p in m[1].split(";")] if m else []


def field(block, name):
    m = re.search(rf"^- {name}:[ \t]*(\S.*)$", "\n".join(block), re.M)
    return m[1] if m else ""


def check(root, slug, gate=False, base="HEAD"):
    """(errors, notes) for one spec's plan files."""
    folder = spec.path(root, slug).parent
    sbody = full_spec(root, slug)
    sdefs = {iid: block for _, lines in spec.sections(sbody).items() for iid, block in spec.items(lines)}
    errs, items, metas, psecs, bodies = [], {}, {}, {}, {}
    for f, (prefix, mandatory, optional) in FILES.items():
        p = folder / f
        rel = p.relative_to(root)
        if not p.exists():
            errs.append(f"{rel} is missing; create the plan files with `nio new plan {slug}`")
            continue
        try:
            meta, body = records.parse(p)
        except ValueError as e:
            errs.append(f"{rel}: {e}")
            continue
        metas[f] = meta
        body = re.sub(r"<!--.*?-->", "", "\n".join(body), flags=re.S).splitlines()
        bodies[rel] = body
        bad = lambda e: errs.append(f"{rel}: {e}")
        if meta.get("slug") != slug:
            bad(f"`slug` must be `{slug}`, the folder name")
        retired = meta.get("retired") or []
        if not isinstance(retired, list) or any(not isinstance(r, str) or not re.fullmatch(rf"{prefix}-\d+", r) for r in retired):
            bad(f"`retired` must be a list of {prefix} IDs, e.g. [{prefix}-3]")
            retired = []
        secs = spec.sections(body)
        bad_secs = [s for s in secs if s not in mandatory + optional]
        for s in bad_secs:
            bad(f"section `## {s}` is not part of {f}")
        for s in mandatory:
            if not "\n".join(secs.get(s, [])).strip():
                bad(f"section `## {s}` is missing or empty")
        for s, lines in secs.items():
            if re.fullmatch(r"(n/?a|none|tbd|-)\.?", "\n".join(lines).strip().lower()):
                bad(f"section `## {s}` says N/A; remove a section that doesn't apply")
            text = re.sub(r"```.*?```", "", "\n".join(lines), flags=re.S)  # expected output may hold anything
            if re.search(r"<[a-z][^>]*>", re.sub(r"`[^`]*`", "", text)):
                bad(f"section `## {s}` still has template `<placeholders>`")
        found = {}
        for s, lines in secs.items():
            if s == "Build order":  # its `### US-n` headings name the spec's stories, not new items
                continue
            for iid, block in spec.items(lines):
                found.setdefault(iid, []).append((s, block))
        for iid, defs in found.items():
            if len(defs) > 1:
                bad(f"{iid} is defined {len(defs)} times")
            if iid.split("-")[0] != prefix:
                bad(f"{iid}: only {prefix} IDs are defined in {f}")
            if iid in retired:
                bad(f"{iid} is retired and can't be used again")
            if prefix != "OP" and not spec.TAG.search(defs[0][1][0]):
                bad(f"{iid}: its heading must end with {spec.TAGS}")
            items[iid] = (f, defs[0][0], defs[0][1])
        # plan.md's build order names the spec's stories; their IDs are the spec's to keep, not this file's
        errs += [f"{rel}: {e}" for e in spec.history(root, rel, found, retired, base) if e.startswith(prefix + "-")]
        if f == "contracts.md":
            for line in [l for l in secs.get("Data model", []) if l.startswith("- ")]:  # its field lines are indented
                if not BIND.search(line) or not spec.TAG.search(line):
                    bad(f"data model `{line[2:40]}…` needs a binding (`file:symbol` (new | existing)) and must end with {spec.TAGS}")
                else:
                    name = re.match(r"- \*\*([^*]+)\*\*", line)
                    errs += binding(root, rel, f"data model {name[1] if name else line[2:40]}", BIND.search(line), metas, "stores new data")
        if f == "plan.md":
            psecs = secs

    arch = metas.get("plan.md", {}).get("architecture")
    if "plan.md" in metas and arch not in ("approved", "none"):
        errs.append(f"{folder.relative_to(root)}/plan.md: `architecture` must be `approved` or `none`")
    if arch == "approved" and not (folder / "architecture.md").exists():
        errs.append(f"{folder.relative_to(root)}/plan.md: `architecture: approved` but there is no architecture.md")
    kind = lambda pre: [i for i in items if i.startswith(pre + "-")]
    of = lambda pre: [i for i in sdefs if i.startswith(pre + "-")]
    where = lambda iid: f"{folder.relative_to(root)}/{items[iid][0]}"
    serves, targets = {}, {}  # CT -> spec IDs it serves; TC or QS -> its spec target
    for iid in kind("CT"):
        _, _, block = items[iid]
        parts = head(block[0])
        ids = [i.strip() for i in parts[0].split(",")] if len(parts) == 1 else []
        if not ids or any(i.split("-")[0] not in ("FR", "NFR") for i in ids):
            errs.append(f"{where(iid)}: {iid}: cite the FRs it serves before its tag, e.g. `### {iid} <name> (FR-1, FR-2) [default]`")
        errs += [f"{where(iid)}: {iid} cites {i}, which isn't in the spec" for i in ids if i not in sdefs]
        serves[iid] = ids
        for name in ("Binding", "Kind", "Shape"):
            if not field(block, name):
                errs.append(f"{where(iid)}: {iid}: needs `- {name}:`")
        if field(block, "Binding"):
            m = BIND.fullmatch(field(block, "Binding").strip())
            if not m:
                errs.append(f"{where(iid)}: {iid}: write the binding as `file:symbol` (new | existing); the symbol is optional")
            else:
                errs += binding(root, Path(where(iid)), iid, m, metas, "adds a module")
                errs += [f"{where(iid)}: {e}" for e in like(root, iid, m[3], field(block, "Like"))]
    for iid in kind("TC"):
        _, _, block = items[iid]
        parts = head(block[0])
        target, level = parts if len(parts) == 2 else ("", "")
        tid = target.removesuffix(" misuse")
        if not re.fullmatch(r"(AC|NFR)-\d+|UJ-\d+ misuse", target) or level not in spec.LEVELS:
            errs.append(f"{where(iid)}: {iid}: write `(AC-n; level)`, `(NFR-n; level)` or `(UJ-n misuse; level)` before its tag, "
                        f"the level one of {', '.join(sorted(spec.LEVELS))}")
        elif tid not in sdefs:
            errs.append(f"{where(iid)}: {iid} tests {tid}, which isn't in the spec")
        elif tid.startswith("AC-"):
            want = re.search(r"Level:\s*([a-z0-9]+)", "\n".join(sdefs[tid]))
            if want and want[1] != level:
                errs.append(f"{where(iid)}: {iid} is {level}, but {tid} asks for {want[1]}")
        targets[iid] = tid
        for name in ("File", "Covers", "Setup", "Action", "Assert"):
            if not field(block, name):
                errs.append(f"{where(iid)}: {iid}: needs `- {name}:`")
        if field(block, "File"):
            m = BIND.fullmatch(field(block, "File").strip())
            if not m:
                errs.append(f"{where(iid)}: {iid}: write the file as `file:test name` (new | existing)")
            else:
                errs += binding(root, Path(where(iid)), iid, m, metas, "")
        if field(block, "Covers") and not ID.findall(field(block, "Covers")):
            errs.append(f"{where(iid)}: {iid}: `Covers:` names the contracts it tests, e.g. CT-1")
        errs += [f"{where(iid)}: {iid} covers {c}, which isn't a contract"
                 for c in ID.findall(field(block, "Covers")) if not c.startswith("CT-") or c not in items]
    for iid in kind("QS"):
        _, _, block = items[iid]
        parts = head(block[0])
        if len(parts) != 2 or not re.fullmatch(r"UJ-\d+", parts[0]) or parts[1] not in ("auto", "manual"):
            errs.append(f"{where(iid)}: {iid}: write `(UJ-n; auto | manual)` before its tag")
        elif parts[0] not in sdefs:
            errs.append(f"{where(iid)}: {iid} walks {parts[0]}, which isn't in the spec")
        else:
            targets[iid] = parts[0]
        text = "\n".join(block)
        if "Expected:" not in text or not field(block, "Pass when"):
            errs.append(f"{where(iid)}: {iid}: needs numbered steps with `Expected:` and a `- Pass when:` line")

    # provenance: a cited research fact exists, and a derived item's sources exist and are settled (as in the spec)
    research = folder / "research.md"
    rfs = set(re.findall(r"\*\*(RF-\d+)\*\*", research.read_text())) if research.exists() else set()
    known = {i: [("", b)] for i, b in sdefs.items()} | {i: [("", b)] for i, (_, _, b) in items.items()}
    for rel, body in bodies.items():
        errs += [f"{rel}: {e}" for e in spec.check_tags(body, known, rfs)]
        errs += [f"{rel}: `{line.strip()[:40]}` cites {rf}, which isn't in research.md"
                 for line in body for rf in re.findall(r"\[research: (RF-\d+)\]", re.sub(r"`[^`]*`", "", line)) if rf not in rfs]

    # coverage: every FR is served, every AC tested, every journey walked
    errs += [f"{fr} has no contract" for fr in of("FR") if not any(fr in s for s in serves.values())]
    errs += [f"{ac} has no test" for ac in of("AC") if ac not in targets.values()]
    errs += [f"{uj} has no quickstart scenario" for uj in of("UJ") if not any(targets.get(q) == uj for q in kind("QS"))]

    secs = psecs
    rel = f"{folder.relative_to(root)}/plan.md"
    if secs:
        errs += [f"{rel}: {e}" for e in check_build(secs, items, sdefs, of)]
        errs += [f"{rel}: {e}" for e in check_coverage(secs, items, sdefs, of, serves, targets)]
        for iid in kind("OP"):
            m = re.match(r"^\((fact|decision);\s*([^)]+)\)\s*\S", spec.DEF.sub("", items[iid][2][0], count=1).strip())
            if items[iid][1] != "Open points" or not m:
                errs.append(f"{rel}: {iid}: write it under `## Open points` as `**{iid}** (fact|decision; <file and ID>) <question>`")
            else:
                errs += [f"{rel}: {iid} is about {t}, which is neither in the plan nor the spec"
                         for t in ID.findall(m[2]) if t not in items and t not in sdefs]
                errs += [f"{rel}: {iid}: name the ID it belongs to, e.g. `(decision; CT-2)`"] * (not ID.findall(m[2]))
        if gate and "\n".join(secs.get("Open points", [])).strip():
            errs.append(f"{rel}: `## Open points` must be empty at the gate")
    manual = [q for q in kind("QS") if "; manual)" in items[q][2][0]]
    notes = [f"manual scenarios: {', '.join(manual)}"] * bool(manual)
    defaults = [i for i in items if (t := spec.TAG.search(items[i][2][0])) and t[1] == "default"]
    notes += [f"proposals for the plan jury: {', '.join(defaults)}"] * bool(defaults)
    return errs, notes


def like(root, iid, kind, value):
    """A new contract names the existing code it follows, `file:symbol`, or `none: <reason>` (#57 FR-28 to FR-30)."""
    if kind != "new":
        return []
    if not value:
        return [f"{iid}: a new contract needs `- Like: <file>:<symbol>` or `- Like: none: <reason>`"]
    if re.match(r"none\b", value):
        return [] if re.match(r"none:\s*\S", value) else [f"{iid}: `Like: none` needs a reason, as `Like: none: <reason>`"]
    m = re.fullmatch(r"`?([^`:\s]+)(?::([^`\s]+))?`?", value.strip())
    if not m:
        return [f"{iid}: write `Like:` as `<file>:<symbol>` or `none: <reason>`"]
    path = root / m[1]
    if not path.is_file() or not path.resolve().is_relative_to(root.resolve()):
        return [f"{iid}: `Like:` names `{m[1]}`, which doesn't exist"]
    if m[2] and not re.search(rf"(?<![\w.]){re.escape(m[2])}(?!\w)", path.read_text()):
        return [f"{iid}: `Like:` names `{m[2]}`, which isn't in `{m[1]}`"]
    return []


def approved(root, slug):
    """(ok, why): may the tasks stage start on this spec (#57 FR-38, FR-39, FR-47)? A bug-fix spec has no plan stage; a
    full spec needs its plan gate approved, or closed by the human, on the current plan and spec."""
    from nio import jury  # jury imports this module for the plan gate's check
    if not spec.path(root, slug).exists():
        raise ValueError(f"no spec at {spec.path(root, slug).relative_to(root)}")
    meta, _ = records.parse(spec.path(root, slug))
    if meta.get("route") == "lite":
        return True, "a bug-fix spec has no plan stage"
    if meta.get("route") != "full":
        return False, f"`{slug}` is route `{meta.get('route')}`: run the tasks stage on each slice's spec"
    if not (spec.path(root, slug).parent / "plan.md").exists():
        return False, "the plan must be approved first (there is no plan.md)"
    st, why = jury.state(root, slug)
    if st in ("approved", "closed-by-human"):
        return True, why
    return False, f"the plan must be approved first ({st}: {why})"


def binding(root, rel, what, m, metas, change):
    """A binding stays inside the repository, and new or existing matches the code. Without an approved architecture, the plan may not add a folder or new
    stored data: those are on the plan skill's stop list."""
    file, symbol, kind = m[1], m[2], m[3]
    if Path(file).is_absolute() or not (root / file).resolve().is_relative_to(root.resolve()):
        return [f"{rel}: {what} binds `{file}`, which is outside the repository"]
    if kind == "existing" and not (root / file).exists():
        return [f"{rel}: {what} binds `{file}` as existing, but there is no such file"]
    if kind == "new" and not symbol and (root / file).exists():
        return [f"{rel}: {what} binds `{file}` as new, but the file exists; mark it existing or name the new symbol"]
    if change and kind == "new" and metas.get("plan.md", {}).get("architecture") == "none":
        # ponytail: a new folder stands in for "a new module"; refine if a language puts modules elsewhere
        if change == "stores new data" or not (root / file).parent.exists():
            return [f"{rel}: {what} {change} (`{file}`) with no approved architecture; stop and run @nio:architecture"]
    return []


def check_build(secs, items, sdefs, of):
    errs, listed = [], {"Delivers": set(), "Tests": set(), "Scenario": set()}
    stories = set()
    prefix = {"Delivers": "CT", "Tests": "TC", "Scenario": "QS"}
    names = [name for name, _ in spec.subsections(secs.get("Build order", []))]
    for name, lines in spec.subsections(secs.get("Build order", [])):
        m = re.match(r"(US-\d+)\b", name)
        if name != "Foundation" and not m:
            errs.append(f"build order `### {name}`: an entry is `Foundation` or a user story, `US-n <title>`")
        elif m and m[1] not in sdefs:
            errs.append(f"build order `### {name}`: {m[1]} isn't in the spec")
        elif m and m[1] in stories:
            errs.append(f"build order: {m[1]} has more than one entry")
        elif m:
            stories.add(m[1])
        if not field(lines, "Delivers"):
            errs.append(f"build order `### {name}`: needs `- Delivers:`")
        for dep in re.findall(r"Foundation|US-\d+", field(lines, "Depends on")):
            if dep != "Foundation" and dep not in sdefs or dep == "Foundation" and "Foundation" not in names:
                errs.append(f"build order `### {name}` depends on {dep}, which has no entry")
        for iid in ID.findall(field(lines, "Delivers")):
            if iid in listed["Delivers"]:
                errs.append(f"build order: {iid} is delivered by more than one entry")
        for key in listed:
            for iid in ID.findall(field(lines, key)):
                if iid not in items:
                    errs.append(f"build order `### {name}` lists {iid}, which isn't in the plan")
                elif not iid.startswith(prefix[key] + "-"):
                    errs.append(f"build order `### {name}` lists {iid} under `{key}:`, which takes {prefix[key]} IDs")
                listed[key].add(iid)
    errs += [f"build order: {us} has no entry" for us in of("US") if us not in stories]
    for key, pre in prefix.items():
        errs += [f"build order: {i} isn't in any `{key}:` line" for i in items if i.startswith(pre + "-") and i not in listed[key]]
    return errs


def check_coverage(secs, items, sdefs, of, serves, targets):
    """One row per FR, AC and NFR, every cell computed from the files so the table can't drift from them:
    Contracts are those citing the FR or NFR (for an AC, its FRs); Tests are those aimed at the AC or NFR (for an FR,
    at its ACs). An NFR no test can measure and no contract
    serves may say `none` in both cells; the plan jury judges that."""
    if "Coverage" not in secs:
        return []  # reported as a missing section
    rows = spec.table(secs["Coverage"])
    if not rows or rows[0] != ["Spec ID", "Contracts", "Tests"]:
        return ["coverage: the table's header is `| Spec ID | Contracts | Tests |`"]
    errs, seen = [], set()
    for r in rows[1:]:
        if len(r) != 3:
            errs.append(f"coverage row {r[0]}: 3 cells, got {len(r)}")
            continue
        sid, cts, tcs = r[0], set(ID.findall(r[1])), set(ID.findall(r[2]))
        if sid in seen:
            errs.append(f"coverage: {sid} has more than one row")
        seen.add(sid)
        if sid not in sdefs or sid.split("-")[0] not in ("FR", "AC", "NFR"):
            errs.append(f"coverage row {sid}: not an FR, AC or NFR of the spec")
            continue
        for col, pre, ids in (("Contracts", "CT", cts), ("Tests", "TC", tcs)):
            errs += [f"coverage row {sid} lists {i}, which isn't in the plan" if i not in items else
                     f"coverage row {sid} lists {i} under {col}, which takes {pre} IDs" for i in ids
                     if i not in items or not i.startswith(pre + "-")]
        frs = spec.cites(sdefs[sid][0]) if sid.startswith("AC-") else [sid]
        acs = [a for a in sdefs if a.startswith("AC-") and sid in spec.cites(sdefs[a][0])] if sid.startswith("FR-") else [sid]
        want_ct = {c for c, ids in serves.items() if set(ids) & set(frs)}
        want_tc = {t for t, tid in targets.items() if tid in acs and t.startswith("TC-")}
        if cts != want_ct:
            errs.append(f"coverage row {sid}: Contracts must be {', '.join(sorted(want_ct)) or 'none'}")
        if tcs != want_tc:
            errs.append(f"coverage row {sid}: Tests must be {', '.join(sorted(want_tc)) or 'none'}")
        if not cts | tcs and not sid.startswith("NFR-"):
            errs.append(f"coverage row {sid}: names no contract and no test")
    errs += [f"coverage: {i} has no row" for pre in ("FR", "AC", "NFR") for i in of(pre) if i not in seen]
    return errs
