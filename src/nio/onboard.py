import hashlib
import re
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


SECRETS = [".env*", "*.tfvars", "*.tfvars.json", "*.tfstate", "*.tfstate.*", "*.pem", "*.key", "*.p12", "*.pfx", ".npmrc", ".pypirc", ".netrc", "credentials*", "secrets.*", "id_rsa*", "id_ed25519*", "id_ecdsa*", "id_dsa*", "*.keystore", "*.jks", ".htpasswd", "service-account*.json"]  # FR-24, matched case-insensitively


def is_secret(name):
    return any(fnmatch(name.lower(), s) for s in SECRETS)


def scan(root="."):
    """Return sorted (category, path, sha12) per candidate; secrets by path only (hash ""). Never file contents."""
    def ls(*a):
        return set(records.git(root, "ls-files", "-z", *a, "--exclude-standard", full=True)[1].split("\0")) - {""}
    out = []
    for f in sorted(ls("-co") | ls("-o", "-i")):
        p = Path(root) / f
        if f.startswith(".nio/") or p.is_symlink() or not p.is_file():
            continue
        if is_secret(p.name):
            out.append(("secrets", f, ""))
            if category(f) == "iac":  # secrets.tf also defines where secrets live: a path-only pointer
                out.append(("iac", f, ""))
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


SOURCE = re.compile(r"\(source: ([^@()\s]+)@([0-9a-f]{12})\)")


SECRET = re.compile(r"ghp_|github_pat_|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY|xox[bp]-|\bsk-[A-Za-z0-9_-]{8,}")
DEV_SOURCE = re.compile(r"\(source: dev, [^()]+\)")


def secret_values(root="."):
    """Values (8+ chars) of `KEY=value` lines in the files the scan lists as secrets; read only to refuse them (J-3)."""
    vals = set()
    for cat, f, _ in scan(root):
        p = Path(root) / f
        if cat != "secrets" or p.is_symlink() or not p.is_file():
            continue
        for l in p.read_text(errors="ignore").splitlines():
            k, sep, v = l.partition("=")
            v = v.strip().strip("'\"")
            if sep and len(v) >= 8:
                vals.add(v)
    return vals


def check_facts(text):
    """The first secret-looking line, or fact line without a source record (CT-4); never prints a value."""
    note, miss = "", ""
    for n, l in enumerate(text.splitlines(), 1):
        if SECRET.search(l):
            return f"line {n} holds a secret-looking value: remove it"
        s = l.strip()
        if s.startswith("<!--"):
            note = "" if "-->" in s else "1"
            continue
        if note:
            note = "" if "-->" in s else note
            continue
        if s and not s.startswith("#") and not s.endswith("NEEDS CLARIFICATION") and not miss \
                and not (SOURCE.search(s) or DEV_SOURCE.search(s)):
            miss = f"line {n} has no (source: ...) record: add one or mark it NEEDS CLARIFICATION"
    return miss


def stale(root="."):
    """(doc, source path, "changed" | "deleted") per recorded source whose file differs or is gone (CT-7)."""
    root, seen, out = Path(root), {}, []
    for f in sorted((root / ".nio/project").rglob("*.md")):
        for src, h in SOURCE.findall(f.read_text()):
            if src not in seen:
                p = root / src
                seen[src] = hashlib.sha256(p.read_bytes()).hexdigest()[:12] if p.is_file() else None
            if seen[src] != h:
                out.append((str(f.relative_to(root / ".nio/project")), src, "deleted" if seen[src] is None else "changed"))
    return out


def _feeds(root):
    """{source path: [docs recording it]} over the project docs."""
    out = {}
    for f in sorted((Path(root) / ".nio/project").rglob("*.md")):
        for src, _ in SOURCE.findall(f.read_text()):
            out.setdefault(src, [])
            d = str(f.relative_to(Path(root) / ".nio/project"))
            if d not in out[src]:
                out[src].append(d)
    return out


def changed(root, ref):
    """(path, docs it feeds) per file `git diff --name-only <ref>` lists that a project doc records (CT-11)."""
    if not ref or ref.startswith("-"):
        raise ValueError(f"not a git ref: {ref}")  # never let a ref become a git option
    code, out, err = records.git(root, "diff", "--name-only", "-z", "--no-renames", "--end-of-options", ref, full=True)  # -z: paths unquoted, like scan
    if code:
        raise ValueError(f"git diff {ref} failed: {err.strip()}")
    feeds = _feeds(root)
    return [(f, feeds[f]) for f in sorted(set(out.split("\0")) - {""}) if f in feeds]


def to_reconcile(root="."):
    """Stale sources, then scan paths (never secrets) in neither `seen` nor a source record, as `<path> new`."""
    out = sorted({f"{s} {w}" for _, s, w in stale(root)})
    seen = {e if isinstance(e, str) else e[1] for e in progress(root)["seen"]}
    known = seen | set(_feeds(root))
    return out + sorted({f"{f} new" for c, f, _ in scan(root) if c != "secrets" and not is_secret(Path(f).name) and f not in known})


def reconciled(root=".", paths=()):
    """Save `seen` from the current scan, outside the secrets category (CT-11). Given paths, only those new files are
    added to `seen`, so a file the dev didn't reach stays listed (FR-21)."""
    import json
    f = Path(root) / ".nio/project/onboarding.json"
    st = progress(root)
    now = [list(e) for e in scan(root) if e[0] != "secrets"]
    if paths:
        keep = {e if isinstance(e, str) else e[1] for e in st["seen"]} | set(paths)
        now = [e for e in now if e[1] in keep]
    st["seen"] = now
    f.parent.mkdir(parents=True, exist_ok=True)
    tmp = f.with_suffix(".tmp")
    tmp.write_text(json.dumps(st))
    tmp.replace(f)


def close_lines(root, ref):
    return [f"project docs: {p} changed, feeds {', '.join(d)}: propose edits with @nio:reconcile-onboarding" for p, d in changed(root, ref)]


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


def act(action, reason="", doc="", empty=False, root=".", apps=None, app=""):
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
        if apps and not resume:
            for slug in apps:
                if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", slug) or slug in DOCS:
                    raise ValueError(f"app {slug}: a slug is lowercase words joined by -, and not a doc name")
            st["apps"] = {k: list(v) for k, v in apps.items()}
        d.mkdir(parents=True, exist_ok=True)
        if empty:
            for a, n in ((a, n) for a in (st["apps"] or [""]) for n in ("stack", "architecture", "infra")):
                (d / a).mkdir(parents=True, exist_ok=True)
                if not (d / a / f"{n}.md").exists():
                    (d / a / f"{n}.md").write_text((Path(__file__).parent / f"templates/project/{n}.md").read_text())
        save()
        return "next: " + (next_doc(st) or DOCS[0])
    if st["state"] != "in progress":
        return f"ignored: onboarding is {st['state']}"
    if st["apps"] and app not in st["apps"]:
        raise ValueError(f"confirm needs --app, one of: {', '.join(st['apps'])}")
    if app and not st["apps"]:
        raise ValueError("this project has no apps: leave out --app")
    full = f"{app}/{doc}" if app else doc
    if full not in expected(st):
        raise ValueError(f"confirm needs a doc: {', '.join(expected(st))}")
    f_doc = d / f"{full}.md"
    if not f_doc.is_file():
        raise ValueError(f"{f_doc.relative_to(root)} does not exist: write it first")
    text = f_doc.read_text()
    if lack := check_doc(doc, text):
        raise ValueError(f"{full}.md lacks: {', '.join(lack)}")
    if bad := check_facts(text):
        raise ValueError(f"{full}.md: {bad}")
    vals = secret_values(root)
    if n := next((n for n, l in enumerate(text.splitlines(), 1) if any(v in l for v in vals)), 0):
        raise ValueError(f"{full}.md: line {n} holds a secret value from a secrets file: remove it")
    if "NEEDS CLARIFICATION" in text:
        raise ValueError(f"{full}.md still has NEEDS CLARIFICATION: answer it first")
    st["confirmed"] = sorted(set(st["confirmed"]) | {full})
    nxt = next_doc(st)
    if not nxt:
        st["state"] = "done"
        st["seen"] = [list(e) for e in scan(root)]
    save()
    return "next: " + nxt if nxt else "done"


def expected(st):
    """The docs this onboarding walks: --empty leaves the three blank stubs out."""
    docs = [n for n in DOCS if not (st["empty"] and n in ("stack", "architecture", "infra"))]
    return [f"{a}/{n}" for a in st.get("apps") or {} for n in docs] or docs


def next_doc(p):
    """The first expected doc not yet confirmed, or None."""
    return next((n for n in expected(p) if n not in p["confirmed"]), None)


def status_lines(root="."):
    st = progress(root)
    return ["onboarding: " + st["state"] + (": " + st["reason"] if st["state"] == "skipped" else "")] + \
        [f"stale: {d} ({s} {w})" for d, s, w in stale(root)]


READERS = {"spec": ["product", "personas"], "scope": ["product", "personas"], "plan": ["stack", "architecture", "infra", "principles"],
           "architecture-fit": ["stack", "architecture", "infra", "principles"], "worker": ["stack", "principles"]}
LIMIT = 16384


def _named(root, slug):
    """The apps the spec's front matter names (records.parse, so comments and both list forms work)."""
    from . import records
    spec = Path(root) / f".nio/specs/{slug}/spec.md"
    try:
        named = records.parse(spec)[0].get("apps") if slug and spec.is_file() else None
    except ValueError:
        return []
    return [str(a) for a in named] if isinstance(named, list) else []


def _pairs(root, reader, slug=""):
    """(label, path) per mapped doc; an app's doc is `api/stack.md`, kept in .nio/project/api/stack.md."""
    root, apps = Path(root), list(progress(root).get("apps") or {})
    named = _named(root, slug)
    apps = [a for a in apps if a in named] if named else apps
    if not apps:
        return [] if named else [(f"{d}.md", root / ".nio/project" / f"{d}.md") for d in READERS[reader]]
    return [(f"{a}/{d}.md" if a else f"{d}.md", root / ".nio/project" / a / f"{d}.md") for a in apps for d in READERS[reader]]


def doc_paths(root, reader, slug=""):
    """The files `docs_for` carries (CT-22)."""
    return [p for _, p in _pairs(root, reader, slug)]


def docs_for(root, reader, slug=""):
    """## Project docs for a reader: the mapped docs that exist, then size, missing and state lines (CT-9)."""
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
    mine = {n for n, _ in have}
    out += [f"stale: {d} ({s} {w})" for d, s, w in stale(root) if d in mine]
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
    import os
    import shutil
    r = Path(root).resolve()
    src = Path(os.path.abspath(file)) if file else Path()  # the path as given: a symlink keeps its own name
    if not file or not src.resolve().is_file() or not src.is_relative_to(r) or not src.resolve().is_relative_to(r) or is_secret(src.name):
        raise ValueError(f"{file or '(no file)'}: not a file inside the repo, or a secret")
    dst = r / ".nio" / "backup" / datetime.date.today().isoformat() / src.relative_to(r)
    if not dst.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        tmp = dst.with_name(dst.name + ".tmp")
        try:
            shutil.copy2(src, tmp)
            os.replace(tmp, dst)
        finally:
            tmp.unlink(missing_ok=True)
    return str(dst.relative_to(r))
