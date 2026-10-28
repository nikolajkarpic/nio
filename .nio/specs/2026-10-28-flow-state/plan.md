---
slug: 2026-10-28-flow-state
architecture: approved
retired: [OP-1]                      # OP IDs removed from this plan; never reused
---
# Plan: flow state

## Build order

### Foundation
- Delivers: CT-1, CT-2, CT-3, CT-5, CT-16, CT-19

### US-1 Any agent picks up where the effort is
- Depends on: Foundation
- Delivers: CT-4, CT-6, CT-9, CT-10, CT-13, CT-18
- Tests: TC-1, TC-2, TC-3, TC-4, TC-5, TC-6, TC-7, TC-8, TC-9, TC-11, TC-12, TC-56, TC-58, TC-59, TC-65, TC-73, TC-74, TC-75, TC-76, TC-77

### US-2 The effort moves on only when its guards pass
- Depends on: US-1
- Delivers: CT-11
- Tests: TC-13, TC-14, TC-15, TC-16, TC-17, TC-18, TC-19, TC-20, TC-21, TC-22, TC-23, TC-24, TC-25, TC-51, TC-52, TC-63, TC-64, TC-68, TC-78
- Scenario: QS-1

### US-4 The human sees every effort at a glance
- Depends on: US-2
- Delivers: CT-12, CT-14, CT-17
- Tests: TC-10, TC-31, TC-32, TC-33, TC-34, TC-35, TC-36, TC-37, TC-53, TC-55, TC-61, TC-62, TC-66, TC-67, TC-69, TC-79
- Scenario: QS-2

### US-3 The human can push a check through, on the record
- Depends on: US-4
- Delivers: CT-15
- Tests: TC-26, TC-27, TC-28, TC-29, TC-30, TC-57, TC-70, TC-72, TC-80
- Scenario: QS-3

### US-5 A change sends the effort back to the stage that owns the file
- Depends on: US-2, US-4
- Delivers: CT-7
- Tests: TC-38, TC-39, TC-40, TC-41, TC-42, TC-71
- Scenario: QS-4

### US-6 The stop list pauses an auto effort that must not go on
- Depends on: US-5
- Delivers: CT-8
- Tests: TC-43, TC-44, TC-45, TC-46, TC-47, TC-48, TC-49, TC-50, TC-54, TC-60

## Coverage
| Spec ID | Contracts | Tests |
| --- | --- | --- |
| FR-1 | CT-2, CT-18 | TC-11 |
| FR-2 | CT-6 | TC-1, TC-8 |
| FR-3 | CT-1 | TC-7 |
| FR-4 | CT-2 | TC-6, TC-13, TC-76, TC-77 |
| FR-5 | CT-2, CT-17 | TC-6, TC-36, TC-76, TC-77 |
| FR-6 | CT-1 | TC-9, TC-10, TC-58, TC-73, TC-74, TC-78, TC-79, TC-80 |
| FR-7 | CT-9, CT-16 | TC-1 |
| FR-8 | CT-6 | TC-2 |
| FR-9 | CT-4, CT-16 | TC-3 |
| FR-10 | CT-10 | TC-3, TC-6, TC-76, TC-77 |
| FR-11 | CT-4 | TC-4, TC-5 |
| FR-12 | CT-5, CT-11 | TC-13 |
| FR-13 | CT-5, CT-11 | TC-14 |
| FR-14 | CT-5 | TC-15 |
| FR-15 | CT-5 | TC-13, TC-14, TC-16 |
| FR-16 | CT-11 | TC-17 |
| FR-17 | CT-11 | TC-18 |
| FR-18 | CT-11 | TC-19 |
| FR-19 | CT-11 | TC-20 |
| FR-20 | CT-11, CT-19 | TC-21 |
| FR-21 | CT-6, CT-11 | TC-22 |
| FR-22 | CT-6 | TC-23 |
| FR-23 | CT-6 | TC-24, TC-25 |
| FR-24 | CT-11 | TC-26, TC-30 |
| FR-25 | CT-2 | TC-26, TC-27 |
| FR-26 | CT-11 | TC-28 |
| FR-27 | CT-5 | TC-29 |
| FR-28 | CT-12, CT-16 | TC-31 |
| FR-29 | CT-4 | TC-32 |
| FR-30 | CT-13 | TC-33 |
| FR-31 | CT-9 | TC-34 |
| FR-32 | CT-13 | TC-35 |
| FR-33 | CT-17 | TC-36 |
| FR-34 | CT-17 | TC-37 |
| FR-35 | CT-7 | TC-38, TC-40, TC-42 |
| FR-36 | CT-7 | TC-39 |
| FR-37 | CT-7 | TC-38, TC-39 |
| FR-38 | CT-7 | TC-41 |
| FR-39 | CT-8 | TC-43, TC-44, TC-50, TC-60 |
| FR-40 | CT-8 | TC-45 |
| FR-41 | CT-8 | TC-46, TC-47 |
| FR-42 | CT-8 | TC-48 |
| FR-43 | CT-9 | TC-49 |
| FR-44 | CT-10 | TC-49 |
| FR-45 | CT-3 | TC-12 |
| FR-46 | CT-12 | TC-31 |
| FR-47 | CT-6 | TC-51 |
| FR-48 | CT-11 | TC-52 |
| FR-49 | CT-6 | TC-52 |
| FR-50 | CT-4 | TC-53 |
| FR-51 | CT-8 | TC-54 |
| FR-52 | CT-7, CT-14, CT-18 | TC-55 |
| FR-53 | CT-10, CT-14 | TC-55 |
| FR-54 | CT-3 | TC-12, TC-56, TC-61 |
| FR-55 | CT-6 | TC-64 |
| FR-56 | CT-6 | TC-63 |
| FR-57 | CT-12, CT-15, CT-18 | TC-57 |
| FR-58 | CT-1, CT-2 | TC-58, TC-73, TC-74 |
| FR-59 | CT-1, CT-2 | TC-59, TC-75 |
| FR-60 | CT-12 | TC-10 |
| FR-61 | CT-14 | TC-62 |
| FR-62 | CT-11 | TC-72 |
| AC-1 | CT-6, CT-9, CT-16 | TC-1 |
| AC-2 | CT-6 | TC-2 |
| AC-3 | CT-4, CT-10, CT-16 | TC-3 |
| AC-4 | CT-4 | TC-4 |
| AC-5 | CT-4 | TC-5 |
| AC-6 | CT-2, CT-10, CT-17 | TC-6, TC-76, TC-77 |
| AC-7 | CT-1 | TC-7 |
| AC-8 | CT-6 | TC-8 |
| AC-9 | CT-1 | TC-9, TC-78, TC-79, TC-80 |
| AC-10 | CT-1, CT-12 | TC-10 |
| AC-11 | CT-2, CT-18 | TC-11 |
| AC-12 | CT-3 | TC-12 |
| AC-13 | CT-2, CT-5, CT-11 | TC-13 |
| AC-14 | CT-5, CT-11 | TC-14 |
| AC-15 | CT-5 | TC-15 |
| AC-16 | CT-5 | TC-16 |
| AC-17 | CT-11 | TC-17 |
| AC-18 | CT-11 | TC-18 |
| AC-19 | CT-11 | TC-19 |
| AC-20 | CT-11 | TC-20 |
| AC-21 | CT-11, CT-19 | TC-21 |
| AC-22 | CT-6, CT-11 | TC-22 |
| AC-23 | CT-6 | TC-23 |
| AC-24 | CT-6 | TC-24 |
| AC-25 | CT-6 | TC-25 |
| AC-26 | CT-2, CT-11 | TC-26 |
| AC-27 | CT-2 | TC-27 |
| AC-28 | CT-11 | TC-28 |
| AC-29 | CT-5 | TC-29 |
| AC-30 | CT-11 | TC-30 |
| AC-31 | CT-12, CT-16 | TC-31 |
| AC-32 | CT-4 | TC-32 |
| AC-33 | CT-13 | TC-33 |
| AC-34 | CT-9 | TC-34 |
| AC-35 | CT-13 | TC-35 |
| AC-36 | CT-2, CT-17 | TC-36 |
| AC-37 | CT-17 | TC-37 |
| AC-38 | CT-7 | TC-38 |
| AC-39 | CT-7 | TC-39 |
| AC-40 | CT-7 | TC-40 |
| AC-41 | CT-7 | TC-41 |
| AC-42 | CT-7 | TC-42 |
| AC-43 | CT-8 | TC-43 |
| AC-44 | CT-8 | TC-44 |
| AC-45 | CT-8 | TC-45 |
| AC-46 | CT-8 | TC-46 |
| AC-47 | CT-8 | TC-47 |
| AC-48 | CT-8 | TC-48 |
| AC-49 | CT-9, CT-10 | TC-49 |
| AC-50 | CT-8 | TC-50 |
| AC-51 | CT-6 | TC-51 |
| AC-52 | CT-6, CT-11 | TC-52 |
| AC-53 | CT-4 | TC-53 |
| AC-54 | CT-8 | TC-54 |
| AC-55 | CT-7, CT-10, CT-14, CT-18 | TC-55 |
| AC-56 | CT-3 | TC-56 |
| AC-57 | CT-12, CT-15, CT-18 | TC-57 |
| AC-58 | CT-1, CT-2 | TC-58, TC-73, TC-74 |
| AC-59 | CT-1, CT-2 | TC-59, TC-75 |
| AC-60 | CT-8 | TC-60 |
| AC-61 | CT-3 | TC-61 |
| AC-62 | CT-14 | TC-62 |
| AC-63 | CT-6 | TC-63 |
| AC-64 | CT-6 | TC-64 |
| AC-65 | CT-11 | TC-72 |
| NFR-1 | CT-9 | TC-65 |
| NFR-2 | CT-9, CT-12 | TC-66 |
| NFR-3 | CT-12 | TC-67 |

## Open points
