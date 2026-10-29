---
slug: 2026-10-29-implement-stage
retired: []
---
# Tasks: Implement stage

## E-1 Shared pieces the implement stage builds on (Foundation)

### T-1 Run a command with a time limit and tell a test runner's wrong-reason failures from real ones
- Files: `src/nio/implement.py`, `tests/test_implement.py`
- Serves: AC-38, AC-12
- Test: direct unit checks calling `run` (a time limit, a missing program, the process group killed) and `runner` and `wrong_reason` on each known runner's error markers; TC-38's CLI red proved later by T-11
- Depends on: none
- Parallel: no
- Tier: strong: timeouts and output classification are ordinary logic with clear tests
- Effort: med

### T-2 Read a full-suite run into failing names, a collected count and a broken flag
- Files: `src/nio/implement.py`, `tests/test_implement.py`
- Serves: AC-44, AC-35
- Test: direct unit checks calling `suite` on captured unittest output (failing names, collected count, a collection error) and on an unknown runner's exit code; TC-44 proved later by T-14
- Depends on: T-1
- Parallel: no
- Tier: strong: output parsing with clear tests
- Effort: med

### T-3 Derive each task's status from history, and pick the next ready task and its mode
- Files: `src/nio/implement.py`, `tests/test_implement.py`
- Serves: AC-8, AC-32, AC-39
- Test: direct unit checks calling `status` and `next_ready` on fixture history lines (epic and dependency order, an open fix task holding its epic, a changed task under a new T-n, a missing `Mode:` read as split); TC-8, TC-32 and TC-39 proved later by T-21
- Depends on: none
- Parallel: no
- Tier: strong: pure derivation from history with clear tests
- Effort: med

### T-4 Add the Mode field to tasks.md: its check, its template line and the evaluator's rating
- Files: `src/nio/tasks.py`, `src/nio/templates/tasks.md`, `src/nio/agents/evaluator.md`, `tests/test_tasks.py`, `tests/test_implement.py`
- Serves: AC-40
- Test: direct unit checks calling `tasks.check` on a list with no `Mode:` approved before and after `tasks.MODE_SINCE`, and on a bad or reasonless `Mode:`; TC-56's claim half proved later by T-8
- Depends on: none
- Parallel: yes
- Tier: cheap: adds one field following the existing field-check pattern
- Effort: low

## E-2 Each task runs in a fresh worker with only its pack (US-1)

### T-5 Build a task's worker pack from its five parts
- Files: `src/nio/implement.py`, `src/nio/pack.py`, `tests/test_pack.py`, `tests/test_implement.py`
- Serves: AC-1
- Test: TC-1
- Depends on: T-3
- Parallel: no
- Tier: strong: assembles parts via the existing pack code, clear tests
- Effort: med

### T-6 Ship the nio-worker card and render it once per tier and host
- Files: `src/nio/agents/worker.md`, `src/nio/agents.py`, `tests/test_agents.py`, `tests/test_implement.py`
- Serves: AC-2, AC-24
- Test: TC-2, TC-24
- Depends on: none
- Parallel: no
- Tier: strong: new card plus a small render-per-tier change in existing sync code
- Effort: low

### T-7 Start the stage on the first claim: effort branch, suite setting and baseline
- Files: `src/nio/implement.py`, `src/nio/cli.py`, `tests/test_implement.py`
- Serves: AC-19, AC-27, AC-34, AC-51
- Test: TC-19, TC-27, TC-34, TC-55
- Depends on: T-2, T-3
- Parallel: no
- Tier: strong: git branch and baseline handling with several cases but clear tests
- Effort: high

### T-8 Guard every claim and tell the orchestrator how to start the worker
- Files: `src/nio/implement.py`, `src/nio/cli.py`, `tests/test_implement.py`
- Serves: AC-3, AC-4, AC-5, AC-6, AC-7, AC-40, AC-46
- Test: TC-3, TC-4, TC-5, TC-6, TC-7, TC-40, TC-46, TC-56
- Depends on: T-4, T-5, T-6, T-7
- Parallel: no
- Tier: max: central gate over shared state; a missed guard breaks the red/green proof
- Effort: high

### T-9 Write the @nio:implement skill the orchestrator follows
- Files: `skills/implement/SKILL.md`
- Serves: AC-40
- Test: `tests/test_talk.py` passes with the new skill, and a direct check that `skills/implement/SKILL.md` names `nio flow claim`, `red`, `green`, `block` and each of split, single and direct in its steps; TC-40 proved later by T-8
- Depends on: T-8
- Parallel: yes
- Tier: strong: precise skill prose against a fixed CLI contract
- Effort: med

## E-3 Red and green are proven by the CLI, not claimed (US-2)

### T-10 Accept red on a failing test, freeze the test files and keep the command
- Files: `src/nio/implement.py`, `src/nio/cli.py`, `tests/test_implement.py`
- Serves: AC-9, AC-12, AC-33, AC-42
- Test: TC-9, TC-12, TC-33, TC-42
- Depends on: T-1, T-8
- Parallel: no
- Tier: max: test-file freezing is integrity logic that is easy to get subtly wrong
- Effort: high

### T-11 Refuse a wrong red, count the attempt and block a task at the third
- Files: `src/nio/implement.py`, `tests/test_implement.py`
- Serves: AC-10, AC-11, AC-38, AC-43, AC-49, AC-23
- Test: TC-10, TC-11, TC-38, TC-43, TC-49, TC-23
- Depends on: T-10
- Parallel: no
- Tier: max: attempt-count state machine with many edge cases in persistent history
- Effort: high

### T-12 Let the human unblock a task
- Files: `src/nio/implement.py`, `src/nio/cli.py`, `tests/test_implement.py`
- Serves: AC-36
- Test: TC-36
- Depends on: T-11
- Parallel: no
- Tier: strong: one command that appends a history event, clear test
- Effort: low

### T-13 Accept green on the red command only, and in direct mode with no red
- Files: `src/nio/implement.py`, `src/nio/cli.py`, `tests/test_implement.py`
- Serves: AC-14, AC-15, AC-21, AC-41
- Test: TC-14, TC-15, TC-21, TC-41, TC-52; TC-41's exit 0 after a passed review proved later by T-15, which adds the commit
- Depends on: T-11
- Parallel: no
- Tier: strong: two modes with clear tests, builds on the red state
- Effort: high

### T-14 Review a green task with checks only
- Files: `src/nio/implement.py`, `tests/test_implement.py`
- Serves: AC-13, AC-16, AC-17, AC-18, AC-35, AC-37, AC-44, AC-45, AC-50
- Test: TC-13, TC-16, TC-17, TC-18, TC-35, TC-37, TC-44, TC-45, TC-50; the exit 0 that TC-13 and TC-17 expect after a passed review proved later by T-15, which adds the commit
- Depends on: T-2, T-13
- Parallel: no
- Tier: max: nine ACs of regression and frozen-test checks; a wrong pass lets bad work through
- Effort: high

## E-4 Each done task is committed on the effort branch (US-4)

### T-15 Commit a task whose review passed as T-n: title on the effort branch
- Files: `src/nio/implement.py`, `tests/test_implement.py`
- Serves: AC-26, AC-20, AC-22
- Test: TC-26, TC-20, TC-22
- Depends on: T-14
- Parallel: no
- Tier: strong: git commit with a fixed message, clear tests
- Effort: med

### T-16 Keep a task green when its commit fails, and keep nio's own steps free of model calls
- Files: `src/nio/implement.py`, `tests/test_implement.py`
- Serves: AC-47
- Test: TC-47, TC-51
- Depends on: T-15
- Parallel: no
- Tier: strong: failure path plus a no-model-call check, clear tests
- Effort: med

## E-5 A worker stops on a spec problem and files a change request (US-3)

### T-17 File a blocked handoff as a pending change request and block the task
- Files: `src/nio/implement.py`, `src/nio/cli.py`, `tests/test_implement.py`
- Serves: AC-25
- Test: TC-25; TC-24 already holds from T-6's card and must still pass
- Depends on: T-11
- Parallel: no
- Tier: strong: writes a change request file and a block event, clear tests
- Effort: med

### T-18 File the same handoff only once, and fail a review of a spec edit
- Files: `src/nio/implement.py`, `tests/test_implement.py`
- Serves: AC-48
- Test: TC-48, TC-53
- Depends on: T-14, T-17
- Parallel: no
- Tier: strong: idempotency and spec-edit detection, clear tests
- Effort: high

## E-6 An epic finishes and the effort moves on (US-5)

### T-19 Skip the epic gate, notify the human and report when an epic finishes
- Files: `src/nio/implement.py`, `tests/test_implement.py`
- Serves: AC-29, AC-30
- Test: TC-29, TC-30, TC-54
- Depends on: T-16
- Parallel: no
- Tier: strong: epic-completion check and a message, clear tests
- Effort: low

### T-20 Drive the implementing stage from nio flow and finish the effort after its last epic
- Files: `src/nio/flow.py`, `src/nio/implement.py`, `tests/test_flow.py`, `tests/test_implement.py`
- Serves: AC-31, AC-28
- Test: TC-31, TC-28
- Depends on: T-19
- Parallel: no
- Tier: max: changes flow state, which only `nio flow` may write, and it can't be undone
- Effort: high

### T-21 Pin task order, fix tasks and resuming after a change request
- Files: `src/nio/implement.py`, `tests/test_implement.py`
- Serves: AC-8, AC-32, AC-39
- Test: TC-8, TC-32, TC-39
- Depends on: T-20
- Parallel: no
- Tier: strong: ordering and resume rules over derived status, clear tests
- Effort: high
