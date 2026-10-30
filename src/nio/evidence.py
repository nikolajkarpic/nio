"""The implementation jury's CLI-first evidence (2026-10-27-implementation-jury): running commands in a throwaway copy of
the repo and the run's results file."""
import json
import os
import re
import shlex
import tempfile
from pathlib import Path

from nio import implement, records

RESULTS = "results.json"  # CT-7, under .nio/runs/<run>/
KEEP = 100_000  # FR-41: bytes kept at each end of a run's output
FIRST_ERRORS = 5  # FR-42: lines of a failed check's output its finding holds
FIRST_CHARS = 2_000  # the same, for a check that prints very long lines
MAX_REQUESTED = 3  # FR-20: a juror's requested runs per round, across all jurors
LISTED = "listed for the human"  # a request not run; its text is a model's, so it stays out of every pack


def cut(output):
    """(output, bytes cut): over 200 KB, its first and last 100 KB around a `cut N bytes` line (FR-41)."""
    raw = output.encode()
    n = len(raw) - 2 * KEEP
    if n <= 0:
        return output, 0
    return f"{raw[:KEEP].decode(errors='replace')}\n[cut {n} bytes]\n{raw[-KEEP:].decode(errors='replace')}", n


def one(copy, command, limit, unstarted="failed"):
    """A command's entry in `in_copy`'s list. `unstarted`: its result when the shell couldn't start the program (126, 127)."""
    if not command:
        return {"command": command, "result": "not configured", "output": "", "cut": 0}
    code, out, cause = implement.run(copy, command, limit)
    output, n = cut(out)
    if cause == "time limit":
        output += f"\ntimed out after {limit} seconds\n"
    return {"command": command, "result": "passed" if code == 0 else unstarted if code in (126, 127) else "failed", "output": output, "cut": n}


def in_copy(root, commit, commands, limit, unstarted="failed"):
    """Run `commands` in order in one throwaway clone at `commit`, removed however the runs end (CT-2, FR-40, FR-41).
    Setup comes first in `commands`, so what it builds is there for the rest. ValueError, and nothing runs, when the
    clone can't be made."""
    limit = limit or implement.DEFAULT_LIMIT
    # A git hook or `rebase --exec` exports GIT_DIR and the like; left set, git in the copy would act on the human's repo.
    outer = {k: os.environ.pop(k) for k in records.git(root, "rev-parse", "--local-env-vars") if k in os.environ}
    try:
        with tempfile.TemporaryDirectory(prefix="nio-copy-", ignore_cleanup_errors=True) as tmp:
            copy = Path(tmp) / "copy"
            # --no-hardlinks: the temp folder is often another filesystem, where --local alone dies, and a linked
            # object file is one a run could write through. hooksPath: no global hooks or template hooks run here.
            clone = ("clone", "--local", "--no-hardlinks", "--no-checkout", "--config", "core.hooksPath=/dev/null",
                     str(Path(root).resolve()), str(copy))
            for where, args in ((tmp, clone), (copy, ("remote", "remove", "origin")),
                                (copy, ("checkout", "-q", "--detach", commit))):
                code, _, err = records.git(where, *args, full=True)
                if code:
                    raise ValueError(f"can't make the throwaway copy: {err.strip()}")
            return [one(copy, command, limit, unstarted) for command in commands]
    finally:
        os.environ.update(outer)


def runs_in_copy(root, commit, commands, unstarted="failed"):
    """`in_copy` under the project's `jury.run_timeout`, with `tests.setup` first when set; its own entry is dropped (a
    failed setup fails what follows)."""
    cfg = records.config(root)
    setup = [s] if (s := (cfg.get("tests") or {}).get("setup")) else []
    return in_copy(root, commit, setup + commands, (cfg.get("jury") or {}).get("run_timeout"), unstarted)[len(setup):]


def path(root, run):
    return Path(root) / ".nio/runs" / run / RESULTS


def load(root, run):
    """The run's results (CT-7), empty when none were written."""
    p = path(root, run)
    if p.exists():
        return json.loads(p.read_text())
    return {"commit": "", "tests": [], "checks": [], "attacks": [], "journeys": [], "hints": [], "requests": [], "evidence": []}


def save(root, run, results):
    p = path(root, run)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n")


def misuse(root, slug):
    """([TC file refs], [TC file refs]): the `file:name` of tests.md's misuse tests, then of its other tests."""
    p = Path(root) / ".nio/specs" / slug / "tests.md"
    mis, rest, section = [], [], ""
    for line in (p.read_text().splitlines() if p.exists() else []):
        if line.startswith("## "):
            section = line[3:].strip()
        elif m := re.match(r"- File: `([^:`]+):([^`]+)`", line):
            (mis if section == "Misuse tests" else rest).append((m[1], m[2]))
    return mis, rest


def one_test(suite, file, name):
    """The command that runs one test through the suite's runner, else None (a runner it can't address)."""
    if m := re.match(r"(.*\bunittest)\b", suite or ""):
        return f"{m[1]} {shlex.quote(file.removesuffix('.py').replace('/', '.') + '.' + name)}"
    if m := re.match(r"(.*\bpytest)\b", suite or ""):
        return f"{m[1]} {shlex.quote(file + '::' + name.replace('.', '::'))}"
    return None


def journeys(root, slug):
    """[(QS id, [(step command, [expected lines or None])])]: quickstart.md's `auto` scenarios. Expected is `contains:`
    lines, or None for exact output."""
    p = Path(root) / ".nio/specs" / slug / "quickstart.md"
    out = []
    for qs, body in re.findall(r"^### (QS-\d+) [^\n]*; auto\)[^\n]*\n(.*?)(?=^### |\Z)", p.read_text() if p.exists() else "", re.M | re.S):
        steps = re.findall(r"^\d+\. `([^`\n]+)`\s*\n\s*Expected:\s*\n\s*```\n(.*?)```", body, re.M | re.S)
        out.append((qs, [(c, e) for c, e in steps]))
    return out


def matched(expected, output):
    lines = [x.strip() for x in expected.strip().splitlines()]
    if lines and all(x.startswith("contains:") for x in lines):
        return all(x[9:].strip() in output for x in lines)
    return output.strip() == expected.strip()


def commits_of(root, slug, epic):
    """The commits named `T-n: ...` for a task of the epic, newest first. The walk stops at the commit that added the
    spec's tasks.md, since an earlier effort has its own T-1."""
    mine = {t["id"] for t in implement.tasks_of(root, slug) if t["epic"] == epic}
    added = records.git(root, "log", "-1", "--format=%H", "--diff-filter=A", "--", f".nio/specs/{slug}/tasks.md")
    out = []
    for x in records.git(root, "log", "--format=%H %s", "HEAD"):
        sha, _, subject = x.partition(" ")
        if subject.split(":")[0] in mine:
            out.append(sha)
        if [sha] == added:
            break
    if not out:
        raise ValueError(f"no commit of epic {epic} found")
    return out


def parent_of(root, commit):
    """The commit's parent; for a root commit, the empty tree, so a diff from it holds everything the commit added."""
    return (records.git(root, "rev-parse", "-q", "--verify", f"{commit}^") or records.git(root, "hash-object", "-t", "tree", "/dev/null"))[0]


DEFINES = re.compile(r"^\s*(?:async\s+)?(?:def|class|function)\s+(\w+)")


def phantoms(root, tasks, base, head):
    """[finding]: one major finding per missing file, file outside the epic's diff, or symbol the diff defines that nothing
    else mentions (CT-4, FR-6, FR-7, FR-8). Read from git at `head`, never from a task's status.
    ponytail: a symbol's own recursive call or a hit in a string or comment counts as a use; CT-5 hints the latter."""
    def finding(title, gap, cite, where):
        return {"title": title, "severity": "major", "gap": gap, "cite": cite, "where": where}

    in_diff = set(records.git(root, "diff", "--name-only", base, head))
    out = []
    for t in tasks:
        cite = ", ".join(t.get("serves") or [])
        for f in t.get("files") or []:
            if records.git(root, "cat-file", "-e", f"{head}:{f}", full=True)[0]:
                out.append(finding(f"{t['id']}: {f} doesn't exist", f"{t['id']} names {f}, which is not in the repo at {head[:8]}", cite, f))
            elif f not in in_diff:
                out.append(finding(f"{t['id']}: {f} isn't in the epic's diff", f"{t['id']} names {f}, which no commit of the epic changed", cite, f))
    defined, file = [], ""
    for line in records.git(root, "diff", "-U0", base, head):
        if line.startswith("+++ "):
            file = line[6:] if line.startswith("+++ b/") else ""
        elif line.startswith("+") and (m := DEFINES.match(line[1:])):
            name = m[1]
            if not (name.startswith("test_") or (name.startswith("__") and name.endswith("__"))):
                defined.append((name, file))
    for name, file in dict.fromkeys(defined):
        hits = [x.split(":", 3)[-1] for x in records.git(root, "grep", "-nwF", "-e", name, head)]
        if not [x for x in hits if not (m := DEFINES.match(x)) or m[1] != name]:
            cite = next((", ".join(t.get("serves") or []) for t in tasks if file in (t.get("files") or [])), "")
            out.append(finding(f"{name} in {file} is never used", f"{name} is defined in {file} and mentioned nowhere else", cite, file))
    return out


TEST_DEF = re.compile(r"^\s*(?:async\s+)?def\s+(test\w*)|^\s*(?:it|test|describe)(?:\.\w+)?\(\s*['\"`]([^'\"`]+)")
SKIP = re.compile(r"pytest\.mark\.skip|pytest\.skip\(|unittest\.skip|\bskipTest\(|\.skip\(|\bx(?:it|test|describe)\(|@Disabled|#\[ignore\]")


def tests_in(root, rev, f):
    """{test name: count of skip markers on it}: its decorators and body, or the skip call on its own line."""
    text = records.git(root, "show", f"{rev}:{f}", full=True)
    out, pending, cur = {}, 0, None
    for line in text[1].splitlines() if not text[0] else []:
        s = len(SKIP.findall(line))
        if m := TEST_DEF.match(line):
            cur = m[1] or m[2]
            out[cur] = out.get(cur, 0) + pending + s
            pending = 0
        elif line.lstrip().startswith("@"):
            pending += s
        elif cur:
            out[cur] += s
    return out


def tampering(root, base, head):
    """[finding]: one major finding per test the epic's diff deletes or newly skips (CT-6, FR-10). Marked `tampering`.
    ponytail: a renamed test reads as a deleted one; skip markers are regexes per known runner, not parsed."""
    out = []
    for line in records.git(root, "diff", "--name-status", "--no-renames", base, head):
        status, _, f = line.partition("\t")
        if not re.search(r"(^|[/_.-])tests?([/_.-]|$)|\.(test|spec)\.", f) or status == "A":
            continue
        before, after = tests_in(root, base, f), tests_in(root, head, f)
        for name, n in before.items():
            if name not in after:
                out.append({"title": f"test tampering: {name} in {f} is deleted", "severity": "major", "tampering": True,
                            "gap": f"the diff deletes the test {name} from {f}", "cite": "", "where": f})
            elif after[name] > n:
                out.append({"title": f"test tampering: {name} in {f} is skipped", "severity": "major", "tampering": True,
                            "gap": f"the diff adds a skip to the test {name} in {f}", "cite": "", "where": f})
    return out


ASSERT = re.compile(r"\bassert|\bexpect\(|\.should\b|\bt\.(?:Error|Fatal|Fail)")
STRING = re.compile(r"\"(?:\\.|[^\"\\])*\"|'(?:\\.|[^'\\])*'")


def added_lines(root, base, head):
    """{file: {line numbers the diff adds}}."""
    out, file = {}, ""
    for line in records.git(root, "diff", "-U0", base, head):
        if line.startswith("+++ "):
            file = line[6:] if line.startswith("+++ b/") else ""
        elif m := re.match(r"@@ -\S+ \+(\d+)(?:,(\d+))? @@", line):
            out.setdefault(file, set()).update(range(int(m[1]), int(m[1]) + int(m[2] or 1)))
    return out


def asserts_in(root, rev, f):
    """{test name: (def line, [its assertion lines])}, read line by line like `tests_in`."""
    text = records.git(root, "show", f"{rev}:{f}", full=True)
    out, cur = {}, None
    for n, line in enumerate(text[1].splitlines() if not text[0] else [], 1):
        if m := TEST_DEF.match(line):
            cur = m[1] or m[2]
            out[cur] = (n, [])
        elif cur and ASSERT.search(line):
            out[cur][1].append(line.strip())
    return out


def hints(root, base, head):
    """[hint]: possible stubs, uncertain references, tests with no assertion, changed or removed assertion lines in the
    epic's diff (CT-5, FR-9, FR-13, FR-36, FR-39). Never findings: a lens that confirms one raises it.
    ponytail: stubs are read for Python only; assertions and references by regex, not parsed."""
    import ast

    def hint(kind, file, name, line, interpretive, note):
        return {"kind": kind, "file": file, "name": name, "line": line, "interpretive": interpretive, "note": note}

    out, added = [], added_lines(root, base, head)
    for f, lines in added.items():
        if f.endswith(".py"):
            code = records.git(root, "show", f"{head}:{f}", full=True)
            try:
                tree = ast.parse(code[1]) if not code[0] else None
            except SyntaxError:
                tree = None
            for node in ast.walk(tree) if tree else []:
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.lineno in lines and all(
                        isinstance(s, ast.Pass) or (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant))
                        or (isinstance(s, ast.Raise) and "NotImplementedError" in ast.dump(s)) for s in node.body):
                    out.append(hint("possible stub", f, node.name, node.lineno, True, "its body is empty or only a TODO"))
        if re.search(r"(^|[/_.-])tests?([/_.-]|$)|\.(test|spec)\.", f):
            after = asserts_in(root, head, f)
            before = asserts_in(root, base, f) if records.git(root, "cat-file", "-e", f"{base}:{f}", full=True)[0] == 0 else {}
            for name, (line, found) in after.items():
                if name not in before and not found:
                    out.append(hint("test with no assertion", f, name, line, False, "no assertion in a test the diff adds"))
                elif name in before and set(before[name][1]) - set(found):
                    out.append(hint("changed assertion", f, name, line, False, "the diff changes or removes an assertion line"))
    defined = []
    for f, lines in added.items():
        text = records.git(root, "show", f"{head}:{f}", full=True)
        for n, line in enumerate(text[1].splitlines() if not text[0] else [], 1):
            if n in lines and (m := DEFINES.match(line)) and not (m[1].startswith("test_") or m[1].startswith("__")):
                defined.append((m[1], f, n))
    for name, f, n in defined:
        hits = [x.split(":", 3)[-1] for x in records.git(root, "grep", "-nwF", "-e", name, head)]
        uses = [x for x in hits if not ((m := DEFINES.match(x)) and m[1] == name)]
        if uses and not any(re.search(rf"\b{name}\b", STRING.sub('""', x)) for x in uses):
            out.append(hint("uncertain reference", f, name, n, True, "uncertain: it is only mentioned in strings, maybe called dynamically"))
    return out


def check_finding(name, check):
    """The major finding of a failed lint or type check, naming it and holding its first errors (FR-42). Its title stays
    the same from run to run, so a repeat adds none (CT-20)."""
    first = "\n".join([x for x in check["output"].splitlines() if x.strip()][:FIRST_ERRORS])[:FIRST_CHARS]
    return {"title": f"the {name} failed", "severity": "major", "gap": f"`{check['command']}` failed:\n{first}", "cite": "", "where": check["command"]}


def collect(root, slug, epic, run):
    """Run the epic's tests, lint, type check, misuse tests and auto journeys, each group in its own throwaway copy at
    the epic's last commit, write the run's results and send the findings of CT-4, CT-6 and a failed check to the ledger
    (CT-3, FR-3, FR-6, FR-7, FR-11, FR-12, FR-42). Returns the lines to print. ValueError when the epic isn't finished."""
    from nio import jury
    root = Path(root)
    jury.epic_gate(root, slug, f"implementation-{epic}")
    cfg = records.config(root)
    t = cfg.get("tests") or {}
    commits = commits_of(root, slug, epic)
    commit, base = commits[0], parent_of(root, commits[-1])
    runs = lambda commands: runs_in_copy(root, commit, commands)
    mis, rest = misuse(root, slug)
    suite = (runs([t.get("suite")]) if t.get("suite") else [{"result": "not configured", "output": "", "cut": 0}])[0]
    code_ok = suite["result"] == "passed"
    # ponytail: a failed suite names a test as failed when its name is in the output, or when the runner can't be read
    tests = [{"name": name, "file": file, "line": 0,
              "result": "passed" if code_ok or (implement.runner(t.get("suite", "")) in implement.SUMMARY
                                                and name.split(".")[-1] not in suite["output"]) else "failed"}
             for file, name in rest]
    attack_cmds = [one_test(t.get("suite"), f, n) for f, n in mis]
    attacks = runs(attack_cmds)
    for a, (f, n) in zip(attacks, mis):
        a["command"] = a["command"] or f"{f}:{n}"
    steps = [(c, e) for _, ss in journeys(root, slug) for c, e in ss]
    done = iter(runs([c for c, _ in steps]))
    journeys_out = []
    for qs, ss in journeys(root, slug):
        rs = [next(done) for _ in ss]
        ok = all(r["result"] == "passed" and matched(e, r["output"]) for r, (_, e) in zip(rs, ss))
        journeys_out.append({"command": " && ".join(c for c, _ in ss), "result": "passed" if ok else "failed",
                             "output": "\n".join(r["output"] for r in rs), "cut": sum(r["cut"] for r in rs)})
    results = {**load(root, run), "commit": commit, "tests": tests, "checks": runs([t.get("lint"), t.get("typecheck")]),
               "attacks": attacks, "journeys": journeys_out, "hints": hints(root, base, commit)}
    save(root, run, results)
    named = zip(("lint check", "type check"), results["checks"])
    jury.record_cli(root, slug, f"implementation-{epic}", [
        *phantoms(root, [x for x in implement.tasks_of(root, slug) if x["epic"] == epic], base, commit), *tampering(root, base, commit),
        *[check_finding(name, c) for name, c in named if c["result"] == "failed"]])
    return [str(path(root, run).relative_to(root))] + [f"{k}: not configured" for k, c in zip(("lint", "typecheck"), results["checks"])
                                                       if c["result"] == "not configured"]


def known_tests(root, slug):
    """{TC id: (file, test name), or None when its `File:` names no test}: every test of tests.md."""
    p = Path(root) / ".nio/specs" / slug / "tests.md"
    out = {}
    for m in re.finditer(r"^### (TC-\d+)\b.*?(?=^#{2,3} |\Z)", p.read_text() if p.exists() else "", re.M | re.S):
        f = re.search(r"^- File: `([^:`]+):([^`]+)`", m[0], re.M)
        out[m[1]] = (f[1], f[2]) if f else None
    return out


def asked(results):
    """The requests a pack may show: the runs made, and those that couldn't start."""
    return [r for r in results.get("requests") or [] if r.get("result") != LISTED]


def requested(root, led, run):
    """Make the runs this round's findings ask for, in a throwaway copy at the epic's last commit, and record them in the
    run's results for the next packs (CT-11, FR-20, FR-40). Returns (results, for the human), every round's. A request is
    only ever a key into tests.md: the command comes from the config's suite and that file, never from the request. A
    request that isn't a test of tests.md, or is over the round's runs, is listed for the human and not run. Calling it
    again in a round makes only the runs not yet made.
    ponytail: a finding's status isn't read, so a refuted finding's request still runs; the cap bounds what that costs."""
    from nio import jury
    root, slug, rnd = Path(root), led["subject"], led["round"]
    epic = jury.epic_gate(root, slug, led["gate"])
    results, known = load(root, run), known_tests(root, slug)
    suite = (records.config(root).get("tests") or {}).get("suite")
    requests = results["requests"]
    made = {r["request"]: r for r in requests if r["round"] == rnd and r["result"] != LISTED}
    started = sum(bool(r["command"]) for r in made.values())
    pending = []
    for f, tc in ((f, s["run"]) for f in led["findings"] for s in f["sources"] if s.get("run") and s.get("round") == rnd):
        command = one_test(suite, *known[tc]) if known.get(tc) else None
        why = "not a test of tests.md" if tc not in known else f"over the {MAX_REQUESTED} runs of a round" if command and started >= MAX_REQUESTED else ""
        if tc in made:  # one run answers every finding asking for it
            made[tc]["findings"] = sorted({*made[tc]["findings"], f["id"]})
        elif why:
            if not any(r["round"] == rnd and r["result"] == LISTED and r["request"] == tc and r["finding"] == f["id"] for r in requests):
                requests.append({"round": rnd, "request": tc, "finding": f["id"], "result": LISTED, "why": why})
        else:
            made[tc] = {"round": rnd, "request": tc, "findings": [f["id"]], "command": command or "", "commit": "",
                        "result": "couldn't run", "output": "" if command else "the test runner has no known way to run one test", "cut": 0}
            requests.append(made[tc])
            if command:
                pending.append(made[tc])
                started += 1
    if pending:
        try:
            commit = commits_of(root, slug, epic)[0]
            for r, out in zip(pending, runs_in_copy(root, commit, [r["command"] for r in pending], "couldn't run")):
                r.update(commit=commit, result=out["result"], output=out["output"], cut=out["cut"])
        except ValueError as e:
            for r in pending:
                r["output"] = str(e)
    save(root, run, results)
    return asked(results), [r for r in requests if r["result"] == LISTED]


def items(root, slug):
    """{ID: its text} for the spec's ACs and FRs and the contracts' CTs, in file order, with each CT's bound file."""
    from nio import jury
    d = Path(root) / ".nio/specs" / slug
    read = lambda n: (d / n).read_text() if (d / n).exists() else ""
    out = dict(jury.parts(read("spec.md"))[0])
    bound = {}
    for m in re.finditer(r"^### (CT-\d+)\b.*?(?=^#{2,3} |\Z)", read("contracts.md"), re.M | re.S):
        out[m[1]] = m[0].rstrip()
        if b := re.search(r"^- Binding:\s*`([^`:]+)", m[0], re.M):
            bound[m[1]] = b[1]
    return out, bound


def pack(root, slug, gate, lens, run):
    """A lens's pack at the implementation gate (CT-9, FR-17, FR-18): the epic's diff, the text of the ACs, FRs and CTs the
    diff touches and no others, the run's results and the hints. In a re-review it is a fix check: the lens's own findings
    and the diff since the commit the last round judged.
    ponytail: the last round's commit is the newest `versions` entry of the ledger, which the gate's collect must write."""
    from nio import jury
    root = Path(root)
    epic = jury.epic_gate(root, slug, gate)
    commits = commits_of(root, slug, epic)
    base, head = parent_of(root, commits[-1]), commits[0]
    results = load(root, run)
    led = jury.load(root, slug, gate)
    out = [f"# Pack: {lens}, {gate} gate of {slug}", "",
           "You may open any file of the project to read it. You have no way to write files or run commands.", ""]
    if led.get("versions") and jury.phase(led) in ("re-review", "final"):
        judged = led["versions"][max(led["versions"], key=int)]
        by_id = {f["id"]: f for f in led["findings"]}
        out += ["This is a fix check, not a review. Give one verdict per finding below, `- J-<n>: fixed | not fixed - <reason>`, "
                "from the diff since the commit the last round judged. Raise a new finding only if it is a blocker.", "",
                "## Your findings to check", *(["None: give no verdicts.", ""] if not jury.pack_ids(led, lens) else [])]
        for i in jury.pack_ids(led, lens):
            f = by_id[i]
            out += [f"### {f['id']} {f['title']}", f"- cites: {', '.join(f['cites'])}", f"- fix asked: {f['fix']}",
                    f"- what was done: {f['note']}", ""]
        if runs := asked(results):
            out += ["## Requested runs", "", json.dumps(runs, indent=2, ensure_ascii=False), ""]
        out += [f"## Diff since {judged[:8]}", "", *records.git(root, "diff", judged, head)]
        return "\n".join(out) + "\n"
    diff = records.git(root, "diff", base, head)
    names = set(records.git(root, "diff", "--name-only", base, head))
    text, bound = items(root, slug)
    serves = {s for t in implement.tasks_of(root, slug) if t["epic"] == epic for s in t["serves"]}
    touched = serves | {c for c, f in bound.items() if f in names}
    out += ["## Diff", "", *diff, "", "## Items the diff touches", "", *[text[i] + "\n" for i in text if i in touched],
            "## Results", "", json.dumps({**{k: v for k, v in results.items() if k != "hints"}, "requests": asked(results)}, indent=2, ensure_ascii=False), "",
            "## Hints (not findings: raise one only if you confirm it)", "", *([
                f"- {h['kind']}{' (interpretive)' if h['interpretive'] else ''}: {h['name']} at {h['file']}:{h['line']}, {h['note']}"
                for h in results.get("hints") or []] or ["None."])]
    return "\n".join(out) + "\n"
