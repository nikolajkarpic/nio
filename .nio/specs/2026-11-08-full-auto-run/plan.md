---
slug: 2026-11-08-full-auto-run
architecture: approved           # approved | none (follows the existing code's structure)
retired: []                      # OP IDs removed from this plan; never reused
---
# Plan: full-auto run

## Build order
### Foundation
- Delivers: CT-4, CT-9, CT-19
- Tests: TC-17

### US-1 The human grants auto once the spec draft is written
- Depends on: Foundation
- Delivers: CT-1, CT-2
- Tests: TC-1, TC-2, TC-3, TC-29, TC-42

### US-2 The driver runs every stage to the end
- Depends on: US-1
- Delivers: CT-5, CT-6, CT-16
- Tests: TC-5, TC-9, TC-11, TC-38, TC-43, TC-44, TC-46, TC-48

### US-3 The fixer settles jury findings within its authority
- Depends on: US-2
- Delivers: CT-10, CT-11, CT-12, CT-13, CT-17, CT-18
- Tests: TC-12, TC-13, TC-14, TC-15, TC-16, TC-19, TC-20, TC-34, TC-36, TC-37, TC-39, TC-47

### US-5 Budgets default to what the effort's gates need
- Depends on: US-2
- Delivers: CT-7
- Tests: TC-8, TC-25, TC-26, TC-32, TC-33, TC-41
- Scenario: QS-2

### US-6 Risky specs still stop at every gate
- Depends on: US-2
- Delivers: CT-8
- Tests: TC-27, TC-28

### US-7 The human keeps control of the grant
- Depends on: US-3
- Delivers: CT-3
- Tests: TC-18, TC-30, TC-31

### US-4 The run ends in a pull request that is the one report
- Depends on: US-3, US-5, US-6, US-7
- Delivers: CT-14, CT-15
- Tests: TC-4, TC-6, TC-7, TC-10, TC-21, TC-22, TC-23, TC-24, TC-35, TC-40, TC-45
- Scenario: QS-1, QS-3

## Coverage
| Spec ID | Contracts | Tests |
| --- | --- | --- |
| FR-1 | CT-1, CT-4 | TC-1 |
| FR-2 | CT-2, CT-4 | TC-2 |
| FR-3 | CT-1, CT-2 | TC-1, TC-2 |
| FR-4 | CT-1, CT-2 | TC-3 |
| FR-5 | CT-16 | TC-11, TC-4, TC-5 |
| FR-6 | CT-16 | TC-6, TC-7 |
| FR-7 | CT-18 | TC-16 |
| FR-8 | CT-18 | TC-16 |
| FR-9 | CT-11, CT-12, CT-17 | TC-12 |
| FR-10 | CT-11, CT-17, CT-6 | TC-13 |
| FR-11 | CT-11, CT-13, CT-17, CT-6 | TC-14 |
| FR-12 | CT-13, CT-6 | TC-15 |
| FR-13 | CT-9 | TC-17 |
| FR-14 | CT-9 | TC-17, TC-18 |
| FR-15 | CT-10 | TC-19 |
| FR-16 | CT-11, CT-12, CT-16 | TC-20 |
| FR-17 | CT-12, CT-14 | TC-21 |
| FR-18 | CT-6 | TC-25, TC-32 |
| FR-19 | CT-6 | TC-26 |
| FR-20 | CT-15, CT-4 | TC-22 |
| FR-21 | CT-15 | TC-22 |
| FR-22 | CT-14 | TC-23 |
| FR-23 | CT-14 | TC-23 |
| FR-24 | CT-15 | TC-24 |
| FR-25 | CT-16, CT-6 | TC-5 |
| FR-26 | CT-16, CT-3, CT-7 | TC-28, TC-8 |
| FR-27 | CT-16 | TC-10 |
| FR-28 | CT-16, CT-8 | TC-27, TC-28 |
| FR-29 | CT-4, CT-5 | TC-9 |
| FR-30 | CT-1, CT-19, CT-2 | TC-29, TC-42 |
| FR-31 | CT-1 | TC-30 |
| FR-32 | CT-3, CT-4 | TC-31 |
| FR-33 | CT-6 | TC-33 |
| FR-34 | CT-12, CT-6 | TC-34 |
| FR-35 | CT-16, CT-6 | TC-35 |
| FR-36 | CT-13, CT-6 | TC-36 |
| FR-37 | CT-13, CT-6 | TC-37 |
| FR-38 | CT-5 | TC-38, TC-43, TC-44 |
| FR-39 | CT-12, CT-14, CT-6 | TC-39, TC-40 |
| FR-40 | CT-6, CT-7 | TC-41 |
| FR-41 | CT-15 | TC-45 |
| AC-1 | CT-1, CT-2, CT-4 | TC-1 |
| AC-2 | CT-1, CT-2, CT-4 | TC-2 |
| AC-3 | CT-1, CT-2 | TC-3 |
| AC-4 | CT-16 | TC-4 |
| AC-5 | CT-16, CT-6 | TC-5 |
| AC-6 | CT-16 | TC-6 |
| AC-7 | CT-16 | TC-7 |
| AC-8 | CT-16, CT-3, CT-7 | TC-8 |
| AC-9 | CT-4, CT-5 | TC-9 |
| AC-10 | CT-16 | TC-10 |
| AC-11 | CT-16 | TC-11 |
| AC-12 | CT-11, CT-12, CT-17 | TC-12 |
| AC-13 | CT-11, CT-17, CT-6 | TC-13 |
| AC-14 | CT-11, CT-13, CT-17, CT-6 | TC-14 |
| AC-15 | CT-13, CT-6 | TC-15 |
| AC-16 | CT-18 | TC-16 |
| AC-17 | CT-9 | TC-17 |
| AC-18 | CT-9 | TC-18 |
| AC-19 | CT-10 | TC-19 |
| AC-20 | CT-11, CT-12, CT-16 | TC-20 |
| AC-21 | CT-12, CT-14 | TC-21 |
| AC-22 | CT-15, CT-4 | TC-22 |
| AC-23 | CT-14 | TC-23 |
| AC-24 | CT-15 | TC-24 |
| AC-25 | CT-6 | TC-25 |
| AC-26 | CT-6 | TC-26 |
| AC-27 | CT-16, CT-8 | TC-27 |
| AC-28 | CT-16, CT-3, CT-7, CT-8 | TC-28 |
| AC-29 | CT-1, CT-19, CT-2 | TC-29 |
| AC-30 | CT-1 | TC-30 |
| AC-31 | CT-3, CT-4 | TC-31 |
| AC-32 | CT-6 | TC-32 |
| AC-33 | CT-6 | TC-33 |
| AC-34 | CT-12, CT-6 | TC-34 |
| AC-35 | CT-16, CT-6 | TC-35 |
| AC-36 | CT-13, CT-6 | TC-36 |
| AC-37 | CT-13, CT-6 | TC-37 |
| AC-38 | CT-5 | TC-38 |
| AC-39 | CT-12, CT-14, CT-6 | TC-39 |
| AC-40 | CT-12, CT-14, CT-6 | TC-40 |
| AC-41 | CT-6, CT-7 | TC-41 |
| AC-42 | CT-1, CT-19, CT-2 | TC-42 |
| AC-43 | CT-5 | TC-43 |
| AC-44 | CT-5 | TC-44 |
| AC-45 | CT-15 | TC-45 |
| NFR-2 | CT-16, CT-5 | TC-46 |

## Decisions
- The plan follows `architecture.md` (approved by the human, 2026-11-08): a driver skill, a fixer card, a git-ignored driver claim, three new history kinds, `--by auto` and `held` in the ledger, a CLI round check and a CLI-built report.
- The driver claim goes stale on its refresh time alone; FR-38 and AC-38 change through C-261108-mplt (pending), and TC-38 tests the new wording.
- The grant line records `unknown` for a model it can't detect, which keeps AC-42 as written (the human, 2026-11-08).
- [agent] An epic's gate has no fixer: its confirmed findings already become fix tasks the implement stage runs (FR-16).
- [agent] Minors are left out of what holds a gate under auto, as the epic gate already does, instead of the fixer disposing each (FR-17).
