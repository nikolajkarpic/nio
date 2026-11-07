---
slug: 2026-11-07-scoped-task-commands
retired: [T-2]
---
# Tasks: scope each task's test command to its own tests

## E-1 Self-check runner (Foundation)

### T-1 Add the self-check runner `selfcheck.main`
- Files: `tests/selfcheck.py`, `tests/test_selfcheck.py`
- Serves: AC-1, AC-2, AC-3
- Test: TC-1, TC-2, TC-3, TC-11
- Depends on: none
- Parallel: no
- Tier: strong: new runner with ordinary logic and clear tests
- Effort: med
- Mode: split: a testable behavior change


### T-3 Run every test script through `selfcheck.main`, keeping every test it ran before (its `ran` count equals the tests its old `__main__` ran)
- Files: `tests/test_agents.py`, `tests/test_evidence.py`, `tests/test_flow.py`, `tests/test_hooks.py`, `tests/test_implement.py`, `tests/test_index.py`, `tests/test_jury.py`, `tests/test_lenses.py`, `tests/test_pack.py`, `tests/test_plan.py`, `tests/test_records.py`, `tests/test_spec.py`, `tests/test_talk.py`, `tests/test_tasks.py`, `tests/test_tasks_e2e.py`, `tests/test_usage.py`, `tests/test_waves.py`, `tests/test_selfcheck.py`
- Serves: AC-2
- Test: TC-13
- Depends on: T-1
- Parallel: no
- Tier: strong: 18 scripts of different shapes (fixed orders, `test` first, `[check]`, `--demo` branches), where a dropped test passes TC-13
- Effort: low
- Mode: single: one worker converts the files and proves TC-13 red then green

## E-2 Run only a task's own tests (US-1)

### T-4 Runner reads self-check output; red accepts scoped commands and refuses zero-test runs before the exit code; review fails a crashed self-check suite
- Files: `src/nio/implement.py`, `tests/test_implement.py`
- Serves: AC-1, AC-2, AC-3, AC-4, AC-5, AC-6 (TC-12, the review rule of CT-3, is filed under AC-6 in tests.md)
- Test: TC-4, TC-5, TC-6, TC-12
- Depends on: T-3
- Parallel: no
- Tier: strong: several gate rules with clear tests
- Effort: med
- Mode: split: a testable behavior change

#### Fixes

### T-8 Fix: review misses a crashed self-check file beside a failing one
- From: J-2 (implementation-E-2, round 1)
- Files: `src/nio/implement.py`, `tests/test_implement.py`
- Serves: CT-3, J-2
- Test: TC-12
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

## E-3 Workers iterate fast and quietly (US-2)

### T-5 Worker card: scoped, foreground, no re-run before first edit
- Files: `src/nio/agents/worker.md`, `tests/test_agents.py`
- Serves: AC-7
- Test: TC-7
- Depends on: T-4, T-6
- Parallel: no
- Tier: cheap: card wording edit checked by a text test
- Effort: low
- Mode: single: wording and its text check are one small change

### T-6 Red prints its last 20 output lines; implement skill passes them on
- Files: `src/nio/implement.py`, `skills/implement/SKILL.md`, `tests/test_implement.py`
- Serves: AC-8
- Test: TC-8
- Depends on: T-4
- Parallel: no
- Tier: strong: small logic change plus skill text, clear test
- Effort: low
- Mode: split: a testable behavior change

#### Fixes

### T-9 Fix: The worker card's no-re-run rule covers only the code phase
- From: J-1 (implementation-E-3, round 1)
- Files: `src/nio/agents/worker.md`, `tests/test_agents.py`
- Serves: AC-7, CT-5, FR-6
- Test: TC-7
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

## E-4 Evidence per test, not per suite (US-3)

### T-7 Evidence records results per test from self-check lines
- Files: `src/nio/evidence.py`, `tests/test_evidence.py`
- Serves: AC-9, AC-10
- Test: TC-9, TC-10
- Depends on: T-4
- Parallel: no
- Tier: strong: line parsing into per-test records with clear tests
- Effort: low
- Mode: split: a testable behavior change

#### Fixes

### T-10 Fix: A pytest-style failing entry matches every test of that name in any file
- From: J-2 (implementation-E-4, round 1)
- Files: `src/nio/evidence.py`, `tests/test_evidence.py`
- Serves: CT-4, FR-8, J-2
- Test: TC-9
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding
