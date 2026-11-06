---
slug: 2026-11-06-faster-checks
retired: []
---
# Tasks: faster checks

## E-1 The jury parser accepts small format slips (US-4)

### T-1 Lens parser reads `none` slips and any-case field labels
- Files: `src/nio/jury.py`, `tests/test_jury.py`
- Serves: AC-12, AC-13, AC-14
- Test: TC-12, TC-13, TC-14, TC-19
- Depends on: none
- Parallel: no
- Tier: strong: ordinary parser logic, with exact cases in the tests
- Effort: low
- Mode: split: clear unit tests lead the code

### T-2 Lens output template shows `gap` and `where`
- Files: `src/nio/templates/lens-output.md`, `tests/test_jury.py`
- Serves: AC-15
- Test: TC-15
- Depends on: none
- Parallel: no
- Tier: cheap: add two lines to a template, the test names the exact text
- Effort: low
- Mode: split: TC-15 can fail first

## E-2 The fix-check round reuses evidence (US-5)

### T-3 The closing task's review line records the suite it ran
- Files: `src/nio/implement.py`, `tests/test_implement.py`
- Serves: AC-9
- Test: TC-20
- Depends on: none
- Parallel: no
- Tier: strong: adds a field to an existing history line, only on the epic-closing task
- Effort: low
- Mode: split: TC-20 leads

## E-3 Jury evidence reuses suite results (US-3)

### T-4 Evidence reuses the review's suite and skips covered journeys; `gate_repo` gains a `tasks=` keyword so TC-16 and TC-18 can make T-3 a task of E-1 in the fixture's tasks.md
- Files: `src/nio/evidence.py`, `tests/test_evidence.py`
- Serves: AC-8, AC-9, AC-10, AC-11, AC-16
- Test: TC-8, TC-9, TC-10, TC-11, TC-16, TC-18
- Depends on: T-3
- Parallel: no
- Tier: strong: several qualifying rules (command, code, task, commit), but the six tests pin each one
- Effort: med
- Mode: split: integration tests define every case

#### Fixes

### T-7 Fix: Reuse never checks the review ran at this commit or on a clean tree
- From: J-1 (implementation-E-3, round 1)
- Files: `src/nio/evidence.py`
- Serves: AC-10, AC-9, CT-5
- Test: TC-10
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

### T-8 Fix: A different interpreter counts as the suite's own per-file command
- From: J-2 (implementation-E-3, round 1)
- Files: `src/nio/evidence.py`
- Serves: AC-8, CT-5
- Test: TC-8
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

### T-9 Fix: A journey is not recognised as covered under the project's own `for f in ...; do ... "$f"` suite
- From: J-5 (implementation-E-3, round 1)
- Files: `src/nio/evidence.py`
- Serves: AC-8, CT-5
- Test: TC-8
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

### T-10 Fix: The glob is matched with `fnmatch`, so a nested path counts as a suite file
- From: J-7 (implementation-E-3, round 1)
- Files: `src/nio/evidence.py`
- Serves: AC-8, CT-5
- Test: TC-8
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

## E-4 Tests call the nio CLI in-process (US-1)

### T-5 In-process `run_main` helper and one embedding model per process
- Files: `tests/test_flow.py`, `tests/test_implement.py`, `src/nio/index.py`
- Serves: AC-1, AC-2, AC-3, AC-4
- Test: TC-1, TC-2, TC-3, TC-4
- Depends on: T-4
- Parallel: no
- Tier: strong: state restore and exit-code parity are subtle, but TC-2 and TC-3 spell them out
- Effort: med
- Mode: split: parity and restore tests lead

## E-5 The suite runs its test files in parallel (US-2)

### T-6 Parallel suite command in config
- Files: `.nio/config.json`, `tests/test_implement.py`
- Serves: AC-5, AC-6, AC-7
- Test: TC-5, TC-6, TC-7, TC-17
- Depends on: T-5
- Parallel: no
- Tier: strong: one shell pipeline, with failure propagation tested by TC-6 and TC-17
- Effort: low
- Mode: split: e2e tests lead the config line
