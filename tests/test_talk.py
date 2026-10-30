"""Self-check: every skill carries NORTH_STAR's "Talking to the human" block word for word (#53).
Run: uv run python tests/test_talk.py"""
import re
import shutil
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LAST = "Before sending, ask: could they act on this without opening a file? If not, rewrite it."
# old instructions that put IDs or sources in front of the human (AC-18), unless the text now says where they go
GONE = [r"each naming its source", r"with the code's file:line(?! in `Refs:`)", r"show each reason with its findings(?! in plain words)"]


def block(text):
    """The block's lines after its heading, up to and including the self-check line; None if absent."""
    m = re.search(r"^#+ Talking to the human\n(.*?^" + re.escape(LAST) + r")$", text, re.M | re.S)
    return m and m[1]


def problems(root):
    source = block((root / "NORTH_STAR.md").read_text())
    if not source:
        return ["NORTH_STAR.md: no Talking to the human block ending in the self-check line"]
    out = []
    for skill in sorted(root.glob("skills/*/SKILL.md")):
        text, name = skill.read_text(), skill.relative_to(root)
        copy = block(text)
        if copy is None:
            out.append(f"{name}: block missing")
        elif copy != source:
            line = next((b for a, b in zip(source.splitlines() + [""], copy.splitlines() + [""]) if a != b), "line endings")
            out.append(f"{name}: block differs from NORTH_STAR.md at: {line!r}")
        for phrase in GONE:
            if re.search(phrase, text):
                out.append(f"{name}: still says {phrase!r}")
    return out


def check():
    start = time.monotonic()
    assert problems(ROOT) == [], problems(ROOT)
    for name in ("spec", "grill", "jury", "plan", "tasks", "implement"):  # #56: every stage hands off through the flow
        stops = re.findall(r"^Stop .*?(?:\n\n|\Z)", (ROOT / f"skills/{name}/SKILL.md").read_text(), re.M | re.S)
        assert any("nio flow next" in s for s in stops), name
    assert time.monotonic() - start < 2  # the real check, not this test's setup below (NFR-1)
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        shutil.copy(ROOT / "NORTH_STAR.md", root)
        shutil.copytree(ROOT / "skills", root / "skills")
        jury, remember = root / "skills/jury/SKILL.md", root / "skills/remember/SKILL.md"
        text = jury.read_text()
        jury.write_text(text.replace(block(text), block(text).replace("Pick one", "Choose one")))
        remember.write_text(remember.read_text().replace("# Talking to the human\n", "# Talking\n"))
        got = problems(root)
        assert any(p.startswith("skills/jury/SKILL.md: block differs") for p in got), got
        assert any(p.startswith("skills/remember/SKILL.md: block missing") for p in got), got
        north = root / "NORTH_STAR.md"
        north.write_text(north.read_text().replace(LAST, "Check it."))
        assert [p for p in problems(root) if p.startswith("NORTH_STAR.md")], problems(root)


if __name__ == "__main__":
    check()
    print("ok")
