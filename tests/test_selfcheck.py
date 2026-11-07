"""Self-check for the self-check runner. Run: uv run python tests/test_selfcheck.py"""
import subprocess
import sys
import tempfile
from pathlib import Path

import selfcheck

HERE = Path(__file__).resolve().parent


def script(tmp, bodies):
    """Write tests/test_demo.py in tmp; bodies maps a test name to its body."""
    path = Path(tmp) / "tests" / "test_demo.py"
    path.parent.mkdir(parents=True, exist_ok=True)
    src = f"import sys\nsys.path.insert(0, {str(HERE)!r})\nimport selfcheck\n\n"
    for name, body in bodies.items():
        src += f"def {name}():\n    {body}\n\n"
    src += "if __name__ == '__main__':\n    selfcheck.main([" + ", ".join(bodies) + "])\n"
    path.write_text(src)


def run(tmp, *names):
    p = subprocess.run([sys.executable, "tests/test_demo.py", *names], cwd=tmp,
                       capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr, p.stdout.splitlines()


OK = "pass"


def test_ac1_one_name_runs_one_test():
    with tempfile.TemporaryDirectory() as tmp:
        script(tmp, {"test_a": OK, "test_b": OK, "test_c": OK})
        code, out, lines = run(tmp, "test_b")
        assert code == 0, out
        assert [l for l in lines if l.startswith("ok ")] == ["ok tests/test_demo.py::test_b"], out
        assert lines and lines[-1] == "ran 1 tests, 0 failed", out
        assert "test_a" not in out and "test_c" not in out, out
    print("ok")


def test_ac2_no_names_runs_all():
    with tempfile.TemporaryDirectory() as tmp:
        script(tmp, {"test_a": OK, "test_b": OK, "test_c": "raise AssertionError('x')"})
        code, out, lines = run(tmp)
        got = [l.split("::")[1] and l.split()[0] for l in lines if l.startswith(("ok ", "FAIL "))]
        assert got == ["ok", "ok", "FAIL"], out
        assert lines and lines[-1] == "ran 3 tests, 1 failed", out
    print("ok")


def test_ac3_fail_goes_on():
    with tempfile.TemporaryDirectory() as tmp:
        script(tmp, {"test_a": "raise RuntimeError('boom')", "test_b": OK})
        code, out, lines = run(tmp)
        assert code == 1, out
        fail, good = "FAIL tests/test_demo.py::test_a", "ok tests/test_demo.py::test_b"
        assert fail in lines and good in lines and lines.index(fail) < lines.index(good), out
        assert "boom" in out, out
        assert lines[-1] == "ran 2 tests, 1 failed", out
    print("ok")


def test_misuse_unknown_name_runs_nothing():
    with tempfile.TemporaryDirectory() as tmp:
        marker = Path(tmp) / "marker"
        script(tmp, {"test_a": f"open({str(marker)!r}, 'w').close()", "test_b": OK, "test_c": OK})
        code, out, lines = run(tmp, "test_a", "test_typo")
        assert code == 1, out
        assert "no test named test_typo" in out, out
        assert lines and lines[-1] == "ran 0 tests, 0 failed", out
        assert not marker.exists()
    print("ok")


def test_every_script_uses_selfcheck():
    bad = [f.name for f in sorted(HERE.glob("test_*.py"))
           if "selfcheck.main(" not in f.read_text().split('if __name__ == "__main__":')[-1]]
    assert not bad, f"not run through selfcheck.main: {bad}"


if __name__ == "__main__":
    selfcheck.main([f for n, f in list(globals().items()) if n.startswith("test_") and callable(f)])
