---
slug: 2026-11-07-fewer-gate-turns
retired: []                      # task IDs removed from this file; never reused
---
<!-- Tasks template: the spec's work, one epic per user story (a full spec: one per entry of the plan's build order, in
its order; a bug-fix spec: one epic, E-1). A foundational epic, when there is shared setup, comes first. Task IDs run
across the whole spec and are never renumbered or reused. No status or checkbox here: a task's status lives in the CLI's
state. Work added after approval goes under the epic's `#### Fixes` heading, with the next free ID and a `From:` line.
`nio check tasks 2026-11-07-fewer-gate-turns` checks all of this and prints the estimate. Remove what doesn't apply; never write N/A. -->
# Tasks: drive a jury gate in fewer orchestrator calls

## E-1 A copied lens name no longer misfiles findings (US-4)

### T-1 File lens output by its file name
- Files: `src/nio/jury.py`, `src/nio/templates/lens-output.md`, `tests/test_jury.py`
- Serves: AC-9, AC-10
- Test: TC-9, TC-10
- Depends on: none
- Parallel: no
- Tier: strong: ordinary filing logic with clear tests
- Effort: low
- Mode: split: clear testable behaviour

## E-2 Dispose several findings in one call (US-2)

### T-2 Let dispose take comma-separated IDs and per-ID notes
- Files: `src/nio/jury.py`, `src/nio/cli.py`, `tests/test_jury.py`
- Serves: AC-6, AC-7, AC-15
- Test: TC-6, TC-7, TC-15
- Depends on: none
- Parallel: no
- Tier: strong: argument parsing and per-ID notes, clear tests
- Effort: low
- Mode: split: clear testable behaviour

## E-3 One command runs a gate step (US-1)

### T-3 Add the gate step `nio jury next` and the pack files it writes
- Files: `src/nio/jury.py`, `src/nio/cli.py`, `src/nio/evidence.py`, `tests/test_jury.py`, `tests/test_evidence.py`
- Serves: AC-1, AC-2, AC-3, AC-4, AC-5, AC-12, AC-13, AC-14, AC-16
- Test: TC-1, TC-2, TC-3, TC-4, TC-5, TC-12, TC-13, TC-14, TC-16, TC-17, TC-19
- Depends on: T-1, T-2
- Parallel: no
- Tier: strong: new multi-step command with many cases, but fully tested
- Effort: med
- Mode: split: many test cases worth writing first by a separate worker

#### Fixes

### T-6 Fix: An over-cap plan is run in full with no human choice
- From: J-1 (implementation-E-3, round 1)
- Files: `src/nio/jury.py`
- Serves: CT-1, J-1
- Test: TC-1
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

### T-7 Fix: `--add` reason text can invent a lens that gets a pack and a juror line
- From: J-2 (implementation-E-3, round 1)
- Files: `src/nio/jury.py`
- Serves: CT-1, J-2
- Test: TC-1
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

### T-8 Fix: The spec-gate consistency juror is given worker instructions it cannot follow
- From: J-6 (implementation-E-3, round 1)
- Files: `src/nio/jury.py`
- Serves: CT-2, J-6
- Test: TC-1
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

### T-9 Fix: Escalation loop on a grill-deferred or CLI blocker
- From: J-8 (implementation-E-3, round 1)
- Files: `src/nio/jury.py`
- Serves: CT-1, AC-14
- Test: TC-1
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

## E-4 Jurors write their own output file (US-3)

### T-4 Give juror cards a write tool limited by instruction
- Files: `src/nio/agents.py`, `src/nio/agents/adversary.md`, `src/nio/agents/architecture-fit.md`, `src/nio/agents/conformance.md`, `src/nio/agents/consistency.md`, `src/nio/agents/correctness.md`, `src/nio/agents/executability.md`, `src/nio/agents/logic.md`, `src/nio/agents/refuter.md`, `src/nio/agents/risk-rollback.md`, `src/nio/agents/scope.md`, `src/nio/agents/security.md`, `src/nio/agents/test-proof.md`, `src/nio/agents/testability.md`, `tests/test_agents.py`
- Serves: AC-8
- Test: TC-8
- Depends on: T-3
- Parallel: no
- Tier: cheap: the same card edit repeated across files, one test
- Effort: low
- Mode: split: one test checks all cards

#### Fixes

## E-5 The jury skill uses the shorter path (US-5)

### T-5 Rewrite the jury skill around `nio jury next`
- Files: `skills/jury/SKILL.md`, `tests/test_jury.py`
- Serves: AC-11
- Test: TC-11, TC-18
- Depends on: T-2, T-3, T-4
- Parallel: no
- Tier: strong: skill prose must match the CLI behaviour exactly
- Effort: low
- Mode: single: one worker writes the prose and the check that guards it
