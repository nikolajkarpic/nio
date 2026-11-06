---
slug: 2026-11-06-faster-checks
route: full
epic: ""                         # "<epic slug>/R-<n>" when this is a slice of an epic
risk: [external-input]           # auth | pii | money | external-input | data-deletion | migration | multi-party | public-api
retired: [OP-1, OP-2, OP-3, OP-4, OP-5, OP-6, OP-7, OP-8, OP-9]                      # IDs removed from this spec; never reused
---
<!-- Spec template. WHAT and WHY only, never HOW. Every item ends with its provenance: [human] (the grill
confirmed it), [agent] (an agent decided it: below the grill's bar, or in a session the human delegated), [research: RF-n] (a finding in research.md) or [default] (your proposal; the grill must confirm it).
IDs are permanent: number new items after the highest ever used, never renumber, list removed IDs in `retired`.
Remove a section that doesn't apply; never write N/A. `nio check spec 2026-11-06-faster-checks` checks all of this. -->
# Faster checks: in-process CLI in tests, parallel suite, evidence reuse, lenient jury parser (#71-#75)

## Summary
One effort that cuts the time NIO runs spend on checks, in the human's priority order: the tests call the nio CLI
in-process (#73), the suite runs its test files in parallel (#72), jury evidence reuses suite results it already has
(#71), also in the implementation gate's fix-check round (#75), and the jury parser accepts small format slips (#74). The suite is the main time sink of every run (346 s
serial), and a failing file must still fail it. The smallest diff that works. [human]

## Actors and journeys
- **A-1 NIO run agent**: a worker, red/green agent or reviewer that runs the suite and single test files many times per effort; wants fast, trustworthy results. [research: RF-1]
- **A-2 Jury evidence**: `nio jury evidence`, which runs the suite and auto journeys before the implementation jury; wants not to repeat work already done at the same commit. [research: RF-1]
- **A-3 Juror**: a model lens whose output the jury parser reads; wants a near-miss format to count, not a re-emit round. [research: RF-1]
- **A-4 Maintainer (Nikolaj)**: wants shorter runs and the before/after numbers in the PR. [human]

**UJ-1 Run the suite** (A-1) [research: RF-1]
1. The agent runs the configured suite command.
2. It reads the exit code and the failing tests from the output.
- Misuse: a failing file is hidden by parallel output, or the suite passes although a file failed.
- Evidence: issue #72, issue #73

**UJ-2 Collect jury evidence** (A-2) [research: RF-1]
1. Evidence collects the suite result for the commit.
2. It runs the auto journeys that the suite did not already cover.
- Misuse: a suite result from another commit or a dirty tree is reused.
- Evidence: issue #71, issue #75

**UJ-3 Parse a juror's output** (A-3) [research: RF-1]
1. The juror writes its findings file.
2. The parser accepts it, or rejects it as INVALID when it is really malformed.
- Misuse: a lenient parser lets truly malformed output through.
- Evidence: issue #74

## User stories

### US-1 Tests call the nio CLI in-process (P1) [human]
- **Why this priority:** 169 of the 178 s of test_implement.py is subprocess startup; the human ranked #73 first. [human]
- **Independent test:** run tests/test_implement.py alone and time it; its tests give the same results as before.

- **AC-1** (FR-1) Given the test helper that runs `nio flow`, when test_implement.py runs, then it finishes in under 60 s and every test result is unchanged. [human]
  Observable: wall-clock of `uv run python tests/test_implement.py` < 60 s; same pass/fail per test as before the change. Level: integration.
- **AC-2** (FR-1) Given a CLI call in-process, when the command writes to stdout and stderr and exits with code n, then the helper returns that stdout, stderr and code n, as the subprocess did. [agent]
  Observable: helper result's stdout, stderr and returncode equal the subprocess's for the same command. Level: unit.
- **AC-3** (FR-1) Given an in-process call that changes directory or environment, when it returns (or raises), then the test process's working directory, environment and `sys.argv` are as before the call, and no flow lock it took is left behind. [agent]
  Observable: `os.getcwd()`, `os.environ` and `sys.argv` equal before and after the call, including a call that exits non-zero or raises; no `flow.lock` remains in the fixture. Level: unit.
- **AC-4** (FR-2) Given a test that needs process isolation (a lock held by another pid, a timeout, a process group), when it runs, then it still runs the CLI as a subprocess. [human]
  Note: these tests start their own subprocess today, outside the shared helpers [research: RF-2]; a lock the test process holds still refuses a second holder in-process [research: RF-3].
  Observable: those tests still pass and still start a subprocess. Level: integration.

### US-2 The suite runs its test files in parallel (P1) [human]
- **Why this priority:** the suite runs about 20 times per effort; parallel files save about 2.8 min per run. [human]
- **Independent test:** run the configured suite once with all files passing and once with one file failing.
- Eight files run at once, a fixed count [agent]; every file runs even after one fails, and the suite exits non-zero when any failed [agent].

- **AC-5** (FR-3) Given all test files pass, when the suite runs, then it exits 0 and its wall-clock is at most 1.5 times that of its slowest file run alone in the same session. [human]
  Observable: exit code 0; suite wall-clock <= 1.5 x the slowest file's own wall-clock. Level: e2e.
- **AC-6** (FR-4) Given one or more test files fail (an assertion, an error, or the process killed by a signal), when the suite runs, then it exits non-zero, after running every other file, and each failing file's output is in the suite's output. [human]
  Observable: exit code != 0 with two deliberately failing files and with one file killed by a signal; each failing file's assertion text appears in the output; a file after them in the list still ran. Level: e2e.
- **AC-7** (FR-5) Given a test file fails, when the CLI reads the parallel suite's result, then it reads it as it reads the serial suite's: the runner is unknown, so only the exit code is read, and the failing file's own output is still in the output. [human]
  Observable: `implement.runner` returns None for both the serial and the parallel command [research: RF-5]; the review reports the non-zero exit of the parallel suite. Level: integration.

### US-3 Jury evidence reuses suite results (P2) [human]
- **Why this priority:** an evidence run took 14m21s and hit the 600 s tool timeout; about 12 min per run is repeat work. Ranked third by the human. [human]
- **Independent test:** run evidence at a commit whose epic-close review ran the suite on a clean tree, and check the suite and covered journeys are not run again.

- **AC-8** (FR-6) Given an auto journey whose every step runs, with the suite's own per-file command and nothing added, a test file the suite runs, and the suite result evidence uses at that commit (reused under FR-7 or run in the copy) passed, when evidence collects, then it does not run that journey and records it as covered by the suite run. [human]
  Observable: no run of that command; the journey's record says covered by the suite run. A step with an added argument or environment variable (for example `NIO_E2E=1`), a step on a file the suite doesn't run, or a journey with one covered step and one other step is not covered and runs in full. [agent] Level: integration.
- **AC-9** (FR-7) Given the epic-close review ran the suite at the same commit with a clean tree, when evidence collects, then it reuses that suite result instead of running the suite again in the copy. [human]
  Observable: no suite run in the copy; the evidence suite result is passed and names the task and commit it was reused from. Level: integration.
- **AC-10** (FR-8) Given the review's suite result is from another commit or a dirty tree, ran a command other than the configured suite, or failed, when evidence collects, then it runs the suite in the copy as before. [agent]
  Observable: the suite runs in the copy. Level: integration.
- **AC-11** (FR-6) Given the suite result evidence uses failed, when evidence collects, then a journey on a test file runs in the copy as before and is not recorded as covered. [agent]
  Observable: the journey's command was run in the copy; its record does not say covered. Level: integration.

### US-4 The jury parser accepts small format slips (P2) [human]
- **Why this priority:** each slip costs a re-emit round and a second refuter pass, about 3–5 min per effort. Ranked last by the human. [human]
- **Independent test:** parse lens outputs with each known slip and with truly malformed output.

- **AC-12** (FR-9) Given `## Findings` holds exactly one line, `none` in any case optionally followed by one `.` or `!` (`none`, `None`, `None.`, `NONE!`), when the parser reads it, then it accepts it as no findings. [human]
  Observable: no "`## Findings` must hold findings" error; zero findings. Level: unit.
- **AC-13** (FR-10) Given a finding whose field labels are written in another case (`- Gap: missing`, `- WHERE: app.py`, `- Fix: ...`), when the parser reads it, then it reads those fields as if written in the expected form. [human]
  Observable: the parsed finding has the same gap, where and fix values as the expected-form finding. Level: unit.
- **AC-15** (FR-12) Given the lens output format a juror is given, when it is printed, then it shows the implementation gate's `gap` and `where` lines with their allowed values, marked as for that gate only. [agent]
  Observable: `nio jury template` output holds `- gap:` and `- where:` lines; a spec-gate output that leaves them out is still valid. Level: unit.
- **AC-14** (FR-11) Given output that is actually malformed (an implementation-gate finding with no `gap` or `where`; `None, but see F1` or `none yet` under `## Findings`; or `None.` followed by a `### F1` finding), when the parser reads it, then it still rejects it as INVALID. [human]
  Observable: the parser returns errors; the lens is INVALID. A spec-, plan- or tasks-gate finding needs no `gap` or `where`, as before. Level: unit.

### US-5 The fix-check round reuses evidence (P2) [human]
- **Why this priority:** a one-line fix re-collected the whole epic's evidence, about 95% of the round's time; filed as #75 during the grill and folded in by the human's coordinator. [human]
- **Independent test:** after a fix task closes an epic, run evidence for the fix-check round and check that the suite and the journeys it covers do not run again.

- **AC-16** (FR-13) Given a fix task closed the epic and its review meets every condition of FR-7, when evidence collects for the fix-check round, then it reuses that suite result and the journeys it covers (FR-6, FR-7), and records the task and commit they came from. [agent]
  Observable: no suite run and no covered journey run in the copy; the suite result names the fix task and its commit. Level: integration.

## Functional requirements
- **FR-1** WHEN a test runs a nio CLI command through the test helper THE SYSTEM SHALL run the CLI's `main()` in the test process and return its stdout, stderr and exit code, with the working directory and environment the subprocess had. [human]
- **FR-2** IF a test needs process isolation (locks held by another pid, timeouts, process groups) THEN THE SYSTEM SHALL keep running the CLI as a subprocess. [human]
- **FR-3** WHEN the configured suite runs THE SYSTEM SHALL run the test files in parallel, eight at a time, each file to its end even when another failed. [human]
- **FR-4** IF any test file fails (exits non-zero or is killed by a signal) THEN THE SYSTEM SHALL exit the suite non-zero once every file has run. A hung file is stopped by the suite's existing time limit (`tests.timeout`), which fails the run. [human]
- **FR-5** WHEN the suite runs in parallel THE SYSTEM SHALL keep its output readable by the runner detection and the failing-test parsing. [human]
- **FR-6** WHEN evidence meets an auto journey whose every step is the suite's own per-file command on a test file the suite runs, and the suite result evidence uses at that commit (reused under FR-7 or run in the copy) passed, THE SYSTEM SHALL skip it and record it as covered by that suite run. [human]
- **FR-7** WHEN the epic-close review ran the configured suite (not `tests.epic`) at the same commit with a clean tree, and it exited 0, THE SYSTEM SHALL reuse that suite result in evidence instead of running the suite in the copy, naming the task and commit it came from. [human]
- **FR-8** IF any condition of FR-7 does not hold (no review suite result, another commit, a dirty tree, a command other than the configured suite, or a non-zero exit) THEN THE SYSTEM SHALL run the suite in the copy as before. [agent]
- **FR-9** WHEN `## Findings` holds exactly one line, `none` in any case optionally followed by one `.` or `!`, THE SYSTEM SHALL accept it as no findings. [human]
- **FR-10** WHEN a finding writes a field label in another case THE SYSTEM SHALL accept it as that field. [human]
- **FR-11** IF juror output is malformed beyond those slips THEN THE SYSTEM SHALL reject it as before. [human]
- **FR-12** WHEN the lens output format is printed THE SYSTEM SHALL show the implementation gate's `gap` and `where` lines, marked as for that gate only. [agent]
- **FR-13** WHEN evidence collects for a fix-check round THE SYSTEM SHALL reuse the suite result and covered journeys of the fix task's review under FR-6 and FR-7, and record where they came from. [agent]

## Rules
### Decision table: evidence suite result
| Review ran the configured suite at same commit (yes, no) | Tree clean (yes, no) | Exited 0 (yes, no) | → suite result | Src |
| --- | --- | --- | --- | --- |
| yes | yes | yes | reuse the review's result | [human] |
| yes | yes | no | run the suite in the copy | [agent] |
| yes | no | - | run the suite in the copy | [agent] |
| no | - | - | run the suite in the copy | [agent] |

## Non-functional requirements
- **NFR-1** THE SYSTEM SHALL run tests/test_implement.py in under 60 s on the maintainer's machine. [human]
- **NFR-2** THE SYSTEM SHALL keep the change to the smallest diff that works. [human]

## Success criteria
- **SC-1** The PR body states before/after wall-clock of the whole suite and of test_implement.py. [human]
- **SC-2** The suite's wall-clock is at most 1.5 times its slowest file's, where it was the sum of all files (346 s in #72). [human]
- **SC-3** In a fix-check round after a fix task that closed the epic, evidence runs neither the suite nor a covered journey. [agent]

## Non-goals
- Making test files other than test_implement.py faster beyond what the in-process helper gives. [agent]
- Speeding up quickstart journeys that are not test files, in the first round or the fix-check round. [agent]
- In the fix-check round, re-running only what the fix diff touched for lint, type checks, misuse tests and non-test journeys: they run as in round 1. [agent]
- Filling a missing `gap` or `where` with a guess: an implementation-gate finding without them stays invalid. [agent]
- Accepting slips beyond `none` variants, field-label case and the template lines. [agent]

## Glossary
- **Covered journey**: an auto journey evidence does not run because each of its steps is a test file the passing suite already ran at that commit. Never "skipped journey".
- **Reused suite result**: the epic-close review's run of the configured suite, taken into evidence instead of a new run in the copy.

## Risks and evidence against
- The review's suite ran in the working tree, not a fresh copy, so a file ignored by git could make it pass where the copy fails (RF-8). [research: RF-8]

## Decisions
- Eight files at once, a fixed count, from the issue's example: D-261106-qo2r (grill Q1, agent, 2026-11-06).
- The parallel suite runs every file and exits non-zero if any failed (grill Q2, agent, 2026-11-06).
- Reuse the review's suite result only when it ran the configured suite and exited 0: D-261106-grjt (grill Q4, agent, 2026-11-06).
- The inline slip is fixed at its root: the template shows `gap` and `where`, and labels match in any case: D-261106-opl2 (grill Q3, agent, 2026-11-06).
- #75 is folded in as the fix-check round's use of FR-6 and FR-7; re-running only what the fix touched is a non-goal (grill Q6, agent, 2026-11-06).

