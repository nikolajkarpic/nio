---
slug: 2026-11-07-lite-path
retired: [T-13, T-14]                      # task IDs removed from this file; never reused
---
# Tasks: lite path of the NIO flow for small bug fixes

## E-1 Run a small fix through the lite route (US-1)

### T-1 Add `flow.skips`, let `kind` drive lite, start tasks on a settled bug-fix spec, and move test_flow's existing lite-unsupported assertions (kind, next, TC-53, TC-62) to an epic spec (CT-1, CT-2, CT-3)
- Files: `src/nio/flow.py`, `src/nio/tasks.py`, `tests/test_flow.py`
- Serves: AC-1
- Test: TC-1
- Depends on: none
- Parallel: no
- Tier: strong: ordinary logic across where/guard/moves/done with a clear end-to-end test
- Effort: med
- Mode: split: new behaviour, test can fail first

### T-2 Grill's lite bar: skip six-facet coverage, zero questions, escalation stop; creates `test_lite_skill_texts` (CT-6)
- Files: `skills/grill/SKILL.md`, `tests/test_flow.py`
- Serves: AC-2
- Test: TC-2
- Depends on: T-1
- Parallel: no
- Tier: cheap: one paragraph of skill text checked by a substring test
- Effort: low
- Mode: single: text edit and its substring test are one small change

### T-3 Test that red refuses a passing test on a lite effort (CT-2, CT-10)
- Files: `tests/test_implement.py`, `src/nio/implement.py`
- Serves: AC-4
- Test: TC-4
- Depends on: T-1
- Parallel: yes
- Tier: cheap: follows the existing impl() test pattern, no code change expected
- Effort: low
- Mode: direct: only tests existing behaviour, nothing can fail first

### T-4 Test that the implementation jury gate reviews a lite fix (CT-2, CT-11)
- Files: `tests/test_flow.py`, `src/nio/jury.py`
- Serves: AC-5
- Test: TC-5
- Depends on: T-1
- Parallel: no
- Tier: strong: multi-step setup reusing TC-1 and the implementing-guard history lines
- Effort: low
- Mode: direct: only tests existing behaviour, nothing can fail first

#### Fixes



### T-15 Fix: Re-running an earlier stage's done is no longer treated as passed when history lags the files
- From: J-3 (implementation-E-1, round 1)
- Files: `src/nio/flow.py`
- Serves: FR-2, FR-15, J-3
- Test: new: FR-2
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

## E-2 Write a mini bugfix spec (US-2)

### T-5 Test the bugfix template and the empty unchanged-behaviour check (CT-9)
- Files: `tests/test_spec.py`, `src/nio/spec.py`
- Serves: AC-6, AC-7
- Test: TC-6, TC-7
- Depends on: T-1
- Parallel: yes
- Tier: cheap: small unit tests over an existing check and fixture
- Effort: low
- Mode: direct: only tests existing behaviour, nothing can fail first

### T-6 Drafter and evaluator cards cut unchanged-behaviour tests as `direct` tasks; tasks skill steps 1 and 3 say so; adds to `test_lite_skill_texts` (CT-8, CT-14, CT-7 in part)
- Files: `src/nio/agents/tasks-drafter.md`, `src/nio/agents/evaluator.md`, `skills/tasks/SKILL.md`, `tests/test_flow.py`
- Serves: AC-8
- Test: TC-8
- Depends on: T-2
- Parallel: no
- Tier: cheap: wording edits in three text files checked by substring tests
- Effort: low
- Mode: single: text edits and their substring test are one small change

#### Fixes

### T-16 Fix: T-5: src/nio/spec.py isn't in the epic's diff
- From: J-1 (implementation-E-2, round 1)
- Files: `src/nio/spec.py`
- Serves: AC-6, AC-7
- Test: TC-6
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

### T-17 Fix: Tasks skill description says a bug fix waits for the spec jury
- From: J-3 (implementation-E-2, round 1)
- Files: `skills/tasks/SKILL.md`
- Serves: CT-7, FR-8, J-3
- Test: TC-8
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

### T-18 Fix: Tasks skill has no escalation stop in step 4
- From: J-4 (implementation-E-2, round 1)
- Files: `skills/tasks/SKILL.md`
- Serves: CT-7, FR-8, J-4
- Test: TC-8
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

## E-3 Escalate a lite effort that turns out bigger (US-3)

### T-7 Folder escalation note in `tasks.check` on a lite spec (CT-4)
- Files: `src/nio/tasks.py`, `tests/test_tasks.py`
- Serves: AC-9
- Test: TC-9
- Depends on: T-1
- Parallel: yes
- Tier: strong: small logic (test-file filter, folder grouping) with a precise test
- Effort: low
- Mode: split: new behaviour, test can fail first

### T-8 Spec skill `## Escalating a bug fix` section and placement test; adds to `test_lite_skill_texts` (CT-13)
- Files: `skills/spec/SKILL.md`, `tests/test_flow.py`
- Serves: AC-11, AC-12
- Test: TC-11, TC-12
- Depends on: T-2
- Parallel: no
- Tier: cheap: a skill section with named phrases; placement test uses existing flow behaviour
- Effort: low
- Mode: single: section text and tests are one change; placement part already works after T-1

### T-9 Tasks skill: description, inputs, stop on `escalate:` note and drafter stops; adds the tasks skill's TC-16 check to `test_lite_skill_texts` (CT-7, rest)
- Files: `skills/tasks/SKILL.md`, `tests/test_flow.py`
- Serves: AC-9, AC-16
- Test: TC-16
- Depends on: T-6
- Parallel: no
- Tier: cheap: wording edits in one skill file
- Effort: low
- Mode: single: skill text and its own substring check are one small change

### T-10 Implement skill: blocked handoff offers the full flow on a trigger; adds the implement skill's TC-16 check to `test_lite_skill_texts` (CT-12)
- Files: `skills/implement/SKILL.md`, `tests/test_flow.py`
- Serves: AC-9, AC-16
- Test: TC-16
- Depends on: T-9
- Parallel: no
- Tier: cheap: one step of skill text
- Effort: low
- Mode: single: skill text and its own substring check are one small change

#### Fixes

### T-19 Fix: The folder note does not offer the full flow, and no test checks that it does
- From: J-1 (implementation-E-3, round 1)
- Files: `src/nio/tasks.py`, `tests/test_tasks.py`
- Serves: AC-9, CT-4
- Test: TC-9
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

### T-20 Fix: The agent-judged folder trigger drops the non-test qualifier that FR-8 and AC-9 keep
- From: J-3 (implementation-E-3, round 1)
- Files: `skills/spec/SKILL.md`, `skills/tasks/SKILL.md`
- Serves: FR-8, AC-9, CT-7, CT-13
- Test: TC-9
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

## E-4 Pick lite or full at intake (US-4)

### T-11 Spec skill step 1 routes lite only when all four hold, full otherwise, in one line; adds to `test_lite_skill_texts` (CT-5)
- Files: `skills/spec/SKILL.md`, `tests/test_flow.py`
- Serves: AC-13, AC-14, AC-15
- Test: TC-13, TC-14, TC-15
- Depends on: T-8
- Parallel: no
- Tier: cheap: wording edit of one step checked by substring tests
- Effort: low
- Mode: single: text edit and its substring test are one small change

### T-12 Test that the grill skill and the drafter card name every trigger; adds to `test_lite_skill_texts`
- Files: `tests/test_flow.py`
- Serves: AC-16
- Test: TC-16
- Depends on: T-2, T-6, T-9, T-10
- Parallel: no
- Tier: cheap: substring checks over four files
- Effort: low
- Mode: direct: text already written by earlier tasks, nothing can fail first
