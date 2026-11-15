"""Self-check for nio.explain. Run: uv run python tests/test_explain.py"""
try:
    from nio import explain
except ImportError:
    explain = None
from pathlib import Path

import selfcheck


def chain(n):
    return "flowchart LR\n" + " --> ".join(f"n{i}" for i in range(1, n + 1)) + "\n"


def test_ac5_node_cap():
    # T-1 part of TC-5: the node count; the check part lands with T-3
    assert explain is not None and hasattr(explain, "nodes"), "nio.explain.nodes missing"
    assert explain.nodes(chain(21)) == {f"n{i}" for i in range(1, 22)}
    assert len(explain.nodes(chain(20))) == 20
    assert explain.nodes('flowchart TD\nA["x --> y"] --> B(z)\n%% c --> d\nsubgraph S\nB -.-> C\nend\n') == {"A", "B", "C"}
    assert explain.nodes("flowchart TD\nendpoint --> api\nend") == {"endpoint", "api"}
    seq = "sequenceDiagram\n" + "".join(f"Client->>Svc{i}: call\n" for i in range(1, 26))
    assert len(explain.nodes(seq)) == 26
    assert explain.nodes("stateDiagram-v2\n[*] --> Idle\nIdle --> Busy: go\nstate Done") == {"Idle", "Busy", "Done"}
    assert explain.nodes("sequenceDiagram\nClient->>Svc3: retry (see note\nClient->>Svc4: ok)") == {"Client", "Svc3", "Svc4"}
    assert explain.nodes("flowchart TD\nA <--> B\nC --o D\nE --x F\nG ---> H\nI ==> J\nK -.-> L") == set("ABCDEFGHIJKL")
    assert explain.nodes("flowchart TD\nA --> B & C\nA -- retry --> D\nE --> F; F --> G") == set("ABCDEFG")


def test_ac11_missing():
    # TC-16: the approved refunds spec with no explainer.md; the CLI exits 1 and names the file
    import subprocess
    import sys
    from test_records import repo
    from test_spec import put

    root = repo()
    put(root, "spec.md")
    code = "import sys; sys.argv = ['nio', 'check', 'explainer', 'checkout-refunds']; from nio.cli import main; main()"
    r = subprocess.run([sys.executable, "-c", code], cwd=root, capture_output=True, text=True)
    assert r.returncode == 1, (r.returncode, r.stdout, r.stderr)
    assert "ERROR explainer missing: .nio/specs/checkout-refunds/explainer.md" in r.stdout, (r.stdout, r.stderr)


def test_ac9_broken_block():
    # TC-14 (render level; check's loop is a later task): a rejected diagram is broken, a fetch failure unreachable
    import os
    import stat
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        npx = Path(d) / "npx"
        npx.write_text('#!/bin/sh\necho "$FAKE_ERR" >&2\nexit 1\n')
        npx.chmod(npx.stat().st_mode | stat.S_IEXEC)
        old = os.environ.copy()
        os.environ["PATH"] = d + os.pathsep + old["PATH"]
        try:
            os.environ["FAKE_ERR"] = "UnknownDiagramError: No diagram type detected for flowchar"
            assert explain.render("flowchar TD", Path(d) / "o.svg").startswith("broken: UnknownDiagramError"), "typo"
            os.environ["FAKE_ERR"] = "npm ERR! code ENOTFOUND"
            assert explain.render("flowchart TD", Path(d) / "o.svg") == "unreachable"
        finally:
            os.environ.clear()
            os.environ.update(old)
    # TC-14: the check names the broken block, and only it
    import subprocess
    import sys
    from test_records import repo
    from test_spec import put

    root = repo()
    put(root, "spec.md")
    ex = root / ".nio/specs/checkout-refunds/explainer.md"
    ex.write_text("## Component map\n\n```mermaid\nflowchart LR\nA --> B\n```\n\nwalk\n\n"
                  "## Build order\n\n```mermaid\nflowchart LR\nA --> B\nBROKEN -->\n```\n\nwalk\n")
    with tempfile.TemporaryDirectory() as d:
        npx = Path(d) / "npx"
        npx.write_text('#!/bin/sh\nwhile [ $# -gt 0 ]; do case $1 in -i) i=$2;; -o) o=$2;; esac; shift; done\n'
                       'if grep -q BROKEN "$i"; then echo "Parse error on line 3" >&2; exit 1; fi\ntouch "$o"\n')
        npx.chmod(npx.stat().st_mode | stat.S_IEXEC)
        env = dict(os.environ, PATH=d + os.pathsep + os.environ["PATH"])
        code = "import sys; sys.argv = ['nio', 'check', 'explainer', 'checkout-refunds']; from nio.cli import main; main()"
        r = subprocess.run([sys.executable, "-c", code], cwd=root, capture_output=True, text=True, env=env)
    assert r.returncode == 1, (r.returncode, r.stdout, r.stderr)
    assert "ERROR broken diagram: Build order" in r.stdout, (r.stdout, r.stderr)
    assert "Component map" not in r.stdout, r.stdout


def good(walk_build="Order walk.", extra="", calls=None, contracts=("CT-1", "CT-2"), cmap_nodes=None, build=True, cmap_walk="Map walk."):
    """(root, run) for a refunds effort with a GOOD explainer; run() -> (exit code, stdout) of the CLI check, with a fake npx."""
    import os
    import stat
    import subprocess
    import sys
    import tempfile
    from test_records import repo
    from test_spec import put

    root = repo()
    slug = put(root, "spec.md")
    d = root / ".nio/specs" / slug
    (d / "contracts.md").write_text("".join(f"### {c} Thing (FR-1) [agent]\n- Kind: function\n\n" for c in contracts))
    m = cmap_nodes or 'A["CT-1 Refund"] --> B["CT-2 Ledger"]'
    t = f"## Component map\n\n```mermaid\nflowchart LR\n{m}\n```\n\n{cmap_walk}\n\n"
    if build:
        t += f"## Build order\n\n```mermaid\nflowchart LR\nA --> B\n```\n\n{walk_build}\n\n"
    if calls:
        t += f"## Calls\n\n```mermaid\n{calls}```\n\nCalls walk.\n"
    (d / "explainer.md").write_text(t + extra)
    bin = Path(tempfile.mkdtemp())
    npx = bin / "npx"
    npx.write_text('#!/bin/sh\nwhile [ $# -gt 0 ]; do case $1 in -o) o=$2;; esac; shift; done\ntouch "$o"\n')
    npx.chmod(npx.stat().st_mode | stat.S_IEXEC)
    env = dict(os.environ, PATH=str(bin) + os.pathsep + os.environ["PATH"])
    code = "import sys; sys.argv = ['nio', 'check', 'explainer', 'checkout-refunds']; from nio.cli import main; main()"

    def run():
        r = subprocess.run([sys.executable, "-c", code], cwd=root, capture_output=True, text=True, env=env)
        return r.returncode, r.stdout + r.stderr
    run.root = root
    return run


def test_ac10_no_node():
    # TC-15: no npx on PATH: render skipped with a note, the other checks still run
    import os
    import subprocess
    import sys
    import tempfile
    root = good().root
    ex = root / ".nio/specs/checkout-refunds/explainer.md"
    bin = Path(tempfile.mkdtemp())
    (bin / "git").symlink_to(__import__("shutil").which("git"))  # git only: no npx
    env = dict(os.environ, PATH=str(bin))
    code = "import sys; sys.argv = ['nio', 'check', 'explainer', 'checkout-refunds']; from nio.cli import main; main()"

    def go():
        r = subprocess.run([sys.executable, "-c", code], cwd=root, capture_output=True, text=True, env=env)
        return r.returncode, r.stdout + r.stderr
    c, out = go()
    assert c == 0 and "render skipped: Node is not installed" in out, (c, out)
    ex.write_text(ex.read_text().replace("CT-2 ", ""))
    c, out = go()
    assert c == 1 and "ERROR component map misses CT-2" in out, (c, out)


def test_ac5_node_cap_check():
    # TC-5: 21 chained IDs fail naming the diagram, 20 pass
    c, out = good(calls=chain(21))()
    assert c == 1 and "ERROR too many nodes: Calls (21 > 20)" in out, (c, out)
    c, out = good(calls=chain(20))()
    assert c == 0 and "too many nodes" not in out, (c, out)


def test_ac36_walk_limit():
    # TC-6
    c, out = good(walk_build="word " * 121)()
    assert c == 1 and "ERROR walk-through too long: Build order (121 words)" in out, (c, out)
    c, out = good(walk_build="word " * 120)()
    assert c == 0, (c, out)


def test_ac6_passes():
    # TC-11
    c, out = good()()
    assert c == 0 and out.strip().splitlines()[-1] == "0 errors", (c, out)


def test_ac7_missing_contract():
    # TC-12
    c, out = good(contracts=("CT-1", "CT-2", "CT-3"), cmap_walk="CT-3 comes later.")()
    assert c == 1 and "ERROR component map misses CT-3" in out, (c, out)
    assert "CT-1" not in out and "CT-2" not in out, out
    # J-1: CT-10 in the map does not name CT-1
    c, out = good(contracts=("CT-1", "CT-10"), cmap_nodes='A["CT-10 Ledger"] --> B["CT-10 Again"]')()
    assert c == 1 and "ERROR component map misses CT-1" in out, (c, out)
    # path spellings of the plan explainer still run the plan checks
    run = good(contracts=("CT-1", "CT-2", "CT-3"))
    ex = run.root / ".nio/specs/checkout-refunds/explainer.md"
    for t in ("./.nio/specs/checkout-refunds/../checkout-refunds/explainer.md", str(ex)):
        errs, _ = explain.check(run.root, t)
        assert "component map misses CT-3" in errs, (t, errs)


def test_ac8_missing_build_order():
    # TC-13
    c, out = good(build=False)()
    assert c == 1 and "ERROR missing core diagram: build order" in out, (c, out)


def test_uj1_huge_diagram():
    # TC-39
    m = " --> ".join(f"c{i}" for i in range(1, 29))
    c, out = good(cmap_nodes=m + '\nc29["CT-1"] --> c30["CT-2"]')()
    assert c == 1 and "ERROR too many nodes: Component map (30 > 20)" in out, (c, out)


DRILL = "## Drill-down: one\n\n```mermaid\nflowchart LR\nX --> Y\n```\n\nDrill walk.\n\n![one](explainer-drill-1.svg)\n"


def fin_repo(drill=True, plan_md=True, approve=True):
    """(root, finish) for the approved refunds fixture with GOOD (+ a drill-down) in explainer.md; no npx on PATH."""
    import os
    import tempfile
    from nio import plan
    run = good(extra=DRILL if drill else "")
    root = run.root
    d = root / ".nio/specs/checkout-refunds"
    if plan_md:
        (d / "plan.md").write_text("# plan\n")
    (d / "quickstart.md").write_text("---\nid: QS\n---\n\n# Quickstart\n\nbody\n")
    (d / "explainer-drill-1.svg").write_text("<svg>drill</svg>")
    if approve:
        plan.approved = lambda root, slug: (True, "ok")  # TC fixture stand-in for the plan jury
    empty = tempfile.mkdtemp()  # no npx: rendering is T-6's, finish must still work

    def finish():
        assert hasattr(explain, "finish"), "nio.explain.finish missing"
        old = os.environ["PATH"]
        os.environ["PATH"] = empty
        try:
            return explain.finish(root, ".nio/specs/checkout-refunds/explainer.md")
        finally:
            os.environ["PATH"] = old
    return root, finish


def raises(fn, text):
    try:
        fn()
    except ValueError as e:
        assert text in str(e), (text, str(e))
        return
    raise AssertionError("no ValueError: " + text)


def test_ct5_refusals():
    from nio import plan
    keep = plan.approved
    try:
        root, fin = fin_repo(plan_md=False, approve=False)
        ex = root / ".nio/specs/checkout-refunds/explainer.md"
        raises(fin, "the plan jury comes first")
        root, fin = fin_repo(approve=False)
        raises(fin, "the plan jury comes first")
    finally:
        plan.approved = keep


def test_ac33_drill_title_separators():
    from nio import plan
    keep = plan.approved
    try:
        global DRILL
        old = DRILL
        DRILL = old.replace("Drill-down: one", "Drill-down: Retries; backoff, x")
        try:
            root, fin = fin_repo()
        finally:
            DRILL = old
        fin()
        assert fin()[-1].startswith("finished:")
    finally:
        plan.approved = keep


def test_ac33_dropped_drill_down():
    # TC-43
    from nio import plan
    keep = plan.approved
    try:
        root, fin = fin_repo()
        fin()
        d = root / ".nio/specs/checkout-refunds"
        ex = d / "explainer.md"
        t = ex.read_text()
        t = t[:t.index("## Drill-down: one")]
        t = t.replace("(images: ", "(images: explainer-flow-uj-2.svg, ") if "(images: " in t else t + "(images: explainer-flow-uj-2.svg)\n"
        ex.write_text(t)
        (d / "explainer-flow-uj-2.svg").write_text("<svg>uj2</svg>")
        names = ["explainer.md", "quickstart.md", "explainer-drill-1.svg", "explainer-flow-uj-2.svg"]
        before = {n: (d / n).read_bytes() for n in names}
        raises(fin, "drill-down sections missing: Drill-down: one")
        assert before == {n: (d / n).read_bytes() for n in names}
    finally:
        plan.approved = keep


def test_ct5_hashes_and_warning():
    from nio import implement, plan
    keep = plan.approved
    try:
        root, fin = fin_repo()
        d = root / ".nio/specs/checkout-refunds"
        (d / "explainer-flow-uj-2.svg").write_text("x")
        (d / "notes.svg").write_text("n")
        (root / ".nio/README.md").write_text("r")
        ex = d / "explainer.md"
        ex.write_text(ex.read_text() + "(images: explainer-flow-uj-2.svg, explainer-drill-1.svg, ../../README.md)\n")
        out = fin()
        t = ex.read_text()
        for f in ("spec.md", "plan.md", "contracts.md"):
            assert f"(source: .nio/specs/checkout-refunds/{f}@{implement.digest(root, '.nio/specs/checkout-refunds/' + f)[:12]})" in t, (f, t)
        import re
        assert re.search(r"\(diagrams: [0-9a-f]{12}\)", t), t
        assert not (d / "explainer-flow-uj-2.svg").exists()
        assert (d / "explainer-drill-1.svg").exists() and (d / "notes.svg").exists() and (root / ".nio/README.md").exists()
        assert any("../../README.md" in l and l.startswith("warning:") for l in out), out
        assert out[-1].startswith("finished: "), out
    finally:
        plan.approved = keep


def test_uj4_marker_once():
    # TC-47
    from nio import plan
    keep = plan.approved
    try:
        root, fin = fin_repo()
        ex = root / ".nio/specs/checkout-refunds/explainer.md"
        fin()
        fin()
        assert "## Drill-down: one\n" in ex.read_text() and "earlier plan" not in ex.read_text()
        sp = root / ".nio/specs/checkout-refunds/spec.md"
        sp.write_text(sp.read_text() + "\nchanged\n")
        fin()
        fin()
        t = ex.read_text()
        assert t.count("(written for an earlier plan)") == 1, t
        assert "## Drill-down: one (written for an earlier plan)" in t
    finally:
        plan.approved = keep


def test_ac4_read_first_once():
    # TC-4, plus one os.replace per file
    import os
    from nio import plan
    keep, real = plan.approved, os.replace
    calls = []
    try:
        root, fin = fin_repo()
        os.replace = lambda a, b: (calls.append(Path(b).name), real(a, b))[1]
        fin()
        assert calls.count("explainer.md") == 1, calls
        fin()
        q = (root / ".nio/specs/checkout-refunds/quickstart.md").read_text()
        line = "Read first: [explainer.md](explainer.md)"
        assert q.count(line) == 1, q
        assert q.split("---\n", 2)[2].lstrip("\n").splitlines()[0] == line, q
    finally:
        os.replace = real
        plan.approved = keep


def test_ct5_comma_drill_title():
    # T-25: a drill-down heading holding ", " must not lock finishing
    from nio import plan
    keep = plan.approved
    try:
        root, fin = fin_repo()
        ex = root / ".nio/specs/checkout-refunds/explainer.md"
        ex.write_text(ex.read_text() + "\n## Drill-down: Retries, backoff\n\ntext\n")
        fin()
        assert fin()[-1].startswith("finished:")
    finally:
        plan.approved = keep


def test_ct5_bad_quickstart_writes_nothing():
    # T-26: a quickstart that can't be edited stops finish before any write or delete
    from nio import plan
    keep = plan.approved
    try:
        root, fin = fin_repo()
        d = root / ".nio/specs/checkout-refunds"
        ex = d / "explainer.md"
        ex.write_text("(images: explainer-old.svg)\n" + ex.read_text())
        (d / "explainer-old.svg").write_text("<svg>old</svg>")
        (d / "quickstart.md").write_text("---\nid: QS\n\n# Quickstart\n")
        names = ["explainer.md", "quickstart.md", "explainer-old.svg"]
        before = {n: (d / n).read_bytes() for n in names}
        try:
            fin()
            assert False, "finish should refuse"
        except ValueError:
            pass
        assert before == {n: (d / n).read_bytes() for n in names}
    finally:
        plan.approved = keep


def test_ct5_keeps_author_lines():
    # T-27: step 6 strips only what an earlier finish wrote
    from nio import plan
    keep = plan.approved
    try:
        root, fin = fin_repo()
        ex = root / ".nio/specs/checkout-refunds/explainer.md"
        mine = ["> Note: refunds are capped", "![logo](logo.png)"]
        ex.write_text(ex.read_text() + "\n" + "\n".join(mine) + "\n\n> Broken diagram: old\n![x](explainer--x.svg)\n> Images not rendered: gone.\n")
        fin()
        t = ex.read_text()
        assert all(m in t for m in mine), t
        assert "Broken diagram: old" not in t and "explainer--x.svg" not in t and "gone." not in t, t
    finally:
        plan.approved = keep


def npx_bin():
    """A PATH dir with a fake npx: copies -i to -o; FAKE_NPX=hang sleeps 5 s first."""
    import stat
    import tempfile
    b = Path(tempfile.mkdtemp())
    n = b / "npx"
    n.write_text('#!/bin/sh\n[ "$FAKE_NPX" = hang ] && sleep 5\nwhile [ $# -gt 0 ]; do case $1 in -i) i=$2;; -o) o=$2;; esac; shift; done\ncat "$i" > "$o"\n')
    n.chmod(n.stat().st_mode | stat.S_IEXEC)
    return b


def fin_at(root, path, bin, hang=False):
    """explain.finish in-process with PATH = bin (+ the system PATH when bin holds npx)."""
    import os
    old = dict(os.environ)
    os.environ["PATH"] = str(bin) + ("" if not (Path(bin) / "npx").exists() else os.pathsep + old["PATH"])
    os.environ.pop("FAKE_NPX", None)
    if hang:
        os.environ["FAKE_NPX"] = "hang"
    try:
        return explain.finish(root, path)
    finally:
        os.environ.clear()
        os.environ.update(old)


EX = ".nio/specs/checkout-refunds/explainer.md"


def test_ac33_safe_delete():
    # TC-10
    from nio import plan
    keep = plan.approved
    try:
        root, _ = fin_repo()
        d = root / ".nio/specs/checkout-refunds"
        for n, b in (("explainer-flow-uj-2.svg", "uj2"), ("notes.svg", "n"), ("other.svg", "o")):
            (d / n).write_text(b)
        (root / ".nio/README.md").write_text("r")
        ex = d / "explainer.md"
        ex.write_text(ex.read_text() + "\n(drill-downs: Drill-down: one)\n(images: explainer-flow-uj-2.svg, explainer-drill-1.svg, other.svg, ../../README.md)\n")
        names = ["explainer-drill-1.svg", "notes.svg", "other.svg"]
        before = {n: (d / n).read_bytes() for n in names}
        out = fin_at(root, EX, npx_bin())
        assert not (d / "explainer-flow-uj-2.svg").exists()
        assert before == {n: (d / n).read_bytes() for n in names}
        assert (root / ".nio/README.md").read_text() == "r"
        img = next(l for l in ex.read_text().splitlines() if l.startswith("(images: "))
        assert "explainer-drill-1.svg" in img, img
        assert "explainer--component-map.svg" in img and (d / "explainer--component-map.svg").is_file(), (img, out)
        assert "warning: ignored other.svg: not this explainer's own image" in out, out
        assert "warning: ignored ../../README.md: not this explainer's own image" in out, out
        assert [l for l in out if l.startswith("deleted:")] == ["deleted: explainer-flow-uj-2.svg"], out
    finally:
        plan.approved = keep


def test_ac29_skill_text():
    import re
    import test_talk
    root = Path(__file__).resolve().parent.parent
    text = (root / "skills/explain/SKILL.md").read_text()
    sec = lambda h: next((b for t, b in re.findall(r"^#+ ([^\n]*)\n(.*?)(?=^#|\Z)", text, re.M | re.S) if h in t), None)
    assert sec("Mermaid cheat-sheet") is not None
    rules = sec("Diagram rules")
    assert rules and "one question" in rules and "20" in rules
    assert re.search(r"^Credit:.*https://", text, re.M)
    assert not [p for p in test_talk.problems(root) if "explain" in p]


def test_nfr2_no_tools():
    # TC-38
    import tempfile
    from nio import plan
    keep = plan.approved
    try:
        root, _ = fin_repo(drill=False)
        d = root / ".nio/specs/checkout-refunds"
        (d / "explainer-drill-1.svg").unlink()
        fin_at(root, EX, tempfile.mkdtemp())
        assert "> Images not rendered: Node is not installed." in (d / "explainer.md").read_text()
        assert not list(root.rglob("*.svg")), list(root.rglob("*.svg"))
        import os
        old = os.environ["PATH"]
        os.environ["PATH"] = tempfile.mkdtemp()
        try:
            errors, _ = explain.check(root, "checkout-refunds")
        finally:
            os.environ["PATH"] = old
        assert errors == [], errors
    finally:
        plan.approved = keep


def test_ac33_rerun_after_partial():
    # TC-45
    from nio import plan
    keep, t = plan.approved, explain.TIMEOUT
    try:
        root, _ = fin_repo(drill=False)
        d = root / ".nio/specs/checkout-refunds"
        (d / "explainer-drill-1.svg").unlink()
        ex = d / "explainer.md"
        ex.write_text(ex.read_text() + "\n(images: explainer-x.svg)\n")
        explain.TIMEOUT = 1
        b = npx_bin()
        out = fin_at(root, EX, b, hang=True)
        assert not [l for l in out if l.startswith("deleted:")], out
        assert "> Images not rendered: the renderer could not be fetched." in ex.read_text(), ex.read_text()
        explain.TIMEOUT = t
        out = fin_at(root, EX, b)
        assert not [l for l in out if l.startswith("deleted:")], out
        text = ex.read_text()
        assert "Images not rendered" not in text, text
        import re
        links = re.findall(r"^!\[[^\]]*\]\(([^)]+)\)$", text, re.M)
        assert sorted(links) == ["explainer--build-order.svg", "explainer--component-map.svg"], text
        assert all((d / l).is_file() for l in links), links
    finally:
        explain.TIMEOUT = t
        plan.approved = keep


def test_ac33_unique_names():
    # TC-46
    from nio import plan
    from test_records import repo
    root = repo()
    r = root / ".nio/research"
    r.mkdir(parents=True, exist_ok=True)
    sec = lambda t, n: f"## {t}\n\n```mermaid\nflowchart LR\n{n}1 --> {n}2\n```\n\nWalk {n}.\n\n"
    (r / "2026-11-08-x-explainer.md").write_text(sec("Overview", "A") + sec("2 Overview", "B"))
    (r / "2026-11-08-x-explainer-2.md").write_text(sec("Overview", "C"))
    b = npx_bin()
    fin_at(root, ".nio/research/2026-11-08-x-explainer-2.md", b)
    s2 = r / "2026-11-08-x-explainer-2--overview.svg"
    assert s2.is_file(), list(r.iterdir())
    before = s2.read_bytes()
    fin_at(root, ".nio/research/2026-11-08-x-explainer.md", b)
    for n in ("2026-11-08-x-explainer--overview.svg", "2026-11-08-x-explainer--2-overview.svg"):
        assert (r / n).is_file(), (n, list(r.iterdir()))
    assert s2.read_bytes() == before
    keep = plan.approved
    try:
        root, _ = fin_repo(drill=False, )
        d = root / ".nio/specs/checkout-refunds"
        ex = d / "explainer.md"
        ex.write_text(ex.read_text() + "\n" + sec("Calls", "D") + sec("calls!", "E"))
        fin_at(root, EX, b)
        assert (d / "explainer--calls.svg").is_file() and (d / "explainer--calls-2.svg").is_file(), list(d.iterdir())
        assert (d / "explainer--calls.svg").read_bytes() != (d / "explainer--calls-2.svg").read_bytes()
    finally:
        plan.approved = keep


def status(root):
    import subprocess
    import sys
    code = "import sys; sys.argv = ['nio', 'status']; from nio.cli import main; main()"
    r = subprocess.run([sys.executable, "-c", code], cwd=root, capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


STALE = "stale: explainer.md (spec, plan or contracts changed)"
HINT = "  in .nio/specs/checkout-refunds/: re-run @nio:explain"


def stale_repo(edit="plan.md"):
    """(root, finish) with the explainer finished, then one source file appended to."""
    root, fin = fin_repo()
    fin()
    f = root / ".nio/specs/checkout-refunds" / edit
    f.write_text(f.read_text() + "\nchanged\n")
    return root, fin


def test_ac21_stale():
    # TC-28
    from nio import plan
    keep = plan.approved
    try:
        root, _ = stale_repo()
        code, out = status(root)
        assert code == 0, out
        assert STALE + "\n" + HINT in out, out
    finally:
        plan.approved = keep


def test_ac22_rerun_clears():
    # TC-29
    from nio import implement, plan
    keep = plan.approved
    try:
        root, fin = stale_repo()
        assert STALE in status(root)[1]
        ex = root / ".nio/specs/checkout-refunds/explainer.md"
        ex.write_text(ex.read_text().replace("```\n\nMap walk.", '    b --> c["CT-2 retry"]\n```\n\nMap walk.', 1))
        fin()
        code, out = status(root)
        assert "stale: explainer.md" not in out, out
        h = implement.digest(root, ".nio/specs/checkout-refunds/plan.md")[:12]
        assert f"(source: .nio/specs/checkout-refunds/plan.md@{h})" in ex.read_text(), ex.read_text()
    finally:
        plan.approved = keep


def test_ac31_sources():
    # TC-31
    from nio import plan
    keep = plan.approved
    try:
        def fresh():
            r, fin = fin_repo()
            fin()
            return r, r / ".nio/specs/checkout-refunds"
        root, d = fresh()
        for n in ("quickstart.md", "tests.md"):
            (d / n).write_text((d / n).read_text() + "\nx\n" if (d / n).exists() else "x\n")
            assert STALE not in status(root)[1], n
        (d / "contracts.md").write_text((d / "contracts.md").read_text() + "\nx\n")
        assert STALE in status(root)[1]
        root, d = fresh()
        (d / "spec.md").write_text((d / "spec.md").read_text() + "\nx\n")
        assert STALE in status(root)[1]
        root, d = fresh()
        (d / "contracts.md").unlink()
        assert STALE in status(root)[1]
    finally:
        plan.approved = keep


def test_uj1_outgrown():
    # TC-40
    from nio import plan
    keep = plan.approved
    try:
        root, _ = stale_repo()
        ex = root / ".nio/specs/checkout-refunds/explainer.md"
        before = ex.read_bytes()
        for _ in range(2):
            assert STALE in status(root)[1]
        assert ex.read_bytes() == before
    finally:
        plan.approved = keep


def test_ac21_finish_alone_keeps_stale():
    # TC-44
    from nio import plan
    keep = plan.approved
    try:
        root, fin = stale_repo()
        ex = root / ".nio/specs/checkout-refunds/explainer.md"
        src = lambda: [l for l in ex.read_text().splitlines() if "(source:" in l]
        before = src()
        out = fin()
        assert "still stale: no diagram changed since the last finish; redraw the diagrams to clear the stale line" in out, out
        assert src() == before
        assert STALE in status(root)[1]
    finally:
        plan.approved = keep


def cli_in(root, *args, env=None):
    import subprocess
    import sys
    code = f"import sys; sys.argv = ['nio'] + {list(args)!r}; from nio.cli import main; main()"
    r = subprocess.run([sys.executable, "-c", code], cwd=root, capture_output=True, text=True, env=env)
    return r.returncode, r.stdout + r.stderr


def test_ac20_topic_render_only():
    # TC-25
    import os
    from test_records import repo
    root = repo()
    (root / ".nio/research").mkdir(parents=True, exist_ok=True)
    (root / ".nio/research/2026-11-08-hooks-explainer.md").write_text(
        "# Hooks\n\n## Overview\n\n```mermaid\nflowchart LR\nA --> B\n```\n\nOne walk.\n")
    env = dict(os.environ, PATH=str(npx_bin()) + os.pathsep + os.environ["PATH"])
    code, out = cli_in(root, "check", "explainer", ".nio/research/2026-11-08-hooks-explainer.md", env=env)
    assert code == 0, out
    assert "core diagram" not in out and "CT-" not in out, out


def test_uj3_topic_not_plan():
    # TC-42
    from test_flow import S, effort
    root = effort("tasking")
    (root / ".nio/research").mkdir(parents=True, exist_ok=True)
    (root / ".nio/research/2026-11-08-refunds-explainer.md").write_text(
        "GOOD\n(source: .nio/specs/" + S + "/plan.md@000000000000)\n")
    assert not (root / ".nio/specs" / S / "explainer.md").exists()
    code, out = cli_in(root, "flow", "next", S)
    assert "suggest:" in out, out
    code, out = cli_in(root, "check", "explainer", S)
    assert code == 1 and "explainer missing" in out, (code, out)
    code, out = cli_in(root, "status")
    assert "stale" not in out, out


def test_ct6_topic():
    # TC-23's CLI calls, TC-26/27 name rules
    import datetime
    from test_records import repo
    root = repo()
    day = datetime.date.today().isoformat()
    code, out = cli_in(root, "explain", "topic", "../Auth / Tokens!")
    assert code == 0 and out.strip() == f"new: .nio/research/{day}-auth-tokens-explainer.md", (code, out)
    code, out = cli_in(root, "explain", "topic", "//")
    assert code == 1 and 'error: the topic "//" gives an empty file name' in out, (code, out)
    r = root / ".nio/research"
    r.mkdir(parents=True, exist_ok=True)
    (r / f"{day}-auth-tokens-explainer.md").write_text("# Auth tokens\n\n(topic: Auth tokens)\n")
    assert explain.topic(root, "Auth tokens") == f"continue: .nio/research/{day}-auth-tokens-explainer.md"
    assert explain.topic(root, "auth/tokens") == f"new: .nio/research/{day}-auth-tokens-explainer-2.md"


def test_finish_rerun_is_byte_stable():
    # TC-26's "earlier sections are byte-equal": a rerun without a renderer adds no blank lines
    import tempfile
    from test_records import repo
    root = repo()
    f = root / ".nio/research/2026-01-01-git-hooks-explainer.md"
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text("# git hooks\n\n(topic: git hooks)\n\n## Overview\n\n```mermaid\nflowchart LR\n  a --> b\n```\n\nText.\n")
    empty = tempfile.mkdtemp()
    fin_at(root, f, empty)
    once = f.read_text()
    fin_at(root, f, empty)
    assert f.read_text() == once, (once, f.read_text())
    assert "Images not rendered" in once


if __name__ == "__main__":
    selfcheck.main([test_finish_rerun_is_byte_stable, test_ac20_topic_render_only, test_uj3_topic_not_plan, test_ct6_topic, test_ac29_skill_text, test_ac33_drill_title_separators, test_ac5_node_cap, test_ac11_missing, test_ac9_broken_block, test_ac5_node_cap_check, test_ac36_walk_limit,
                    test_ac6_passes, test_ac7_missing_contract, test_ac8_missing_build_order, test_uj1_huge_diagram, test_ac10_no_node,
                    test_ct5_refusals, test_ac33_dropped_drill_down, test_ct5_hashes_and_warning, test_uj4_marker_once, test_ac4_read_first_once,
                    test_ac33_safe_delete, test_nfr2_no_tools, test_ac33_rerun_after_partial, test_ac33_unique_names, test_ct5_comma_drill_title, test_ct5_bad_quickstart_writes_nothing, test_ct5_keeps_author_lines,
                    test_ac21_stale, test_ac22_rerun_clears, test_ac31_sources, test_uj1_outgrown, test_ac21_finish_alone_keeps_stale])
