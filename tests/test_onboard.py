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
    assert r.returncode == 1, (r.stdout, r.stderr)


if __name__ == "__main__":
    selfcheck.main([test_scan_lists_each_category, test_scan_secrets_path_only, test_scan_prints_no_dependency, test_scan_skips_ignored_and_nio,
                    test_scan_empty_repo, test_scan_outside_git_repo, test_scan_keeps_non_ascii_paths, test_scan_contract_categories,
                    test_skip_needs_reason, test_empty_start_writes_blank_docs])
