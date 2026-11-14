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
HEADINGS = {'product': ['What it does', 'Users', 'Main flows', 'Non-goals', 'Glossary'], 'personas': [], 'stack': ['Languages', 'Dependencies', 'Commands', 'CI'], 'architecture': ['Modules', 'Boundaries', 'Data flow'], 'infra': ['Cloud provider', 'Deployables', 'Eventing and queues', 'Storage', 'Secrets', 'Environments', 'Deploys'], 'principles': ['Principles']}


def check_doc(doc, text):
    """What a project doc lacks against its template (CT-12)."""
    import re
    if doc == "personas":
        parts = re.split(r"^### P-\d+.*$", text, flags=re.M)[1:]
        if not parts:
            return ["no persona entry"]
        return [f"persona entry lacks {k}:" for p in parts for k in ("Who", "Wants", "Allowed to", "How often") if k + ":" not in p]
    have = {l[3:].strip() for l in text.splitlines() if l.startswith("## ")}
    return [h for h in HEADINGS[doc] if h not in have]


def progress(root="."):
    import json
    f = Path(root) / ".nio/project/onboarding.json"
    if not f.exists():
        return {"state": "not started", "reason": "", "empty": False, "apps": {}, "confirmed": [], "seen": []}
    try:
        st = json.loads(f.read_text())
        if not (isinstance(st, dict) and isinstance(st["state"], str) and isinstance(st["reason"], str)
                and isinstance(st["empty"], bool) and isinstance(st["confirmed"], list) and isinstance(st["seen"], list)):
            raise ValueError
        return st
    except (ValueError, KeyError):
        raise ValueError(".nio/project/onboarding.json is not valid: fix or restore it") from None


def act(action, reason="", doc="", empty=False, root="."):
    """start/confirm/pause/skip; returns the line to print, raises ValueError on refusal."""
    import json
    d = Path(root) / ".nio/project"
    f = d / "onboarding.json"
    st = progress(root)

    def save():
        d.mkdir(parents=True, exist_ok=True)
        tmp = f.with_suffix(".tmp")
        tmp.write_text(json.dumps(st))
        tmp.replace(f)
    if action == "skip":
        if not reason.strip():
            raise ValueError("skip needs a reason: nio onboard skip <reason>")
        if st["state"] == "done":
            raise ValueError("onboarding is done already")
        if st["state"] == "skipped":
            return "ignored: onboarding is skipped"
        st.update(state="skipped", reason=" ".join(reason.split()))
        save()
        return "skipped"
    if action == "pause":
        if st["state"] != "in progress":
            return f"ignored: onboarding is {st['state']}"
        st["state"] = "paused"
        save()
        return "paused"
    if action == "start":
        if st["state"] == "done":
            raise ValueError("onboarding is done; it runs once: use @nio:reconcile-onboarding")
        if st["state"] == "in progress":
            return "ignored: onboarding is in progress"
        resume = st["state"] in ("paused", "skipped")  # resuming keeps saved progress and ignores new flags
        st["state"] = "in progress"
        if resume:
            empty = False
        st["empty"] = st["empty"] or empty
        d.mkdir(parents=True, exist_ok=True)
        if empty:
            for n in ("stack", "architecture", "infra"):
                if not (d / f"{n}.md").exists():
                    (d / f"{n}.md").write_text((Path(__file__).parent / f"templates/project/{n}.md").read_text())
        save()
        return "next: " + (next_doc(st) or DOCS[0])
    if st["state"] != "in progress":
        return f"ignored: onboarding is {st['state']}"
    if doc not in expected(st):
        raise ValueError(f"confirm needs a doc: {', '.join(expected(st))}")
    f_doc = d / f"{doc}.md"
    if not f_doc.is_file():
        raise ValueError(f"{f_doc.relative_to(root)} does not exist: write it first")
    text = f_doc.read_text()
    if lack := check_doc(doc, text):
        raise ValueError(f"{doc}.md lacks: {', '.join(lack)}")
    if "NEEDS CLARIFICATION" in text:
        raise ValueError(f"{doc}.md still has NEEDS CLARIFICATION: answer it first")
    st["confirmed"] = sorted(set(st["confirmed"]) | {doc})
    nxt = next_doc(st)
    if not nxt:
        st["state"] = "done"
        st["seen"] = [list(e) for e in scan(root)]
    save()
    return "next: " + nxt if nxt else "done"


def expected(st):
    """The docs this onboarding walks: --empty leaves the three blank stubs out."""
    return [n for n in DOCS if not (st["empty"] and n in ("stack", "architecture", "infra"))]


def next_doc(p):
    """The first expected doc not yet confirmed, or None."""
    return next((n for n in expected(p) if n not in p["confirmed"]), None)


def status_lines(root="."):
    st = progress(root)
    return ["onboarding: " + st["state"] + (": " + st["reason"] if st["state"] == "skipped" else "")]


READERS = {"spec": ["product", "personas"], "scope": ["product", "personas"], "plan": ["stack", "architecture", "infra", "principles"],
           "architecture-fit": ["stack", "architecture", "infra", "principles"], "worker": ["stack", "principles"]}
LIMIT = 16384


def _named(root, slug):
    """The apps the spec's front matter names, in `[a, b]` or block-list form."""
    import re
    spec = Path(root) / f".nio/specs/{slug}/spec.md"
    if not (slug and spec.is_file()):
        return []
    fm = re.match(r"---\n(.*?)\n---", spec.read_text(), re.S)
    m = fm and re.search(r"^apps:[ \t]*(.*(?:\n[ \t]+-.*)*)", fm.group(1), re.M)
    return [a for a in (x.strip(" -'\"") for x in re.split(r"[,\n]", m.group(1).strip("[] \n"))) if a] if m else []


def _pairs(root, reader, slug=""):
    """(label, path) per mapped doc; an app's doc is `api/stack.md`, kept in .nio/project/api/stack.md."""
    root, apps = Path(root), list(progress(root).get("apps") or {})
    named = _named(root, slug)
    apps = [a for a in apps if a in named] or apps
    return [(f"{a}/{d}.md" if a else f"{d}.md", root / ".nio/project" / a / f"{d}.md") for a in (apps or [""]) for d in READERS[reader]]


def doc_paths(root, reader, slug=""):
    """The files `docs_for` carries (CT-22)."""
    return [p for _, p in _pairs(root, reader, slug)]


def docs_for(root, reader, slug=""):
    """## Project docs for a reader: the mapped docs that exist, then size, missing and state lines (CT-9).
    ponytail: no stale line yet, it needs the docs' source records (CT-7)."""
    try:
        st = progress(root)
    except ValueError:  # docs only help a reader; a damaged file must not block the stage
        return "## Project docs\n\nonboarding: unreadable: fix .nio/project/onboarding.json\n"
    pairs = _pairs(root, reader, slug)
    r = Path(root).resolve()
    bad = {n for n, p in pairs if p.is_symlink() or not p.resolve().is_relative_to(r)}  # never follow a link (CT-1)
    have = [(n, p) for n, p in pairs if p.is_file() and n not in bad]
    if st["state"] == "not started" and not have:
        return ""
    out = ["## Project docs", ""]
    out += [f"not onboarded: {a}" for a in _named(root, slug) if a not in (st.get("apps") or {})]
    for n, p in have:
        out += [f"### {n}", ""] + ["##" + l if l.startswith("#") else l for l in p.read_text().splitlines()] + [""]
    out += [f"over 16 KB: {n} ({-(-p.stat().st_size // 1024)} KB)" for n, p in have if p.stat().st_size > LIMIT]
    out += [f"missing: {n} (symlink or outside the repo, not read)" for n in sorted(bad)]
    if st["state"] == "done":
        out += [f"missing: {n}" for n, p in pairs if not p.is_file() and n not in bad]
    else:
        out.append("onboarding: " + st["state"] + (": " + st["reason"] if st["state"] == "skipped" else ""))
    return "\n".join(out) + "\n"


def backup(file, root="."):
    """Copy file to .nio/backup/<today>/<repo path>; a second copy the same day keeps the first (CT-17)."""
    import datetime
    import shutil
    r = Path(root).resolve()
    src = Path(file).resolve()
    if not file or not src.is_file() or not src.is_relative_to(r):
        raise ValueError(f"{file or '(no file)'}: not a file inside the repo")
    dst = r / ".nio" / "backup" / datetime.date.today().isoformat() / src.relative_to(r)
    if not dst.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    return str(dst.relative_to(r))
