"""Self-check: every skill carries NORTH_STAR's "Talking to the human" block word for word (#53).
Run: uv run python tests/test_talk.py"""
import re
import shutil
import tempfile
import time
from pathlib import Path
import selfcheck

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


# --- 2026-11-14-short-lived-drivers: the driver and waiting rules in the implement and jury skills (#128) ---

def drivers(name):
    """(whole skill, its "Drivers and waiting" section, the main session's part, the driver's part), whitespace folded."""
    text = (ROOT / f"skills/{name}/SKILL.md").read_text()
    sec = text.split("\n## Drivers and waiting\n")[1].split("\n## ")[0]
    fold = lambda s: " ".join(s.split())
    main = sec.split("**The main session**")[1].split("**The driver**")[0]
    return fold(text), fold(sec), fold(main), fold(sec.split("**The driver**")[1].split("**Waiting for long work.**")[0])


BOTH = ("implement", "jury")


def test_drivers_ac1_ac2_one_fresh_driver_per_unit():
    for name in BOTH:
        _, sec, main, drv = drivers(name)
        assert "one gate (spec, plan or tasks), or one epic with its tasks and its implementation jury" in sec, name
        assert "a fresh agent that runs that one unit and then ends" in sec and "Start a fresh driver for it" in main, name
        assert "several drivers one after another; a unit resumed after a hand-back gets a new one" in main, name
        assert "never go on into the next unit" in drv, name


def test_drivers_ac3_driver_starts_from_the_brief_alone():
    for name in BOTH:
        main = drivers(name)[2]
        assert "whose first input is what `nio flow brief <slug>` prints, and nothing else: no note from an earlier driver" in main, name


def test_drivers_ac4_summary_three_parts_15_lines():
    for name in BOTH:
        drv = drivers(name)[3]
        assert "at most 15 lines" in drv and all(x in drv for x in ("`closed:`", "`open:`", "`next:`")), name


def test_drivers_ac5_hand_back_never_decide_for_the_human():
    for name in BOTH:
        drv = drivers(name)[3]
        assert "end there with the summary naming that item and the command to continue" in drv, name
        assert "a blocked task" in drv and "Never make the human's decision yourself" in drv, name


def test_drivers_ac6_one_driver_at_a_time():
    for name in BOTH:
        main = drivers(name)[2]
        assert "only once the previous one for this effort has ended; never two at once" in main, name
        assert "ended without a summary counts as ended: go on from `nio flow brief <slug>` alone" in main, name


def test_drivers_ac7_ac16_main_session_only_routes():
    for name in BOTH:
        text, _, main, drv = drivers(name)
        assert "Read nothing else yourself" in main and "runs every step under Steps below" in drv, name
        for word in ("pack", "juror output", "nio jury evidence", "nio flow red", "nio flow green", "test log", ".nio/runs"):
            assert word not in main, (name, word)
    assert "Optional: a gate driver" not in drivers("jury")[0]  # the old step kept dispositions with the main session


def test_drivers_ac8_relay_from_the_summary_alone():
    for name in BOTH:
        assert "what needs the human goes to them from the summary alone" in drivers(name)[2], name


def wait(name):
    return drivers(name)[1].split("**Waiting for long work.**")[1]


def test_drivers_ac9_background_and_completion_notice():
    for name in BOTH:
        w = wait(name)
        assert "`nio flow green`, `nio jury evidence`, a suite run, and any subagent" in w, name
        assert "start it in the background, then act on its notice when it arrives" in w and "no sleep, no loop, no status check" in w, name


def test_drivers_ac10_ac11_blocking_wait_three_times():
    for name in BOTH:
        w = wait(name)
        assert "it is not known whether it has them" in w and "wait blocking, with a 10-minute timeout" in w, name
        assert "check once whether the command finished; if not, wait again. At most three waits" in w, name
        assert "after the third that times out, end with the summary naming the command as still running" in w, name
        assert "Never check at an interval" in w and "every few" not in w and "poll " not in w, name


def test_drivers_ac12_refused_background_green_goes_to_step_3():
    text = drivers("implement")[0]
    step3 = text.split("3. **On a refusal**")[1].split("4. **")[0]
    assert "A `nio flow green` started in the background that refuses" in step3 and "with the text it printed, exactly" in step3


def test_drivers_ac13_host_neutral():
    for name in BOTH:
        sec = drivers(name)[1]
        claude = [s for s in sec.split(". ") if "Claude" in s]
        assert claude and all("Optional, on Claude Code" in s for s in claude), (name, claude)


def test_drivers_ac14_no_subagents_main_session_runs_it():
    for name in BOTH:
        sec = drivers(name)[1]
        assert "On a host without subagents, the main session runs the unit itself from `nio flow brief <slug>`" in sec, name
        assert "goes on without stopping for the human" in sec and "new session" not in sec, name


def test_drivers_ac19_no_notices_no_timed_wait_hands_back():
    for name in BOTH:
        w = wait(name)
        assert "**Neither:** don't run the long command; end with the summary naming it as open" in w, name
        assert "foreground" not in w.replace("outlast the host's foreground limit", ""), name


def test_drivers_ac20_running_brief_means_wait():
    for name in BOTH:
        _, sec, _, drv = drivers(name)
        assert "If it shows `running: <command>, started <time>`" in drv and "wait on that run (below), never start it again" in drv, name
        assert "`nio flow green` and `nio jury evidence` record themselves as running" in sec, name


if __name__ == "__main__":
    selfcheck.main([check] + [f for n, f in list(globals().items()) if n.startswith("test_drivers") and callable(f)])
