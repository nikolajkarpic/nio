import hashlib
from fnmatch import fnmatch
from pathlib import Path

from nio import records

# implementation-docs first: docs/adr/* must win over docs/*.md (fnmatch's * crosses "/")
CATEGORIES = {
    "implementation-docs": ["ARCHITECTURE*", "CONTRIBUTING*", "docs/adr/*"],
    "agent-docs": ["CLAUDE.md", "AGENTS.md", "GEMINI.md", ".cursor/rules/*.mdc", ".github/copilot-instructions.md",
                   ".github/instructions/*.instructions.md", ".windsurfrules", ".clinerules", ".kiro/steering/*"],
    "product-docs": ["README*", "docs/*.md"],
    "manifests": ["pyproject.toml", "package.json", "go.mod", "Cargo.toml", "requirements*.txt", "Gemfile", "pom.xml",
                  "build.gradle*"],
    "iac": ["*.tf", "Pulumi.yaml", "cdk.json", "serverless.yml", "cloudbuild.yaml", "Dockerfile", "docker-compose*.yml",
            "Chart.yaml", "fly.toml", "vercel.json", "app.yaml"],
    "ci": [".github/workflows/*", ".gitlab-ci.yml", "Jenkinsfile", ".circleci/config.yml"],
}


def category(path):
    if path.startswith(".nio/"):
        return None
    name = Path(path).name
    for cat, pats in CATEGORIES.items():
        if any(fnmatch(path, q) or fnmatch(name, q) for q in pats):
            return cat


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


DOCS = ["product", "personas", "stack", "architecture", "infra", "principles"]
SECTIONS = {"product": ["Purpose", "Users"], "personas": ["Personas"], "stack": ["Languages", "Frameworks"],
            "architecture": ["Components", "Data flow"], "infra": ["Hosting", "CI"], "principles": ["Principles"]}


def act(action, reason="", doc="", empty=False, root="."):
    """start/confirm/pause/skip; returns the line to print, raises ValueError on refusal."""
    import json
    d = Path(root) / ".nio/project"
    f = d / "onboarding.json"
    st = json.loads(f.read_text()) if f.exists() else {"state": "new", "confirmed": []}

    def save():
        d.mkdir(parents=True, exist_ok=True)
        f.write_text(json.dumps(st))
    if action == "skip":
        if not reason.strip():
            raise ValueError("skip needs a reason: nio onboard skip <reason>")
        st.update(state="skipped", reason=reason.strip())
        save()
        return "skipped"
    if action == "pause":
        if st["state"] == "paused":
            return "ignored: onboarding is paused"
        st["state"] = "paused"
        save()
        return "paused"
    if st["state"] == "paused":
        raise ValueError("onboarding is paused")
    if action == "start":
        st["state"] = "started"
        d.mkdir(parents=True, exist_ok=True)
        if empty:
            for n in DOCS:
                (d / f"{n}.md").write_text(f"# {n.title()}\n" + "".join(f"\n## {s}\n\nNEEDS CLARIFICATION\n" for s in SECTIONS[n]))
        save()
        return "next: " + DOCS[0]
    if doc not in DOCS:
        raise ValueError(f"confirm needs a doc: {', '.join(DOCS)}")
    st["confirmed"] = sorted(set(st["confirmed"]) | {doc})
    save()
    rest = [n for n in DOCS if n not in st["confirmed"]]
    return "next: " + rest[0] if rest else "done"
