"""Self-check for the status pane: runs `claude plugin test` and prints one ok/FAIL line per pane test. Run: uv run python tests/test_pane.py"""
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import selfcheck

PLUGIN = "tools/claude-mods/nio-status-pane"


def pane_tests():
    root = Path(__file__).resolve().parent.parent
    p = subprocess.run(["claude", "plugin", "test", PLUGIN], cwd=root, capture_output=True, text=True)
    res = re.findall(r"^\((pass|fail)\) (.+?)(?: \[[\d.]+m?s\])?$", p.stdout, re.M)
    if not res:
        print(p.stdout[-2000:] + p.stderr[-2000:])

    def make(ok, n):
        def t():
            assert ok == "pass", n
        t.__name__ = n
        return t
    return [make(ok, n) for ok, n in res]


if __name__ == "__main__":
    selfcheck.main(pane_tests())
