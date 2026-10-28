---
slug: 2026-10-27-tasks-stage
architecture: approved           # approved | none (follows the existing code's structure)
retired: []                      # OP IDs removed from this plan; never reused
---
# Plan: the tasks stage

## Build order

### US-1 Draft tasks.md from an approved spec
- Delivers: CT-1, CT-2, CT-3, CT-4, CT-8
- Tests: TC-1, TC-2, TC-3, TC-4, TC-5, TC-6, TC-7, TC-8, TC-9, TC-10, TC-11, TC-12, TC-13, TC-14, TC-15, TC-16, TC-17, TC-18, TC-19, TC-20, TC-21, TC-25, TC-26, TC-27, TC-28, TC-30, TC-31, TC-34, TC-36, TC-37, TC-41, TC-46, TC-63, TC-65
- Scenario: QS-1

### US-2 Every task carries seven fields and permanent IDs
- Depends on: US-1
- Delivers: CT-6, CT-7
- Tests: TC-45, TC-48, TC-61

### US-3 Coverage, cycles and parallel clashes are checked for free
- Depends on: US-1
- Delivers: CT-10, CT-11, CT-12
- Tests: TC-22, TC-23, TC-24

### US-4 The evaluator rates each task's model tier and effort
- Depends on: US-1
- Delivers: CT-9
- Tests: TC-32, TC-47

### US-5 The human sees the estimate and approves before implementation
- Depends on: US-3
- Delivers: CT-5, CT-14
- Tests: TC-29, TC-33, TC-35, TC-42, TC-49, TC-50, TC-51, TC-52, TC-62, TC-64
- Scenario: QS-2

### US-6 Tasks added later go under Fixes and cite their source
- Depends on: US-1
- Delivers: CT-16
- Tests: TC-38, TC-39, TC-40, TC-53, TC-54, TC-55, TC-56, TC-57
- Scenario: QS-3

### US-7 Status, "finished" and each epic's jury ledger are fixed
- Depends on: US-1
- Delivers: CT-13, CT-15
- Tests: TC-43, TC-44, TC-58, TC-59, TC-60

## Coverage
| Spec ID | Contracts | Tests |
| --- | --- | --- |
| FR-1 | CT-1, CT-8 | TC-1 |
| FR-2 | CT-1, CT-3 | TC-3, TC-25, TC-30, TC-31 |
| FR-3 | CT-2 | TC-1 |
| FR-4 | CT-1, CT-8 | TC-1 |
| FR-5 | CT-1, CT-8 | TC-2, TC-27 |
| FR-6 | CT-2 | TC-11 |
| FR-7 | CT-2 | TC-7 |
| FR-8 | CT-4 | TC-7 |
| FR-9 | CT-4 | TC-8, TC-9, TC-28 |
| FR-10 | CT-4 | TC-15, TC-21 |
| FR-11 | CT-4 | TC-16, TC-21 |
| FR-12 | CT-4 | TC-17, TC-18, TC-21 |
| FR-13 | CT-4 | TC-19, TC-20, TC-21 |
| FR-14 | CT-5 | TC-49, TC-50 |
| FR-15 | CT-2 | TC-13 |
| FR-16 | CT-4 | TC-13 |
| FR-17 | CT-7 | TC-48 |
| FR-18 | CT-1, CT-9 | TC-47 |
| FR-19 | CT-1, CT-8 | TC-6 |
| FR-20 | CT-1, CT-8 | TC-5 |
| FR-21 | CT-1, CT-8 | TC-6 |
| FR-23 | CT-2 | TC-14 |
| FR-24 | CT-4 | TC-14 |
| FR-25 | CT-15 | TC-43, TC-44, TC-58 |
| FR-26 | CT-15 | TC-59 |
| FR-27 | CT-1, CT-16 | TC-53, TC-55 |
| FR-28 | CT-16 | TC-56 |
| FR-29 | CT-1, CT-16 | TC-54 |
| FR-30 | CT-16 | TC-57 |
| FR-31 | CT-13 | TC-60 |
| FR-32 | CT-1, CT-11 | TC-22 |
| FR-33 | CT-14 | TC-42, TC-51, TC-52 |
| FR-34 | CT-4 | TC-46 |
| FR-35 | CT-6 | TC-61 |
| FR-36 | CT-4 | TC-12 |
| FR-37 | CT-4 | TC-12 |
| FR-38 | CT-4 | TC-11 |
| FR-39 | CT-1, CT-3 | TC-4 |
| FR-40 | CT-4 | TC-10 |
| FR-41 | CT-10 | TC-23 |
| FR-42 | CT-11 | TC-24 |
| FR-43 | CT-9 | TC-32 |
| FR-44 | CT-1, CT-14 | TC-33, TC-42 |
| FR-45 | CT-4 | TC-34 |
| FR-47 | CT-5 | TC-35 |
| FR-48 | CT-4 | TC-36, TC-37 |
| FR-49 | CT-16 | TC-38 |
| FR-50 | CT-16 | TC-39, TC-40 |
| FR-51 | CT-1, CT-8 | TC-41 |
| FR-52 | CT-7 | TC-45 |
| FR-53 | CT-4 | TC-5 |
| FR-54 | CT-1, CT-8 | TC-26 |
| FR-55 | CT-4, CT-8 | TC-28 |
| FR-56 | CT-12, CT-14 | TC-29 |
| AC-1 | CT-1, CT-2, CT-8 | TC-1 |
| AC-2 | CT-1, CT-8 | TC-2 |
| AC-3 | CT-1, CT-3 | TC-3 |
| AC-4 | CT-1, CT-3 | TC-4 |
| AC-5 | CT-1, CT-4, CT-8 | TC-5 |
| AC-6 | CT-1, CT-8 | TC-6 |
| AC-8 | CT-2, CT-4 | TC-7 |
| AC-9 | CT-4 | TC-8 |
| AC-10 | CT-4 | TC-9 |
| AC-11 | CT-4 | TC-10 |
| AC-12 | CT-2, CT-4 | TC-11 |
| AC-13 | CT-4 | TC-12 |
| AC-14 | CT-2, CT-4 | TC-13 |
| AC-15 | CT-2, CT-4 | TC-14 |
| AC-16 | CT-4 | TC-15 |
| AC-17 | CT-4 | TC-16 |
| AC-18 | CT-4 | TC-17 |
| AC-19 | CT-4 | TC-18 |
| AC-20 | CT-4 | TC-19 |
| AC-21 | CT-4 | TC-20 |
| AC-22 | CT-4 | TC-21 |
| AC-23 | CT-1, CT-11 | TC-22 |
| AC-24 | CT-4 | TC-46 |
| AC-25 | CT-1, CT-9 | TC-47 |
| AC-26 | CT-7 | TC-48 |
| AC-27 | CT-5 | TC-49 |
| AC-28 | CT-5 | TC-50 |
| AC-29 | CT-14 | TC-51 |
| AC-30 | CT-14 | TC-52 |
| AC-31 | CT-1, CT-16 | TC-53 |
| AC-32 | CT-1, CT-16 | TC-54 |
| AC-33 | CT-1, CT-16 | TC-55 |
| AC-34 | CT-16 | TC-56 |
| AC-35 | CT-16 | TC-57 |
| AC-36 | CT-15 | TC-58 |
| AC-37 | CT-15 | TC-59 |
| AC-38 | CT-13 | TC-60 |
| AC-39 | CT-6 | TC-61 |
| AC-40 | CT-10 | TC-23 |
| AC-41 | CT-11 | TC-24 |
| AC-42 | CT-1, CT-3 | TC-30 |
| AC-43 | CT-1, CT-3 | TC-31 |
| AC-44 | CT-9 | TC-32 |
| AC-45 | CT-1, CT-14 | TC-33 |
| AC-46 | CT-4 | TC-34 |
| AC-48 | CT-5 | TC-35 |
| AC-49 | CT-4 | TC-36 |
| AC-50 | CT-4 | TC-37 |
| AC-51 | CT-16 | TC-38 |
| AC-52 | CT-16 | TC-39 |
| AC-53 | CT-16 | TC-40 |
| AC-54 | CT-1, CT-8 | TC-41 |
| AC-55 | CT-1, CT-14 | TC-42 |
| AC-56 | CT-15 | TC-43 |
| AC-57 | CT-15 | TC-44 |
| AC-58 | CT-7 | TC-45 |
| AC-59 | CT-1, CT-3 | TC-25 |
| AC-60 | CT-1, CT-8 | TC-26 |
| AC-61 | CT-1, CT-8 | TC-27 |
| AC-62 | CT-4, CT-8 | TC-28 |
| AC-63 | CT-12, CT-14 | TC-29 |
| NFR-1 | CT-4, CT-5 | TC-62 |

## Decisions
- The implement stage's refusals (AC-29, AC-30, AC-55, AC-63) are tested through `tasks.approved`, and an epic's being finished (AC-37) through `tasks.finished`, which those stages will call (plan-jury grill Q12, 2026-10-28). The state machine's refusals (AC-36, AC-56, AC-57) wait for #45, as the spec's non-goal says; their tests live in `tests/test_flow.py`.
- The tasks approval covers the planned tasks, the plan and the spec, not the `#### Fixes` sections, so the implementation jury appends fix tasks without a new approval (FR-27, FR-50; plan jury J-1).
- An epic's dependencies are its tasks' dependencies; `tasks.md` has no epic-level line (plan jury J-9).
- End-to-end tests of the drafter and the evaluator run on real models only with `NIO_E2E=1`, as `tests/test_lenses.py` does (plan-jury grill Q13, 2026-10-28).

## Open points

