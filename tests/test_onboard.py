"""Self-check for nio onboard scan (2026-11-08-project-onboarding, T-1).
Run: uv run python tests/test_onboard.py"""
import hashlib
import subprocess
import tempfile
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
import selfcheck


def repo(files, ignore=""):
    root = Path(tempfile.mkdtemp())
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    (root / ".gitignore").write_text(ignore)
    for p, text in files.items():
        f = root / p
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(text)
    return root


def scan(root):
    r = subprocess.run(["uv", "run", "--project", str(Path(__file__).parent.parent), "nio", "onboard", "scan"],
                       cwd=root, capture_output=True, text=True)
    return r.returncode, r.stdout


def test_scan_lists_each_category():
    files = {"CLAUDE.md": "a", "README.md": "b", "ARCHITECTURE.md": "c", "pyproject.toml": "d", "main.tf": "e",
             ".github/workflows/ci.yml": "f"}
    want = {"CLAUDE.md": "agent-docs", "README.md": "product-docs", "ARCHITECTURE.md": "implementation-docs",
            "pyproject.toml": "manifests", "main.tf": "iac", ".github/workflows/ci.yml": "ci"}
    root = repo(files)
    code, out = scan(root)
    lines = out.strip().splitlines()
    assert lines and lines[-1] == "6 candidate files", out
    got = {l.split()[1]: l.split() for l in lines[:-1]}
    assert len(lines) == 7 and set(got) == set(want), out
    assert [l.split()[:2] for l in lines[:-1]] == sorted([c, p] for p, c in want.items()), out
    for p, cat in want.items():
        h = hashlib.sha256((root / p).read_bytes()).hexdigest()[:12]
        assert got[p] == [cat, p, h], (p, got[p])


def test_scan_secrets_path_only():
    sys_path = str(Path(__file__).parent.parent / "src")
    root = repo({".env": "K=1", "README.md": "r", "secret.pem": "x"}, ignore=".env\n")
    r = subprocess.run(["python3", "-c", "import sys;sys.path.insert(0,%r);from nio import onboard;print(onboard.scan('.'))" % sys_path],
                       cwd=root, capture_output=True, text=True)
    assert ("'secrets', '.env', ''" in r.stdout and "'secrets', 'secret.pem', ''" in r.stdout
            and "product-docs" in r.stdout), (r.stdout, r.stderr)


def test_scan_prints_no_dependency():
    root = repo({"pyproject.toml": '[project]\ndependencies = ["requests>=2", "rich"]\n'})
    code, out = scan(root)
    assert "requests" not in out and "rich" not in out, out
    h = hashlib.sha256((root / "pyproject.toml").read_bytes()).hexdigest()[:12]
    assert f"manifests pyproject.toml {h}" in out.splitlines(), out


def test_scan_skips_ignored_and_nio():
    paths = ["build/README.md", ".nio/project/README.md", ".nio/backup/2026-11-08/CLAUDE.md"]
    root = repo({p: "x" for p in paths}, ignore="build/\n")
    code, out = scan(root)
    assert code == 0 and "candidate files" in out or "no candidate" in out, out
    assert not any(p in out for p in paths), out


def test_scan_empty_repo():
    root = repo({})
    subprocess.run(["git", "add", "."], cwd=root, check=True)
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "init"], cwd=root, check=True)
    code, out = scan(root)
    assert code == 0 and out.strip() == "no candidate files found", (code, out)


def test_scan_outside_git_repo():
    root = Path(tempfile.mkdtemp())
    r = subprocess.run(["uv", "run", "--project", str(Path(__file__).parent.parent), "nio", "onboard", "scan"],
                       cwd=root, capture_output=True, text=True)
    assert r.returncode == 1 and "nio onboard scan needs a git repository" in r.stderr, (r.returncode, r.stdout, r.stderr)


def test_scan_keeps_non_ascii_paths():
    root = repo({"docs/résumé.md": "x", "docs/a b.md": "y"})
    code, out = scan(root)
    assert "docs/résumé.md" in out and "docs/a b.md" in out and "2 candidate files" in out, out


def test_scan_contract_categories():
    want = {"docs/x.md": "product-docs", "docs/adr/1.md": "implementation-docs", ".windsurfrules": "agent-docs",
            ".cursor/rules/a.mdc": "agent-docs", "Jenkinsfile": "ci", "fly.toml": "iac", "README.rst": "product-docs",
            "requirements-dev.txt": "manifests", "build.gradle.kts": "manifests", "docker-compose.prod.yml": "iac",
            ".gitlab-ci.yml": "ci"}
    root = repo(dict.fromkeys(want, "z"))
    code, out = scan(root)
    got = {l.split()[1]: l.split()[0] for l in out.strip().splitlines()[:-1]}
    assert got == want, got


def nio(root, *args):
    return subprocess.run(["uv", "run", "--project", str(Path(__file__).parent.parent), "nio", "onboard", *args],
                          cwd=root, capture_output=True, text=True)


def test_skip_needs_reason():
    root = repo({})
    r = nio(root, "skip", "  ")
    assert r.returncode == 1, (r.stdout, r.stderr)
    assert not (root / ".nio/project/onboarding.json").exists()


def test_project_templates_match_headings():
    from nio import onboard
    d = Path(__file__).parent.parent / "src/nio/templates/project"
    for doc in onboard.DOCS:
        f = d / f"{doc}.md"
        assert f.exists(), f
        text = f.read_text()
        assert onboard.check_doc(doc, text) == [], (doc, onboard.check_doc(doc, text))
        assert [l[3:] for l in text.splitlines() if l.startswith("## ")] == onboard.HEADINGS[doc], doc


def test_empty_start_writes_blank_docs():
    root = repo({})
    r = nio(root, "start", "--empty")
    assert r.returncode == 0 and "next: product" in r.stdout, (r.stdout, r.stderr)
    for d in ("stack", "architecture", "infra"):
        text = (root / f".nio/project/{d}.md").read_text()
        bodies = [b for b in text.split("\n## ")[1:]]
        assert bodies and all("NEEDS CLARIFICATION" in b for b in bodies), (d, text)
    assert nio(root, "pause").returncode == 0
    r = nio(root, "pause")
    assert r.returncode == 0 and "ignored: onboarding is paused" in r.stdout, (r.stdout, r.stderr)
    r = nio(root, "confirm", "stack")
    assert r.returncode == 0 and "ignored: onboarding is paused" in r.stdout, (r.stdout, r.stderr)


def test_empty_start_keeps_existing_docs():
    root = repo({})
    d = root / ".nio/project"
    d.mkdir(parents=True)
    (d / "stack.md").write_text("confirmed stack\n")
    (d / "product.md").write_text("mine\n")
    assert nio(root, "start", "--empty").returncode == 0
    assert (d / "stack.md").read_text() == "confirmed stack\n"
    assert (d / "product.md").read_text() == "mine\n"
    assert (d / "architecture.md").exists() and (d / "infra.md").exists()
    assert not (d / "personas.md").exists() and not (d / "principles.md").exists()


def test_state_table_cells():
    import json
    # (state to reach, action) -> (exit, stdout fragment); "x" is the skip reason
    def at(state):
        root = repo({})
        steps = {"not started": [], "in progress": [["start"]], "paused": [["start"], ["pause"]], "skipped": [["skip", "r"]],
                 "done": [["start", "--empty"]]}[state]
        for a in steps:
            assert nio(root, *a).returncode == 0, a
        if state == "done":
            d = root / ".nio/project"
            tpl = Path(__file__).parent.parent / "src/nio/templates/project"
            for n in ("product", "personas", "principles"):
                (d / f"{n}.md").write_text((tpl / f"{n}.md").read_text().replace("NEEDS CLARIFICATION", "filled"))
                nio(root, "confirm", n)
        return root
    cells = {
        ("not started", "pause"): (0, "ignored"), ("not started", "confirm"): (0, "ignored"), ("not started", "start"): (0, "next:"),
        ("not started", "skip"): (0, "skipped"),
        ("in progress", "start"): (0, "ignored"), ("in progress", "pause"): (0, "paused"), ("in progress", "skip"): (0, "skipped"),
        ("paused", "start"): (0, "next:"), ("paused", "pause"): (0, "ignored"), ("paused", "confirm"): (0, "ignored"),
        ("paused", "skip"): (0, "skipped"),
        ("skipped", "start"): (0, "next:"), ("skipped", "pause"): (0, "ignored"), ("skipped", "confirm"): (0, "ignored"),
        ("skipped", "skip"): (0, "ignored"),
        ("done", "start"): (1, "onboarding is done"), ("done", "skip"): (1, "onboarding is done already"),
        ("done", "pause"): (0, "ignored"), ("done", "confirm"): (0, "ignored"),
    }
    for (state, action), (code, frag) in cells.items():
        root = at(state)
        before = (root / ".nio/project/onboarding.json")
        before = before.read_text() if before.exists() else None
        args = {"skip": ["skip", "y"], "confirm": ["confirm", "product"]}.get(action, [action])
        r = nio(root, *args)
        assert r.returncode == code and frag in r.stdout + r.stderr, (state, action, r.returncode, r.stdout, r.stderr)
        if frag == "ignored" or code == 1:
            f = root / ".nio/project/onboarding.json"
            assert (f.read_text() if f.exists() else None) == before, (state, action)
    root = at("paused")
    nio(root, "pause")
    f = root / ".nio/project/onboarding.json"
    st = json.loads(f.read_text()); st["confirmed"] = ["product"]; f.write_text(json.dumps(st))
    assert nio(root, "start", "--empty").returncode == 0
    st = json.loads(f.read_text())
    assert st["state"] == "in progress" and st["confirmed"] == ["product"] and st["empty"] is False, st


def newspec(root, route):
    return subprocess.run(["uv", "run", "--project", str(Path(__file__).parent.parent), "nio", "new", "spec", "x", "--route", route],
                          cwd=root, capture_output=True, text=True)


def test_spec_waits_for_onboarding():
    root = repo({})
    for step in (None, ["start"], ["pause"]):
        if step:
            assert nio(root, *step).returncode == 0
        for route in ("full", "epic"):
            r = newspec(root, route)
            msg = r.stdout + r.stderr
            assert r.returncode == 1 and "@nio:onboard" in msg and "nio onboard skip" in msg, (step, route, msg)
            assert not list((root / ".nio/specs").glob("*")), (step, route)


def test_lite_spec_starts():
    root = repo({})
    r = newspec(root, "lite")
    assert r.returncode == 0, (r.stdout, r.stderr)
    assert list((root / ".nio/specs").glob("*/spec.md"))


def test_torn_progress_file():
    root = repo({})
    assert nio(root, "start").returncode == 0
    f = root / ".nio/project/onboarding.json"
    f.write_bytes(f.read_bytes()[:10])
    before = f.read_bytes()
    for r in (nio(root, "start"), newspec(root, "full")):
        assert r.returncode == 1 and ".nio/project/onboarding.json" in r.stdout + r.stderr, (r.stdout, r.stderr)
    assert f.read_bytes() == before


def status(root):
    return subprocess.run(["uv", "run", "--project", str(Path(__file__).parent.parent), "nio", "status"],
                          cwd=root, capture_output=True, text=True)


def test_torn_progress_file_status():
    root = repo({})
    assert nio(root, "start").returncode == 0
    f = root / ".nio/project/onboarding.json"
    for bad in (f.read_bytes()[:10], b"[]", b'{"state": "paused"}'):
        f.write_bytes(bad)
        for r in (status(root), nio(root, "start"), nio(root, "confirm", "product")):
            out = r.stdout + r.stderr
            assert "Traceback" not in out and ".nio/project/onboarding.json" in out, (bad, out)
    f.unlink()
    assert nio(root, "skip", "a\nonboarding: done").returncode == 0
    assert sum(l.startswith("onboarding:") for l in status(root).stdout.splitlines()) == 1
    assert not list(f.parent.glob("*.tmp"))


def test_skip_lets_spec_start():
    root = repo({})
    assert nio(root, "skip", "prototype").returncode == 0
    import json
    got = json.loads((root / ".nio/project/onboarding.json").read_text())
    assert got["state"] == "skipped" and got["reason"] == "prototype", got
    r = newspec(root, "full")
    assert r.returncode == 0, (r.stdout, r.stderr)
    assert list((root / ".nio/specs").glob("*/spec.md"))
    r = status(root)
    assert "onboarding: skipped: prototype" in r.stdout, (r.stdout, r.stderr)


def test_skip_stays_visible():
    root = repo({})
    assert nio(root, "skip", "prototype").returncode == 0
    assert newspec(root, "full").returncode == 0
    r = status(root)
    assert "onboarding: skipped: prototype" in r.stdout, (r.stdout, r.stderr)
    r = nio(root, "start")
    assert r.returncode == 0, (r.stdout, r.stderr)
    assert "onboarding: in progress" in status(root).stdout


def test_confirm_checks_docs_and_finishes():
    import json
    root = repo({"README.md": "hi\n"})
    d = root / ".nio/project"
    assert nio(root, "confirm", "product").returncode == 0  # not started: ignored
    assert not (d / "onboarding.json").exists()
    assert nio(root, "start", "--empty").returncode == 0
    r = nio(root, "confirm", "product")
    assert r.returncode == 1, (r.stdout, r.stderr)
    r = nio(root, "confirm", "stack")  # blank stub still holds NEEDS CLARIFICATION
    assert r.returncode == 1, (r.stdout, r.stderr)
    tpl = Path(__file__).parent.parent / "src/nio/templates/project"
    for n in ("product", "personas", "principles"):
        (d / f"{n}.md").write_text((tpl / f"{n}.md").read_text().replace("NEEDS CLARIFICATION", "filled"))
        r = nio(root, "confirm", n)
        assert r.returncode == 0, (n, r.stdout, r.stderr)
    assert "done" in r.stdout, r.stdout
    got = json.loads((d / "onboarding.json").read_text())
    assert got["state"] == "done" and got["seen"], got
    for a in ("start", "pause", "skip x"):
        nio(root, *a.split())
    assert json.loads((d / "onboarding.json").read_text())["state"] == "done"
    assert newspec(root, "full").returncode == 0


def test_onboard_from_subdirectory_uses_repo_root():
    root = repo({"src/a.py": "x"})
    r = nio(root / "src", "skip", "prototype")
    assert r.returncode == 0, (r.stdout, r.stderr)
    assert (root / ".nio/project/onboarding.json").exists()
    assert not (root / "src/.nio").exists()


def test_onboard_act_outside_git_repo():
    import tempfile
    r = nio(Path(tempfile.mkdtemp()), "skip", "x")
    assert r.returncode == 1 and "needs a git repository" in r.stderr, (r.stdout, r.stderr)


def test_next_doc_first_unconfirmed():
    from nio import onboard
    p = {"empty": True, "confirmed": ["product", "personas"]}
    assert onboard.next_doc(p) == "principles", onboard.next_doc(p)
    assert onboard.next_doc({"empty": False, "confirmed": ["product", "personas"]}) == "stack"
    assert onboard.next_doc({"empty": True, "confirmed": ["product", "personas", "principles"]}) is None


if __name__ == "__main__":
    selfcheck.main([test_scan_lists_each_category, test_scan_secrets_path_only, test_scan_prints_no_dependency, test_scan_skips_ignored_and_nio,
                    test_scan_empty_repo, test_scan_outside_git_repo, test_scan_keeps_non_ascii_paths, test_scan_contract_categories,
                    test_skip_needs_reason, test_project_templates_match_headings, test_empty_start_writes_blank_docs, test_empty_start_keeps_existing_docs, test_state_table_cells,
                    test_spec_waits_for_onboarding, test_lite_spec_starts, test_torn_progress_file, test_torn_progress_file_status,
                    test_skip_lets_spec_start, test_skip_stays_visible, test_confirm_checks_docs_and_finishes,
                    test_onboard_from_subdirectory_uses_repo_root, test_onboard_act_outside_git_repo, test_next_doc_first_unconfirmed])
