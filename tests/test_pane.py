"""Self-check for the status pane: runs `claude plugin test` and prints one ok/FAIL line per pane test. Run: uv run python tests/test_pane.py"""
import re
import subprocess
import sys
from pathlib import Path

PLUGIN = "tools/claude-mods/nio-status-pane"
FILE = f"{PLUGIN}/hooks/register.test.tsx"


def main():
    names = [a for a in sys.argv[1:] if not a.startswith("-")]
    root = Path(__file__).resolve().parent.parent
    p = subprocess.run(["claude", "plugin", "test", PLUGIN], cwd=root, capture_output=True, text=True)
    res = re.findall(r"^\((pass|fail)\) (.+?)(?: \[[\d.]+m?s\])?$", p.stdout, re.M)
    if names:
        res = [r for r in res if any(n in r[1] for n in names)]
    for ok, n in res:
        print(f"{'ok' if ok == 'pass' else 'FAIL'} {FILE}::{n}")
    failed = sum(ok == "fail" for ok, _ in res)
    if not res:
        print(p.stdout[-2000:] + p.stderr[-2000:])
    print(f"ran {len(res)} tests, {failed} failed")
    sys.exit(0 if res and not failed and (names or p.returncode == 0) else 1)


main()
