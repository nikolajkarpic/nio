"""Memory records: parse, lint and create files under .nio/memory/<area>/."""
import datetime
import difflib
import fnmatch
import json
import os
import re
import secrets
import subprocess
from importlib import resources
from pathlib import Path

from ruamel.yaml import YAML
from ruamel.yaml.error import YAMLError

BASE32 = "abcdefghijklmnopqrstuvwxyz234567"
LETTER = {"decision": "D", "verdict": "V", "lesson": "L", "change": "C", "run": "R"}
ID_RE = re.compile(r"^[DVLC]-\d{6}-[a-z2-7]{4}$")
MAX_BODY_LINES = 40

# decisions and lessons carry `status`; verdicts and changes carry `outcome` instead
COMMON = ["id", "type", "title", "answers", "date", "by"]
REQUIRED = {
    "decision": COMMON + ["status"],
    "verdict": COMMON + ["subject", "outcome", "tier"],
    "lesson": COMMON + ["status", "paths", "tags"],
    "change": COMMON + ["against", "outcome"],
}
# `outdated_by` is added to a committed record later, pointing at what replaced or challenged it
OPTIONAL = {"run", "serves", "task", "paths", "tags", "supersedes", "subject", "outcome", "tier", "against", "outdated_by"}
ENUMS = {
    # how the record entered memory; jury standing is derived from verdicts whose `subject` points here
    "status": {"proposed", "human", "recorded"},
    "answers": {"why", "reuse", "jury"},
    "tier": {"low", "medium", "high"},
}
OUTCOMES = {"verdict": {"approved", "rejected", "human"}, "change": {"pending", "accepted", "rejected"}}
SECTIONS = {
    "decision": ["Decision", "Why", "Rejected alternatives", "Reuse"],
    "verdict": ["Ruling", "Jurors", "Reasons", "What was rejected"],
    "lesson": ["Problem", "Solution", "Where it applies"],
    "change": ["What is wrong", "Proposed change", "Human decision"],
}


def git(root, *args, full=False):
    """git's stdout lines; with `full`, (exit code, stdout, stderr), for a caller that must see git fail (CT-19)."""
    r = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True)
    return (r.returncode, r.stdout, r.stderr) if full else r.stdout.splitlines()


def repo_root():
    return Path(git(".", "rev-parse", "--show-toplevel")[0])


def home():
    """~/.nio, or $NIO_HOME: global config and personal agent cards."""
    return Path(os.environ.get("NIO_HOME") or Path.home() / ".nio")


def merge(base, over):
    out = dict(base)
    for k, v in over.items():
        out[k] = merge(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) else v
    return out


def config(root):
    """Global, then team, then local config; later layers win, key by key."""
    out = {}
    for path in (home() / "config.json", root / ".nio/config.json", root / ".nio/config.local.json"):
        if path.exists():
            out = merge(out, json.loads(path.read_text()))
    return out


def areas(root):
    return config(root).get("memory", {}).get("areas", ["project"])  # verdicts file under project, so a bare config still works


def parse(path, text=None):
    """Return (frontmatter dict, body lines). Raises ValueError on a bad header."""
    text = Path(path).read_text() if text is None else text
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        raise ValueError("missing --- frontmatter block")
    head, body = text[4:].split("\n---\n", 1)
    try:
        meta = YAML(typ="safe", pure=True).load(head)  # YAML 1.2: `no` stays a string
    except YAMLError as e:
        raise ValueError(f"frontmatter is not valid YAML: {str(e).splitlines()[0]}") from None
    if not isinstance(meta, dict):
        raise ValueError("frontmatter is not a mapping")
    return meta, body.splitlines()


def sections(body):
    out, name = {}, None
    for line in body:
        if line.startswith("## "):
            name = line[3:].strip()
            out[name] = []
        elif name:
            out[name].append(line)
    return {k: "\n".join(v).strip() for k, v in out.items()}


def check_record(path, meta, body, area_list, known_ids):
    """Lint one record. Returns a list of error strings; paths are checked separately."""
    errs = []
    rtype = meta.get("type")
    if rtype not in REQUIRED:
        return [f"type must be one of {sorted(REQUIRED)}"]
    for key, val in meta.items():
        if key not in REQUIRED[rtype] and key not in OPTIONAL:
            errs.append(f"unknown field `{key}`")
        if isinstance(val, list):
            if not all(isinstance(v, str) for v in val):
                errs.append(f"`{key}` must be a list of plain strings")
        elif not isinstance(val, (str, datetime.date)):
            errs.append(f"`{key}` must be a quoted string or a list, got {type(val).__name__}")
    for key in REQUIRED[rtype]:
        if meta.get(key) in (None, "", []):
            errs.append(f"missing required field `{key}`")
    for key, allowed in ENUMS.items():
        if key in meta and meta[key] not in allowed:
            errs.append(f"`{key}` must be one of {sorted(allowed)}")
    if rtype in OUTCOMES and meta.get("outcome") not in OUTCOMES[rtype]:
        errs.append(f"`outcome` must be one of {sorted(OUTCOMES[rtype])}")
    rid = str(meta.get("id", ""))
    if not ID_RE.match(rid) or rid[0] != LETTER[rtype]:
        errs.append(f"id `{rid}` must look like {LETTER[rtype]}-yymmdd-xxxx")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(meta.get("date", ""))):
        errs.append("`date` must be YYYY-MM-DD")
    if not path.name.startswith(rid + "-"):
        errs.append("filename must start with the id")
    if path.parent.name not in area_list:
        errs.append(f"folder `{path.parent.name}` is not a listed area {area_list}")
    links = list(meta.get("supersedes") or []) + list(meta.get("outdated_by") or [])
    if ID_RE.match(str(meta.get("subject", ""))):
        links.append(meta["subject"])
    errs += [f"links to unknown record `{x}`" for x in links if x not in known_ids]
    if len(body) > MAX_BODY_LINES:
        errs.append(f"body is {len(body)} lines, max {MAX_BODY_LINES}")
    if any("TODO" in line for line in body):
        errs.append("body still has TODO placeholders")
    secs = sections(body)
    for name in SECTIONS[rtype]:
        if not secs.get(name):
            errs.append(f"section `## {name}` is missing or empty")
    if rtype == "decision" and secs.get("Why") and secs.get("Decision"):
        why, dec = secs["Why"].lower(), secs["Decision"].lower()
        if why in dec or difflib.SequenceMatcher(None, why, dec).ratio() > 0.8:
            errs.append("Why only repeats the Decision")
    return errs


def added_in(root):
    """Map record ID -> the commit that first added it. Keyed by ID so `git mv` between areas keeps it."""
    commit, out = None, {}
    for line in git(root, "log", "--diff-filter=A", "--format=%H", "--name-only", "--", ".nio/memory"):
        if len(line) == 40 and "/" not in line:
            commit = line
        elif line:
            out[Path(line).name[:13]] = commit  # log is newest first, so the oldest add wins
    return out


def renamed_since(root, commit):
    """Map each file tracked at `commit` to its name at HEAD, following every rename since."""
    origin = {f: f for f in git(root, "ls-tree", "-r", "--name-only", commit)}  # current name -> name at commit
    for line in git(root, "log", "--reverse", "-M", "--diff-filter=R", "--name-status", "--format=", f"{commit}..HEAD"):
        _, old, new = line.split("\t")
        if old in origin:
            origin[new] = origin.pop(old)
    return {then: now for now, then in origin.items()}


def touches(globs, files, renamed=None):
    """Files the globs match now, plus files they matched when the record was committed, followed through renames."""
    hit = {f for g in globs for f in fnmatch.filter(files, g)}
    if renamed:
        live = set(files)
        hit |= {now for then, now in renamed.items() if now in live and any(fnmatch.fnmatch(then, g) for g in globs)}
    return sorted(hit)


def edits(root, base):
    """Errors for committed records changed since `base` other than repointing `paths` or growing `outdated_by`."""
    errs = []
    for line in git(root, "diff", "--name-status", "-M", base, "--", ".nio/memory"):
        status, *names = line.split("\t")
        if status[0] not in "MR":
            continue
        try:
            before = parse(names[0], "\n".join(git(root, "show", f"{base}:{names[0]}")) + "\n")
            after = parse(root / names[-1])
        except Exception:
            continue  # a parse error is reported by the lint
        frozen = lambda meta: {k: v for k, v in meta.items() if k not in ("paths", "outdated_by")}
        if frozen(before[0]) != frozen(after[0]) or before[1] != after[1]:
            errs.append(f"{names[-1]}: a committed record may only change `paths` and `outdated_by`; write a new record that supersedes it")
        elif not set(before[0].get("outdated_by") or []) <= set(after[0].get("outdated_by") or []):
            errs.append(f"{names[-1]}: `outdated_by` may only grow")
    return errs


def check(root, base="HEAD"):
    """Lint every record, and every edit since `base`. Returns (errors, warnings, record count) as lists of 'path: message'."""
    mem = root / ".nio/memory"
    files = sorted(mem.rglob("*.md"))
    area_list = areas(root)
    # untracked but not ignored files count, so a record can describe code written in the same change
    tracked = git(root, "ls-files", "--cached", "--others", "--exclude-standard")
    committed = set(git(root, "ls-tree", "-r", "--name-only", "HEAD", ".nio/memory"))
    commits, renames = added_in(root), {}
    errors, warnings, parsed = edits(root, base), [], {}
    for f in files:
        rel = f.relative_to(root)
        try:
            parsed[f] = parse(f)
        except Exception as e:
            errors.append(f"{rel}: {e}")
    ids = {}
    for f, (meta, _) in parsed.items():
        ids.setdefault(str(meta.get("id")), []).append(f)
    errors += [f"{p[1].relative_to(root)}: duplicate id `{i}`" for i, p in ids.items() if len(p) > 1]
    rejected = {str(m.get("subject")) for m, _ in parsed.values() if m.get("type") == "verdict" and m.get("outcome") == "rejected"}
    superseded_by = {}
    for f, (meta, body) in parsed.items():
        rel = f.relative_to(root)
        errors += [f"{rel}: {e}" for e in check_record(f, meta, body, area_list, ids)]
        commit = commits.get(str(meta.get("id")))
        if commit not in renames:
            renames[commit] = renamed_since(root, commit) if commit else None
        for glob in meta.get("paths") or []:
            if not touches([glob], tracked, renames[commit]):
                # a stale path in an old record only warns: the code moved or went away after it was written
                (warnings if str(rel) in committed else errors).append(f"{rel}: path `{glob}` matches no tracked file, even after following renames")
        subject = ids.get(str(meta.get("subject")))
        if meta.get("type") == "verdict" and subject and subject[0].parent != f.parent:
            errors.append(f"{rel}: verdict must sit in its subject's area `{subject[0].parent.name}`")
        if meta.get("id") not in rejected:
            for old in meta.get("supersedes") or []:
                superseded_by.setdefault(old, []).append(meta.get("id"))
    for old, new in superseded_by.items():
        if len(new) > 1:
            errors.append(f".nio/memory: `{old}` is superseded by several records {new}; a human must pick one")
    errors += outdated_links(root, {i: (f[0], parsed[f[0]][0]) for i, f in ids.items() if f[0] in parsed})
    return errors, warnings, len(files)


def outdated_links(root, by_id):
    """`outdated_by` on the old record and `supersedes` / `against` on the new one must agree both ways."""
    errs = []
    for rid, (f, meta) in by_id.items():
        rel = f.relative_to(root)
        for new in meta.get("outdated_by") or []:
            n = by_id.get(new, (None, {}))[1]
            if rid not in (n.get("supersedes") or []) and n.get("against") != rid:
                errs.append(f"{rel}: `outdated_by` names `{new}`, which neither supersedes this record nor is a change request against it")
        olds = list(meta.get("supersedes") or [])
        if meta.get("type") == "change":
            olds.append(meta.get("against"))
        for old in olds:
            if old in by_id and rid not in (by_id[old][1].get("outdated_by") or []):
                errs.append(f"{by_id[old][0].relative_to(root)}: add `outdated_by: [\"{rid}\"]`, since `{rid}` supersedes or challenges it")
    return errs


def new_id(rtype, known):
    while True:
        rid = f"{LETTER[rtype]}-{datetime.date.today():%y%m%d}-{''.join(secrets.choice(BASE32) for _ in range(4))}"
        if rid not in known:
            return rid


def slug(title):
    # dashes, slashes and underscores separate words ("refund-double-charge"); other punctuation just goes ("don't")
    return "-".join(re.sub(r"[^a-z0-9 ]", "", re.sub(r"[-/_]", " ", title.lower())).split()[:6])


def new(root, rtype, area, title, by="human", run=""):
    """Create a record from its template and return the path."""
    if area not in areas(root):
        raise ValueError(f"`{area}` is not a listed area; ask the human to add it to memory.areas in .nio/config.json")
    known = {p.name[:13] for p in (root / ".nio/memory").rglob("*.md")}
    rid = new_id(rtype, known)
    text = resources.files("nio").joinpath(f"templates/{rtype}.md").read_text()
    text = text.format(id=rid, title=title.replace('"', '\\"'), date=datetime.date.today(), by=by, run=run)
    path = root / ".nio/memory" / area / f"{rid}-{slug(title)}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return path


def new_run(root, link=None):
    """Create .nio/runs/<run>/promote.md and return the run ID. Given `link` (the effort and the stage or task the run
    serves), also write it as flow.json, unchecked: the caller checks it (2026-10-28-flow-state CT-17)."""
    known = {p.name for p in (root / ".nio/runs").glob("R-*")}
    rid = new_id("run", known)
    run = root / ".nio/runs" / rid
    run.mkdir(parents=True)
    (run / "promote.md").write_text(f"# Memory candidates for {rid}\n")
    if link is not None:
        (run / "flow.json").write_text(json.dumps(link, indent=2) + "\n")
    return rid
