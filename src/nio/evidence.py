"""The implementation jury's CLI-first evidence (2026-10-27-implementation-jury): running commands in a throwaway copy of
the repo and the run's results file."""
import json
import os
import re
import tempfile
from pathlib import Path

from nio import implement, records

RESULTS = "results.json"  # CT-7, under .nio/runs/<run>/
KEEP = 100_000  # FR-41: bytes kept at each end of a run's output


def cut(output):
    """(output, bytes cut): over 200 KB, its first and last 100 KB around a `cut N bytes` line (FR-41)."""
    raw = output.encode()
    n = len(raw) - 2 * KEEP
    if n <= 0:
        return output, 0
    return f"{raw[:KEEP].decode(errors='replace')}\n[cut {n} bytes]\n{raw[-KEEP:].decode(errors='replace')}", n


def one(copy, command, limit):
    """A command's entry in `in_copy`'s list."""
    if not command:
        return {"command": command, "result": "not configured", "output": "", "cut": 0}
    code, out, cause = implement.run(copy, command, limit)
    output, n = cut(out)
    if cause == "time limit":
        output += f"\ntimed out after {limit} seconds\n"
    return {"command": command, "result": "passed" if code == 0 else "failed", "output": output, "cut": n}


def in_copy(root, commit, commands, limit):
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
            return [one(copy, command, limit) for command in commands]
    finally:
        os.environ.update(outer)


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
        return f"{m[1]} {file.removesuffix('.py').replace('/', '.')}.{name}"
    if m := re.match(r"(.*\bpytest)\b", suite or ""):
        return f"{m[1]} {file}::{name.replace('.', '::')}"
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


def commit_of(root, slug, epic):
    """The newest commit named `T-n: ...` for a task of the epic (the epic's last commit)."""
    from nio import implement
    mine = {t["id"] for t in implement.tasks_of(root, slug) if t["epic"] == epic}
    for x in records.git(root, "log", "--format=%H %s", "HEAD"):
        sha, _, subject = x.partition(" ")
        if subject.split(":")[0] in mine:
            return sha
    raise ValueError(f"no commit of epic {epic} found")


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


def collect(root, slug, epic, run):
    """Run the epic's tests, lint, type check, misuse tests and auto journeys, each group in its own throwaway copy at
    the epic's last commit, and write the run's results (CT-3, FR-3, FR-6, FR-7, FR-11, FR-12). Returns the lines to print.
    ValueError when the epic isn't finished. ponytail: the findings of CT-4, CT-6 and a failed check go to CT-20 once it exists."""
    from nio import jury
    root = Path(root)
    jury.epic_gate(root, slug, f"implementation-{epic}")
    cfg = records.config(root)
    t, limit = cfg.get("tests") or {}, (cfg.get("jury") or {}).get("run_timeout")
    commit = commit_of(root, slug, epic)

    def runs(commands):
        """in_copy with `tests.setup` first when set; its own entry is dropped (a failed setup fails what follows)."""
        out = in_copy(root, commit, ([t["setup"]] if t.get("setup") else []) + commands, limit)
        return out[bool(t.get("setup")):]

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
               "attacks": attacks, "journeys": journeys_out}
    save(root, run, results)
    return [str(path(root, run).relative_to(root))] + [f"{k}: not configured" for k, c in zip(("lint", "typecheck"), results["checks"])
                                                       if c["result"] == "not configured"]
