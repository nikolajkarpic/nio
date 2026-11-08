---
slug: 2026-11-08-project-onboarding
architecture: approved
retired: []                      # OP IDs removed from this plan; never reused
---
# Plan: project onboarding

## Build order

### US-1 List what the repo already has
- Delivers: CT-1, CT-2
- Tests: TC-1, TC-2, TC-3, TC-4

### US-4 Spec waits for onboarding
- Depends on: US-1
- Delivers: CT-3, CT-4, CT-5, CT-7, CT-8, CT-12, CT-15
- Tests: TC-25, TC-26, TC-27, TC-28, TC-29, TC-50, TC-53, TC-56

### US-5 Stages read the project docs
- Depends on: US-4
- Delivers: CT-9, CT-10, CT-16, CT-18, CT-19, CT-22
- Tests: TC-30, TC-31, TC-32, TC-33, TC-34, TC-55
- Scenario: QS-4

### US-2 Onboard an existing repo through a grill
- Depends on: US-5
- Delivers: CT-6, CT-13, CT-17
- Tests: TC-5, TC-6, TC-7, TC-8, TC-9, TC-10, TC-11, TC-12, TC-13, TC-14, TC-15, TC-16, TC-17, TC-18, TC-19, TC-20, TC-21, TC-22, TC-42, TC-46, TC-47, TC-48, TC-52
- Scenario: QS-1

### US-3 Onboard an empty repo
- Depends on: US-2
- Delivers: CT-21
- Tests: TC-23, TC-24
- Scenario: QS-2

### US-6 Flag stale docs and reconcile them
- Depends on: US-2
- Delivers: CT-11, CT-14
- Tests: TC-35, TC-36, TC-37, TC-38, TC-39, TC-40, TC-41, TC-43, TC-49, TC-51, TC-54
- Scenario: QS-3

### US-7 An effort's changes reach the project docs
- Depends on: US-6
- Delivers: CT-20
- Tests: TC-44, TC-45

## Coverage
| Spec ID | Contracts | Tests |
| --- | --- | --- |
| FR-1 | CT-1, CT-2 | TC-1, TC-4 |
| FR-2 | CT-1, CT-2 | TC-2 |
| FR-3 | CT-1 | TC-3, TC-48 |
| FR-4 | CT-13 | TC-5 |
| FR-5 | CT-12, CT-13 | TC-5, TC-6 |
| FR-6 | CT-12, CT-13 | TC-7 |
| FR-7 | CT-7, CT-12 | TC-8 |
| FR-8 | CT-13, CT-14 | TC-9, TC-42 |
| FR-9 | CT-3, CT-4, CT-13 | TC-10 |
| FR-10 | CT-3, CT-4, CT-13 | TC-11 |
| FR-11 | CT-13 | TC-12 |
| FR-12 | CT-3, CT-4, CT-13 | TC-23 |
| FR-13 | CT-21 | TC-24 |
| FR-14 | CT-5 | TC-25, TC-26, TC-27 |
| FR-15 | CT-3, CT-4, CT-8 | TC-27, TC-28 |
| FR-16 | CT-15 | TC-29 |
| FR-17 | CT-9, CT-10, CT-18, CT-19, CT-22 | TC-31, TC-33 |
| FR-18 | CT-9 | TC-32 |
| FR-19 | CT-7, CT-8 | TC-35 |
| FR-20 | CT-7, CT-8 | TC-37 |
| FR-21 | CT-14 | TC-38, TC-39, TC-41, TC-43 |
| FR-22 | CT-14 | TC-40, TC-43 |
| FR-23 | CT-11, CT-14, CT-20 | TC-44, TC-45 |
| FR-24 | CT-1 | TC-12, TC-13, TC-19 |
| FR-25 | CT-7, CT-9 | TC-36 |
| FR-26 | CT-16 | TC-30 |
| FR-27 | CT-3, CT-4, CT-13 | TC-14 |
| FR-28 | CT-6, CT-9, CT-10, CT-16, CT-19 | TC-15, TC-16, TC-46, TC-47 |
| FR-29 | CT-13, CT-17 | TC-17, TC-18 |
| FR-30 | CT-13 | TC-20 |
| FR-31 | CT-13, CT-14 | TC-21 |
| FR-32 | CT-4, CT-13, CT-14 | TC-22 |
| FR-33 | CT-9 | TC-34 |
| AC-1 | CT-1, CT-2 | TC-1 |
| AC-2 | CT-1, CT-2 | TC-2 |
| AC-3 | CT-1 | TC-3 |
| AC-4 | CT-1, CT-2 | TC-4 |
| AC-5 | CT-12, CT-13 | TC-5 |
| AC-6 | CT-12, CT-13 | TC-6 |
| AC-7 | CT-12, CT-13 | TC-7 |
| AC-8 | CT-7, CT-12 | TC-8 |
| AC-9 | CT-13, CT-14 | TC-9 |
| AC-10 | CT-3, CT-4, CT-13 | TC-10 |
| AC-11 | CT-3, CT-4, CT-13 | TC-11 |
| AC-12 | CT-1, CT-13 | TC-12 |
| AC-13 | CT-3, CT-4, CT-13 | TC-23 |
| AC-14 | CT-21 | TC-24 |
| AC-15 | CT-5 | TC-25 |
| AC-16 | CT-3, CT-4, CT-5, CT-8 | TC-27 |
| AC-17 | CT-15 | TC-29 |
| AC-18 | CT-9, CT-10, CT-18, CT-19, CT-22 | TC-31 |
| AC-19 | CT-9 | TC-32 |
| AC-20 | CT-9, CT-10, CT-18, CT-19, CT-22 | TC-33 |
| AC-21 | CT-7, CT-8 | TC-35 |
| AC-22 | CT-7, CT-8 | TC-37 |
| AC-23 | CT-14 | TC-38 |
| AC-24 | CT-14 | TC-39 |
| AC-25 | CT-14 | TC-40 |
| AC-26 | CT-11, CT-14, CT-20 | TC-44 |
| AC-27 | CT-11, CT-14, CT-20 | TC-45 |
| AC-28 | CT-1 | TC-13 |
| AC-29 | CT-5 | TC-26 |
| AC-30 | CT-3, CT-4, CT-8 | TC-28 |
| AC-31 | CT-7, CT-9 | TC-36 |
| AC-32 | CT-16 | TC-30 |
| AC-33 | CT-3, CT-4, CT-13 | TC-14 |
| AC-34 | CT-6, CT-9, CT-10, CT-16, CT-19 | TC-15 |
| AC-35 | CT-6, CT-9, CT-10, CT-16, CT-19 | TC-16 |
| AC-36 | CT-13, CT-17 | TC-17 |
| AC-37 | CT-13, CT-17 | TC-18 |
| AC-38 | CT-1 | TC-19 |
| AC-39 | CT-13 | TC-20 |
| AC-40 | CT-13, CT-14 | TC-21 |
| AC-41 | CT-4, CT-13, CT-14 | TC-22 |
| AC-42 | CT-14 | TC-41 |
| AC-43 | CT-13, CT-14 | TC-42 |
| AC-44 | CT-14 | TC-43 |
| AC-45 | CT-6, CT-9, CT-10, CT-16, CT-19 | TC-46 |
| AC-46 | CT-6, CT-9, CT-10, CT-16, CT-19 | TC-47 |
| AC-47 | CT-9 | TC-34 |
| AC-48 | CT-1 | TC-48 |
| NFR-2 | CT-8 | TC-49 |

## Decisions
- Architecture note approved under the human's standing grant (grill Q23, agent, 2026-11-08); it settles `onboard.py`, the stored data and the shared commands the plan builds on.
- The per-doc grill questions live in the doc templates, read by both skills (architecture note; the call J-19 moved out of the spec).
- e2e tests run each skill on a real model with a scripted dev, only with `NIO_E2E=1`, like `tests/test_tasks_e2e.py` (agent, 2026-11-08).

## Open points
