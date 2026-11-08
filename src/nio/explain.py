"""Helpers for the explainer: its sections, a diagram's node IDs and rendering one Mermaid block."""
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from nio import spec

MERMAID = "@mermaid-js/mermaid-cli@11.4.2"
TIMEOUT = 120
ARROW = re.compile(r"-->>|->>|-\.->|==>|-->|---|->")
SKIP = ("%%", "classDef", "class ", "style ", "linkStyle", "click ", "subgraph", "end")
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
    for line in DROP.sub("", block).splitlines()[1:]:
        line = line.strip()
        if not line or line.startswith(SKIP):
            continue
        if m := re.match(r"(?:participant|actor|state)\s+(\w+)", line):
            found.add(m[1])
        parts = ARROW.split(line)
        if len(parts) > 1 or ID.fullmatch(line):
            found.update(p.strip() for p in parts if ID.fullmatch(p.strip()))
    return found


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
    if r.returncode != 0 and "Parse error" in both:
        return "broken: " + next(l for l in both.splitlines() if "Parse error" in l).strip()
    return "unreachable"


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
    return [], []
