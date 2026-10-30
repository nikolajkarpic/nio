---
slug: 2026-10-27-implementation-jury
architecture: approved
retired: []                      # OP IDs removed from this plan; never reused
---
# Plan: implementation jury

## Build order

### Foundation
- Delivers: CT-2, CT-7, CT-18
- Tests: none: proven through the stories tests

### US-1 The gate runs only on an implemented epic
- Depends on: Foundation
- Delivers: CT-1, CT-17
- Tests: TC-2, TC-3, TC-70
- Scenario: QS-1

### US-2 The CLI collects observed evidence before any lens runs
- Depends on: US-1
- Delivers: CT-3, CT-4, CT-5, CT-6, CT-20
- Tests: TC-7, TC-8, TC-9, TC-11, TC-12, TC-15, TC-16, TC-40, TC-41, TC-42, TC-43, TC-62, TC-63

### US-7 Lens cards know the implementation gate
- Depends on: US-2
- Delivers: CT-10
- Tests: TC-60, TC-61

### US-3 The lens plan has two core lenses, triggered lenses and a cap
- Depends on: US-7
- Delivers: CT-8
- Tests: TC-1, TC-19, TC-20, TC-21, TC-22, TC-67
- Scenario: QS-4

### US-4 Jurors read a focused pack and never run code
- Depends on: US-3
- Delivers: CT-9, CT-11
- Tests: TC-10, TC-17, TC-25, TC-26, TC-27, TC-28, TC-29, TC-30

### US-5 Findings carry a gap type and are grounded in the code
- Depends on: US-4
- Delivers: CT-12, CT-13, CT-21
- Tests: TC-4, TC-5, TC-6, TC-13, TC-14, TC-18, TC-23, TC-31, TC-32, TC-33, TC-34, TC-35, TC-36, TC-37, TC-39, TC-45, TC-48, TC-49, TC-66, TC-68, TC-73

### US-6 Findings become appended tasks or change requests, and the outcome follows the spec jury
- Depends on: US-5
- Delivers: CT-14, CT-15, CT-16, CT-19
- Tests: TC-24, TC-38, TC-44, TC-46, TC-47, TC-50, TC-51, TC-52, TC-53, TC-54, TC-55, TC-56, TC-57, TC-58, TC-59, TC-64, TC-65, TC-69, TC-71, TC-72, TC-74, TC-75
- Scenario: QS-2, QS-3

## Coverage
| Spec ID | Contracts | Tests |
| --- | --- | --- |
| FR-1 | CT-1, CT-17, CT-19 | TC-1, TC-58, TC-69, TC-70, TC-75 |
| FR-2 | CT-1 | TC-2, TC-3 |
| FR-3 | CT-3, CT-7 | TC-4, TC-18 |
| FR-4 | CT-10, CT-21 | TC-4, TC-39 |
| FR-5 | CT-10, CT-12, CT-21 | TC-5, TC-6, TC-73 |
| FR-6 | CT-3, CT-4 | TC-7 |
| FR-7 | CT-3, CT-4 | TC-7 |
| FR-8 | CT-4 | TC-7, TC-8, TC-9 |
| FR-9 | CT-5 | TC-10 |
| FR-10 | CT-6, CT-12, CT-20 | TC-11, TC-12, TC-13, TC-45 |
| FR-11 | CT-3, CT-7 | TC-15 |
| FR-12 | CT-3, CT-7 | TC-16, TC-18 |
| FR-13 | CT-5 | TC-17 |
| FR-14 | CT-8, CT-19 | TC-19 |
| FR-15 | CT-8 | TC-20, TC-21, TC-22, TC-67 |
| FR-16 | CT-8 | TC-23, TC-24 |
| FR-17 | CT-9 | TC-25 |
| FR-18 | CT-9 | TC-26 |
| FR-19 | CT-10 | TC-26 |
| FR-20 | CT-11 | TC-27, TC-28, TC-29, TC-30 |
| FR-21 | CT-12 | TC-31, TC-35 |
| FR-22 | CT-12 | TC-32 |
| FR-23 | CT-12 | TC-33 |
| FR-24 | CT-12, CT-20 | TC-34, TC-36, TC-68 |
| FR-25 | CT-13 | TC-50, TC-56, TC-72, TC-74 |
| FR-26 | CT-14, CT-17 | TC-38, TC-50, TC-58, TC-69, TC-72, TC-74, TC-75 |
| FR-27 | CT-14 | TC-51 |
| FR-28 | CT-13 | TC-52 |
| FR-29 | CT-14 | TC-53 |
| FR-30 | CT-15 | TC-54, TC-71 |
| FR-31 | CT-13, CT-16 | TC-55 |
| FR-32 | CT-13 | TC-56, TC-58, TC-69, TC-75 |
| FR-33 | CT-16 | TC-57 |
| FR-34 | CT-10 | TC-60 |
| FR-35 | CT-10 | TC-61 |
| FR-36 | CT-5 | TC-13, TC-14, TC-45 |
| FR-37 | CT-14 | TC-59 |
| FR-38 | CT-13 | TC-37 |
| FR-39 | CT-5, CT-21 | TC-39 |
| FR-40 | CT-2 | TC-40, TC-41 |
| FR-41 | CT-2, CT-7 | TC-43 |
| FR-42 | CT-3, CT-20 | TC-42 |
| FR-43 | CT-13 | TC-44 |
| FR-44 | CT-15, CT-17 | TC-46, TC-47 |
| FR-45 | CT-18 | TC-48 |
| FR-46 | CT-18 | TC-49 |
| AC-1 | CT-1, CT-17, CT-19 | TC-1, TC-70 |
| AC-2 | CT-1 | TC-2 |
| AC-3 | CT-1 | TC-3 |
| AC-4 | CT-10, CT-21, CT-3, CT-7 | TC-4 |
| AC-5 | CT-10, CT-12, CT-21 | TC-5 |
| AC-6 | CT-10, CT-12, CT-21 | TC-6, TC-73 |
| AC-7 | CT-3, CT-4 | TC-7 |
| AC-8 | CT-4 | TC-8 |
| AC-9 | CT-4 | TC-9 |
| AC-10 | CT-5 | TC-10 |
| AC-11 | CT-12, CT-20, CT-6 | TC-11 |
| AC-12 | CT-12, CT-20, CT-6 | TC-12 |
| AC-13 | CT-12, CT-20, CT-5, CT-6 | TC-13 |
| AC-43 | CT-5 | TC-14 |
| AC-14 | CT-3, CT-7 | TC-15 |
| AC-15 | CT-3, CT-7 | TC-16 |
| AC-16 | CT-5 | TC-17 |
| AC-17 | CT-3, CT-7 | TC-18 |
| AC-18 | CT-8, CT-19 | TC-19 |
| AC-19 | CT-8 | TC-20 |
| AC-20 | CT-8 | TC-21, TC-67 |
| AC-21 | CT-8 | TC-22 |
| AC-22 | CT-8 | TC-23 |
| AC-23 | CT-8 | TC-24 |
| AC-24 | CT-9 | TC-25 |
| AC-25 | CT-9, CT-10 | TC-26 |
| AC-26 | CT-11 | TC-27 |
| AC-27 | CT-11 | TC-28 |
| AC-44 | CT-11 | TC-29 |
| AC-45 | CT-11 | TC-30 |
| AC-28 | CT-12 | TC-31 |
| AC-29 | CT-12 | TC-32 |
| AC-30 | CT-12 | TC-33 |
| AC-31 | CT-12, CT-20 | TC-34, TC-68 |
| AC-47 | CT-12 | TC-35 |
| AC-48 | CT-12, CT-20 | TC-36 |
| AC-49 | CT-13 | TC-37 |
| AC-50 | CT-14, CT-17 | TC-38 |
| AC-51 | CT-10, CT-21, CT-5 | TC-39 |
| AC-52 | CT-2 | TC-40 |
| AC-53 | CT-2 | TC-41 |
| AC-54 | CT-20, CT-3 | TC-42 |
| AC-55 | CT-2, CT-7 | TC-43 |
| AC-56 | CT-13 | TC-44 |
| AC-57 | CT-12, CT-20, CT-5, CT-6 | TC-45 |
| AC-58 | CT-15, CT-17 | TC-46 |
| AC-59 | CT-15, CT-17 | TC-47 |
| AC-60 | CT-18 | TC-48 |
| AC-61 | CT-18 | TC-49 |
| AC-32 | CT-13, CT-14, CT-17 | TC-50, TC-72, TC-74 |
| AC-33 | CT-14 | TC-51 |
| AC-34 | CT-13 | TC-52 |
| AC-35 | CT-14 | TC-53 |
| AC-36 | CT-15 | TC-54, TC-71 |
| AC-37 | CT-13, CT-16 | TC-55 |
| AC-38 | CT-13 | TC-56 |
| AC-39 | CT-16 | TC-57 |
| AC-40 | CT-1, CT-17, CT-19, CT-14, CT-13 | TC-58, TC-69, TC-75 |
| AC-46 | CT-14 | TC-59 |
| AC-41 | CT-10 | TC-60 |
| AC-42 | CT-10 | TC-61 |
| NFR-1 | none | TC-62 |

## Decisions
- The next epic waits for this epic's gate, and unset lint or type-check commands are reported and skipped: grill Q22, Q23 (architecture.md, 2026-10-30).
- The CLI's findings skip the refuter, a reviewer states the right side with the spec as default, the tests run in a local clone, old skipped epics stay closed and are reported, and a new major in a re-review goes to the human: grill Q25 to Q29 (2026-10-30).
