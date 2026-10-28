---
slug: 2026-10-28-plan-jury
architecture: none               # approved | none (follows the existing code's structure)
retired: [OP-1, OP-2]            # OP IDs removed from this plan; never reused
---
# Plan: the plan gate's jury

## Build order

### US-1 Plan and run the plan gate
- Delivers: CT-1, CT-2, CT-3, CT-4, CT-5, CT-13, CT-14, CT-15
- Tests: TC-1, TC-2, TC-3, TC-4, TC-5, TC-6, TC-7, TC-8, TC-9, TC-10, TC-11, TC-12, TC-13, TC-14, TC-15, TC-16, TC-17, TC-18, TC-60, TC-61, TC-62
- Scenario: QS-1

### US-2 The test-proof lens asks whether each planned test would catch a broken AC
- Depends on: US-1
- Delivers: CT-11
- Tests: TC-19, TC-20, TC-21, TC-22, TC-23, TC-24, TC-25, TC-26

### US-3 The architecture-fit lens asks whether the plan fits the code and its rules
- Depends on: US-1
- Delivers: CT-12
- Tests: TC-27, TC-28, TC-29, TC-30, TC-31, TC-32, TC-33

### US-4 New contracts name the existing code they copy
- Delivers: CT-9, CT-10
- Tests: TC-34, TC-35, TC-36, TC-37, TC-38, TC-39, TC-40, TC-41

### US-5 A plan finding is fixed in the plan, or sent back to the spec
- Depends on: US-1
- Delivers: CT-6, CT-7, CT-8
- Tests: TC-42, TC-43, TC-44, TC-45, TC-46, TC-47, TC-48, TC-49, TC-50, TC-63
- Scenario: QS-2

### US-6 The plan is approved and the tasks stage reads the approval
- Depends on: US-5
- Delivers: CT-16
- Tests: TC-51, TC-52, TC-53, TC-54, TC-55, TC-56, TC-57, TC-58, TC-59

## Coverage
| Spec ID | Contracts | Tests |
| --- | --- | --- |
| FR-1 | CT-1, CT-2 | TC-1 |
| FR-2 | CT-2 | TC-2, TC-3 |
| FR-3 | CT-1 | TC-1 |
| FR-4 | CT-2 | TC-4, TC-5 |
| FR-5 | CT-2 | TC-6, TC-10 |
| FR-6 | CT-2 | TC-9, TC-11, TC-12 |
| FR-8 | CT-2 | TC-4, TC-6, TC-9, TC-10, TC-11 |
| FR-9 | CT-2 | TC-12 |
| FR-10 | CT-4 | TC-14 |
| FR-11 | CT-3 | TC-13 |
| FR-12 | CT-5, CT-8 | TC-17, TC-48, TC-49, TC-50 |
| FR-13 | CT-15 | TC-18 |
| FR-14 | CT-11 | TC-19 |
| FR-15 | CT-11 | TC-19, TC-20 |
| FR-16 | CT-11 | TC-21, TC-22 |
| FR-17 | CT-11 | TC-23 |
| FR-18 | CT-11 | TC-24 |
| FR-19 | CT-11 | TC-25 |
| FR-20 | CT-11 | TC-26 |
| FR-21 | CT-12 | TC-27 |
| FR-22 | CT-12 | TC-27, TC-28 |
| FR-23 | CT-12 | TC-29 |
| FR-24 | CT-12 | TC-30 |
| FR-25 | CT-12 | TC-31 |
| FR-26 | CT-12 | TC-32 |
| FR-27 | CT-12 | TC-33 |
| FR-28 | CT-9, CT-10 | TC-34, TC-35, TC-39, TC-40 |
| FR-29 | CT-9 | TC-34 |
| FR-30 | CT-9 | TC-37, TC-38, TC-39 |
| FR-31 | CT-9 | TC-41 |
| FR-32 | CT-6, CT-8 | TC-42 |
| FR-33 | CT-6 | TC-43 |
| FR-34 | CT-6, CT-15 | TC-44 |
| FR-35 | CT-7 | TC-44, TC-45 |
| FR-36 | CT-15 | TC-46 |
| FR-37 | CT-15 | TC-51 |
| FR-38 | CT-16 | TC-52, TC-53, TC-58 |
| FR-39 | CT-7, CT-16 | TC-57, TC-59 |
| FR-40 | CT-11, CT-12, CT-13 | TC-7, TC-19, TC-27 |
| FR-41 | CT-6 | TC-47 |
| FR-42 | CT-4, CT-5 | TC-15 |
| FR-43 | CT-4 | TC-16 |
| FR-44 | CT-13 | TC-7 |
| FR-45 | CT-14 | TC-8 |
| FR-46 | CT-12 | TC-36 |
| FR-47 | CT-3, CT-7, CT-16 | TC-54 |
| FR-48 | CT-6 | TC-55 |
| FR-49 | CT-6, CT-7 | TC-56 |
| FR-50 | CT-5, CT-7, CT-16 | TC-57 |
| AC-1 | CT-1, CT-2 | TC-1 |
| AC-2 | CT-2 | TC-2 |
| AC-3 | CT-2 | TC-3 |
| AC-4 | CT-2 | TC-4 |
| AC-5 | CT-2 | TC-5 |
| AC-6 | CT-2 | TC-6 |
| AC-7 | CT-2 | TC-12 |
| AC-8 | CT-3 | TC-13 |
| AC-9 | CT-4 | TC-14 |
| AC-10 | CT-5, CT-8 | TC-17 |
| AC-11 | CT-15 | TC-18 |
| AC-12 | CT-11, CT-12, CT-13 | TC-19 |
| AC-13 | CT-11 | TC-20 |
| AC-14 | CT-11 | TC-21 |
| AC-15 | CT-11 | TC-22 |
| AC-16 | CT-11 | TC-23 |
| AC-17 | CT-11 | TC-24 |
| AC-18 | CT-11 | TC-25 |
| AC-19 | CT-11 | TC-26 |
| AC-20 | CT-11, CT-12, CT-13 | TC-27 |
| AC-21 | CT-12 | TC-28 |
| AC-22 | CT-12 | TC-29 |
| AC-23 | CT-12 | TC-30 |
| AC-24 | CT-12 | TC-31 |
| AC-25 | CT-12 | TC-32 |
| AC-26 | CT-12 | TC-33 |
| AC-27 | CT-9, CT-10 | TC-34 |
| AC-28 | CT-9 | TC-37 |
| AC-29 | CT-9 | TC-38 |
| AC-30 | CT-9, CT-10 | TC-39 |
| AC-31 | CT-9, CT-10 | TC-40 |
| AC-32 | CT-9 | TC-41 |
| AC-33 | CT-6, CT-8 | TC-42 |
| AC-34 | CT-6 | TC-43 |
| AC-35 | CT-6, CT-7, CT-15 | TC-44 |
| AC-36 | CT-7 | TC-45 |
| AC-37 | CT-15 | TC-46 |
| AC-38 | CT-5, CT-8 | TC-48 |
| AC-39 | CT-15 | TC-51 |
| AC-40 | CT-16 | TC-52 |
| AC-41 | CT-16 | TC-58 |
| AC-42 | CT-7, CT-16 | TC-59 |
| AC-43 | CT-6 | TC-47 |
| AC-44 | CT-4, CT-5 | TC-15 |
| AC-45 | CT-4 | TC-16 |
| AC-46 | CT-11, CT-12, CT-13 | TC-7 |
| AC-47 | CT-14 | TC-8 |
| AC-48 | CT-2 | TC-9 |
| AC-49 | CT-9, CT-10 | TC-35 |
| AC-50 | CT-12 | TC-36 |
| AC-51 | CT-5, CT-8 | TC-49 |
| AC-52 | CT-5, CT-8 | TC-50 |
| AC-53 | CT-2 | TC-10 |
| AC-54 | CT-2 | TC-11 |
| AC-55 | CT-16 | TC-53 |
| AC-56 | CT-3, CT-7, CT-16 | TC-54 |
| AC-57 | CT-6 | TC-55 |
| AC-58 | CT-6, CT-7 | TC-56 |
| AC-59 | CT-5, CT-7, CT-16 | TC-57 |
| NFR-1 | CT-2, CT-9 | TC-60 |

## Decisions
- The plan delivers `nio check plan <slug> --approved`, the check the tasks stage will call, and tests its answer; the tasks stage's own refusal is proven when #42 wires it in (grill Q12, 2026-10-28).
- The end-to-end tests in `tests/test_lenses.py` run the lenses on real models only when `NIO_E2E=1` is set; the normal self-checks stay free (grill Q13, 2026-10-28).

## Open points

