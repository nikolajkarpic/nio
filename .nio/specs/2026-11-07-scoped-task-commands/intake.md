# Intake

## Human

Goal: one NIO effort that implements GitHub issue #70 (workers wait on whole test files: scope each task's command to its own tests), folding in #84 (red should accept a single-test command and find the file from it) and #88 (one failing test file marks every test failed in evidence; plain-script self-checks should print per-test ok/FAIL lines so results are per test). Read them, and also #77 (the roadmap) and .nio/research/2026-11-06-speedup.md for the numbers.

Lazy and minimal: smallest diff that works. Measure worker wait (red/green time for one task) before and after and put it in the PR.

Delegated (2026-11-07): the human gave the orchestrator standing authority to answer every grill question with the recommended option and approve each gate.

## Source: https://github.com/nikolajkarpic/nio/issues/70

# Workers wait on whole test files: scope each task's command to its own tests

## Problem

Workers take 8–12 minutes per task, and almost none of that is the model. From the transcripts of the last 8 worker runs (all sonnet, effort low or medium):

- **T-1 code phase (split), 8 min:** the model's turns took about 40 s in total. Two runs of `uv run python tests/test_implement.py` took about 116 s and 120 s, and waiting on another test run took a further 3 min.
- **T-45 (single), 12.5 min:** the model's turns took about 1 min in total. Every `test_evidence.py` run, plus `nio flow red`, took about 75 s, and `nio flow green` took over 3 min.

A task's command is always a whole self-check file. The worker runs it while iterating, then red and green each run it again. So every loop costs 1–2 minutes, however small the task.

Lowering the tier or effort won't fix this (that was considered and dropped).

## Proposal

1. **Run only the task's own tests.** Let the self-check scripts take test names (`uv run python tests/test_implement.py test_block_record test_block_handoff`), with no names still meaning the whole file. Tell the worker card to iterate with, and hand off, a command scoped to the tests it wrote or the task's TC-n names. Red and green then run in seconds.
2. **Keep red and green cheap.** #66 already moved the suite to the task that closes an epic, which runs `tests.epic` or the full suite. What's left is to make sure green never runs more than the handed-off command. Also check whether a scoped command makes red's "fails for the right reason" check weaker: a filter that matches no test must not count as red. The `none` patterns in `RUNNERS` may need an equivalent for the self-check scripts.

## Open questions

- Should `nio flow red` refuse a scoped command that selects zero tests? (Probably yes. Otherwise red is vacuous.)
- Should the pack name the test function names, or should the worker choose them?
- Is it worth profiling why one file takes 75–120 s (a git repo set up per case?) as a separate issue?


Comment: Folding in from the speed-up investigation: the code-phase worker re-runs the whole test file at its first step (T-1: 116 s, T-2: 115 s), right after `flow red` has run it and recorded the failure. Put red's output tail in the code-phase pack, and tell the worker card not to re-run before its first edit. In an earlier effort, workers ran test_evidence 122 times (115 min) and spent 37 min polling with until/sleep. The card should say to run the scoped command in the foreground, never with sleep or polling.

## Source: https://github.com/nikolajkarpic/nio/issues/84

# `nio flow red --run` should accept a single-test command without the file path appended

## Problem
The red step requires the command to name the test file, so a command scoped to one test (`... tests/test_x.py test_name`) works only with the file path appended in a specific form. This gets in the way of #70 (scoped worker commands).

## Proposal
Resolve the test file from the command's arguments (first `tests/*.py` token), and fold the fix into #70.

## Source: https://github.com/nikolajkarpic/nio/issues/88

# One failing test file marks every test failed in evidence, and the gate auto-files a fix task per AC

## Problem
In the parallel-waves effort (#59, PR #87), one timing flake in `tests/test_flow.py` made `nio jury evidence` record every test as failed. The conformance reviewer found no passing evidence for any AC and the tool auto-filed nine near-empty fix tasks (J-7..J-15). They could not be retired (#83), so each was landed as a no-change task. About 1h20m lost.

Plain-script self-checks also record each test as `unknown`, so a strict reviewer says "not fixed" until the refuter overrules it.

## Proposal
- Record results per file at least: a failing file fails only its own tests, not the whole suite.
- When the only failures are outside the epic's test files, file one "suite red" fix task, not one per AC.
- Have the self-check scripts print one `ok <name>` / `FAIL <name>` line per test so the runner can parse them (fits #70's per-test names).

The flake itself is fixed by #65's T-6 (`NIO_PERF=1` gate). Refs: #59, #83, #86, #70
