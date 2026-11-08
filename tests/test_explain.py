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
    return run


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


def test_ac8_missing_build_order():
    # TC-13
    c, out = good(build=False)()
    assert c == 1 and "ERROR missing core diagram: build order" in out, (c, out)


def test_uj1_huge_diagram():
    # TC-39
    m = " --> ".join(f"c{i}" for i in range(1, 29))
    c, out = good(cmap_nodes=m + '\nc29["CT-1"] --> c30["CT-2"]')()
    assert c == 1 and "ERROR too many nodes: Component map (30 > 20)" in out, (c, out)


if __name__ == "__main__":
    selfcheck.main([test_ac5_node_cap, test_ac11_missing, test_ac9_broken_block, test_ac5_node_cap_check, test_ac36_walk_limit,
                    test_ac6_passes, test_ac7_missing_contract, test_ac8_missing_build_order, test_uj1_huge_diagram])
