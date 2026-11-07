---
slug: 2026-11-05-implement-followups
architecture: none               # approved | none (follows the existing code's structure)
retired: []                      # OP IDs removed from this plan; never reused
---
# Plan: Implement follow-ups

## Build order

### US-1 A blocked task's change record passes the memory check
- Delivers: CT-1
- Tests: TC-1, TC-2, TC-3, TC-16, TC-17, TC-26
- Scenario: QS-1

### US-2 Red asks only for the test files of the TC IDs the task proves itself
- Delivers: CT-2, CT-3
- Tests: TC-4, TC-5, TC-6, TC-7, TC-18, TC-19, TC-27
- Scenario: QS-2

### US-5 A wall-clock limit can't fail a task's review
- Delivers: CT-9, CT-10, CT-12
- Tests: TC-13, TC-14, TC-15, TC-25, TC-30
- Scenario: QS-5

### US-3 The tasks-gate fix check shows tasks added under Fixes
- Delivers: CT-4, CT-5, CT-6
- Tests: TC-8, TC-9, TC-10, TC-11, TC-20, TC-21, TC-28
- Scenario: QS-3

### US-4 The evaluator edits only the rating lines
- Delivers: CT-7, CT-8, CT-11
- Tests: TC-12, TC-22, TC-23, TC-24, TC-29
- Scenario: QS-4

## Coverage
| Spec ID | Contracts | Tests |
| --- | --- | --- |
| FR-1 | CT-1 | TC-1, TC-3 |
| FR-2 | CT-1 | TC-2, TC-3 |
| FR-3 | CT-2, CT-3 | TC-4, TC-5, TC-6, TC-18, TC-19 |
| FR-4 | CT-3 | TC-5, TC-18 |
| FR-5 | CT-3 | TC-7 |
| FR-6 | CT-4, CT-5 | TC-8, TC-11 |
| FR-7 | CT-4, CT-6 | TC-9, TC-11, TC-20 |
| FR-8 | CT-4 | TC-10, TC-21 |
| FR-9 | CT-7 | TC-22, TC-23 |
| FR-10 | CT-8 | TC-12 |
| FR-11 | CT-9 | TC-13, TC-14 |
| FR-15 | CT-10 | TC-15 |
| FR-16 | CT-1 | TC-16, TC-17 |
| FR-17 | CT-11 | TC-24 |
| FR-18 | CT-12 | TC-25 |
| AC-1 | CT-1 | TC-1 |
| AC-2 | CT-1 | TC-2 |
| AC-3 | CT-1 | TC-3 |
| AC-4 | CT-2, CT-3 | TC-4 |
| AC-5 | CT-2, CT-3 | TC-5 |
| AC-6 | CT-2, CT-3 | TC-6 |
| AC-7 | CT-3 | TC-7 |
| AC-8 | CT-4, CT-5 | TC-8 |
| AC-9 | CT-4, CT-6 | TC-9 |
| AC-10 | CT-4 | TC-10 |
| AC-11 | CT-4, CT-5, CT-6 | TC-11 |
| AC-12 | CT-8 | TC-12 |
| AC-14 | CT-9 | TC-13 |
| AC-15 | CT-9 | TC-14 |
| AC-18 | CT-10 | TC-15 |
| AC-20 | CT-1 | TC-16 |
| AC-21 | CT-1 | TC-17 |
| AC-22 | CT-2, CT-3 | TC-18 |
| AC-23 | CT-2, CT-3 | TC-19 |
| AC-24 | CT-4, CT-6 | TC-20 |
| AC-25 | CT-4 | TC-21 |
| AC-26 | CT-7 | TC-22 |
| AC-27 | CT-7 | TC-23 |
| AC-28 | CT-11 | TC-24 |
| AC-29 | CT-12 | TC-25 |
