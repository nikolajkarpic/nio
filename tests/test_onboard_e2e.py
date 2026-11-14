"""End-to-end checks of the onboarding flow (2026-11-08-project-onboarding): each runs a skill on a real model in a fresh
git repo. They cost a model run each, so they run only when asked:
    NIO_E2E=1 uv run python tests/test_onboard_e2e.py
Without NIO_E2E they print `skipped` and pass."""
import datetime
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


@e2e
def test_ac32_actor_names_persona():
    root = fresh_repo()
    nio = ["uv", "run", "--project", str(ROOT), "nio"]
    (root / ".nio/project").mkdir(parents=True)
    (root / ".nio/project/personas.md").write_text("### P-1 Shop owner\nWho: owns a shop\nWants: orders\n"
                                                   "Allowed to: manage stock\nHow often: daily\n")
    slug = datetime.date.today().isoformat() + "-shop"
    subprocess.run(nio + ["onboard", "skip", "e2e fixture"], cwd=root, check=True, capture_output=True)
    subprocess.run(nio + ["new", "spec", "shop", "--route", "full"], cwd=root, check=True, capture_output=True)
    intake = root / ".nio/specs" / slug / "intake.md"
    intake.write_text("The shop owner can see today's orders. A courier collects parcels.\n")
    run = subprocess.run(nio + ["run"], cwd=root, check=True, capture_output=True, text=True).stdout.split()[-1]
    subprocess.run(nio + ["pack", "shop owner orders and courier", "--run", run, "--reader", "spec", "--slug", slug],
                   cwd=root, check=True, capture_output=True)
    pack = next((root / ".nio/runs" / run / "packs").glob("*.md"))
    card = (ROOT / "src/nio/agents/spec-drafter.md").read_text().split("---", 2)[2].strip()
    r = subprocess.run(["claude", "-p", "--system-prompt", card, "--allowedTools", TOOLS],
                       input=f"Slug: {slug}. Intake: {intake.relative_to(root)}. Spec: .nio/specs/{slug}/spec.md. "
                       f"Pack: {pack.relative_to(root)}. CLI: {' '.join(nio)}. Write the spec and report the actor lines.",
                       cwd=root, capture_output=True, text=True, timeout=1500)
    assert r.stdout.strip(), r.stderr
    spec = (root / ".nio/specs" / slug / "spec.md").read_text()
    owner = [l for l in spec.splitlines() if "shop owner" in l.lower()]
    courier = [l for l in spec.splitlines() if "courier" in l.lower()]
    assert any("P-1" in l for l in owner), spec
    assert any("no persona" in l for l in courier), spec


@e2e
def test_ac5_mismatch_asked():
    root = fresh_repo()
    nio = ["uv", "run", "--project", str(ROOT), "nio"]
    (root / "README.md").write_text("# Shop\n\nBuilt with Django.\n")
    (root / "pyproject.toml").write_text("[project]\nname = 'shop'\ndependencies = ['flask']\n")
    scan = subprocess.run(nio + ["onboard", "scan"], cwd=root, capture_output=True, text=True).stdout
    h = next(l.split()[2] for l in scan.splitlines() if l.split()[1:2] == ["pyproject.toml"])
    ask = ("Run @nio:onboard. The CLI here is `" + " ".join(nio) + "`. You play both roles: the dev's scripted answers "
           "are: product and personas confirmed as written; to the framework question answer `Flask; the README is old`; "
           "confirm stack.md; then `stop`. Print every question you ask the dev and every command you run.")
    out = run_skill(root, "onboard", ask)
    q = next((i for i, l in enumerate(out.splitlines()) if "Django" in l and "Flask" in l), None)
    c = next((i for i, l in enumerate(out.splitlines()) if "onboard confirm stack" in l), len(out))
    assert q is not None and q < c, out
    stack = (root / ".nio/project/stack.md").read_text()
    assert "Flask" in stack and "Django" not in stack, stack
    assert all(f"(source: pyproject.toml@{h})" in l for l in stack.splitlines() if "Flask" in l), stack


if __name__ == "__main__":
    selfcheck.main([f for n, f in list(globals().items()) if n.startswith("test_ac") and callable(f)])
