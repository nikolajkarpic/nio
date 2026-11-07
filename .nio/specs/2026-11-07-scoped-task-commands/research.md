# Research: 2026-11-07-scoped-task-commands

Facts the grill looked up instead of asking.

## Grill session 1 (2026-11-07)

- **RF-1** Workers and the orchestrator run whole self-check files at every step: while iterating, at red and at green; the slow part is the test run, not the model. Source: issue #70: "Two runs of `uv run python tests/test_implement.py` took about 116 s and 120 s"
- **RF-2** The self-check scripts take no test names: 8 run every global `test_*` function in definition order, 9 call a fixed list (every `test_*` function they define, in a hand-picked order); `test_records.py`, `test_index.py` and `test_talk.py` also run functions not named `test_*`. Source: tests/test_flow.py:2392: "for name, test in list(globals().items()):\n        if name.startswith(\"test_\"):"
- **RF-3** Red checks only that the command contains the test file's path as a substring, so `uv run python tests/test_x.py test_a` already passes it; the #84 refusals came from `python -c "import test_implement as t; t.test_x()"` commands, written because the scripts take no test names. Source: src/nio/implement.py:527: "if named and not any(f in command for f in named):"
- **RF-4** Whole-file times today on this machine (after #73's in-process CLI), one run each: test_implement.py 56 s, test_evidence.py 94 s, test_flow.py 22 s, test_waves.py 11 s. Source: measured 2026-11-07 with `uv run python tests/test_<f>.py`, wall clock.
- **RF-5** Each TC entry in tests.md names its test function in its `File:` line, and the worker pack carries the task's TC entries whole, so the pack already names the tests to scope to. Source: src/nio/implement.py:190: "+ body(\"Tests\", block(tests, tcs))"
- **RF-6** Evidence reads per-test results only for runners with a summary reader (pytest, unittest); the repo's suite command is an `xargs` pipeline with no known runner, so a failed suite marks every test `failed` and a passing one marks every test `unknown`. Source: src/nio/evidence.py:432: "result = ((\"unknown\" if code_ok else \"failed\") if not fail else"
- **RF-7** The worker pack is written once, at claim, before red runs; red records only a hash of its output. Source: src/nio/implement.py:540: "line = entry(\"red\", tid, command=command, output=flow.sha(out.encode()), runner=name or \"unknown\", frozen=frozen)"
- **RF-8** The per-AC fix tasks in #88 came from `join`, which files one blocker per AC with no passing test; with per-test results, a failure in another file leaves the epic's own tests `passed`, so no AC finding is filed for it. Source: src/nio/evidence.py:541: "if not any(e[\"result\"] == \"passed\" or (e[\"result\"] == \"unknown\" and e[\"line\"]) for e in mine):"
- **RF-9** Green runs exactly the command red recorded and refuses another; only the task closing an epic runs more (the suite or `tests.epic`, per #66). Source: src/nio/implement.py:717: "if command and command != ev[\"command\"]:"
