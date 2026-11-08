import hashlib
from fnmatch import fnmatch
from pathlib import Path

from nio import records

CATS = [
    ("agent-docs", {"claude.md", "agents.md", "gemini.md", ".cursorrules"}),
    ("product-docs", {"readme.md", "readme", "changelog.md"}),
    ("implementation-docs", {"architecture.md", "design.md", "contributing.md"}),
    ("manifests", {"pyproject.toml", "package.json", "cargo.toml", "go.mod", "pom.xml", "gemfile", "requirements.txt"}),
    ("iac", {"dockerfile", "docker-compose.yml", "docker-compose.yaml"}),
]


def category(path):
    p = Path(path)
    if p.parts[0] == ".nio":
        return None
    if p.parts[:2] == (".github", "workflows"):
        return "ci"
    if p.suffix == ".tf":
        return "iac"
    for cat, names in CATS:
        if p.name.lower() in names:
            return cat
    if p.parts[0] == "docs" and p.suffix == ".md":
        return "implementation-docs"


SECRETS = [".env", ".env.*", "*.pem", "*.key", "id_rsa", "id_ed25519", "*.p12", "*.pfx", "credentials*", ".npmrc", ".pypirc", "*.tfvars", "secrets.*"]


def scan(root="."):
    """Return sorted (category, path, sha12) per candidate; secrets by path only (hash ""). Never file contents."""
    def ls(*a):
        return set(records.git(root, "ls-files", "-z", *a, "--exclude-standard", full=True)[1].split("\0")) - {""}
    out = []
    for f in sorted(ls("-co") | ls("-o", "-i")):
        p = Path(root) / f
        if f.startswith(".nio/") or p.is_symlink() or not p.is_file():
            continue
        if any(fnmatch(p.name, s) for s in SECRETS):
            out.append(("secrets", f, ""))
        elif (cat := category(f)) and f in ls("-co"):
            out.append((cat, f, hashlib.sha256(p.read_bytes()).hexdigest()[:12]))
    return sorted(out, key=lambda e: e[:2])
