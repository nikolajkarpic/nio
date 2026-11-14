---
slug: 2026-11-08-explainer
architecture: approved           # approved | none (follows the existing code's structure)
retired: []                      # OP IDs removed from this plan; never reused
---
# Plan: explain an approved plan, or a topic, with diagrams and a short walk-through

## Build order
### Foundation
- Delivers: CT-1, CT-2, CT-3, CT-10

### US-2 Check the explainer
- Depends on: Foundation
- Delivers: CT-4
- Tests: TC-5, TC-6, TC-11, TC-12, TC-13, TC-14, TC-15, TC-16, TC-39

### US-3 Images beside the explainer
- Depends on: US-2
- Delivers: CT-5
- Tests: TC-10, TC-38, TC-43, TC-45, TC-46

### US-1 Explain an approved plan
- Depends on: US-3
- Delivers: CT-9, CT-11
- Tests: TC-1, TC-2, TC-3, TC-4, TC-7, TC-8, TC-9, TC-17, TC-18, TC-19, TC-37
- Scenario: QS-1

### US-7 Flow suggests explaining once the plan is approved
- Depends on: US-1
- Delivers: CT-8
- Tests: TC-32, TC-33

### US-6 Flag a stale explainer, never block
- Depends on: US-7
- Delivers: CT-7
- Tests: TC-28, TC-29, TC-30, TC-31, TC-40, TC-44, TC-47
- Scenario: QS-4

### US-5 Explain a topic
- Depends on: US-6
- Delivers: CT-6
- Tests: TC-23, TC-24, TC-25, TC-27, TC-42
- Scenario: QS-3

### US-4 Drill down interactively
- Depends on: US-5
- Delivers: CT-12
- Tests: TC-20, TC-21, TC-22, TC-26, TC-41
- Scenario: QS-2

### US-8 Choose the diagram format
- Depends on: US-1
- Delivers: CT-13
- Tests: TC-34, TC-35, TC-36

## Coverage
| Spec ID | Contracts | Tests |
| --- | --- | --- |
| FR-1 | CT-4, CT-11 | TC-1, TC-16 |
| FR-2 | CT-1, CT-11 | TC-1 |
| FR-3 | CT-1, CT-11 | TC-2, TC-3 |
| FR-4 | CT-11 | TC-12 |
| FR-5 | CT-5, CT-9, CT-10 | TC-4 |
| FR-6 | CT-1, CT-4, CT-11 | TC-1, TC-6 |
| FR-7 | CT-2, CT-4, CT-11 | TC-5 |
| FR-8 | CT-4, CT-10 | TC-6, TC-11, TC-12, TC-13, TC-14 |
| FR-9 | CT-3, CT-5 | TC-17 |
| FR-10 | CT-3, CT-5 | TC-14, TC-18 |
| FR-11 | CT-3, CT-4, CT-5 | TC-15, TC-19 |
| FR-12 | CT-12 | TC-20 |
| FR-13 | CT-12 | TC-21, TC-22 |
| FR-14 | CT-6, CT-10, CT-11 | TC-23, TC-24 |
| FR-15 | CT-4 | TC-25 |
| FR-16 | CT-7, CT-10 | TC-28, TC-29, TC-31, TC-44 |
| FR-17 | CT-7, CT-8, CT-9 | TC-30 |
| FR-18 | CT-8 | TC-32, TC-33 |
| FR-19 | CT-13 | TC-34 |
| FR-20 | CT-4, CT-13 | TC-35 |
| FR-21 | CT-13 | TC-36 |
| FR-22 | CT-11 | TC-7 |
| FR-23 | CT-5, CT-11 | TC-8 |
| FR-24 | CT-1, CT-5 | TC-31 |
| FR-25 | CT-5, CT-11 | TC-9 |
| FR-26 | CT-5 | TC-10, TC-43, TC-45, TC-46 |
| FR-27 | CT-6, CT-11 | TC-26, TC-27 |
| AC-1 | CT-1, CT-4, CT-11 | TC-1 |
| AC-2 | CT-1, CT-11 | TC-2 |
| AC-3 | CT-1, CT-11 | TC-3 |
| AC-4 | CT-5, CT-9, CT-10 | TC-4 |
| AC-5 | CT-2, CT-4, CT-11 | TC-5 |
| AC-6 | CT-4, CT-10 | TC-11 |
| AC-7 | CT-4, CT-10, CT-11 | TC-12 |
| AC-8 | CT-4, CT-10 | TC-13 |
| AC-9 | CT-3, CT-4, CT-5, CT-10 | TC-14 |
| AC-10 | CT-3, CT-4, CT-5 | TC-15 |
| AC-11 | CT-4, CT-11 | TC-16 |
| AC-12 | CT-3, CT-5 | TC-17 |
| AC-13 | CT-3, CT-5 | TC-18 |
| AC-14 | CT-3, CT-4, CT-5 | TC-19 |
| AC-15 | CT-12 | TC-20 |
| AC-16 | CT-12 | TC-21 |
| AC-17 | CT-12 | TC-22 |
| AC-18 | CT-6, CT-10, CT-11 | TC-23 |
| AC-19 | CT-6, CT-10, CT-11 | TC-24 |
| AC-20 | CT-4 | TC-25 |
| AC-21 | CT-7, CT-10 | TC-28, TC-44 |
| AC-22 | CT-7, CT-10 | TC-29 |
| AC-23 | CT-7, CT-8, CT-9 | TC-30 |
| AC-24 | CT-8 | TC-32 |
| AC-25 | CT-8 | TC-33 |
| AC-26 | CT-13 | TC-34 |
| AC-27 | CT-4, CT-13 | TC-35 |
| AC-28 | CT-13 | TC-36 |
| AC-29 | CT-11 | TC-7 |
| AC-30 | CT-5, CT-11 | TC-8 |
| AC-31 | CT-1, CT-5, CT-7, CT-10 | TC-31 |
| AC-32 | CT-5, CT-11 | TC-9 |
| AC-33 | CT-5 | TC-10, TC-43, TC-45, TC-46 |
| AC-34 | CT-6, CT-11 | TC-26 |
| AC-35 | CT-6, CT-11 | TC-27 |
| AC-36 | CT-1, CT-4, CT-10, CT-11 | TC-6 |
| NFR-1 | CT-2, CT-4 | TC-37 |
| NFR-2 | CT-11 | TC-38 |

## Decisions
- The plan gate reads quickstart.md without its one "Read first" line: the human, Q12 (grill.md).
- One `nio explain` command (`finish`, `topic`) does hashes, rendering, safe deletes, the quickstart line and topic names: the human, Q13.
- `nio flow next` suggests `@nio:explain` after plan approval only while explainer.md is missing: the human, Q14.
- Finish refuses when a recorded drill-down section is gone, before deleting anything: the human, Q15.
- Finish rewrites the source hashes only after a diagram changed, else says the explainer is still stale: the human, Q16.
- A clone on an older nio may read the "Read first" line as a plan edit: accepted as risk, the human, Q17.
- Explainer layout, node-ID rule, check messages, image names, stale line wording and test doubles: agent calls, logged in grill.md (Call · CT-1 to CT-13 and Call · J-1 to J-15, 2026-11-08).
