---
slug: 2026-11-08-full-auto-run
retired: [T-2, T-8, T-11]
---
# Tasks: full-auto run

## E-1 Foundation: the tag, the flags and the no-`--by human` rule (Foundation)

### T-1 `[auto]` is a spec provenance tag, and `fs`/`fd` parse `--auto`
- Files: `src/nio/spec.py`, `tests/test_spec.py`, `src/nio/cli.py`
- Serves: AC-17, AC-18
- Test: TC-17
- Depends on: none
- Parallel: yes
- Tier: strong: a new tag in the spec parser with a clear test
- Effort: low
- Mode: split: behaviour a test can lead


### T-3 Every skill and card carries the ban on agents passing `--by human`
- Files: `skills/*/SKILL.md`, `skills/jury/SKILL.md`, `src/nio/agents/*.md`, `tests/test_flow.py`
- Serves: AC-29, AC-42
- Test: TC-47
- Depends on: none
- Parallel: no
- Tier: cheap: the same sentence added to many cards, checked by a text test
- Effort: low
- Mode: single: mechanical text edit plus a grep-style check

## E-2 The human grants auto once the spec draft is written (US-1)

### T-4 `flow.start --auto` grants auto, human only, history `grant` line with host and model
- Files: `src/nio/flow.py`, `tests/test_flow.py`, `src/nio/cli.py`
- Serves: AC-1, AC-3, AC-29, AC-42
- Test: TC-1, TC-3, TC-29, TC-42
- Depends on: T-3
- Parallel: no
- Tier: max: the human-only grant is a security boundary
- Effort: low
- Mode: split: behaviour a test can lead

### T-5 `flow.done drafting --auto` grants auto as drafting closes
- Files: `src/nio/flow.py`, `tests/test_flow.py`, `src/nio/cli.py`
- Serves: AC-2
- Test: TC-2
- Depends on: T-4
- Parallel: no
- Tier: strong: reuses the grant from T-4 on another path
- Effort: low
- Mode: split: behaviour a test can lead

## E-3 The driver runs every stage to the end (US-2)

### T-6 The driver claim `flow.drive` with atomic take, refresh, stale takeover and release
- Files: `src/nio/flow.py`, `tests/test_flow.py`, `src/nio/cli.py`
- Serves: AC-9, AC-38, AC-43, AC-44
- Test: TC-9, TC-38, TC-43, TC-51
- Depends on: T-5
- Parallel: no
- Tier: max: atomic take, stale takeover and races on shared state
- Effort: med
- Mode: split: behaviour a test can lead

### T-7 A grant puts the work on the effort branch `nio/<slug>`
- Files: `src/nio/flow.py`, `tests/test_flow.py`
- Serves: AC-1
- Test: TC-53
- Depends on: T-6
- Parallel: no
- Tier: strong: a git branch step with a clear test
- Effort: low
- Mode: split: behaviour a test can lead


### T-9 A passing gate under auto reads as working, so a new driver carries on without repeating a gate
- Files: `src/nio/flow.py`, `tests/test_flow.py`
- Serves: AC-11
- Test: TC-11, TC-46, TC-49
- Depends on: T-7
- Parallel: no
- Tier: max: resume state must not repeat or skip a gate
- Effort: med
- Mode: split: behaviour a test can lead

### T-10 The stop list under auto and the driver skill `@nio:auto` with its stop messages
- Files: `src/nio/flow.py`, `skills/auto/SKILL.md`, `tests/test_auto_e2e.py`, `tests/test_flow.py`
- Serves: AC-5
- Test: TC-5, TC-44, TC-48, TC-56
- Depends on: T-9
- Parallel: no
- Tier: strong: the stop list plus the driver skill, both from clear contracts
- Effort: med
- Mode: split: stop rules a test can lead, then the skill text

## E-4 The fixer settles jury findings within its authority (US-3)


### T-12 `held` and `--by auto` dispositions
- Files: `src/nio/jury.py`, `tests/test_jury.py`
- Serves: AC-13
- Test: TC-13
- Depends on: T-10
- Parallel: no
- Tier: strong: two new dispositions with a clear test
- Effort: low
- Mode: split: behaviour a test can lead

### T-13 Each judged version stays reachable, the round check `jury.cuts` and the gate composer under auto: fixer acts on `rejected`, no refuter verdict and a round-check hit hand over
- Files: `src/nio/jury.py`, `tests/test_jury.py`
- Serves: AC-12, AC-14, AC-15, AC-34, AC-36, AC-37, AC-39
- Test: TC-12, TC-14, TC-15, TC-34, TC-36, TC-37, TC-39, TC-52, TC-57
- Depends on: T-12
- Parallel: no
- Tier: strong: several branching rules, each with a test
- Effort: high
- Mode: split: behaviour a test can lead

### T-14 The spec jury's packs list every `[auto]` default
- Files: `src/nio/jury.py`, `tests/test_jury.py`
- Serves: AC-19
- Test: TC-19
- Depends on: T-13
- Parallel: no
- Tier: strong: pack listing with a clear test
- Effort: low
- Mode: split: behaviour a test can lead

### T-15 The fixer card `nio-fixer` acts on each row of the fixer table
- Files: `src/nio/agents/fixer.md`, `tests/test_auto_e2e.py`
- Serves: AC-13, AC-14
- Test: TC-55
- Depends on: T-12
- Parallel: yes
- Tier: strong: a card that must follow a table of authority limits
- Effort: low
- Mode: single: card text and its e2e check go together

### T-16 The jury skill's `## Under auto` hands `rejected` to the fixer
- Files: `skills/jury/SKILL.md`, `tests/test_flow.py`
- Serves: AC-12
- Test: TC-47, TC-50
- Depends on: T-14, T-15
- Parallel: no
- Tier: cheap: one skill section that follows the contract
- Effort: low
- Mode: single: text edit plus a check

### T-17 The grill's `## Under auto` settles open points and `[default]` items as `[auto]`
- Files: `skills/grill/SKILL.md`, `tests/test_auto_e2e.py`
- Serves: AC-16
- Test: TC-16
- Depends on: T-14
- Parallel: no
- Tier: cheap: one skill section that follows the contract
- Effort: low
- Mode: single: text edit plus an e2e check

### T-18 An epic jury's confirmed major is fixed and re-judged before the next epic
- Files: `src/nio/flow.py`, `tests/test_flow.py`
- Serves: AC-20
- Test: TC-20
- Depends on: T-16
- Parallel: no
- Tier: strong: a fix and re-judge loop in the flow with a clear test
- Effort: med
- Mode: split: behaviour a test can lead

## E-5 Budgets default to what the effort's gates need (US-5)

### T-19 `cap()` and the jury and subagent caps in `stops`
- Files: `src/nio/flow.py`, `tests/test_flow.py`
- Serves: AC-25, AC-26, AC-32, AC-33
- Test: TC-25, TC-26, TC-32, TC-33
- Depends on: T-18
- Parallel: no
- Tier: strong: cap arithmetic with clear tests
- Effort: low
- Mode: split: behaviour a test can lead

### T-20 Resume keeps auto and raises the cap and the stopped gate's rounds
- Files: `src/nio/flow.py`, `tests/test_flow.py`
- Serves: AC-8, AC-41
- Test: TC-8, TC-41
- Depends on: T-19
- Parallel: no
- Tier: strong: resume raising limits with clear tests
- Effort: low
- Mode: split: behaviour a test can lead

## E-6 Risky specs still stop at every gate (US-6)

### T-21 A risky spec stops the driver at every gate until the human commits, then carries on in auto
- Files: `src/nio/flow.py`, `tests/test_flow.py`
- Serves: AC-27, AC-28
- Test: TC-27, TC-28
- Depends on: T-20
- Parallel: no
- Tier: max: the risky-spec stop is a safety rule and a missed stop can't be undone
- Effort: med
- Mode: split: behaviour a test can lead

## E-7 The human keeps control of the grant (US-7)

### T-22 `flow.manual` switches auto off, with restore lines
- Files: `src/nio/flow.py`, `tests/test_flow.py`, `src/nio/cli.py`
- Serves: AC-31
- Test: TC-31
- Depends on: T-21
- Parallel: no
- Tier: strong: a state switch with restore lines and a clear test
- Effort: low
- Mode: split: behaviour a test can lead

### T-23 `[auto]` items still pass the spec gate after auto is switched off
- Files: `tests/test_spec.py`
- Serves: AC-17, AC-18
- Test: TC-18
- Depends on: T-1, T-22
- Parallel: no
- Tier: cheap: one test case on code that already exists
- Effort: low
- Mode: single: the task is the test, nothing to split

### T-24 Auto granted mid-effort carries on from that stage
- Files: `src/nio/flow.py`, `tests/test_flow.py`
- Serves: AC-30
- Test: TC-30
- Depends on: T-22
- Parallel: no
- Tier: strong: stage pickup with a clear test
- Effort: low
- Mode: split: behaviour a test can lead

### T-25 A held finding needs the human in every mode
- Files: `src/nio/jury.py`, `tests/test_jury.py`
- Serves: AC-13
- Test: TC-54
- Depends on: T-24
- Parallel: no
- Tier: strong: one rule on top of T-12 with a clear test
- Effort: low
- Mode: split: behaviour a test can lead

## E-8 The run ends in a pull request that is the one report (US-4)

### T-26 The run report `flow.report` and the minor and refuted findings it lists
- Files: `src/nio/flow.py`, `tests/test_flow.py`, `tests/test_jury.py`
- Serves: AC-21, AC-23, AC-40
- Test: TC-21, TC-23, TC-40, TC-58
- Depends on: T-18, T-20, T-21, T-25
- Parallel: no
- Tier: strong: gathers findings across modules into one report, with tests
- Effort: med
- Mode: split: behaviour a test can lead

### T-27 `flow.pr` opens the pull request, never merges, pauses with the report when it fails
- Files: `src/nio/flow.py`, `tests/test_flow.py`, `src/nio/cli.py`
- Serves: AC-24, AC-45
- Test: TC-24, TC-45
- Depends on: T-26
- Parallel: no
- Tier: strong: a pull request call with a never-merge rule and a failure path
- Effort: low
- Mode: split: behaviour a test can lead

### T-28 End-to-end runs: full route, lite route, subagents or none, waiting without polling, one pull request
- Files: `tests/test_auto_e2e.py`
- Serves: AC-4, AC-6, AC-7, AC-10, AC-22, AC-35
- Test: TC-4, TC-6, TC-7, TC-10, TC-22, TC-35
- Depends on: T-27
- Parallel: no
- Tier: strong: long e2e scenarios over finished parts
- Effort: med
- Mode: single: the task is the tests, nothing to split
