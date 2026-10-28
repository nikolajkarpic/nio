---
slug: 2026-10-28-flow-state
retired: []                      # task IDs removed from this file; never reused
---
# Tasks: flow state

## E-1 The flow files, the lock, the guards, the command line and git's exit code (Foundation)

### T-6 The test helpers `effort`, `history`, `cli`, `snap` in tests/test_flow.py, and `flow.pick` / `flow.kind` (CT-4)
- Files: `src/nio/flow.py`, `tests/test_flow.py`
- Serves: AC-4
- Test: TC-4
- Depends on: none
- Parallel: no
- Tier: strong: test helpers and two small lookups; ordinary logic
- Effort: med

### T-1 Read and record an effort's flow files: `flow.load`, `flow.record`, `STATE_KEYS`, `flow.Broken` and the `--by` parsing (CT-1, CT-2)
- Files: `src/nio/flow.py`, `tests/test_flow.py`
- Serves: AC-6, AC-7, AC-9, AC-58, AC-59
- Test: direct unit checks calling `load` and `record` (defaults, hash on the `end` line, unknown key, torn tail cut and noted, `state.json.new` rolled forward or dropped); TC-6 and TC-7 proved later by T-8, TC-59, TC-74 and TC-75 by T-9, TC-9, TC-58 and TC-73 by T-10
- Depends on: T-6
- Parallel: no
- Tier: strong: append-only history and state parsing with torn-line and Broken detection; exact formats matter
- Effort: high

### T-2 The effort's lock: `flow.lock`, `flow.Busy`, the effort folder's `.gitignore`, stale takeover (CT-3)
- Files: `src/nio/flow.py`, `tests/test_flow.py`
- Serves: AC-12, AC-56, AC-61
- Test: direct unit checks calling `lock` (a held lock raises `Busy`, a stale one is taken over, a live one is not, the lock is removed on exit, `.gitignore` lines); TC-12 and TC-56 proved later by T-9, TC-61 by T-16
- Depends on: T-1, T-6
- Parallel: no
- Tier: max: a cross-process lock with stale takeover; races are easy to get wrong
- Effort: high

### T-3 `records.git` gains `full=True`, returning exit code, stdout and stderr; current callers unchanged (CT-19)
- Files: `src/nio/records.py`, `tests/test_flow.py`
- Serves: AC-21
- Test: a direct unit check calling `records.git(..., full=True)` on a failing and a passing git command; TC-21 proved later by T-13
- Depends on: T-6
- Parallel: no
- Tier: cheap: adds an optional return shape to an existing helper, callers unchanged
- Effort: low

### T-4 The guards: `flow.STAGES` (the state table "Flow") and `flow.guard` per the decision table "Guards" (CT-5)
- Files: `src/nio/flow.py`, `tests/test_flow.py`
- Serves: AC-13, AC-14, AC-15, AC-16, AC-29
- Test: direct unit checks calling `guard` per stage of the decision table "Guards" (pass, fail with its output, `closed`); TC-13 to TC-16 proved later by T-12, TC-29 by T-19
- Depends on: T-6
- Parallel: no
- Tier: strong: a transcription of the state and decision tables with clear tests
- Effort: med

### T-5 The `nio flow` subparser: `next`, `start`, `done`, `status`, `park`, `abandon`, `seen`, required `--by` on writers, `ValueError`/`Broken`/`Busy` as `error: ...` exit 1 (CT-16)
- Files: `src/nio/cli.py`, `tests/test_flow.py`
- Serves: AC-6
- Test: TC-77, and a check that a `ValueError`, `flow.Broken` or `flow.Busy` raised by a stubbed `flow` function prints `error: ...` and exits 1
- Depends on: T-1, T-2, T-6
- Parallel: no
- Tier: cheap: an argparse subparser following the existing cli.py pattern plus error mapping
- Effort: med

## E-2 Any agent picks up where the effort is (US-1)

### T-7 Where an effort is and what to do next: `flow.GATES`, `flow.where`, `flow.next_step` with its working and "Talking to the human" outputs (CT-6, CT-9)
- Files: `src/nio/flow.py`, `tests/test_flow.py`
- Serves: AC-1, AC-2, AC-4, AC-8
- Test: TC-1, TC-2, TC-4, TC-8; TC-65 proved later by T-20, which adds unseen overrides to `next`
- Depends on: T-4, T-6
- Parallel: no
- Tier: strong: derives the current stage from history across gates; many outputs to get exactly right
- Effort: high

### T-8 `nio flow start`: create the flow files, start and resume lines (CT-10)
- Files: `src/nio/flow.py`, `tests/test_flow.py`
- Serves: AC-3, AC-5, AC-6, AC-7
- Test: TC-3, TC-5, TC-6, TC-7, TC-76, TC-77
- Depends on: T-2, T-5, T-7
- Parallel: no
- Tier: strong: creates the flow files and prints start/resume lines on top of load/record and the lock
- Effort: med

### T-9 `nio flow park`, and the write path's lock, torn-line and temp-state tests through it (CT-13)
- Files: `src/nio/flow.py`, `tests/test_flow.py`
- Serves: AC-12, AC-56, AC-58, AC-59
- Test: TC-12, TC-56, TC-59, TC-74, TC-75
- Depends on: T-8
- Parallel: no
- Tier: max: the write path under the lock with torn-line and temp-state crash cases
- Effort: high

### T-10 A broken effort stops `next`, `start` and `park`; a leftover temp state is rolled forward
- Files: `src/nio/flow.py`, `src/nio/cli.py`, `tests/test_flow.py`
- Serves: AC-9, AC-58
- Test: TC-9, TC-58, TC-73
- Depends on: T-9
- Parallel: no
- Tier: max: crash recovery that rolls a temp state forward; wrong handling loses or corrupts state
- Effort: high

### T-11 The flow rule line in every skill and agent card; every other mention of the flow files names a `nio flow` command (CT-18)
- Files: `skills/grill/SKILL.md`, `skills/jury/SKILL.md`, `skills/plan/SKILL.md`, `skills/recall/SKILL.md`, `skills/remember/SKILL.md`, `skills/spec/SKILL.md`, `skills/tasks/SKILL.md`, `src/nio/agents/adversary.md`, `src/nio/agents/architecture-fit.md`, `src/nio/agents/consistency.md`, `src/nio/agents/evaluator.md`, `src/nio/agents/executability.md`, `src/nio/agents/logic.md`, `src/nio/agents/refuter.md`, `src/nio/agents/risk-rollback.md`, `src/nio/agents/scope.md`, `src/nio/agents/security.md`, `src/nio/agents/spec-drafter.md`, `src/nio/agents/tasks-drafter.md`, `src/nio/agents/test-proof.md`, `src/nio/agents/testability.md`, `tests/test_flow.py`
- Serves: AC-11
- Test: TC-11
- Depends on: T-6
- Parallel: no
- Tier: cheap: one rule line copied into many markdown files, checked by a test
- Effort: low

## E-3 The effort moves on only when its guards pass (US-2)

### T-12 `nio flow done`: stage checks, `pass` and `skip` lines, a stage not reached or already passed, a broken state (CT-11)
- Files: `src/nio/flow.py`, `tests/test_flow.py`
- Serves: AC-9, AC-13, AC-14, AC-15, AC-16, AC-17, AC-18, AC-22
- Test: TC-13, TC-14, TC-15, TC-16, TC-17, TC-18, TC-22, TC-68, TC-78
- Depends on: T-4, T-9
- Parallel: no
- Tier: strong: many guard outcomes and refusal cases in done, tested case by case
- Effort: high

### T-13 `done` at a gate: `--commit` makes one approval commit of the effort folder, no commit off a gate, rollback when git fails (CT-11, CT-19)
- Files: `src/nio/flow.py`, `tests/test_flow.py`
- Serves: AC-19, AC-20, AC-21, AC-52
- Test: TC-19, TC-20, TC-21, TC-52
- Depends on: T-3, T-12
- Parallel: no
- Tier: max: approval commit with rollback when git fails; flow state and git must not diverge
- Effort: high

### T-14 Gates and rejections as `where` reads them: implementing waits, rejected rounds send back, re-review after an edit, past approvals count only with their commit (CT-6)
- Files: `src/nio/flow.py`, `tests/test_flow.py`
- Serves: AC-23, AC-24, AC-25, AC-51, AC-63, AC-64
- Test: TC-23, TC-24, TC-25, TC-51, TC-63, TC-64
- Depends on: T-13
- Parallel: no
- Tier: max: subtle state: rejections send back, edits force re-review, approvals count only with their commit
- Effort: high

## E-4 The human sees every effort at a glance (US-4)

### T-15 `nio flow status`: one line per folder, newest activity first, legacy, unsupported and broken lines, idle time (CT-12)
- Files: `src/nio/flow.py`, `tests/test_flow.py`
- Serves: AC-10, AC-31, AC-32, AC-53
- Test: TC-10, TC-31, TC-32, TC-53, TC-67, TC-69
- Depends on: T-14
- Parallel: no
- Tier: strong: a read-only listing with sorting and a few special lines
- Effort: med

### T-16 Park and resume as the human sees them: the reason recorded, `next` resumes, refusals, a live lock kept, no network or model (CT-13, CT-9)
- Files: `src/nio/flow.py`, `tests/test_flow.py`
- Serves: AC-33, AC-34, AC-35, AC-61
- Test: TC-33, TC-34, TC-35, TC-61, TC-66
- Depends on: T-15
- Parallel: no
- Tier: strong: park/resume paths reusing existing write and lock code
- Effort: med

### T-17 `nio flow abandon`: freeze until `start`, the four refusals, a broken state (CT-14)
- Files: `src/nio/flow.py`, `tests/test_flow.py`
- Serves: AC-9, AC-55, AC-62
- Test: TC-55, TC-62, TC-79
- Depends on: T-15
- Parallel: no
- Tier: strong: a freeze state with four refusals, clearly specified
- Effort: med

### T-18 `nio run [<slug> <stage|T-n>]` writes `flow.json`; a history line's `run` is looked up from it (CT-17)
- Files: `src/nio/records.py`, `src/nio/cli.py`, `src/nio/flow.py`, `tests/test_flow.py`
- Serves: AC-36, AC-37
- Test: TC-36, TC-37
- Depends on: T-12, T-15
- Parallel: no
- Tier: strong: writes and reads a small run record across records, cli and flow
- Effort: med

## E-5 The human can push a check through, on the record (US-3)

### T-19 Overrides in `done`: `--human` passes a failing check on its own line, refuses an empty reason and a jury gate, a closed gate passes as an override (CT-11)
- Files: `src/nio/flow.py`, `tests/test_flow.py`
- Serves: AC-26, AC-27, AC-28, AC-29, AC-30, AC-65
- Test: TC-26, TC-27, TC-28, TC-29, TC-30, TC-72
- Depends on: T-13, T-15
- Parallel: no
- Tier: strong: override rules must refuse empty reasons and jury gates and stay on the record
- Effort: high

### T-20 `nio flow seen` and unseen overrides in `next` and `status` (CT-15)
- Files: `src/nio/flow.py`, `tests/test_flow.py`
- Serves: AC-9, AC-57
- Test: TC-57, TC-65, TC-70, TC-80
- Depends on: T-19
- Parallel: no
- Tier: strong: a small acknowledgement command and a flag in two outputs
- Effort: low

## E-6 A change sends the effort back to the stage that owns the file (US-5)

### T-21 `flow.changes`: pending change records and edited approved files move the effort back once, `done` refused while one is pending, parked and abandoned efforts handled (CT-7)
- Files: `src/nio/flow.py`, `tests/test_flow.py`
- Serves: AC-38, AC-39, AC-40, AC-41, AC-42
- Test: TC-38, TC-39, TC-40, TC-41, TC-42, TC-71
- Depends on: T-14, T-17
- Parallel: no
- Tier: max: moves an effort back exactly once on changes; subtle state interplay with park and abandon
- Effort: high

## E-7 The stop list pauses an auto effort that must not go on (US-6)

### T-22 `flow.stops`: round cap, no-progress pause, jury and subagent caps, a manual effort ignored, the suspended effort's output (CT-8)
- Files: `src/nio/flow.py`, `tests/test_flow.py`
- Serves: AC-43, AC-44, AC-45, AC-49, AC-50, AC-60
- Test: TC-43, TC-44, TC-45, TC-49, TC-50, TC-60
- Depends on: T-21
- Parallel: no
- Tier: strong: several caps and a no-progress check over history; counting must be exact
- Effort: high

### T-23 Stuck after three identical failures, wait before a change moves an auto effort, wait for `--commit` on a risky spec (CT-8)
- Files: `src/nio/flow.py`, `tests/test_flow.py`
- Serves: AC-46, AC-47, AC-48, AC-54
- Test: TC-46, TC-47, TC-48, TC-54
- Depends on: T-22
- Parallel: no
- Tier: strong: failure-repeat detection and wait conditions over history; edge cases in counting
- Effort: high
