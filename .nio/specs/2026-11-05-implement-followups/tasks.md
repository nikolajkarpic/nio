---
slug: 2026-11-05-implement-followups
retired: []                      # task IDs removed from this file; never reused
---
# Tasks: Implement follow-ups

## E-1 A blocked task's change record passes the memory check (US-1)

### T-1 File the change record with the sections the memory check requires, carrying the handoff's texts
- Files: `src/nio/implement.py`, `tests/test_implement.py`
- Serves: AC-1, AC-2, AC-3
- Test: TC-1, TC-2, TC-3, TC-26
- Depends on: none
- Parallel: no
- Tier: strong: ordinary logic, but the record must satisfy the existing memory check
- Effort: med
- Mode: split: clear failing tests exist before the code

### T-2 Refuse a handoff with a forged section line or an empty text, filing no record
- Files: `src/nio/implement.py`, `tests/test_implement.py`
- Serves: AC-20, AC-21
- Test: TC-16, TC-17
- Depends on: T-1
- Parallel: no
- Tier: strong: input validation with clear tests
- Effort: low
- Mode: split: both tests fail on today's code

#### Fixes

### T-14 Fix: Backslash in spec_says breaks the record title, leaving a half-done block
- From: J-1 (implementation-E-1, round 1)
- Files: `src/nio/implement.py`
- Serves: CT-1, J-1
- Test: TC-1
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

## E-2 Red asks only for the test files of the TC IDs the task proves itself (US-2)

### T-3 Add `tasks.own`, a task's own TC IDs without those a later task proves
- Files: `src/nio/tasks.py`, `tests/test_tasks.py`
- Serves: AC-23
- Test: a direct unit check `test_own` in `tests/test_tasks.py`, calling `own` on the three `Test:` lines quoted in the setups of TC-4, TC-6 and TC-19 and asserting the own IDs each expects (the first ID only, none, and the ID cited outside the deferral part); TC-19 proved later by T-4, which owns TC-19's red assertion in `tests/test_implement.py`
- Depends on: none
- Parallel: no
- Tier: strong: small text-parsing function with a stated example
- Effort: low
- Mode: single: tiny function, one worker writes check and code

### T-4 Make red's file check read own TC IDs (`tasks_of` gains `own`, `test_files` uses it)
- Files: `src/nio/implement.py`, `tests/test_implement.py`
- Serves: AC-4, AC-5, AC-6, AC-7, AC-22, AC-23
- Test: TC-4, TC-5, TC-6, TC-7, TC-18, TC-19, TC-27
- Depends on: T-3
- Parallel: no
- Tier: strong: ordinary logic with many clear cases
- Effort: low
- Mode: split: TC-5, TC-6, TC-7, TC-19 fail today, so red can be proved; TC-4, TC-18 and TC-27 are regression guards that already pass

## E-3 A wall-clock limit can't fail a task's review (US-5)

### T-5 Run the review's test suite with `NIO_PERF` removed from the environment
- Files: `src/nio/implement.py`, `tests/test_implement.py`
- Serves: AC-14, AC-15
- Test: TC-13, TC-14, TC-30
- Depends on: none
- Parallel: no
- Tier: strong: small env change, tests need an elaborate fixture
- Effort: med
- Mode: split: TC-13 fails today (TC-14 is a guard)

### T-6 Add `status_speed` to the flow tests, asserting the 2-second limit only under `NIO_PERF=1`
- Files: `tests/test_flow.py`
- Serves: AC-18
- Test: TC-15 (its fake clock is recreated for each call, reading 0.0 then 3.0)
- Depends on: none
- Parallel: no
- Tier: strong: the work is itself a test with a fake clock
- Effort: low
- Mode: direct: the work is a test file, nothing to fail first

### T-7 List the `NIO_PERF=1` status-speed self-check in `CLAUDE.md`
- Files: `CLAUDE.md`, `tests/test_flow.py`
- Serves: AC-29
- Test: TC-25
- Depends on: T-6
- Parallel: no
- Tier: cheap: one doc line plus a string-match test
- Effort: low
- Mode: single: doc line and its string check by one worker

#### Fixes

### T-15 Fix: The journey that claims to run the 2-second limit sets NIO_PERF for the wrong command
- From: J-1 (implementation-E-3, round 1)
- Files: `tests/test_flow.py`
- Serves: AC-18, AC-29
- Test: TC-15; J-1 was accepted as risk and its change request C-261106-mao2 rejected (QS-5 serves UJ-5, a review on a loaded machine), so nothing changes: this task only re-runs TC-15 to confirm the limit stays gated
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: direct: no change to make; the run confirms TC-15 still passes

### T-16 Fix: AC-14 and AC-15 tests sit after the `__main__` runner and never run
- From: J-4 (implementation-E-3, round 1)
- Files: `tests/test_implement.py`
- Serves: AC-14, AC-15, CT-9
- Test: TC-13
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

## E-4 The tasks-gate fix check shows tasks added under Fixes (US-3)

### T-8 Record the fix tasks of each round, add `jury.fixes_added`, and show added fix tasks in the fix-check pack
- Files: `src/nio/jury.py`, `tests/test_jury.py`
- Serves: AC-8, AC-24
- Test: TC-8, TC-20, TC-28; TC-11 proved later by T-9
- Depends on: none
- Parallel: no
- Tier: strong: new jury round state and pack part, clear tests
- Effort: med
- Mode: split: TC-8, TC-20, TC-28 fail today

### T-9 Print `added under Fixes:` in `nio jury changed`
- Files: `src/nio/cli.py`, `tests/test_jury.py`
- Serves: AC-9, AC-11
- Test: TC-9, TC-11
- Depends on: T-8
- Parallel: no
- Tier: strong: one CLI output line over T-8's function
- Effort: low
- Mode: split: TC-9 fails today

### T-10 Prove an added fix task keeps the tasks gate approved and an edited planned task withdraws it
- Files: `tests/test_tasks.py`
- Serves: AC-10, AC-25
- Test: TC-10, TC-21
- Depends on: none
- Parallel: no
- Tier: cheap: only regression tests on existing behaviour
- Effort: low
- Mode: direct: both tests pass on today's code, so red can't be proved

#### Fixes

### T-17 Fix: AC-9 calls T-30 a changed ID, but the code and CT-6 keep it out of the changed line
- From: J-8 (implementation-E-4, round 1)
- Files: `src/nio/cli.py`
- Serves: AC-9, CT-6, FR-7
- Test: TC-9
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

## E-5 The evaluator edits only the rating lines (US-4)

### T-11 Add `tasks.rated_from` and `--rated-from` on `nio check tasks`
- Files: `src/nio/tasks.py`, `src/nio/cli.py`, `tests/test_tasks.py`
- Serves: AC-26, AC-27
- Test: TC-22, TC-23, TC-29
- Depends on: none
- Parallel: no
- Tier: strong: line-diff check with a CLI flag, clear tests
- Effort: med
- Mode: split: all three tests fail today

### T-12 Give the evaluator card an edit tool and no whole-file write tool, and tell it to edit in place
- Files: `src/nio/agents.py`, `src/nio/agents/evaluator.md`, `tests/test_agents.py`
- Serves: AC-12
- Test: TC-12
- Depends on: none
- Parallel: no
- Tier: cheap: card tool list and one sentence, following the card pattern
- Effort: low
- Mode: single: small edit with one string test

### T-13 Make the tasks skill copy `tasks.md` before the evaluator and run `--rated-from` after
- Files: `skills/tasks/SKILL.md`, `tests/test_tasks.py`
- Serves: AC-28
- Test: TC-24; step 3 also says, per CT-11, to run `nio run`, copy to `.nio/runs/<run>/tasks.before.md`, and send a failing `--rated-from` back to the evaluator once
- Depends on: T-11
- Parallel: no
- Tier: cheap: skill wording edit with a string-order test
- Effort: low
- Mode: single: small edit with one string test

