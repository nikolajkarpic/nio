"""Extensions: a folder with a manifest that adds steps, cards and hooks. Add copies it and runs none of its commands."""
import hashlib
import json
import os
import re
import shutil
import tempfile
from importlib import resources
from pathlib import Path

from nio import flow, records

EVENTS = ["step-passed", "step-skipped", "gate-approved", "gate-rejected", "epic-closed", "waiting-on-human", "effort-done"]
CHANGE = ("remove", "skip", "replace", "reorder", "before")  # FR-20: extensions only add
NAME = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_-]*")
TOP = {"name", "version", "steps", "cards", "hooks"}
STEP = {"name", "after", "skill", "check", "card", "output", "trigger", "timeout", "gate"}
HOOK = {"event", "command", "timeout"}
TRIGGERS = {"spec_level": ("unit", "integration", "e2e"), "plan_path": None}


def shipped_cards():
    return {p.name[:-3] for p in Path(str(resources.files("nio").joinpath("agents"))).glob("*.md") if not p.name.endswith(".append.md")}


def _named(v):  # a string or a list of them, as the names a FR-20 key points at
    return [str(x) for x in v] if isinstance(v, list) else [str(v)]


def check(folder, manifest, others, stages):
    """The refusal reasons for adding `manifest` (None: read it from `folder`), in CT-2's order; empty when it may be added."""
    folder = Path(folder)
    if manifest is None:
        try:
            manifest = json.loads((folder / "manifest.json").read_text())
        except FileNotFoundError:
            return ["manifest.json is missing"]
        except ValueError as e:
            return [f"manifest.json is not JSON: {e}"]
    if not isinstance(manifest, dict):
        return ["manifest.json: must be an object"]
    errs, m = [], "manifest.json: "
    steps = manifest.get("steps") if isinstance(manifest.get("steps"), list) else []
    cards = manifest.get("cards") if isinstance(manifest.get("cards"), list) else []
    hooks = manifest.get("hooks") if isinstance(manifest.get("hooks"), list) else []

    def secs(path, v):
        if v is not None and (not isinstance(v, int) or isinstance(v, bool) or v < 1):
            errs.append(f"{m}{path}.timeout must be a whole number of seconds of at least 1")

    def text(path, v):
        if not isinstance(v, str) or not v:
            errs.append(f"{m}{path} must be a non-empty string")
            return False
        return True

    for k in ("name", "version", "steps", "cards", "hooks"):
        if k not in manifest:
            errs.append(f"{m}missing field {k}")
    errs += [f"{m}unknown field {k}" for k in manifest if k not in TOP and k not in CHANGE]
    if "name" in manifest and not (isinstance(manifest["name"], str) and NAME.fullmatch(manifest["name"])):
        errs.append(f"{m}name must be a word of letters, digits, - and _")
    if "version" in manifest:
        text("version", manifest["version"])
    for k in ("steps", "cards", "hooks"):
        if k in manifest and not isinstance(manifest[k], list):
            errs.append(f"{m}{k} must be a list")
    for i, c in enumerate(cards):
        if text(f"cards[{i}]", c) and not (folder / "agents" / f"{c}.md").is_file():
            errs.append(f"{m}cards[{i}] names agents/{c}.md, which isn't in the extension")
    for i, s in enumerate(steps):
        p = f"steps[{i}]"
        if not isinstance(s, dict):
            errs.append(f"{m}{p} must be an object")
            continue
        for k in ("name", "after", "skill", "check"):
            if k not in s:
                errs.append(f"{m}missing field {p}.{k}")
            elif not isinstance(s[k], str) or not s[k]:
                errs.append(f"{m}{p}.{k} must be a non-empty string")
        if "gate" in s and "output" not in s:
            errs.append(f"{m}missing field {p}.output")
        errs += [f"{m}unknown field {p}.{k}" for k in s if k not in STEP and k not in CHANGE]
        for k in ("card", "output"):
            if k in s:
                text(f"{p}.{k}", s[k])
        if isinstance(s.get("skill"), str) and s["skill"] and not (folder / s["skill"]).is_file():
            errs.append(f"{m}{p}.skill names {s['skill']}, which isn't in the extension")
        t = s.get("trigger")
        if "trigger" in s and not (isinstance(t, dict) and len(t) == 1 and next(iter(t)) in TRIGGERS and isinstance(next(iter(t.values())), str)
                                   and (TRIGGERS[next(iter(t))] is None or next(iter(t.values())) in TRIGGERS[next(iter(t))])):
            errs.append(f"{m}{p}.trigger must be {{\"spec_level\": unit|integration|e2e}} or {{\"plan_path\": <path>}}")
        if "timeout" in s:
            secs(p, s["timeout"])
        g = s.get("gate")
        if "gate" in s and not (isinstance(g, dict) and set(g) == {"lenses"} and isinstance(g["lenses"], list)
                                and all(x in cards for x in g["lenses"])):
            errs.append(f"{m}{p}.gate must be {{\"lenses\": [card names of this extension]}}")
    for i, h in enumerate(hooks):
        p = f"hooks[{i}]"
        if not isinstance(h, dict):
            errs.append(f"{m}{p} must be an object")
            continue
        for k in ("event", "command"):
            if k not in h:
                errs.append(f"{m}missing field {p}.{k}")
            elif not isinstance(h[k], str) or not h[k]:
                errs.append(f"{m}{p}.{k} must be a non-empty string")
        errs += [f"{m}unknown field {p}.{k}" for k in h if k not in HOOK]
        if "timeout" in h:
            secs(p, h["timeout"])

    for where, d in [("", manifest), *[(f"steps[{i}]", s) for i, s in enumerate(steps) if isinstance(s, dict)]]:
        for k in CHANGE:
            if k in d:
                errs.append(f"{k} would change built-in {', '.join(_named(d[k]))}: extensions only add steps")
    own = [s for s in steps if isinstance(s, dict) and isinstance(s.get("name"), str) and isinstance(s.get("after"), str)]
    name = manifest.get("name") if isinstance(manifest.get("name"), str) else "?"
    order = list(flow.STAGES)
    for s in own:
        if s["name"] in flow.STAGES:
            errs.append(f"step {s['name']} would replace built-in {s['name']}")
        if s["after"] == "done":
            errs.append(f"step {s['name']} can't follow done")
    after = {f"{name}.{s['name']}": s["after"] for s in own}
    for o in others:
        after.update({f"{o['name']}.{s['name']}": s["after"] for s in o.get("steps", [])})
    known = set(stages) | set(after)
    for s in own:
        a = s["after"]
        if a == "done":
            continue
        if a not in known:
            errs.append(f"step {s['name']} follows {a}, which is neither a built-in step nor a step of an added extension")
            continue
        chain, cur = [f"{name}.{s['name']}"], a
        while cur not in flow.STAGES and cur not in chain and cur in after:
            chain.append(cur)
            cur = after[cur]
        if cur not in flow.STAGES:
            errs.append(f"step {s['name']} follows {a}, which never reaches a built-in step: {' → '.join(chain + [cur])}")
        elif "plan_path" in (s.get("trigger") or {}) and order.index(cur) < order.index("plan_jury"):
            errs.append(f"step {s['name']}: trigger plan_path reads the plan, which isn't approved before plan_jury; it follows {a}")
    errs += [f"card {c} has the name of a shipped card" for c in cards if c in shipped_cards()]
    for o in others:
        errs += [f"step {s['name']} is already a step of extension {o['name']}" for s in own if s["name"] in [x["name"] for x in o.get("steps", [])]]
        errs += [f"card {c} is already a card of extension {o['name']}" for c in cards if c in o.get("cards", [])]
    errs += [f"hook on {h['event']}: NIO fires only {', '.join(EVENTS)}" for h in hooks
             if isinstance(h, dict) and isinstance(h.get("event"), str) and h["event"] not in EVENTS]
    return errs


def folder(root):
    return root / ".nio/extensions"


def read_record(root):
    try:
        return json.loads((folder(root) / "record.json").read_text())
    except (OSError, ValueError):
        return {}


def write_record(root, rec):
    d = folder(root)
    d.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".record.", suffix=".tmp")
    with os.fdopen(fd, "w") as f:
        json.dump(rec, f, indent=2, sort_keys=True)
        f.write("\n")
    os.replace(tmp, d / "record.json")


def digest(path):
    h = hashlib.sha256()
    for p in sorted(x for x in Path(path).rglob("*") if x.is_file()):
        h.update(p.relative_to(path).as_posix().encode() + b"\0" + p.read_bytes())
    return h.hexdigest()


def active(root, guard=True):
    """The added extensions' manifests, each with `dir`, in name order. ponytail: guard (CT-18) comes with its task."""
    out = []
    for p in sorted(folder(root).glob("*")) if folder(root).is_dir() else []:
        if p.is_dir() and not p.name.startswith("."):
            try:
                out.append({**json.loads((p / "manifest.json").read_text()), "dir": str(p)})
            except (OSError, ValueError):
                pass
    return out


def stage_names(others):
    return list(flow.STAGES) + [f"{o['name']}.{s['name']}" for o in others for s in o.get("steps", [])]


def followers(others, name, kept):
    """Refusals: another extension's step follows a stage of `name` that `kept` no longer has."""
    return [f"refused: {o['name']}.{s['name']} follows {s['after']}" for o in others for s in o.get("steps", [])
            if s["after"].startswith(f"{name}.") and s["after"][len(name) + 1:] not in kept]


def resolve(root, source):
    """(folder, source label, version or None, temp folder to delete) or a refusal line."""
    if "://" in source or source.startswith("git@") or source.endswith(".git"):
        tmp = tempfile.mkdtemp()
        code, _, err = records.git(tmp, "clone", "--depth", "1", source, tmp + "/c", full=True)
        if code:
            shutil.rmtree(tmp, ignore_errors=True)
            return f"refused: git clone {source} failed: {(err.strip().splitlines() or [''])[0]}"
        return Path(tmp, "c"), source, records.git(Path(tmp, "c"), "rev-parse", "HEAD")[0], tmp
    if Path(source).is_dir():
        return Path(source), source, None, None
    for base, label in ((records.home() / "extensions", f"~/.nio/extensions/{source}"), (Path(str(resources.files("nio").joinpath("shipped"))), "shipped")):
        if (base / source).is_dir():
            return base / source, label, None if label != "shipped" else _nio_version(), None
    return f"refused: no extension {'at' if '/' in source else 'named'} {source}"


def _nio_version():
    from importlib import metadata
    try:
        return metadata.version("nio")
    except metadata.PackageNotFoundError:
        return "0"


def add(root, source):
    """`nio extensions add` (CT-1): check, copy, record; runs no command. Returns (code, lines)."""
    r = resolve(root, source)
    if isinstance(r, str):
        return 1, [r]
    src, label, version, tmp = r
    try:
        try:
            manifest = json.loads((src / "manifest.json").read_text())
        except (OSError, ValueError):
            manifest = None
        name = manifest.get("name") if isinstance(manifest, dict) else None
        others = [m for m in active(root, guard=False) if m["name"] != name]
        reasons = check(src, manifest, others, stage_names(others)) if manifest is not None else check(src, None, [], [])
        if not reasons:
            reasons = [x[len("refused: "):] for x in followers(others, name, {s["name"] for s in manifest["steps"]})]
        if reasons:
            return 1, [f"refused: {reasons[0]}"]
        dest, rec = folder(root) / name, read_record(root)
        if src.resolve() == dest.resolve():  # a hand edit accepted: only the hash changes
            rec[name] = {**rec.get(name, {"source": label, "version": manifest["version"]}), "hash": digest(dest)}
            write_record(root, rec)
        else:
            new, old = folder(root) / f".{name}.new", folder(root) / f".{name}.old"
            for p in (new, old):
                shutil.rmtree(p, ignore_errors=True)
            shutil.copytree(src, new, ignore=shutil.ignore_patterns(".git"))
            if dest.exists():
                dest.rename(old)
            new.rename(dest)
            rec[name] = {"source": label, "version": version or manifest["version"], "hash": digest(dest)}
            write_record(root, rec)
            shutil.rmtree(old, ignore_errors=True)
        cmds = [f"check {name}.{s['name']}: {s['check']}" for s in manifest["steps"]] + [f"hook {h['event']}: {h['command']}" for h in manifest["hooks"]]
        return 0, [f"added {name} {rec[name]['version']} from {label}",
                   *(["commands it brings (none run):", *cmds] if cmds else ["commands it brings: none"]),
                   "commit .nio/extensions to share it with the team"]
    finally:
        if tmp:
            shutil.rmtree(tmp, ignore_errors=True)


def listing(root):
    """`nio extensions list` (CT-3)."""
    exts, rec = active(root), read_record(root)
    if not exts:
        return 0, ["no extensions in .nio/extensions"]
    out = []
    for m in exts:
        join = lambda xs, sep: sep.join(xs) or "none"
        out += [f"{m['name']} · {m['version']} · {rec.get(m['name'], {}).get('source', '?')}",
                f"  steps: {join([f'{m['name']}.{s['name']} (after {s['after']})' for s in m['steps']], ', ')}",
                f"  cards: {join(m['cards'], ', ')}",
                f"  hooks: {join([f'{h['event']}: {h['command']}' for h in m['hooks']], '; ')}"]
    return 0, out


def remove(root, name):
    """`nio extensions remove` (CT-4): the record first, then the folder. ponytail: effort-stage refusal comes with T-8."""
    rec, d = read_record(root), folder(root) / name
    if name not in rec and not d.is_dir():
        return 1, [f"refused: no extension named {name} in .nio/extensions"]
    others = [m for m in active(root, guard=False) if m["name"] != name]
    if bad := followers(others, name, set()):
        return 1, [bad[0]]
    rec.pop(name, None)
    write_record(root, rec)
    shutil.rmtree(d, ignore_errors=True)
    return 0, [f"removed {name}", "commit .nio/extensions to share it with the team"]
