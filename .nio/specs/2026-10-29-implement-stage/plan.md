---
slug: 2026-10-29-implement-stage
architecture: approved
retired: []                      # OP IDs removed from this plan; never reused
---
# Plan: implement stage

## Build order

### Foundation
- Delivers: CT-1, CT-2, CT-3, CT-4, CT-16
- Tests: none: Foundation's functions are proven through the stories' tests

### US-1 Each task runs in a fresh worker with only its pack
- Depends on: Foundation
- Delivers: CT-5, CT-6, CT-15, CT-17
- Tests: TC-1, TC-2, TC-3, TC-4, TC-5, TC-6, TC-7, TC-19, TC-27, TC-34, TC-40, TC-46

### US-2 Red and green are proven by the CLI, not claimed
- Depends on: US-1
- Delivers: CT-7, CT-8, CT-10, CT-12
- Tests: TC-35, TC-38, TC-9, TC-10, TC-11, TC-12, TC-13, TC-14, TC-15, TC-16, TC-17, TC-18, TC-21, TC-23, TC-33, TC-36, TC-37, TC-41, TC-42, TC-43, TC-44, TC-45, TC-49, TC-50, TC-52
- Scenario: QS-1

### US-4 Each done task is committed on the effort branch
- Depends on: US-2
- Delivers: CT-9
- Tests: TC-20, TC-22, TC-26, TC-47, TC-51

### US-3 A worker stops on a spec problem and files a change request
- Depends on: US-2
- Delivers: CT-11
- Tests: TC-24, TC-25, TC-48, TC-53
- Scenario: QS-2

### US-5 An epic finishes and the effort moves on
- Depends on: US-4
- Delivers: CT-13, CT-14
- Tests: TC-8, TC-28, TC-29, TC-30, TC-31, TC-32, TC-39, TC-54
- Scenario: QS-3

## Coverage
| Spec ID | Contracts | Tests |
| --- | --- | --- |
| FR-1 | CT-4, CT-5 | TC-8 |
| FR-2 | CT-5 | TC-6 |
| FR-3 | CT-4, CT-5 | TC-4, TC-5 |
| FR-4 | CT-6 | TC-1 |
| FR-5 | CT-15, CT-17 | TC-2 |
| FR-6 | CT-5, CT-15 | TC-2, TC-3 |
| FR-7 | CT-5 | TC-3 |
| FR-8 | CT-1, CT-2, CT-7 | TC-9, TC-10, TC-11, TC-43 |
| FR-9 | CT-2, CT-7 | TC-12 |
| FR-10 | CT-7 | TC-9, TC-33 |
| FR-11 | CT-7 | TC-15 |
| FR-12 | CT-1, CT-8 | TC-13, TC-14 |
| FR-13 | CT-8 | TC-15 |
| FR-14 | CT-1, CT-3, CT-8 | TC-16, TC-44 |
| FR-15 | CT-8 | TC-17 |
| FR-16 | CT-1, CT-3, CT-5 | TC-19 |
| FR-17 | CT-3, CT-8 | TC-16 |
| FR-18 | CT-4 | TC-20 |
| FR-19 | CT-9 | TC-26, TC-47 |
| FR-20 | CT-5, CT-9 | TC-27, TC-46 |
| FR-21 | CT-9 | TC-28 |
| FR-22 | CT-5 | TC-7 |
| FR-23 | CT-11, CT-15 | TC-24 |
| FR-24 | CT-11, CT-17 | TC-25, TC-48 |
| FR-25 | CT-8 | TC-18, TC-45 |
| FR-26 | CT-10 | TC-23 |
| FR-27 | CT-13, CT-14 | TC-29 |
| FR-28 | CT-13, CT-17 | TC-29 |
| FR-29 | CT-13 | TC-30 |
| FR-30 | CT-13, CT-14 | TC-31 |
| FR-31 | CT-4, CT-13 | TC-32 |
| FR-32 | CT-7, CT-8 | TC-22 |
| FR-33 | CT-8 | TC-21 |
| FR-34 | CT-2 | TC-38 |
| FR-35 | CT-5 | TC-34 |
| FR-36 | CT-3, CT-5 | TC-35 |
| FR-37 | CT-7, CT-8, CT-10 | TC-37 |
| FR-38 | CT-12 | TC-36 |
| FR-39 | CT-4 | TC-39 |
| FR-40 | CT-4, CT-5, CT-16, CT-17 | TC-40 |
| FR-41 | CT-7, CT-8 | TC-41 |
| FR-42 | CT-7, CT-15 | TC-42 |
| FR-43 | CT-2, CT-7 | TC-43 |
| FR-44 | CT-1, CT-7 | TC-49 |
| FR-45 | CT-8 | TC-50 |
| AC-1 | CT-6 | TC-1 |
| AC-2 | CT-5, CT-15, CT-17 | TC-2 |
| AC-3 | CT-5, CT-15 | TC-3 |
| AC-4 | CT-4, CT-5 | TC-4 |
| AC-5 | CT-4, CT-5 | TC-5 |
| AC-6 | CT-5 | TC-6 |
| AC-7 | CT-5 | TC-7 |
| AC-8 | CT-4, CT-5 | TC-8 |
| AC-9 | CT-1, CT-2, CT-7 | TC-9 |
| AC-10 | CT-1, CT-2, CT-7 | TC-10 |
| AC-11 | CT-1, CT-2, CT-7 | TC-11 |
| AC-12 | CT-2, CT-7 | TC-12 |
| AC-13 | CT-1, CT-8 | TC-13 |
| AC-14 | CT-1, CT-8 | TC-14 |
| AC-15 | CT-7, CT-8 | TC-15 |
| AC-16 | CT-1, CT-3, CT-8 | TC-16 |
| AC-17 | CT-8 | TC-17 |
| AC-18 | CT-8 | TC-18 |
| AC-19 | CT-1, CT-3, CT-5 | TC-19 |
| AC-20 | CT-4 | TC-20 |
| AC-21 | CT-8 | TC-21 |
| AC-22 | CT-7, CT-8 | TC-22 |
| AC-23 | CT-10 | TC-23 |
| AC-24 | CT-11, CT-15 | TC-24 |
| AC-25 | CT-11, CT-17 | TC-25 |
| AC-26 | CT-9 | TC-26 |
| AC-27 | CT-5, CT-9 | TC-27 |
| AC-28 | CT-9 | TC-28 |
| AC-29 | CT-13, CT-14, CT-17 | TC-29 |
| AC-30 | CT-13 | TC-30 |
| AC-31 | CT-13, CT-14 | TC-31 |
| AC-32 | CT-4, CT-13 | TC-32 |
| AC-33 | CT-7 | TC-33 |
| AC-34 | CT-5 | TC-34 |
| AC-35 | CT-3, CT-5 | TC-35 |
| AC-36 | CT-12 | TC-36 |
| AC-37 | CT-7, CT-8, CT-10 | TC-37 |
| AC-38 | CT-2 | TC-38 |
| AC-39 | CT-4 | TC-39 |
| AC-40 | CT-4, CT-5, CT-16, CT-17 | TC-40 |
| AC-41 | CT-7, CT-8 | TC-41 |
| AC-42 | CT-7, CT-15 | TC-42 |
| AC-43 | CT-1, CT-2, CT-7 | TC-43 |
| AC-44 | CT-1, CT-3, CT-8 | TC-44 |
| AC-45 | CT-8 | TC-45 |
| AC-46 | CT-5, CT-9 | TC-46 |
| AC-47 | CT-9 | TC-47 |
| AC-48 | CT-11, CT-17 | TC-48 |
| AC-49 | CT-1, CT-7 | TC-49 |
| AC-50 | CT-8 | TC-50 |
| NFR-1 | CT-8 | TC-51 |

## Decisions
- A blocked task's unfinished edits are saved as a patch in the run folder and the tree is cleaned (grill Q28, human, 2026-10-29).
- A suite broken before the first task pauses the stage: C-261029-kubi (grill Q29, human, 2026-10-29).
- A task with no `Mode:` line runs in split mode: C-261029-nbrg (grill Q30, human, 2026-10-29).
- Where the stage's code, stored data and commands go: architecture.md, approved by the human (grill Q27, 2026-10-29).
