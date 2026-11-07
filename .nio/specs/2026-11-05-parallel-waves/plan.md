---
slug: 2026-11-05-parallel-waves
architecture: none               # approved | none (follows the existing code's structure)
retired: []                      # OP IDs removed from this plan; never reused
---
# Plan: parallel waves

## Build order

### US-1 Claim and work a wave in worktrees
- Delivers: CT-1, CT-2, CT-3, CT-6, CT-8
- Tests: TC-1, TC-2, TC-3, TC-5, TC-6, TC-11, TC-16, TC-17

### US-2 Land each wave task as one commit
- Depends on: US-1
- Delivers: CT-4, CT-5, CT-7
- Tests: TC-4, TC-7, TC-8, TC-9, TC-10, TC-12, TC-13, TC-14, TC-15, TC-18, TC-19
- Scenario: QS-1

## Coverage
| Spec ID | Contracts | Tests |
| --- | --- | --- |
| FR-1 | CT-1 | TC-1 |
| FR-2 | CT-1 | TC-2 |
| FR-3 | CT-1 | TC-1 |
| FR-4 | CT-2 | TC-3 |
| FR-5 | CT-3 | TC-3 |
| FR-6 | CT-4, CT-5 | TC-7, TC-14, TC-15 |
| FR-7 | CT-4 | TC-8, TC-15 |
| FR-8 | CT-4, CT-7 | TC-9, TC-19 |
| FR-9 | CT-1 | TC-4, TC-18 |
| FR-10 | CT-6 | TC-5 |
| FR-11 | CT-3 | TC-6 |
| FR-12 | CT-8 | TC-11 |
| FR-13 | CT-2, CT-7 | TC-12 |
| FR-14 | CT-4 | TC-13 |
| FR-15 | CT-1 | TC-17 |
| FR-16 | CT-4 | TC-10 |
| FR-17 | CT-2 | TC-16 |
| AC-1 | CT-1 | TC-1 |
| AC-2 | CT-1 | TC-2 |
| AC-3 | CT-2, CT-3 | TC-3 |
| AC-4 | CT-1 | TC-4, TC-18 |
| AC-5 | CT-6 | TC-5 |
| AC-6 | CT-3 | TC-6 |
| AC-7 | CT-4, CT-5 | TC-7 |
| AC-8 | CT-4 | TC-8 |
| AC-9 | CT-4, CT-7 | TC-9, TC-19 |
| AC-10 | CT-4 | TC-10 |
| AC-11 | CT-8 | TC-11 |
| AC-12 | CT-2, CT-7 | TC-12 |
| AC-13 | CT-4 | TC-13 |
| AC-14 | CT-4, CT-5 | TC-14 |
| AC-15 | CT-4, CT-5 | TC-15 |
| AC-16 | CT-2 | TC-16 |
| AC-17 | CT-1 | TC-17 |
## Decisions
- No architecture stage: every change extends existing functions in `implement.py` and `records.py`; no new module, dependency or state key (the wave lives in the existing `claims` object, the worktree path on the existing `claim` line) (plan, agent, 2026-11-06).
- A wave's `claims` is `{"task": <first>, "wave": [ids]}`, so today's "`<T-n>` is claimed" guard and `nio flow next` keep working unchanged (plan, agent, 2026-11-06).
- The patch is made in the worktree with `git add -A` and `git diff --cached --binary <claim commit>`, so untracked files ride along; `git apply` leaves out the effort's `state.json` and `history.jsonl` (plan, agent, 2026-11-06).
- `nio` resolves to the project root only inside `.nio/runs/<run>/worktree`, so the human's own linked worktrees keep their own root (plan, agent, 2026-11-06).
- The new tests go in their own `tests/test_waves.py`, reusing `tests/test_implement.py`'s helpers (plan, agent, 2026-11-06).
