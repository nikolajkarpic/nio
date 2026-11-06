---
slug: 2026-11-06-faster-checks
retired: []                      # TC IDs removed from this plan; never reused
---
# Tests: faster checks

Fixtures: every test is a plain function in an existing script under `tests/`, run by `uv run python tests/<file>`, like
the others. Helpers used below:
- `test_flow.repo()` / `test_flow.effort(stage)`: a fixture repo in the per-process temp folder; `test_flow.S` is its slug.
- `suite_dir(files)`: new in `tests/test_implement.py`; a fresh temp folder with `tests/<name>` written from `files`
  (`{"test_a.py": "print('A RAN')\n", ...}`); returns its path. `SUITE` is the `tests.suite` string read from the repo's
  own `.nio/config.json` (the real command, CT-3).
- `gate_repo()`, `start(root)`, `entry()` in `tests/test_evidence.py` (existing): a finished epic E-1 of spec `s`
  whose commits are `T-1: One` then `T-2: Two`. The tests below rewrite its `.nio/config.json` and `quickstart.md` and
  its `tests/` before the commits, through a new keyword `gate_repo(suite=..., quickstart=..., files=..., history=...)`:
  `history` is a list of history lines written to `.nio/specs/s/history.jsonl` before the `T-2: Two` commit.
- A run counter: test files given to evidence fixtures append one line to the file named by the env var `NIO_COUNT`
  (an absolute path outside the copy) each time they run, so a test can count how often a file ran.
- `lens(gate, findings_text)` in `tests/test_jury.py`: writes a lens output for `gate` with valid front matter and
  reasoning and the given `## Findings` text; `jury.parse_lens(path, gate, "s")` reads it.

## Acceptance tests

### TC-1 The flow helper runs the CLI without a new Python process (AC-1; integration) [agent]
- File: `tests/test_flow.py:test_cli_runs_in_process` (new)
- Covers: CT-1
- Setup: `root = effort("planning")`, `flow.start(root, S, by=BY)`; wrap `subprocess.Popen.__init__` to record each argv.
- Action: `test_flow.cli(root, "next", S)`.
- Assert: exit code 0 and `"state: planning"` in the output; no recorded argv starts with `sys.executable`. The time limit itself (under 60 s) is QS-1's measurement.

### TC-2 In-process results equal the subprocess's (AC-2; unit) [agent]
- File: `tests/test_flow.py:test_run_main_matches_subprocess` (new)
- Covers: CT-1
- Setup: `root = effort("planning")`, `flow.start(root, S, by=BY)`.
- Action: for each of `["flow", "next", S]` (exit 0), `["flow", "next", "nosuch"]` (an `error:` exit 1) and `["flow", "park", S]` (argparse exit 2, no reason), call `run_main(root, *args)` and `subprocess.run([sys.executable, "-c", "from nio.cli import main; main()", *args], cwd=root, capture_output=True, text=True)`.
- Assert: for each, `(code, stdout, stderr)` equals `(returncode, stdout, stderr)` exactly.

### TC-3 An in-process call leaves the test process as it found it (AC-3; unit) [agent]
- File: `tests/test_flow.py:test_run_main_restores_process_state` (new)
- Covers: CT-1
- Setup: `root = effort("planning")`, `flow.start(root, S, by=BY)`; note `os.getcwd()`, `dict(os.environ)` and `list(sys.argv)`.
- Action: `run_main(root, "flow", "next", S)`; `run_main(root, "flow", "next", "nosuch")`; then with `flow.record` replaced by a function that sets `os.environ["NIO_LEAK"] = "1"`, calls `os.chdir("/")` and raises `RuntimeError("boom")`, `run_main(root, "flow", "park", S, "x", "--by", BY)` (it takes the flow lock, then fails inside it); restore `flow.record` and run the same `park` again.
- Assert: after each call `os.getcwd()`, `dict(os.environ)` and `sys.argv` equal the noted values; the failing `park` returns code 1 with `RuntimeError: boom` in stderr, after which no `flow.lock` file exists under `root / ".nio/specs" / S`; the second `park` exits 0.

### TC-4 Tests that need their own process still start one (AC-4; integration) [agent]
- File: `tests/test_flow.py:test_isolated_tests_keep_a_subprocess` (new)
- Covers: CT-1
- Setup: none.
- Action: read the source of `test_cli_errors` and `test_nfr2_offline` in tests/test_flow.py and of `test_nfr1_no_model_calls` in tests/test_implement.py.
- Assert: each source holds `subprocess.run(` and none calls `cli(` or `run_main(` (`test_implement` read as a file, not imported, since it imports `test_flow`).

### TC-5 The suite runs its files at once (AC-5; e2e) [agent]
- File: `tests/test_implement.py:test_parallel_suite_takes_about_its_slowest_file` (new)
- Covers: CT-3
- Setup: `suite_dir` with eight files `test_1.py` … `test_8.py`, each `import time; time.sleep(4); print("ok")` (run serially or two at a time they'd take 16 s or more).
- Action: time `uv run python tests/test_1.py` alone in that folder; then time `SUITE` run by `sh -c` in that folder.
- Assert: the suite exits 0, and its wall-clock is at most 1.5 times the single file's.

### TC-6 Every failing file fails the suite, and every file runs (AC-6; e2e) [agent]
- File: `tests/test_implement.py:test_parallel_suite_fails_on_any_file` (new)
- Covers: CT-3
- Setup: `suite_dir` with ten files, in this sort order: `test_a.py` killing itself with `os.kill(os.getpid(), signal.SIGKILL)`; `test_b.py` `assert 1 == 2, "B FAILED"`; `test_c.py` `raise SystemExit("D FAILED")`; `test_d.py` … `test_i.py` each sleeping 1 s and printing `<NAME> RAN`; `test_z.py` (the tenth, started only once a slot frees) printing `Z RAN`.
- Action: run `SUITE` by `sh -c` in that folder, capturing stdout and stderr together.
- Assert: exit code is not 0; the output holds `B FAILED`, `D FAILED`, each `<NAME> RAN` and `Z RAN` (so `xargs` kept starting files after the kill and the failures).

### TC-7 The CLI reads the parallel suite as it read the serial one (AC-7; integration) [agent]
- File: `tests/test_implement.py:test_parallel_suite_reads_as_unknown_runner` (new)
- Covers: CT-3
- Setup: `suite_dir` with `test_ok.py` printing `ok` and `test_bad.py` `assert False, "BAD"`; a config `{"tests": {"suite": SUITE}}`.
- Action: `implement.runner(SUITE)`, `implement.runner('for f in tests/test_*.py; do uv run python "$f" || exit 1; done')` and `implement.suite(folder, cfg)`.
- Assert: both runners are None; the suite result has `code` not 0, `runner` None, `failing` None, `broken` False and `BAD` in `output`.

### TC-8 A journey of test files the passing suite ran is covered, not run (AC-8; integration) [agent]
- File: `tests/test_evidence.py:test_covered_journey_is_not_run_again` (new)
- Covers: CT-5
- Setup: `gate_repo(suite="printf '%s\n' tests/test_*.py | xargs -P8 -I{} sh -c 'python3 {} || exit 1'", files={"tests/test_ok.py": <appends a line to NIO_COUNT, prints ok>})`, no review line in history; `quickstart.md` with auto scenarios: QS-1 one step `python3 tests/test_ok.py`; QS-2 `NIO_E2E=1 python3 tests/test_ok.py`; QS-3 `python3 tests/test_ok.py` then `echo other`; QS-4 `python3 other_ok.py` (a file outside `tests/`, same body). Each expects `contains: ok`.
- Action: `start(root)` with `NIO_COUNT` set.
- Assert: the suite ran in the copy (result `passed`, no `reused` key); QS-1's journey entry has `covered: true`, result `passed` and output starting `covered by the suite run at`; QS-2, QS-3 and QS-4 entries have no `covered` key and result `passed`; `NIO_COUNT` holds 4 lines (the suite once, QS-2, QS-3, QS-4).

### TC-9 Evidence reuses the closing task's passing suite run (AC-9; integration) [agent]
- File: `tests/test_evidence.py:test_review_suite_is_reused` (new)
- Covers: CT-4, CT-5
- Setup: as TC-8 with only QS-1, and `history` holding `{"kind": "review", "evidence": {"task": "T-2", "passed": true, "suite": {"command": <the suite>, "code": 0}}}` (plus the line fields `flow.record` writes) before the `T-2: Two` commit.
- Action: `start(root)` with `NIO_COUNT` set.
- Assert: `results["suite"]` has result `passed`, `reused == {"task": "T-2", "commit": <last>}` and output starting `reused: the review of T-2`; `NIO_COUNT` doesn't exist (nothing ran the file); QS-1 has `covered: true`.

### TC-10 Anything short of FR-7 runs the suite in the copy (AC-10; integration) [agent]
- File: `tests/test_evidence.py:test_review_suite_is_not_reused_unless_it_qualifies` (new)
- Covers: CT-5
- Setup: as TC-9, once per variant: the review line's `suite.code` is 1; its `suite.command` is another command (`python3 tests/test_ok.py`, as `tests.epic` would be); its task is `T-1`; it has `passed: false`; it has no `suite` key.
- Action: `start(root)` with a fresh `NIO_COUNT` for each.
- Assert: for each, `results["suite"]` has no `reused` key and `NIO_COUNT` holds at least one line (the suite ran in the copy).

### TC-11 A failed suite covers no journey (AC-11; integration) [agent]
- File: `tests/test_evidence.py:test_failed_suite_covers_no_journey` (new)
- Covers: CT-5
- Setup: as TC-8 with only QS-1, plus `tests/test_bad.py` with `assert False`; no review line.
- Action: `start(root)` with `NIO_COUNT` set.
- Assert: the suite result is `failed`; QS-1's entry has no `covered` key; `NIO_COUNT` holds 2 lines (the suite's run of `test_ok.py` and the journey's).

### TC-12 `none` slips are read as no findings (AC-12; unit) [agent]
- File: `tests/test_jury.py:test_none_slips_mean_no_findings` (new)
- Covers: CT-6
- Setup: `lens("spec", t)` for each `t` in `none`, `None`, `None.`, `NONE!`.
- Action: `jury.parse_lens(path, "spec", "s")`.
- Assert: errors `[]` and findings `[]` for each.

### TC-13 Field labels in another case are read (AC-13; unit) [agent]
- File: `tests/test_jury.py:test_field_labels_in_any_case` (new)
- Covers: CT-6
- Setup: an implementation-gate finding written twice: once with every label lower case (`- cites: AC-1`, `- kind: gap`, `- severity: major`, `- evidence: observed`, `- quote: "x"`, `- situation: s`, `- fix: f`, `- gap: missing`, `- where: app.py`), once with `- Gap: missing`, `- WHERE: app.py`, `- Fix: f`, `- Severity: major`.
- Action: `jury.parse_lens` of each at gate `implementation-E-1`.
- Assert: both have no errors and their one finding is equal.

### TC-14 Truly malformed output stays invalid (AC-14; unit) [agent]
- File: `tests/test_jury.py:test_malformed_output_stays_invalid` (new)
- Covers: CT-6
- Setup: `lens("spec", t)` for `t` in `None, but see F1`, `none yet`, `none?`; and an implementation-gate finding without `- gap:` and one without `- where:`; and a spec-gate finding without `gap` or `where`.
- Action: `jury.parse_lens` of each.
- Assert: each of the first five has at least one error; the spec-gate finding without `gap` and `where` has none.

### TC-15 The template shows the implementation gate's lines (AC-15; unit) [agent]
- File: `tests/test_jury.py:test_template_shows_gap_and_where` (new)
- Covers: CT-7
- Setup: `text = resources.files("nio").joinpath("templates/lens-output.md").read_text()` (what `nio jury template` prints).
- Action: write `text` with `subject: s` as a spec-gate lens output and parse it with `jury.parse_lens(path, "spec", "s")`.
- Assert: `text` holds a line starting `- gap:` and one starting `- where:`, each with `implementation gate only`; the parse has no errors.

### TC-16 A fix-check round reuses the fix task's review (AC-16; integration) [agent]
- File: `tests/test_evidence.py:test_fix_check_round_reuses_the_fix_review` (new)
- Covers: CT-4, CT-5
- Setup: as TC-9, then a third commit `T-3: Fix one` (a fix task) whose history holds a later review line for `T-3` with the suite's command and code 0; a run `R-1` collected before the fix.
- Action: `start(root, "R-2")` with `NIO_COUNT` set.
- Assert: `results["suite"]["reused"] == {"task": "T-3", "commit": <the T-3 commit>}`; `NIO_COUNT` doesn't exist; QS-1 has `covered: true`.

### TC-20 The closing task's review records the suite it ran (AC-9; integration) [agent]
- File: `tests/test_implement.py:test_closing_review_records_its_suite` (new)
- Covers: CT-4
- Setup: `impl()` with one epic of two tasks in direct mode (as the existing epic-close tests build it), its suite the fixture's `tests.suite`.
- Action: for each task in turn: claim, write the code, `nio flow green` with `--run` the task's test; read each task's `review` history line.
- Assert: the first task's review line has no `suite` key; the second's (it closes the epic) holds `suite == {"command": <tests.suite>, "code": 0}`.

## Misuse tests

### TC-17 A failure in the last file isn't lost among parallel files (UJ-1 misuse; e2e) [agent]
- File: `tests/test_implement.py:test_parallel_suite_fails_when_only_the_last_file_fails` (new)
- Covers: CT-3
- Setup: `suite_dir` with seven passing files `test_1.py` … `test_7.py` and `test_z.py` with `assert False, "LAST"`.
- Action: run `SUITE` by `sh -c` in that folder.
- Assert: exit code is not 0 and `LAST` is in the output.

### TC-18 A review of an older commit is not reused (UJ-2 misuse; integration) [agent]
- File: `tests/test_evidence.py:test_older_review_is_not_reused` (new)
- Covers: CT-5
- Setup: as TC-9, with `T-3` a third task of E-1 in the fixture's `tasks.md`; then a commit `T-3: Three` changing `a.py` whose history adds T-3's `task_done` line but no review line (the last review line is still T-2's).
- Action: `start(root)` with `NIO_COUNT` set.
- Assert: `results["suite"]` has no `reused` key and `NIO_COUNT` holds at least one line.

### TC-19 `none` with findings after it is invalid (UJ-3 misuse; unit) [agent]
- File: `tests/test_jury.py:test_none_with_findings_is_invalid` (new)
- Covers: CT-6
- Setup: `lens("spec", "None.\n\n### F1 x\n<a complete spec-gate finding>")`.
- Action: `jury.parse_lens(path, "spec", "s")`.
- Assert: the errors include one naming `none and findings`.
