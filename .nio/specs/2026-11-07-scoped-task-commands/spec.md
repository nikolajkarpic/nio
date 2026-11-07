---
slug: 2026-11-07-scoped-task-commands
route: full
epic: ""                         # "<epic slug>/R-<n>" when this is a slice of an epic
risk: []                         # auth | pii | money | external-input | data-deletion | migration | multi-party | public-api
retired: [OP-1, OP-2, OP-3, OP-4, OP-5, OP-6, OP-7]                      # IDs removed from this spec; never reused
---
<!-- Spec template. WHAT and WHY only, never HOW. Every item ends with its provenance: [human] (the grill
confirmed it), [research: RF-n] (a finding in research.md) or [default] (your proposal; the grill must confirm it).
IDs are permanent: number new items after the highest ever used, never renumber, list removed IDs in `retired`.
Remove a section that doesn't apply; never write N/A. `nio check spec 2026-11-07-scoped-task-commands` checks all of this. -->
# Scope each task's test command to its own tests

## Summary
Workers spend 8–12 minutes per task waiting on whole self-check files: every iteration, red and green each run a
whole file (75–120 s in #70, before the in-process CLI; 11–94 s today, RF-4). This effort lets a task's command name only its own tests, has red accept such a command and
refuse one that runs no test, and makes the self-checks print one result line per test so evidence records results per
test instead of failing every test when one file fails. It implements #70 and folds in #84 and #88, as the smallest
change that works. [human]

## Actors and journeys
- **A-1 Worker**: the model agent that writes a task's code and tests and hands off a command; wants fast feedback loops; follows its card literally. [research: RF-1]
- **A-2 Orchestrator**: runs `nio flow red` and `nio flow green` for split-mode tasks and the implementation jury; wants red and green to be cheap and evidence to be honest per test. [research: RF-6]

**UJ-1 Scoped task loop** (A-1) [research: RF-9]
1. The code-phase worker reads red's output tail, which red printed and the orchestrator passed on, and makes its first edit without re-running the tests.
2. It runs the command scoped to its own tests in the foreground until they pass.
3. It hands off the scoped command; green runs that command and nothing more (unless the task closes an epic).
- Misuse: scopes to a test name that does not exist, so red would pass vacuously; polls a background run with sleep.
- Evidence: #70 transcripts (T-1, T-45), #70 comment (122 runs of test_evidence, 37 min polling).

**UJ-2 Evidence after one failing file** (A-2) [research: RF-8]
1. The jury evidence run executes the suite; one file fails.
2. Evidence marks failed only the tests that printed FAIL, and passed those that printed ok.
- Misuse: a crashing file prints no lines; its tests must not read as passed.
- Evidence: #88 (parallel-waves, nine fix tasks J-7..J-15, about 1h20m lost).

## User stories

### US-1 Run only a task's own tests (P1) [human]
- **Why this priority:** it removes the 1–2 minutes each worker loop, red and green spend on whole files, the main cost named in #70.
- **Independent test:** run a self-check script with one test name and see only that test run; run it with none and see the whole file run.

- **AC-1** (FR-1, FR-2) Given a self-check script with several tests, when it is run with one test name, then only that test runs and the output has exactly one `ok <file>::<name>` line and the line `ran 1 tests, 0 failed`. [human]
  Observable: exit code 0, one ok line naming that test, no line for any other test. Level: integration.
- **AC-2** (FR-1, FR-2) Given the same script, when it is run with no test names, then every test runs and prints an ok or FAIL line. [human]
  Observable: one ok/FAIL line per test function in the file. Level: integration.
- **AC-3** (FR-2) Given a test that raises, when the script runs, then it prints `FAIL <file>::<name>`, runs the remaining tests, and exits non-zero. [human]
  Observable: the FAIL line and a non-zero exit code. Level: integration.
- **AC-4** (FR-3) Given a task whose test file is `tests/test_x.py`, when `nio flow red` runs `uv run python tests/test_x.py test_new` and that test fails, then red is accepted. [human]
  Observable: a `red` line in history with that command. Level: integration.
- **AC-5** (FR-1, FR-4) Given a scoped command where one or all of its test names match no test, when `nio flow red` runs it, then red is refused as "no tests ran". [agent]
  Observable: a `refused` line whose reason says no tests ran. Level: integration.
- **AC-6** (FR-5) Given a non-closing task handed off with a scoped command, when `nio flow green` runs, then it runs that command and no other test command. [human]
  Observable: the green and review lines record only the handed-off command. Level: integration.

### US-2 Workers iterate fast and quietly (P1) [human]
- **Why this priority:** without the card change the scoped command exists but workers keep running whole files and polling (122 runs, 37 min of polling in one effort).
- **Independent test:** render the worker card and read its instructions; accept a red and read the tail it prints.

- **AC-7** (FR-6) Given the worker card, when it is rendered, then it tells the worker to iterate with and hand off a command scoped to its own tests, run it in the foreground, never poll a test run with sleep, and not re-run before its first edit. [human]
  Observable: the rendered card contains each of those instructions. Level: unit.
- **AC-8** (FR-7) Given a task whose red is accepted, when `nio flow red` prints its result, then it prints the last 20 lines of the red run's output, and the implement skill tells the orchestrator to give them to the code-phase worker. [agent]
  Observable: red's printed lines end with the last 20 lines of the command's output; the skill text says to pass them on. Level: integration.

### US-3 Evidence per test, not per suite (P2) [human]
- **Why this priority:** a single failing file cost about 1h20m in #88, but it hits at the jury, not on every task.
- **Independent test:** run jury evidence on a suite where one file fails and read the per-test results.

- **AC-9** (FR-8) Given a suite where one self-check file fails one test, when `nio jury evidence` runs, then that test is `failed`, the tests that printed ok are `passed`, and no test of another file is `failed`. [human]
  Observable: the results JSON per test. Level: integration.
- **AC-10** (FR-8) Given a self-check file that crashes before printing any result line, when evidence runs, then its tests are recorded as `failed`. [agent]
  Observable: each of that file's tests has result `failed`. Level: integration.

## Functional requirements
- **FR-1** WHEN a self-check script is given test names THE SYSTEM SHALL run only those tests, and with no names run every test in the file; given a name the file does not define, it runs no test, prints `ran 0 tests, 0 failed` and exits non-zero. [human]
- **FR-2** THE SYSTEM SHALL print one `ok <file>::<name>` or `FAIL <file>::<name>` line per test a self-check script runs, `<file>` being the script's path relative to the working directory, then one last line `ran <n> tests, <m> failed`. [human]
- **FR-3** WHEN `nio flow red` gets a command that names the task's test file followed by test names THE SYSTEM SHALL treat it as naming that test file. [research: RF-3]
- **FR-4** IF a red command's output ends its run with `ran 0 tests` THEN THE SYSTEM SHALL refuse red with the reason "no tests ran", whatever the exit code. [agent]
- **FR-5** WHEN a task that does not close an epic goes green THE SYSTEM SHALL run only its handed-off command. [human]
- **FR-6** THE SYSTEM SHALL tell the worker, in its card, to iterate with and hand off a command scoped to its own tests (the test names its pack's TC entries give in their `File:` lines), to run it in the foreground without polling it with sleep (the short wait on `try again` stays), and not to re-run the tests before its first edit. [human]
- **FR-7** WHEN red is accepted THE SYSTEM SHALL print the last 20 lines of its output, for the orchestrator to hand to the code-phase worker with the pack. [agent]
- **FR-8** WHEN jury evidence reads a suite run whose output has self-check lines THE SYSTEM SHALL record a test `passed` when an `ok` line names its file and name, `failed` when a `FAIL` line does, and, with no line for it, `failed` when the suite exits non-zero, so a failing file fails only its own failing tests. [human]

## Rules
### Decision table: red outcome
Rows are read top to bottom; the first that matches decides. "none" is a `ran 0 tests` line (FR-4); "some" is any other output, including one with no `ran` line (a runner red can't read, as today).
| Tests run (none, some) | Exit code (zero, non-zero) | → outcome | Src |
| --- | --- | --- | --- |
| none | - | → refused: no tests ran | [agent] |
| some | zero | → refused: the test passes before the code exists | [research: RF-3] |
| some | non-zero | → accepted | [research: RF-3] |

## Non-functional requirements
- **NFR-1** THE SYSTEM SHALL let red and green of a task scoped to one test of `tests/test_implement.py` each finish in under 15 s, one run each on the machine of RF-4, where the whole file took 56 s. [agent]

## Success criteria
- **SC-1** The PR states worker wait (red and green time for one task) measured before and after the change. [human]

## Non-goals
- Lowering the worker's model tier or effort (considered and dropped in #70). [human]
- Profiling why one self-check file takes 75–120 s; that is a separate issue. [agent]
- Telling a self-check script that crashes before its `ran` line from a failing test at red: it reads as a runner red can't read, as today. [agent]
- Changing which tests the task closing an epic runs (`tests.epic` or the full suite, per #66). [agent]

## Glossary
- **Self-check script**: a plain `tests/test_*.py` file run with `uv run python`, not through pytest. Never "test suite".
- **Scoped command**: a task's test command that names its test file followed by test names.

## Decisions
- An unreadable runner's suite keeps its rule (a non-zero suite gives no passing evidence): C-261030-gk3z. Self-check lines make the runner readable; a test with no line on a non-zero suite stays `failed` (FR-8).
- The worker scopes to the test names its pack's TC entries already give; no new pack field (grill Q1, [agent]).
- #88's single "suite red" fix task is left out: per-test results already stop the per-AC fix tasks (grill Q2, [agent], RF-8).
- Red prints its output tail instead of a code-phase pack, which is written at claim (grill Q3, [agent], RF-7).
- A self-check run that selects no test counts as no tests ran (grill Q4, [agent]).
- The suite runs every file even after one fails, so per-file results are available: D-261106-qo2r (research, 2026-11-06).
- A task's Test line cites the plan's TC-n: D-261028-scwb (research, 2026-10-28).
- Jury evidence reuses the epic-close suite run only when it ran the configured suite and passed: D-261106-grjt (research, 2026-11-06).

## Open points
