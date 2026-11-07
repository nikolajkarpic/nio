---
slug: 2026-11-07-scoped-task-commands
retired: []                      # TC IDs removed from this plan; never reused
---
# Tests: scope each task's test command to its own tests

Fixtures: every test is a plain function in a script under `tests/`, run by `uv run python tests/<file>` through CT-1.
Helpers used below:
- Every fixture script below defines its tests as `def test_<name>():` functions and runs them through `selfcheck.main` (a copy of `tests/selfcheck.py` beside it), so its result lines come from real `def` lines.
- `script(tmp, body)`: new in `tests/test_selfcheck.py`; writes `tests/test_demo.py` under the temp folder `tmp`, with
  `body` (test functions) and a `__main__` block calling `selfcheck.main` on its `test_*` functions, and a copy of
  `tests/selfcheck.py` beside it; returns `tmp`. Run it with `subprocess.run([sys.executable, "tests/test_demo.py", *names], cwd=tmp)`.
- `test_flow.effort(stage)`, `test_implement`'s fixture of a claimed split-mode task whose TC names `tests/test_x.py`
  (existing helpers): the tests below write `tests/test_x.py` in the fixture repo as a script that prints given lines
  and exits with a given code.
- `gate_repo()` in `tests/test_evidence.py` (existing): a finished epic E-1; the tests below give it `files=` and `suite=`.

## Acceptance tests

### TC-1 One test name runs only that test (AC-1; integration) [agent]
- File: `tests/test_selfcheck.py:test_ac1_one_name_runs_one_test` (new)
- Covers: CT-1
- Setup: `script(tmp, ...)` with passing tests `test_a`, `test_b`, `test_c`.
- Action: run it with the name `test_b`.
- Assert: exit code 0; stdout lines that start `ok ` are exactly `["ok tests/test_demo.py::test_b"]`; the last line is `ran 1 tests, 0 failed`; no line names `test_a` or `test_c`.

### TC-2 No names runs every test (AC-2; integration) [agent]
- File: `tests/test_selfcheck.py:test_ac2_no_names_runs_all` (new)
- Covers: CT-1
- Setup: the same script as TC-1, with `test_c` raising `AssertionError`.
- Action: run it with no names.
- Assert: one `ok` or `FAIL` line for each of `test_a`, `test_b`, `test_c`, in that order (`ok`, `ok`, `FAIL`); last line `ran 3 tests, 1 failed`.

### TC-3 A raising test prints FAIL, the rest still run, exit non-zero (AC-3; integration) [agent]
- File: `tests/test_selfcheck.py:test_ac3_fail_goes_on` (new)
- Covers: CT-1
- Setup: tests `test_a` raising `RuntimeError("boom")` and `test_b` passing.
- Action: run it with no names.
- Assert: exit code 1; stdout has `FAIL tests/test_demo.py::test_a` before `ok tests/test_demo.py::test_b`; `boom` appears in the output; last line `ran 2 tests, 1 failed`.

### TC-4 Red accepts a command scoped to one test (AC-4; integration) [agent]
- File: `tests/test_implement.py:test_ac4_red_takes_a_scoped_command` (new)
- Covers: CT-3
- Setup: a claimed split-mode task whose TC names `tests/test_x.py`; `tests/test_x.py` prints `FAIL tests/test_x.py::test_new` then `ran 1 tests, 1 failed` and exits 1.
- Action: `nio flow red <slug> T-1 --run "python tests/test_x.py test_new"`.
- Assert: exit code 0, `red: T-1 accepted` printed; the history's last `red` line has `command` equal to that command and `runner` equal to `self-check`.

### TC-5 Red refuses a run of zero tests, whatever its exit code (AC-5; integration) [agent]
- File: `tests/test_implement.py:test_ac5_red_refuses_zero_tests` (new)
- Covers: CT-3, CT-7
- Setup: as TC-4, but `tests/test_x.py` prints `no test named test_typo` then `ran 0 tests, 0 failed`; once with exit 1, once (a fresh claim) with exit 0.
- Action: `nio flow red <slug> T-1 --run "python tests/test_x.py test_typo"` in each case.
- Assert: both exit 1 and print `refused: no tests ran`; each writes a `refused` line whose `cause` is `no tests ran`; no `red` line.

### TC-6 Green of a non-closing task runs only the red command (AC-6; integration) [agent]
- File: `tests/test_implement.py:test_ac6_green_runs_only_the_scoped_command` (new)
- Covers: CT-3
- Setup: an epic of two tasks; T-1 red accepted with `python tests/test_x.py test_new` (the script now exits 0 printing `ok tests/test_x.py::test_new` and `ran 1 tests, 0 failed`); `tests.suite` set to a command that writes a marker file when run.
- Action: `nio flow green <slug> T-1`.
- Assert: (a regression guard: today's code already passes it) exit 0; the `green` line's `command` equals the red command; the `review` line has no `suite` key; the marker file does not exist.

### TC-7 The worker card says to scope, run in the foreground and not re-run first (AC-7; unit) [agent]
- File: `tests/test_agents.py:test_ac7_worker_card_scopes_its_tests` (new)
- Covers: CT-5
- Setup: the shipped card `src/nio/agents/worker.md`, rendered for Claude Code by `agents.sync` into a temp folder.
- Action: read the rendered `nio-worker-strong.md`.
- Assert: it contains each of `scoped to the task's own tests`, `File:`, `in the foreground`, `never polled with sleep`, `before running the tests`, and still contains `try again`.

### TC-8 Red prints the last 20 lines of its output (AC-8; integration) [agent]
- File: `tests/test_implement.py:test_ac8_red_prints_its_tail` (new)
- Covers: CT-3, CT-6
- Setup: as TC-4, with `tests/test_x.py` printing `line 1` … `line 30` before its FAIL and `ran` lines.
- Action: `nio flow red` as in TC-4.
- Assert: the printed lines after `output:` are exactly the script's last 20 output lines, each indented two spaces (so `line 13` is the first, `line 12` is absent); one line of `skills/implement/SKILL.md` contains both `output:` and `code-phase worker`.

### TC-9 One failing test fails only itself in evidence (AC-9; integration) [agent]
- File: `tests/test_evidence.py:test_ac9_evidence_reads_self_check_lines` (new)
- Covers: CT-4
- Setup: `gate_repo` whose tests.md names `tests/test_a.py:test_one`, `tests/test_a.py:test_two` and `tests/test_b.py:test_one`; in `test_a.py`, `test_one` raises and `test_two` passes (it prints `FAIL tests/test_a.py::test_one`, `ok tests/test_a.py::test_two`, `ran 2 tests, 1 failed` and exits 1); in `test_b.py`, `test_one` passes (`ok tests/test_b.py::test_one`); `tests.suite` runs both files and exits non-zero.
- Action: `nio jury evidence s E-1 --run <run>`.
- Assert: in results.json, `tests/test_a.py` `test_one` is `failed`, `tests/test_a.py` `test_two` is `passed`, and `tests/test_b.py` `test_one` is `passed`, though the failing test of the other file has the same name.

### TC-10 A file that crashes before any line records its tests failed (AC-10; integration) [agent]
- File: `tests/test_evidence.py:test_ac10_crashed_file_is_failed` (new)
- Covers: CT-4
- Setup: as TC-9, but `test_a.py` raises at import (prints a traceback, no result line, exits 1).
- Action: `nio jury evidence s E-1 --run <run>`.
- Assert: both `tests/test_a.py` tests are `failed`; `tests/test_b.py` `test_one` is `passed`.

## Misuse tests
### TC-11 Some of the names are typos (UJ-1 misuse; integration) [agent]
- File: `tests/test_selfcheck.py:test_misuse_unknown_name_runs_nothing` (new)
- Covers: CT-1
- Setup: the TC-1 script, with `test_a` writing a marker file when it runs.
- Action: run it with the names `test_a test_typo`.
- Assert: exit code 1; output has `no test named test_typo` and last line `ran 0 tests, 0 failed`; the marker file does not exist.

### TC-12 A self-check suite that crashed fails the epic-closing review (AC-6; integration) [agent]
- File: `tests/test_implement.py:test_review_fails_a_crashed_self_check_suite` (new)
- Covers: CT-3, CT-7
- Setup: an epic whose last task T-1 has red accepted; `tests.suite` prints `ok tests/test_b.py::test_one`, `ran 1 tests, 0 failed`, then a traceback with no result line, and exits 1.
- Action: `nio flow green <slug> T-1`.
- Assert: exit 1; `review: failed` and `the suite exits 1 and names no failing test` printed; the `review` line has `passed` false.

### TC-13 Every self-check script runs through selfcheck.main (AC-2; integration) [agent]
- File: `tests/test_selfcheck.py:test_every_script_uses_selfcheck` (new)
- Covers: CT-2
- Setup: the repo's own `tests/test_*.py` files.
- Action: read each file's text after its `if __name__ == "__main__":` line.
- Assert: every file's block contains `selfcheck.main(`; the failure message names each file that doesn't.
