"""Real-browser and real-model checks of the shipped e2e extension (2026-11-15-extensions TC-29, TC-34, TC-35). They need
Node, Chromium (`npx playwright install chromium`), the network for `npm install`, and for TC-29 a model, so they run
only when asked:
    NIO_E2E=1 uv run python tests/test_extensions_e2e.py
Without NIO_E2E they print `skipped` and pass."""
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
from pathlib import Path

from test_lenses import e2e

from nio import agents, evidence, implement
import selfcheck

HERE = Path(__file__).parent
APP = HERE / "fixtures/e2e-app"
SHIPPED = HERE.parent / "src/nio/shipped/e2e"
S = "2026-11-16-demo"


def app_copy():
    """A temp git repo holding the e2e-app fixture with its dependencies installed."""
    root = Path(tempfile.mkdtemp())
    shutil.copytree(APP, root, dirs_exist_ok=True)
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["npm", "install", "--no-audit", "--no-fund"], cwd=root, check=True, capture_output=True)
    return root


def refused(port=4173):
    with socket.socket() as s:
        return s.connect_ex(("127.0.0.1", port)) != 0


@e2e
def test_app_started_and_stopped():
    root = app_copy()
    for file, name, want in (("e2e/pass.spec.ts", "AC-1 shows the title", 0), ("e2e/fail.spec.ts", "AC-2 shows another title", 1)):
        code, out, _ = implement.run(root, evidence.one_test(None, file, name, root), 300)
        assert (code == 0) == (want == 0), out
        assert subprocess.run(["pgrep", "-f", "nio-e2e-marker"], capture_output=True).returncode == 1
        assert refused()


def spec_files(root, acs):
    d = root / ".nio/specs" / S
    d.mkdir(parents=True)
    (d / "spec.md").write_text("## Acceptance criteria\n\n" + "".join(f"- **{ac}** (FR-1) {t} [agent]\n  Observable: {o}. Level: e2e.\n" for ac, t, o in acs))
    (d / "tests.md").write_text("## Acceptance tests\n\n" + "".join(
        f"### TC-{n} {t} ({ac}; e2e) [agent]\n- File: `e2e/{ac}.spec.ts:{ac} {t}` (new)\n\n" for n, (ac, t, _) in enumerate(acs, 1)))


@e2e
def test_failure_keeps_trace_and_screenshot():
    root = app_copy()
    (root / "playwright.config.ts").write_text((root / "playwright.config.ts").read_text().replace(
        "use: {", "use: { trace: 'retain-on-failure', screenshot: 'only-on-failure',").replace("pw-out", "test-results"))
    (root / ".gitignore").write_text("node_modules/\ntest-results/\n")
    spec_files(root, [("AC-2", "shows another title", "the title is Not the title")])
    shutil.copy(root / "e2e/fail.spec.ts", root / "e2e/AC-2.spec.ts")
    (root / "e2e/pass.spec.ts").unlink()
    (root / "e2e/fail.spec.ts").unlink()
    subprocess.run(["git", "add", "-A"], cwd=root, check=True)
    r = subprocess.run([sys.executable, str(SHIPPED / "check.py")], cwd=root, capture_output=True, text=True, env={**os.environ, "NIO_SLUG": S})
    assert r.returncode == 0, r.stdout + r.stderr
    trace, shot = re.search(r"^trace: (test-results/\S+/trace\.zip)$", r.stdout, re.M), re.search(r"^screenshot: (test-results/\S+\.png)$", r.stdout, re.M)
    assert trace and shot and (root / trace[1]).exists() and (root / shot[1]).exists(), r.stdout
    assert "test-results/" not in subprocess.run(["git", "status", "--porcelain"], cwd=root, capture_output=True, text=True).stdout


@e2e
def test_tester_writes_one_test_per_e2e_ac():
    root = app_copy()
    for f in ("pass", "fail"):
        (root / f"e2e/{f}.spec.ts").unlink()
    spec_files(root, [("AC-1", "shows the title", "the page title is NIO Demo"), ("AC-2", "shows the message", "clicking Greet shows Hello from NIO")])
    subprocess.run([sys.executable, "-c", "import sys; from nio.cli import main; sys.argv = ['nio', 'extensions', 'add', 'e2e']; main()"],
                   cwd=root, check=True, capture_output=True)
    meta, body, _ = agents.load(root)["e2e-tester"]
    ask = (f"Read .nio/specs/{S}/spec.md and tests.md and write the Playwright tests as your instructions say, then list them in "
           f".nio/specs/{S}/e2e.md. Run no other command.")
    r = subprocess.run(["claude", "-p", "--model", agents.DEFAULT_TIERS["claude"][meta["tier"]], "--system-prompt", body, "--allowedTools", "Read Edit Write Bash"],
                       input=ask, cwd=root, capture_output=True, text=True, timeout=1500)
    assert r.stdout.strip(), r.stderr
    for ac in ("AC-1", "AC-2"):
        text = next((root / "e2e").glob(f"{ac}.spec.ts")).read_text()
        assert len(re.findall(r"\btest\(", text)) == 1 and re.search(rf"test\(\s*['\"`][^'\"`]*{ac}", text), text
    assert "AC-1" in (root / f".nio/specs/{S}/e2e.md").read_text() and "AC-2" in (root / f".nio/specs/{S}/e2e.md").read_text()
    config = (root / "playwright.config.ts").read_text()
    assert "timeout: 12345" in config and "outputDir: 'pw-out'" in config and "pw-out" in (root / ".gitignore").read_text()
    r = subprocess.run([sys.executable, str(SHIPPED / "check.py")], cwd=root, capture_output=True, text=True, env={**os.environ, "NIO_SLUG": S})
    assert r.returncode == 0, r.stdout + r.stderr


selfcheck.main([v for k, v in list(globals().items()) if k.startswith("test_") and callable(v)])
