"""End-to-end checks of the onboarding flow (2026-11-08-project-onboarding): each runs a skill on a real model in a fresh
git repo. They cost a model run each, so they run only when asked:
    NIO_E2E=1 uv run python tests/test_onboard_e2e.py
Without NIO_E2E they print `skipped` and pass."""
import subprocess
import tempfile
from pathlib import Path

from test_lenses import e2e

import selfcheck

ROOT = Path(__file__).resolve().parent.parent
TOOLS = "Read Grep Glob Edit Write Bash"


def skill_body(name):
    text = (ROOT / "skills" / name / "SKILL.md").read_text()
    return text.split("---", 2)[2].strip()


def fresh_repo():
    root = Path(tempfile.mkdtemp())
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    return root


def run_skill(root, name, ask):
    r = subprocess.run(["claude", "-p", "--system-prompt", skill_body(name), "--allowedTools", TOOLS],
                       input=ask, cwd=root, capture_output=True, text=True, timeout=1500)
    assert r.stdout.strip(), r.stderr
    return r.stdout


def last_paragraph(text):
    """The closing paragraph, skipping the `Refs:` line the talk shape ends with."""
    paras = [p for p in text.strip().split("\n\n") if p.strip() and not p.strip().startswith("Refs:")]
    return paras[-1]


@e2e
def test_ac17_install_points_to_onboard():
    root = fresh_repo()
    out = run_skill(root, "install", "Set NIO up in this repo. The CLI here is `uv run --project " + str(ROOT) +
                    " nio`. Answer the one question with: Keep every prompt.")
    closing = last_paragraph(out)
    assert "onboard" in closing.lower(), out
    assert not (root / ".nio" / "project").exists(), "onboarding started"


if __name__ == "__main__":
    selfcheck.main([f for n, f in list(globals().items()) if n.startswith("test_ac") and callable(f)])
