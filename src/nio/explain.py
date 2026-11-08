"""Helpers for the explainer: its sections, a diagram's node IDs and rendering one Mermaid block."""
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
    """(errors, notes) for an explainer: a slug (plan mode) or a .md path. Only the missing-file error so far."""
    if target.endswith(".md"):
        p = Path(target) if Path(target).is_absolute() else root / target
    else:
        if not spec.path(root, target).exists():
            raise ValueError(f"no effort {target} under .nio/specs/")
        p = spec.path(root, target).parent / "explainer.md"
    if not p.exists():
        return [f"explainer missing: {p.relative_to(root)}"], []
    errors, secs = [], sections(p.read_text())
    plan_mode = target in {p.parent.name} or p == spec.path(root, p.parent.name).parent / "explainer.md"
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
