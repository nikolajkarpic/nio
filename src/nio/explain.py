"""Helpers for the explainer: its sections, a diagram's node IDs and rendering one Mermaid block."""
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from nio import spec

MERMAID = "@mermaid-js/mermaid-cli@11.4.2"
TIMEOUT = 120
ARROW = re.compile(r"<?(?:-\.+-|[-=]{3,}|[-=]{2}(?=[>ox])|->)(?:>>?|[ox])?")
SKIP = ("%%", "classDef", "class ", "style ", "linkStyle", "click ", "subgraph")
DROP = re.compile(r'"[^"]*"|\[[^\]]*\]|\([^)]*\)|\{[^}]*\}|\|[^|]*\|')
ID = re.compile(r"[A-Za-z_]\w*")


def sections(text):
    """One dict per `## ` section: title, fence, block, walk, drill."""
    out, cur, fenced = [], None, None
    for line in text.splitlines():
        if fenced is None and line.startswith("## "):
            cur = {"title": line[3:].strip(), "fence": None, "block": None, "walk": [], "img": False}
            out.append(cur)
        elif cur is None:
            continue
        elif fenced is not None:
            if line.strip().startswith("```"):
                if cur["block"] is None:
                    cur["fence"], cur["block"] = fenced[0], "\n".join(fenced[1]) + "\n"
                fenced = None
            else:
                fenced[1].append(line)
        elif line.strip().startswith("```"):
            fenced = (line.strip()[3:].strip() or None, [])
        elif line.startswith("![") or line.startswith("> "):
            cur["img"] |= line.startswith("![")
        else:
            cur["walk"].append(line)
    for s in out:
        s["walk"] = "\n".join(s["walk"]).strip()
        s["drill"] = s["title"].startswith("Drill-down: ")
        s["diagram"] = s.pop("img") or s["block"] is not None
    return out


def nodes(block):
    """The distinct node IDs of a diagram block."""
    found = set()
    for line in block.splitlines()[1:]:
        line = DROP.sub("", line).strip()
        if not line or line.startswith(SKIP) or line == "end" or line.startswith("end "):
            continue
        if m := re.match(r"(?:participant|actor|state)\s+(\w+)", line):
            found.add(m[1])
        for stmt in line.split(":")[0].split(";"):
            parts = ARROW.split(stmt)
            for piece in (q for p in parts for q in p.split("&")):
                m = re.fullmatch(r"\s*([A-Za-z_]\w*)(?:\s+(?:--|==|-\.).*)?\s*", piece)
                if m and (len(parts) > 1 or ID.fullmatch(stmt.strip())):
                    found.add(m[1])
    return found


COULD_NOT_RUN = ("npm ERR", "ENOTFOUND", "EAI_AGAIN", "ETIMEDOUT", "ECONNREFUSED", "Failed to launch", "Could not find Chrome")


def render(block, out):
    """Render a Mermaid block to the SVG `out`: ok, broken: <reason>, no node or unreachable."""
    if shutil.which("npx") is None:
        return "no node"
    with tempfile.TemporaryDirectory() as d:
        src = Path(d) / "d.mmd"
        src.write_text(block)
        try:
            r = subprocess.run(["npx", "-y", MERMAID, "-i", str(src), "-o", str(out)],
                               capture_output=True, text=True, timeout=TIMEOUT)
        except (OSError, subprocess.SubprocessError):
            return "unreachable"
    both = r.stdout + r.stderr
    if r.returncode == 0 and Path(out).exists():
        return "ok"
    if r.returncode == 0 or any(m in both for m in COULD_NOT_RUN):
        return "unreachable"
    lines = [l.strip() for l in both.splitlines() if l.strip()]
    # ponytail: marker list is a heuristic; add markers when a new fetch/launch failure shows up
    return "broken: " + next((l for l in lines if "Parse error" in l), lines[0] if lines else "exit %d" % r.returncode)


def check(root, target, gate=False, base="HEAD"):
    """(errors, notes) for an explainer: a slug (plan mode) or a .md path (CT-4): plan mode checks the core
    diagrams, contract IDs, node cap and walk-throughs; every mode renders its Mermaid blocks."""
    if target.endswith(".md"):
        p = Path(target) if Path(target).is_absolute() else root / target
    else:
        if not spec.path(root, target).exists():
            raise ValueError(f"no effort {target} under .nio/specs/")
        p = spec.path(root, target).parent / "explainer.md"
    p = p.resolve()
    if not p.exists():
        return [f"explainer missing: {p.relative_to(root)}"], []
    fmt = "mermaid"
    errors, secs = [], sections(p.read_text())
    plan_mode = not target.endswith(".md") or p == (spec.path(root, p.parent.name).parent / "explainer.md").resolve()  # J-6: a slug is plan mode, symlink or not
    if plan_mode:
        from nio import records
        fmt = records.config(root).get("explain", {}).get("format", "mermaid")
        core = {s["title"].lower(): s for s in secs}
        for name in ("component map", "build order"):
            if not core.get(name, {}).get("diagram"):
                errors.append(f"missing core diagram: {name}")
        cm = core.get("component map")
        if cm and cm["diagram"]:
            labels = " ".join(re.findall(r'"[^"]*"|\[[^\]]*\]', cm["block"] or "")) if fmt == "mermaid" else cm["walk"] + (cm["block"] or "")
            errors += [f"component map misses {c}" for c, _ in spec.items((p.parent / "contracts.md").read_text().splitlines() if (p.parent / "contracts.md").exists() else []) if c.startswith("CT-") and not re.search(rf"\b{re.escape(c)}(?!\d)", labels)]
        for s in secs:
            if s["block"] and len(nodes(s["block"])) > 20:
                errors.append(f"too many nodes: {s['title']} ({len(nodes(s['block']))} > 20)")
            if s["diagram"]:
                n = len(s["walk"].split())
                if not n:
                    errors.append(f"walk-through missing: {s['title']}")
                elif n > 120:
                    errors.append(f"walk-through too long: {s['title']} ({n} words)")
    notes = []
    if plan_mode and fmt != "mermaid":
        notes.append(f"render skipped: diagrams drawn with {fmt}")  # J-42: a Mermaid fallback block is still rendered below
    for s in secs:
        if s["fence"] == "mermaid" and s["block"]:
            with tempfile.TemporaryDirectory() as d:
                r = render(s["block"], Path(d) / "o.svg")
            if r == "no node":
                notes.append("render skipped: Node is not installed")
                break
            if r == "unreachable":
                notes.append("render skipped: the renderer could not be fetched")
                break
            if r.startswith("broken"):
                errors.append(f"broken diagram: {s['title']}")
    return errors, notes


REC = re.compile(r"^\((source|diagrams|images|drill-downs|drill-down): (.*)\)$")
EARLIER = " (written for an earlier plan)"
LINK = re.compile(r"^!\[[^\]]*\]\(([^)]+)\)$")


def _put(path, text):
    with tempfile.NamedTemporaryFile("w", dir=path.parent, delete=False, suffix=".tmp") as f:
        f.write(text)
    os.replace(f.name, path)


READ_FIRST = "Read first: [explainer.md](explainer.md)\n\n"


def _front(text):
    """(front matter with its closing `---` line, the rest)."""
    m = re.match(r"---\r?\n.*?\n---\r?\n", text, re.S)  # CRLF files too (pr gate adversary F1)
    return (m[0], text[m.end():]) if m else ("", text)


def read_first(text):
    """quickstart.md with the `Read first` line right after its front matter (J-48): `unread_first` is its exact inverse."""
    fm, rest = _front(text)
    if re.match(r"---\r?\n", text) and not fm:
        raise ValueError("quickstart.md's front matter has no closing `---`; fix it before finishing")
    return text if rest.startswith(READ_FIRST) else fm + READ_FIRST + rest


def unread_first(text):
    """quickstart.md without the `Read first` line finish adds, and only there: the plan gate judges the rest (J-116)."""
    fm, rest = _front(text)
    return fm + rest[len(READ_FIRST):] if rest.startswith(READ_FIRST) else text


def finish(root, path):
    """The lines `nio explain finish` prints (CT-5 steps 1-8). ValueError refuses."""
    from nio import flow, implement, plan
    if not path:
        raise ValueError("finish needs the explainer's path")
    p = (Path(path) if Path(path).is_absolute() else root / path).resolve()
    d = p.parent
    plan_mode = p == (spec.path(root, d.name).parent / "explainer.md").resolve()
    if not (p.suffix == ".md" and p.is_file() and (plan_mode or d == (root / ".nio/research").resolve())):  # J-10
        raise ValueError(f"{path} is not an explainer: finish takes .nio/specs/<slug>/explainer.md or a .md under .nio/research/")
    rel = lambda f: str((d / f).relative_to(root.resolve()))
    if plan_mode:
        try:
            ok, why = (False, "there is no plan.md") if not (d / "plan.md").exists() else plan.approved(root, d.name)
        except ValueError as e:
            ok, why = False, str(e)
        if not ok:
            raise ValueError(f"the plan jury comes first ({why}); explain a topic instead")
    q = d / "quickstart.md"
    qtext = None
    if plan_mode and q.exists() and (added := read_first(q.read_text())) != q.read_text():
        qtext = added
    rec, body = {}, []
    for l in p.read_text().splitlines():
        m = REC.match(l.strip())
        if m:
            rec.setdefault(m[1], []).append(m[2])
        else:
            body.append(l)
    drill = [s["title"] for s in sections("\n".join(body)) if s["drill"]]
    plain = [t.removesuffix(EARLIER) for t in drill]
    old_drills = [h for v in rec.get("drill-downs", []) for h in v.split("; ") if h] + rec.get("drill-down", [])  # old joined line, then one-per-line
    if gone := [h for h in old_drills if h not in plain]:
        raise ValueError(f"drill-down sections missing: {', '.join(gone)}; restore them before finishing")
    out, stale = [], False
    if plan_mode:
        src = {}
        for v in rec.get("source", []):
            f, _, h = v.rpartition("@")
            src[f] = h
        stale = any(implement.digest(root, f)[:12] != h for f, h in src.items())
        if stale:
            body = [l + EARLIER if l.startswith("## Drill-down: ") and not l.endswith(EARLIER) else l for l in body]
        blocks, fenced, skip = [], None, False
        for l in body:
            if fenced is None and l.startswith("## "):
                skip = l.startswith("## Drill-down: ")
            if l.strip().startswith("```"):
                if fenced is None:
                    fenced = []
                else:
                    blocks += [] if skip else fenced
                    fenced = None
            elif fenced is not None:
                fenced.append(l)
        dg = flow.sha(("\n".join(blocks)).encode())[:12]
        if not src or rec.get("diagrams", [""])[0] != dg:
            rec["source"] = [f"{rel(f)}@{implement.digest(root, rel(f))[:12]}" for f in ("spec.md", "plan.md", "contracts.md")]
            rec["diagrams"] = [dg]
        elif stale:
            out.append("still stale: no diagram changed since the last finish; redraw the diagrams to clear the stale line")
    prefix = "explainer-" if plan_mode else p.stem + "--"
    # step 6, without drawing: drop image links and notes, except in a drill-down whose image exists
    new, keep, fenced, kept_sec, kept_titles = [], [], False, False, set()
    for l in body:
        if not fenced and l.startswith("## "):
            kept_sec = False
        if l.strip().startswith("```"):
            fenced = not fenced
        elif not fenced and (l.startswith(("> Images not rendered:", "> Broken diagram:")) or (LINK.match(l) and LINK.match(l)[1].startswith(prefix))):
            m = LINK.match(l)
            if m and any(h.startswith("Drill-down: ") for h in [new_title(new)]) and (d / m[1]).is_file():
                keep.append(m[1])
                kept_titles.add(new_title(new))
            else:
                if new and not new[-1].strip():  # the blank line finish wrote before it goes too, or reruns add blanks
                    new.pop()
                continue
        new.append(l)
    # step 6, drawing: name and render each other Mermaid section's first block
    drawn, used, plans, title, fenced, first, halt = [], set(), [], "", False, False, False
    for i, l in enumerate(new):
        if not fenced and l.startswith("## "):
            title, first, ti = l[3:].strip().removesuffix(EARLIER), True, i
        if l.strip().startswith("```"):
            fenced = not fenced
            if fenced:
                start, lang = i, l.strip()[3:].strip()
            elif first and title and lang == "mermaid":
                first = False
                if new[ti][3:].strip() in kept_titles:
                    continue
                base = p.stem + "--" + "-".join(re.sub(r"[^a-z0-9 ]", "", re.sub(r"[-/_]", " ", title.lower())).split())
                name, k = base + ".svg", 1
                while name in used:
                    k += 1
                    name = f"{base}-{k}.svg"
                used.add(name)
                plans.append((ti, i, name, "\n".join(new[start + 1:i]) + "\n"))
    adds = {}
    for ti, i, name, block in plans:
        if halt:
            break
        r = render(block, d / name)
        if r in ("no node", "unreachable"):
            why = "Node is not installed" if r == "no node" else "the renderer could not be fetched"
            adds.setdefault(ti, []).append(f"> Images not rendered: {why}.")
            halt = True
        elif r == "ok":
            drawn.append(name)
            adds.setdefault(i, []).append(f"![{new[ti][3:].strip().removesuffix(EARLIER)}]({name})")
        else:
            adds.setdefault(i, []).append(f"> Broken diagram: {r.removeprefix('broken: ')}")
    new = [y for i, l in enumerate(new) for y in [l] + (["", *adds[i]] if i in adds else [])]
    old_imgs = [x for v in rec.get("images", []) for x in v.split(", ") if x]
    dels = []
    for x in old_imgs:
        f = (d / x).resolve()
        if f.parent != d or not f.name.startswith(prefix):
            out.append(f"warning: ignored {x}: not this explainer's own image")
        elif f.is_file() and x not in keep and f.name not in drawn:  # J-11: an image this run didn't redraw is stale
            dels.append(f)
    text = "\n".join(new).rstrip() + "\n"
    recs = [f"({k}: {v})" for k in ("source", "diagrams") for v in rec.get(k, [])]
    recs += [f"(images: {', '.join(drawn + keep)})"] + [f"(drill-down: {t.removesuffix(EARLIER)})" for t in drill]
    i = text.find("## ") if text.startswith("## ") else text.find("\n## ") + 1  # records sit above the first section
    head = text[:i].rstrip("\n")
    _put(p, (head + "\n\n" if head else "") + "\n".join(recs) + "\n\n" + text[i:])
    for f in dels:  # only once the explainer no longer links them (CT-5: nothing changes before step 8's write)
        f.unlink()
        out.append(f"deleted: {f.name}")
    if qtext is not None:
        _put(q, qtext)
    out.append(f"finished: {path}")
    return out


def new_title(lines):
    """The title of the last `## ` heading in lines."""
    return next((l[3:].strip() for l in reversed(lines) if l.startswith("## ")), "")


def stale(root):
    """CT-7: status lines for each spec explainer whose recorded sources are gone or changed."""
    from nio import implement
    out = []
    for e in sorted((root / ".nio/specs").glob("*/explainer.md")):
        try:
            text = e.read_text()
        except (OSError, UnicodeDecodeError):  # J-19: one bad file never breaks `nio status`
            out += [f"error: can't read .nio/specs/{e.parent.name}/explainer.md"]
            continue
        for l in text.splitlines():
            m = REC.match(l.strip())
            if m and m[1] == "source":
                f, _, h = m[2].rpartition("@")
                if not (root / f).is_file() or implement.digest(root, f)[:12] != h:  # J-41: a gone source is stale
                    out += ["stale: explainer.md (spec, plan or contracts changed)", f"  in .nio/specs/{e.parent.name}/: re-run @nio:explain"]
                    break
    return out


def topic(root, text, today=None):
    """CT-6: `continue: <path>` for the file storing this topic, else `new: <path>` for the first free name."""
    import datetime
    name = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:40]
    if not name:
        raise ValueError(f'the topic "{text}" gives an empty file name')
    day = today or datetime.date.today().isoformat()
    n, want = 1, f"(topic: {' '.join(text.split())})"
    while True:
        rel = f".nio/research/{day}-{name}-explainer{'' if n == 1 else f'-{n}'}.md"
        p = root / rel
        if not p.exists():
            return f"new: {rel}"
        head = p.read_text(errors="replace").split("\n## ", 1)[0]  # the stored topic line sits above the first section
        if want in " ".join(head.split()):  # J-9: padding and line breaks don't change the topic
            return f"continue: {rel}"
        n += 1
