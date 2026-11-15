"""The e2e step's check (CT-15): every `Level: e2e` AC of the spec has a Playwright test, and every such test fails on a
web-first assertion now, before any code exists. Standard library only; run in the repo root with NIO_SLUG set."""
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ANSI = re.compile(r"\x1b\[[0-9;]*m")
clean = lambda s: ANSI.sub("", s or "")
first = lambda s: (clean(s).strip().splitlines() or [""])[0]


def e2e_acs(text):
    """AC IDs whose own `Level:` (the last one after `Observable:`) is e2e."""
    out = []
    for m in re.finditer(r"^- \*\*(AC-\d+)\*\*.*?(?=^- \*\*|^#|\Z)", text, re.M | re.S):
        block = m[0]
        found = re.findall(r"Level:\s*([a-z0-9]+)", block[max(block.find("Observable:"), 0):])
        if found and found[-1] == "e2e":
            out.append(m[1])
    return out


def tests_of(text, ac):
    """[(file, name)] of the TCs aimed at `ac`, from their `### TC-n ... (AC-n; level)` headings and `File:` lines."""
    out = []
    for m in re.finditer(r"^### TC-\d+[^\n]*\(([^)\n]*)\)[^\n]*\n(.*?)(?=^#{2,3} |\Z)", text, re.M | re.S):
        f = re.search(r"^- File: `([^:`]+):([^`]+)`", m[2], re.M)
        if f and ac in re.findall(r"AC-\d+", m[1]):
            out.append((f[1], f[2]))
    return out


def walk(suites):
    for s in suites or []:
        for spec in s.get("specs", []):
            yield spec
        yield from walk(s.get("suites"))


def main():
    folder = Path(".nio/specs") / os.environ["NIO_SLUG"]
    acs = e2e_acs((folder / "spec.md").read_text())
    tests = (folder / "tests.md").read_text() if (folder / "tests.md").exists() else ""
    files, bad = [], []
    for ac in acs:
        ok = [(f, n) for f, n in tests_of(tests, ac) if Path(f).is_file() and ac in (Path(f).read_text()) and n in Path(f).read_text()]
        if ok:
            files.append(ok[0][0])
        else:
            bad.append(f"{ac} has no e2e test")
    if bad:
        print("\n".join(bad))
        return 1
    with tempfile.TemporaryDirectory() as tmp:
        report = Path(tmp) / "report.json"
        r = subprocess.run(["npx", "playwright", "test", *dict.fromkeys(files), "--reporter=json"], capture_output=True, text=True,
                           env={**os.environ, "PLAYWRIGHT_JSON_OUTPUT_NAME": str(report)})
        output = clean(r.stdout + r.stderr)
        if line := next((x.strip() for x in output.splitlines() if "config.webServer" in x), None):
            print(f"setup error: the app didn't start: {line}")
            return 1
        try:
            data = json.loads(report.read_text())
        except (OSError, ValueError):
            print(f"setup error: no report from playwright: {first(output)}")
            return 1
    if data.get("errors"):
        e = data["errors"][0]
        where = os.path.relpath((e.get("location") or {}).get("file") or "playwright", os.getcwd())
        print(f"setup error: {where}: {first(e.get('message'))}")
        return 1
    failing, problems, lines = 0, [], []
    for spec in walk(data.get("suites")):
        ac = (re.search(r"AC-\d+", spec["title"]) or [""])[0]
        for t in spec.get("tests", []):
            res = (t.get("results") or [{}])[-1]
            msg = clean((res.get("error") or {}).get("message")).strip()
            if res.get("status") == "passed":
                problems.append(f"{ac} {spec['title']}: passes before any code is written")
            elif res.get("status") == "failed" and re.match(r"expect\((page|locator)\)", re.sub(r"^Error: ", "", msg)):
                failing += 1
                for a in res.get("attachments", []):
                    if a.get("path") and a.get("name") in ("trace", "screenshot"):
                        lines.append(f"{a['name']}: {os.path.relpath(a['path'], os.getcwd())}")
            else:
                problems.append(f"{ac} {spec['title']}: fails on {first(msg or res.get('status', 'no result'))}, not on a web-first assertion")
    if problems:
        print("\n".join(problems))
        return 1
    print(f"e2e: {failing} tests fail on their assertions, as they should before implementation")
    print("\n".join(lines))
    return 0


sys.exit(main())
