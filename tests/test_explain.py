"""Self-check for nio.explain. Run: uv run python tests/test_explain.py"""
try:
    from nio import explain
except ImportError:
    explain = None
import selfcheck


def chain(n):
    return "flowchart LR\n" + " --> ".join(f"n{i}" for i in range(1, n + 1)) + "\n"


def test_ac5_node_cap():
    # T-1 part of TC-5: the node count; the check part lands with T-3
    assert explain is not None and hasattr(explain, "nodes"), "nio.explain.nodes missing"
    assert explain.nodes(chain(21)) == {f"n{i}" for i in range(1, 22)}
    assert len(explain.nodes(chain(20))) == 20
    assert explain.nodes('flowchart TD\nA["x --> y"] --> B(z)\n%% c --> d\nsubgraph S\nB -.-> C\nend\n') == {"A", "B", "C"}


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


if __name__ == "__main__":
    selfcheck.main([test_ac5_node_cap, test_ac11_missing])
