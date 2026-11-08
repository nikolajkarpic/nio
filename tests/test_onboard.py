"""Self-check for nio onboard scan (2026-11-08-project-onboarding, T-1).
Run: uv run python tests/test_onboard.py"""
import hashlib
import subprocess
import tempfile
from pathlib import Path

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
    for p, cat in want.items():
        h = hashlib.sha256((root / p).read_bytes()).hexdigest()[:12]
        assert got[p] == [cat, p, h], (p, got[p])


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


if __name__ == "__main__":
    selfcheck.main([test_scan_lists_each_category, test_scan_prints_no_dependency, test_scan_skips_ignored_and_nio,
                    test_scan_empty_repo])
