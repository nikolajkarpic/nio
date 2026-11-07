---
slug: 2026-11-05-parallel-waves
retired: []                      # task IDs removed from this file; never reused
---
<!-- Tasks template: the spec's work, one epic per user story (a full spec: one per entry of the plan's build order, in
its order; a bug-fix spec: one epic, E-1). A foundational epic, when there is shared setup, comes first. Task IDs run
across the whole spec and are never renumbered or reused. No status or checkbox here: a task's status lives in the CLI's
state. Work added after approval goes under the epic's `#### Fixes` heading, with the next free ID and a `From:` line.
`nio check tasks 2026-11-05-parallel-waves` checks all of this and prints the estimate. Remove what doesn't apply; never write N/A. -->
# Tasks: parallel waves

## E-1 Claim and work a wave in worktrees (US-1)

### T-1 Claim a wave and make a worktree for each task, with the `waves()` fixture and `--demo` of tests/test_waves.py
- Files: `src/nio/implement.py`, `tests/test_waves.py`
- Serves: AC-1, AC-2, AC-17, AC-16
- Test: TC-1, TC-2, TC-16, TC-17
- Depends on: none
- Parallel: no
- Tier: strong: ordinary claim logic and git worktree calls, with exact tests for each branch
- Effort: med
- Mode: single: one context pack

### T-2 Run red and green in the task's worktree; nio resolves to the project root there
- Files: `src/nio/implement.py`, `src/nio/records.py`, `tests/test_waves.py`
- Serves: AC-3, AC-5, AC-6
- Test: TC-3, TC-5, TC-6
- Depends on: T-1
- Parallel: no
- Tier: strong: cwd plumbing and repo_root through linked worktrees, clear tests
- Effort: low
- Mode: single: one context pack

### T-3 The implement skill starts a worker per wave task at once
- Files: `skills/implement/SKILL.md`, `src/nio/agents/worker.md`, `tests/test_waves.py`
- Serves: AC-11
- Test: TC-11
- Depends on: T-1
- Parallel: no
- Tier: cheap: skill text edit checked by phrase asserts
- Effort: low
- Mode: direct: docs, the test only checks phrases in the text

#### Fixes

### T-6 Fix: No E-1 AC test has a passing result in the evidence
- From: J-1 (implementation-E-1, round 1)
- Files: `tests/test_waves.py`
- Serves: AC-1, AC-2, AC-3, AC-5, AC-6, AC-11, AC-16, AC-17
- Test: TC-1
- Depends on: none
- Parallel: no
- Tier: cheap: no code change: the evidence suite stopped on an unrelated timing flake before tests/test_waves.py
- Effort: low
- Mode: direct: a passing run of tests/test_waves.py is the fix

### T-7 Fix: AC-1 has no passing evidence
- From: J-7 (implementation-E-1, round 1)
- Files: `src/nio/implement.py`, `tests/test_waves.py`
- Serves: AC-1
- Test: TC-1
- Depends on: none
- Parallel: no
- Tier: cheap: no code change: the evidence suite stopped on an unrelated timing flake before tests/test_waves.py
- Effort: low
- Mode: direct: a passing run of tests/test_waves.py is the fix

### T-8 Fix: AC-2 has no passing evidence
- From: J-8 (implementation-E-1, round 1)
- Files: `src/nio/implement.py`, `tests/test_waves.py`
- Serves: AC-2
- Test: TC-2
- Depends on: none
- Parallel: no
- Tier: cheap: no code change: the evidence suite stopped on an unrelated timing flake before tests/test_waves.py
- Effort: low
- Mode: direct: a passing run of tests/test_waves.py is the fix

### T-9 Fix: AC-3 has no passing evidence
- From: J-9 (implementation-E-1, round 1)
- Files: `src/nio/implement.py`, `src/nio/records.py`, `tests/test_waves.py`
- Serves: AC-3
- Test: TC-3
- Depends on: none
- Parallel: no
- Tier: cheap: no code change: the evidence suite stopped on an unrelated timing flake before tests/test_waves.py
- Effort: low
- Mode: direct: a passing run of tests/test_waves.py is the fix

### T-10 Fix: AC-5 has no passing evidence
- From: J-10 (implementation-E-1, round 1)
- Files: `src/nio/implement.py`, `src/nio/records.py`, `tests/test_waves.py`
- Serves: AC-5
- Test: TC-5
- Depends on: none
- Parallel: no
- Tier: cheap: no code change: the evidence suite stopped on an unrelated timing flake before tests/test_waves.py
- Effort: low
- Mode: direct: a passing run of tests/test_waves.py is the fix

### T-11 Fix: AC-6 has no passing evidence
- From: J-11 (implementation-E-1, round 1)
- Files: `src/nio/implement.py`, `src/nio/records.py`, `tests/test_waves.py`
- Serves: AC-6
- Test: TC-6
- Depends on: none
- Parallel: no
- Tier: cheap: no code change: the evidence suite stopped on an unrelated timing flake before tests/test_waves.py
- Effort: low
- Mode: direct: a passing run of tests/test_waves.py is the fix

### T-12 Fix: AC-11 has no passing evidence
- From: J-12 (implementation-E-1, round 1)
- Files: `skills/implement/SKILL.md`, `src/nio/agents/worker.md`, `tests/test_waves.py`
- Serves: AC-11
- Test: TC-11
- Depends on: none
- Parallel: no
- Tier: cheap: no code change: the evidence suite stopped on an unrelated timing flake before tests/test_waves.py
- Effort: low
- Mode: direct: a passing run of tests/test_waves.py is the fix

### T-13 Fix: AC-16 has no passing evidence
- From: J-13 (implementation-E-1, round 1)
- Files: `src/nio/implement.py`, `tests/test_waves.py`
- Serves: AC-16
- Test: TC-16
- Depends on: none
- Parallel: no
- Tier: cheap: no code change: the evidence suite stopped on an unrelated timing flake before tests/test_waves.py
- Effort: low
- Mode: direct: a passing run of tests/test_waves.py is the fix

### T-14 Fix: AC-17 has no passing evidence
- From: J-14 (implementation-E-1, round 1)
- Files: `src/nio/implement.py`, `tests/test_waves.py`
- Serves: AC-17
- Test: TC-17
- Depends on: none
- Parallel: no
- Tier: cheap: no code change: the evidence suite stopped on an unrelated timing flake before tests/test_waves.py
- Effort: low
- Mode: direct: a passing run of tests/test_waves.py is the fix

## E-2 Land each wave task as one commit (US-2)

### T-4 Land a green wave task on the main tree, release it from claims, restore on a failed review or commit; the review judges only its own changes
- Files: `src/nio/implement.py`, `tests/test_waves.py`
- Serves: AC-4, AC-7, AC-8, AC-9, AC-10, AC-13, AC-14, AC-15
- Test: TC-4, TC-7, TC-8, TC-9, TC-10, TC-13, TC-14, TC-15, TC-19
- Depends on: T-2
- Parallel: no
- Tier: max: applies patches onto the shared main tree in order and restores it on failure; a wrong step damages the human's tree
- Effort: high
- Mode: single: one context pack

### T-5 Shelve a blocked wave task from its worktree and remove it; claim refuses while any task is blocked
- Files: `src/nio/implement.py`, `tests/test_waves.py`
- Serves: AC-12, AC-4
- Test: TC-12, TC-18
- Depends on: T-4
- Parallel: no
- Tier: strong: the attempt cap and block paths already exist; this passes the worktree and releases one claim
- Effort: med
- Mode: single: one context pack

#### Fixes

### T-15 Fix: The third-attempt or block shelve destroys a wave task's effort-folder edits and overwrites land's fuller patch
- From: J-2 (implementation-E-2, round 1)
- Files: `src/nio/implement.py`, `tests/test_waves.py`
- Serves: CT-7, CT-2, J-2
- Test: TC-12
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

### T-16 Fix: An exception from commit after the apply leaves the applied files in the main tree with no restore
- From: J-3 (implementation-E-2, round 1)
- Files: `src/nio/implement.py`, `tests/test_waves.py`
- Serves: CT-4, J-3
- Test: TC-7
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

### T-17 Fix: The snapshot and restore miss git-quoted (non-ASCII) paths, so a failed review or commit leaves those changes applied
- From: J-4 (implementation-E-2, round 1)
- Files: `src/nio/implement.py`, `tests/test_waves.py`
- Serves: CT-4, J-4
- Test: TC-7
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

### T-18 Fix: Green on a wave task falls back to the main tree when its worktree is gone
- From: J-6 (implementation-E-2, round 1)
- Files: `src/nio/implement.py`, `tests/test_waves.py`
- Serves: CT-2, CT-3, CT-4, FR-5, J-6
- Test: TC-3
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

### T-19 Fix: The demo makes T-1 split while the quickstart assumes direct tasks
- From: J-1 (implementation-E-2, round 1)
- Files: `tests/test_waves.py`
- Serves: J-1
- Test: QS-1: `uv run python tests/test_waves.py --demo` builds a repo whose T-1 and T-2 are both direct, so QS-1 steps 1 to 4 pass when walked by hand
- Depends on: none
- Parallel: no
- Tier: cheap: a one-line fixture change
- Effort: low
- Mode: direct: a fixture change, proven by walking QS-1
