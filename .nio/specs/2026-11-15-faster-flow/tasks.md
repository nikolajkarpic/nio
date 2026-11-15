---
slug: 2026-11-15-faster-flow
retired: []                      # task IDs removed from this file; never reused
---
# Tasks: Faster flow

## E-1 A task can't depend on a later epic (US-2)

### T-1 Reject a dependency on a later epic in the tasks check (CT-7)
- Files: `src/nio/tasks.py`, `tests/test_tasks.py`
- Serves: AC-12, AC-13
- Test: TC-12, TC-13
- Depends on: none
- Parallel: no
- Tier: strong: ordinary check logic with clear tests
- Effort: low
- Mode: split: clear test leads

## E-2 One agent implements a whole epic, and the flow runs its tests at the end (US-1)

### T-2 Move tier and effort to the epic, drop `Mode`, keep the task map (CT-6, tasks half of CT-5)
- Files: `src/nio/tasks.py`, `src/nio/templates/tasks.md`, `src/nio/agents/evaluator.md`, `src/nio/agents/tasks-drafter.md`, `tests/test_tasks.py`
- Serves: AC-7
- Test: TC-7
- Depends on: T-1
- Parallel: no
- Tier: strong: parser field move with clear test
- Effort: low
- Mode: split: clear test leads

### T-3 Claim a whole epic, add `nio flow finish`, per-epic commit and epic state; remove red/green (CT-1, CT-2, CT-3, CT-4, CT-5)
- Files: `src/nio/implement.py`, `src/nio/cli.py`, `src/nio/flow.py`, `tests/test_implement.py`, `tests/test_waves.py`
- Serves: AC-1, AC-2, AC-3, AC-4, AC-5, AC-9, AC-10, AC-11, AC-43, AC-44, AC-45, AC-47
- Test: TC-1, TC-2, TC-3, TC-4, TC-9, TC-10, TC-11, TC-41, TC-42, TC-43, TC-45, TC-48, TC-50, TC-52, TC-57, TC-58
- Depends on: T-2
- Parallel: no
- Tier: max: claim, git commit and epic state machine across three modules, state can be left wrong
- Effort: med
- Mode: split: many testable behaviours

### T-4 Rewrite the implement skill, the worker card and NORTH_STAR for per-epic work (CT-8, CT-9, CT-10)
- Files: `skills/implement/SKILL.md`, `skills/jury/SKILL.md`, `src/nio/agents/worker.md`, `NORTH_STAR.md`, `tests/test_implement.py`, `tests/test_talk.py`, `tests/test_effort.py`
- Serves: AC-5, AC-6, AC-8
- Test: TC-5, TC-6, TC-8, TC-49
- Depends on: T-3
- Parallel: no
- Tier: strong: skill and card prose that must match the new flow
- Effort: low
- Mode: single: prose plus its checks together

## E-3 What the closed issues still need keeps working (US-7)

### T-5 Guard fix tasks around a retired one (CT-26)
- Files: `src/nio/tasks.py`, `tests/test_tasks.py`, `tests/test_flow.py`
- Serves: AC-36, AC-37
- Test: TC-34, TC-35
- Depends on: T-4
- Parallel: no
- Tier: strong: guard logic with clear tests
- Effort: low
- Mode: split: clear test leads

### T-6 Evidence: existing tests count, unchanged files are no phantom, test-proof at the pr gate (CT-27, CT-30, CT-31)
- Files: `src/nio/evidence.py`, `src/nio/jury.py`, `src/nio/agents/test-proof.md`, `tests/test_evidence.py`
- Serves: AC-38, AC-41, AC-42
- Test: TC-36, TC-39, TC-40, TC-51
- Depends on: T-4
- Parallel: no
- Tier: strong: evidence rules across code and a card, clear tests
- Effort: med
- Mode: split: clear test leads

### T-7 Change requests the flow writes lint clean; a spec-rooted pr finding asks for a change (CT-28, CT-29)
- Files: `src/nio/jury.py`, `src/nio/evidence.py`, `tests/test_jury.py`, `tests/test_evidence.py`
- Serves: AC-39, AC-40
- Test: TC-37, TC-38
- Depends on: T-6
- Parallel: no
- Tier: strong: output format and a finding rule with clear tests
- Effort: low
- Mode: split: clear test leads

### T-8 Executability flags a task blocked until a later epic (CT-32)
- Files: `src/nio/agents/executability.md`, `tests/test_lenses.py`
- Serves: AC-46
- Test: TC-44
- Depends on: T-4
- Parallel: no
- Tier: cheap: one rule added to an agent card
- Effort: low
- Mode: direct: card edit, its check is a costly e2e run

## E-4 Jury gates don't drop, re-send or blow up findings (US-5)

### T-9 Grounding, all-ungrounded re-run, reopen ruling, escalation votes (CT-14, CT-15, CT-16, CT-17)
- Files: `src/nio/jury.py`, `tests/test_jury.py`
- Serves: AC-24, AC-25, AC-26, AC-27
- Test: TC-22, TC-23, TC-24, TC-25
- Depends on: T-7
- Parallel: no
- Tier: strong: four jury rules in one module, clear tests
- Effort: med
- Mode: split: clear test leads

### T-10 Refuter files, kept confirmation, fix check version, whole plan items (CT-18, CT-19, CT-20, CT-21)
- Files: `src/nio/jury.py`, `tests/test_jury.py`
- Serves: AC-28, AC-29, AC-30, AC-31
- Test: TC-26, TC-27, TC-28, TC-29
- Depends on: T-9
- Parallel: no
- Tier: strong: jury rules with clear tests
- Effort: low
- Mode: split: clear test leads

## E-5 Claims, indexes and hand-offs don't break the run (US-6)

### T-11 Replace the index in one step and skip a missing record (CT-23)
- Files: `src/nio/index.py`, `src/nio/pack.py`, `tests/test_pack.py`
- Serves: AC-32
- Test: TC-30
- Depends on: T-4
- Parallel: no
- Tier: strong: atomic replace and a skip, clear test
- Effort: low
- Mode: split: clear test leads

### T-12 A failed claim removes the worktrees it made (CT-24)
- Files: `src/nio/implement.py`, `tests/test_waves.py`
- Serves: AC-33
- Test: TC-31
- Depends on: T-3
- Parallel: no
- Tier: strong: cleanup on failure path, clear test
- Effort: low
- Mode: split: clear test leads

### T-13 Warn on another root; hand-off names the skill file (CT-22, CT-25)
- Files: `src/nio/jury.py`, `src/nio/flow.py`, `tests/test_jury.py`, `tests/test_flow.py`
- Serves: AC-34, AC-35
- Test: TC-32, TC-33
- Depends on: T-10
- Parallel: no
- Tier: cheap: a warning and a message string following existing patterns
- Effort: low
- Mode: split: clear test leads

## E-6 Long commands run in the background in every effort session (US-3)

### T-14 Mod matches `nio jury evidence` and `nio flow finish`; brief warns when the mod is off (CT-11, CT-13)
- Files: `tools/claude-mods/background-nio-commands/hooks/register.ts`, `tools/claude-mods/background-nio-commands/hooks/register.test.ts`, `tools/claude-mods/background-nio-commands/README.md`, `src/nio/flow.py`, `tests/test_flow.py`, `tests/test_talk.py`
- Serves: AC-14, AC-16
- Test: TC-14, TC-16, TC-56
- Depends on: T-13
- Parallel: no
- Tier: strong: TypeScript hook match plus a brief warning
- Effort: low
- Mode: single: small change across hook and brief

### T-15 Install turns the mod on (CT-12). Builds only after #142 has landed on main and this branch has merged main
- Files: `skills/install/SKILL.md`, `tests/test_auto_e2e.py`
- Serves: AC-15
- Test: TC-15
- Depends on: T-14
- Parallel: no
- Tier: cheap: one e2e test on #142's install step; this effort adds no install step
- Effort: low
- Mode: single: one e2e test, no code of its own

## E-7 The full-auto run drives the effort to the end, with one agent fixing all findings (US-4)

### T-16 Carry #122's code over; grant and revoke auto; gates approve themselves; `--by human` steps under auto (CT-33, CT-34, CT-35, CT-36)
- Files: `src/nio/flow.py`, `src/nio/cli.py`, `src/nio/implement.py`, `src/nio/jury.py`, `skills/*/SKILL.md` (the `--by human` ban line), `src/nio/agents/*.md` (the ban line), `tests/test_flow.py`, `tests/test_talk.py`, `tests/test_effort.py`
- Serves: AC-17, AC-48, AC-49
- Test: TC-17, TC-46, TC-47, TC-53
- Depends on: T-10
- Parallel: no
- Tier: max: auth-like grant/revoke and self-approving gates, human-step rules
- Effort: med
- Mode: split: clear tests lead

### T-17 Dispositions, composer and round check under auto (CT-37, CT-38)
- Files: `src/nio/jury.py`, `tests/test_jury.py`, `tests/test_flow.py`
- Serves: AC-20
- Test: TC-54, TC-55
- Depends on: T-16
- Parallel: no
- Tier: strong: jury logic under auto with clear tests
- Effort: med
- Mode: split: clear test leads

### T-18 Driver loop and fix agent in the skills, run report as the PR body, pause message (CT-39, CT-40, CT-41)
- Files: `skills/jury/SKILL.md`, `skills/implement/SKILL.md`, `src/nio/flow.py`, `src/nio/jury.py`, `tests/test_flow.py`, `tests/test_auto_e2e.py`
- Serves: AC-18, AC-19, AC-20, AC-23
- Test: TC-18, TC-19, TC-20, TC-21
- Depends on: T-17
- Parallel: no
- Tier: strong: skill prose plus report and message code
- Effort: med
- Mode: single: prose and code must agree
