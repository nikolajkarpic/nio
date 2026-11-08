import hashlib
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


def scan(root="."):
    """Print `category path sha12` per candidate file (tracked or untracked, not ignored); never file contents."""
    n = 0
    for f in sorted(set(records.git(root, "ls-files", "-z", "-co", "--exclude-standard", full=True)[1].split("\0")) - {""}):
        cat = category(f)
        if cat and (Path(root) / f).is_file():
            print(cat, f, hashlib.sha256((Path(root) / f).read_bytes()).hexdigest()[:12])
            n += 1
    print(f"{n} candidate files" if n else "no candidate files found")
