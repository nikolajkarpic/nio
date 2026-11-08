---
slug: 2026-11-08-explainer
retired: [T-24, T-28]                      # task IDs removed from this file; never reused
---
# Tasks: explainer

## E-1 Explainer helpers and CLI wiring (Foundation)
### T-1 Add `sections`, `nodes` and `render` (CT-1, CT-2, CT-3)
- Files: `src/nio/explain.py`, `tests/test_explain.py`
- Serves: AC-5, AC-9
- Test: TC-5 (its `explain.nodes` assertion only; the check part is T-3's)
- Depends on: none
- Parallel: no
- Tier: strong: new parsing helpers with clear contracts and tests
- Effort: med
- Mode: split: logic with a test that can lead

### T-2 Wire `check explainer` (starting with the missing-explainer error) and the `explain` group (`finish`, `topic` stubs T-5 and T-13 replace) into the CLI (CT-10)
- Files: `src/nio/cli.py`, `src/nio/explain.py`, `tests/test_explain.py`
- Serves: AC-11
- Test: TC-16
- Depends on: T-1
- Parallel: no
- Tier: cheap: wiring a command group by an existing CLI pattern
- Effort: low
- Mode: split: CLI behaviour has a test (TC-16)

#### Fixes

### T-17 Fix: Node cap undercounts common Mermaid syntax, so oversized diagrams pass
- From: J-1 (implementation-E-1, round 1)
- Files: `src/nio/explain.py`
- Serves: CT-2, AC-5
- Test: TC-5
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

### T-18 Fix: Any non-parse render failure becomes "unreachable", which skips the check and hides every later block
- From: J-2 (implementation-E-1, round 1)
- Files: `src/nio/explain.py`
- Serves: CT-3, CT-4, AC-9
- Test: TC-14
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

### T-19 Fix: A node whose ID starts with `end` is skipped
- From: J-9 (implementation-E-1, round 1)
- Files: `src/nio/explain.py`
- Serves: CT-2, FR-7, J-9
- Test: TC-5
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

### T-20 Fix: AC-9 has no passing evidence
- From: J-14 (implementation-E-1, round 1)
- Files: `src/nio/explain.py`, `tests/test_explain.py`
- Serves: AC-9
- Test: TC-14
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

### T-21 Fix: Node cap still undercounts: labels cleaned across lines and arrow forms `<-->`, `--o`, `--x` missed
- From: J-1 (implementation-E-1, round 2)
- Files: `src/nio/explain.py`, `tests/test_explain.py`
- Serves: CT-2, AC-5
- Test: TC-5
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

## E-2 Check the explainer (US-2)
### T-3 Add the plan-mode checks of `explain.check` (CT-4)
- Files: `src/nio/explain.py`, `tests/test_explain.py`
- Serves: AC-5, AC-6, AC-7, AC-8, AC-11, AC-36
- Test: TC-5, TC-6, TC-11, TC-12, TC-13, TC-16, TC-39
- Depends on: T-2
- Parallel: no
- Tier: strong: several checks with clear tests
- Effort: low
- Mode: split: test cases lead the checks

### T-4 Add the render check and its notes to `explain.check` (CT-4)
- Files: `src/nio/explain.py`, `tests/test_explain.py`
- Serves: AC-9, AC-10
- Test: TC-14, TC-15
- Depends on: T-3
- Parallel: no
- Tier: strong: render check with clear tests
- Effort: low
- Mode: split: TC-14/15 lead the code

#### Fixes

### T-22 Fix: CT-1 counts as named when only CT-10 is in the map
- From: J-1 (implementation-E-2, round 1)
- Files: `src/nio/explain.py`
- Serves: AC-7, CT-4
- Test: TC-12
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

### T-23 Fix: A path that resolves to a plan explainer but is spelled differently runs as topic mode
- From: J-2 (implementation-E-2, round 1)
- Files: `src/nio/explain.py`
- Serves: CT-4, AC-7
- Test: TC-12
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

## E-3 Images beside the explainer (US-3)
### T-5 Add `explain.finish`: refusals, hashes, drill-down markers, one atomic write (CT-5 steps 1-4, 7, 8)
- Files: `src/nio/explain.py`, `tests/test_explain.py`
- Serves: AC-33
- Test: TC-43, TC-44, TC-47, TC-4
- Depends on: T-4
- Parallel: no
- Tier: strong: refusals, hashes and an atomic write, specified by the contract
- Effort: low
- Mode: split: TC-43 leads the code

### T-6 Add image rendering and safe deletion to `finish` (CT-5 steps 5, 6); TC-45 calls `finish` in-process
- Files: `src/nio/explain.py`, `tests/test_explain.py`
- Serves: AC-33
- Test: TC-10, TC-38, TC-45, TC-46
- Depends on: T-5
- Parallel: no
- Tier: max: deletes files, which can't be undone, so the safety rules must be exact
- Effort: med
- Mode: split: four tests lead the code

#### Fixes

### T-25 Fix: A drill-down heading containing ", " locks finishing forever
- From: J-1 (implementation-E-3, round 1)
- Files: `src/nio/explain.py`
- Serves: CT-5, J-1
- Test: TC-4
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

### T-26 Fix: A quickstart with unusual front matter fails after explainer.md is already written and images deleted
- From: J-2 (implementation-E-3, round 1)
- Files: `src/nio/explain.py`
- Serves: CT-5, J-2
- Test: TC-4
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

### T-27 Fix: Step 6 strips every `> ` line and image line, not only the ones an earlier finish wrote
- From: J-4 (implementation-E-3, round 1)
- Files: `src/nio/explain.py`
- Serves: CT-5, J-4
- Test: TC-4
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

### T-29 Fix: A drill-down heading containing "; " still locks finishing
- From: J-1 (implementation-E-3, round 2)
- Files: `src/nio/explain.py`, `tests/test_explain.py`
- Serves: CT-5, AC-33
- Test: TC-43
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

## E-4 Explain an approved plan (US-1)
### T-7 Make the plan gate ignore the quickstart `Read first` line (CT-9)
- Files: `src/nio/jury.py`, `src/nio/flow.py`, `tests/test_explain.py`
- Serves: AC-4
- Test: TC-4, TC-30
- Depends on: T-6
- Parallel: no
- Tier: strong: touches the gate in two modules, so the change must stay narrow
- Effort: med
- Mode: split: TC-4 leads the code

### T-8 Write the `@nio:explain` skill, plan mode, cheat-sheet and rules, and the README row (CT-11)
- Files: `skills/explain/SKILL.md`, `README.md`, `tests/test_explain.py`
- Serves: AC-29
- Test: TC-7, TC-38
- Depends on: T-7
- Parallel: no
- Tier: strong: skill prose that the contracts and tests pin down
- Effort: low
- Mode: single: the skill text and its checks are written together

### T-9 Write the skill's end-to-end tests for plan mode
- Files: `tests/test_explain_e2e.py`
- Serves: AC-1, AC-2, AC-3, AC-12, AC-13, AC-14, AC-30, AC-32
- Test: TC-1, TC-2, TC-3, TC-8, TC-9, TC-17, TC-18, TC-19, TC-37
- Depends on: T-8
- Parallel: no
- Tier: strong: e2e tests on real models following the lenses pattern
- Effort: low
- Mode: direct: the task is the tests, nothing to lead

## E-5 Flow suggests explaining once the plan is approved (US-7)
### T-10 Add the `suggest:` line to `flow.next_step` (CT-8)
- Files: `src/nio/flow.py`, `tests/test_flow.py`
- Serves: AC-24, AC-25
- Test: TC-32, TC-33
- Depends on: T-9
- Parallel: no
- Tier: strong: one added line in `next_step` with clear tests
- Effort: low
- Mode: split: TC-32/33 lead the code

## E-6 Flag a stale explainer, never block (US-6)
### T-11 Add `explain.stale` and print it from `nio status` (CT-7)
- Files: `src/nio/explain.py`, `src/nio/cli.py`, `tests/test_explain.py`
- Serves: AC-21, AC-22, AC-31
- Test: TC-28, TC-29, TC-31, TC-40, TC-44, TC-47
- Depends on: T-10
- Parallel: no
- Tier: strong: staleness logic with many cases, all covered by tests
- Effort: low
- Mode: split: six tests lead the code

### T-12 Test that a stale or missing explainer blocks no flow command
- Files: `tests/test_flow.py`
- Serves: AC-23
- Test: TC-30
- Depends on: T-11
- Parallel: no
- Tier: cheap: one test on existing behaviour
- Effort: low
- Mode: direct: the task is only a test

## E-7 Explain a topic (US-5)
### T-13 Add `explain.topic` and the topic-mode check (CT-6, CT-4)
- Files: `src/nio/explain.py`, `tests/test_explain.py`
- Serves: AC-20, AC-34, AC-35
- Test: TC-25, TC-42, TC-23 (its `nio explain topic` calls), TC-26, TC-27
- Depends on: T-12
- Parallel: no
- Tier: strong: topic function that reuses the plan-mode helpers
- Effort: low
- Mode: split: TC-25/42 lead the code

### T-14 Add topic mode to the skill and its end-to-end tests (CT-11)
- Files: `skills/explain/SKILL.md`, `tests/test_explain_e2e.py`
- Serves: AC-18, AC-19, AC-35
- Test: TC-23, TC-24, TC-27
- Depends on: T-13
- Parallel: no
- Tier: strong: skill prose plus e2e tests, patterned on plan mode
- Effort: low
- Mode: single: skill text and e2e tests are written together

## E-8 Drill down interactively (US-4)
### T-15 Add the `Drill-down` section to the skill and its end-to-end tests (CT-12)
- Files: `skills/explain/SKILL.md`, `tests/test_explain_e2e.py`
- Serves: AC-15, AC-16, AC-17, AC-34
- Test: TC-20, TC-21, TC-22, TC-26, TC-41
- Depends on: T-14
- Parallel: no
- Tier: strong: interactive skill section plus e2e tests
- Effort: low
- Mode: single: skill text and e2e tests are written together

## E-9 Choose the diagram format (US-8)
### T-16 Add the `Format` section to the skill and the format tests (CT-13)
- Files: `skills/explain/SKILL.md`, `tests/test_explain.py`, `tests/test_explain_e2e.py`
- Serves: AC-26, AC-27, AC-28
- Test: TC-34, TC-35, TC-36
- Depends on: T-15
- Parallel: no
- Tier: strong: skill section plus format tests
- Effort: low
- Mode: single: skill text and tests are written together
