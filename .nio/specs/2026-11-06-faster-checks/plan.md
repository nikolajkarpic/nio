---
slug: 2026-11-06-faster-checks
architecture: none               # approved | none (follows the existing code's structure)
retired: []                      # OP IDs removed from this plan; never reused
---
# Plan: faster checks

## Build order
### US-4 The jury parser accepts small format slips
- Delivers: CT-6, CT-7
- Tests: TC-12, TC-13, TC-14, TC-15, TC-19
- Scenario: QS-3

### US-5 The fix-check round reuses evidence
- Depends on: US-4
- Delivers: CT-4
- Tests: TC-20

### US-3 Jury evidence reuses suite results
- Depends on: US-5
- Delivers: CT-5
- Tests: TC-8, TC-9, TC-10, TC-11, TC-16, TC-18
- Scenario: QS-2

### US-1 Tests call the nio CLI in-process
- Depends on: US-3
- Delivers: CT-1, CT-2
- Tests: TC-1, TC-2, TC-3, TC-4
- Scenario: QS-1

### US-2 The suite runs its test files in parallel
- Depends on: US-1
- Delivers: CT-3
- Tests: TC-5, TC-6, TC-7, TC-17
- Scenario: QS-1

## Coverage
| Spec ID | Contracts | Tests |
| --- | --- | --- |
| FR-1 | CT-1 | TC-1, TC-2, TC-3 |
| FR-2 | CT-1 | TC-4 |
| FR-3 | CT-3 | TC-5 |
| FR-4 | CT-3 | TC-6 |
| FR-5 | CT-3 | TC-7 |
| FR-6 | CT-5 | TC-8, TC-11 |
| FR-7 | CT-4, CT-5 | TC-9, TC-20 |
| FR-8 | CT-5 | TC-10 |
| FR-9 | CT-6 | TC-12 |
| FR-10 | CT-6 | TC-13 |
| FR-11 | CT-6 | TC-14 |
| FR-12 | CT-7 | TC-15 |
| FR-13 | CT-5 | TC-16 |
| AC-1 | CT-1 | TC-1 |
| AC-2 | CT-1 | TC-2 |
| AC-3 | CT-1 | TC-3 |
| AC-4 | CT-1 | TC-4 |
| AC-5 | CT-3 | TC-5 |
| AC-6 | CT-3 | TC-6 |
| AC-7 | CT-3 | TC-7 |
| AC-8 | CT-5 | TC-8 |
| AC-9 | CT-4, CT-5 | TC-9, TC-20 |
| AC-10 | CT-5 | TC-10 |
| AC-11 | CT-5 | TC-11 |
| AC-12 | CT-6 | TC-12 |
| AC-13 | CT-6 | TC-13 |
| AC-14 | CT-6 | TC-14 |
| AC-15 | CT-7 | TC-15 |
| AC-16 | CT-5 | TC-16 |
| NFR-1 | CT-2 | none |
| NFR-2 | none | none |

## Decisions
- Build in the coordinator's recommended order (#74, #71, #75, #73, #72), with the review line (CT-4, the #75 story's part) before the evidence change that reads it: the parser and evidence changes are independent of the test helpers, and the parallel suite is measured last, on the faster files [agent].
- The embedding model is built once per process (CT-2): with the CLI in-process, its 145 loads were the largest remaining cost of test_implement.py (RF-11) [agent].
- The parallel suite wraps each file in `sh -c '… || exit 1'`, so a file killed by a signal doesn't stop `xargs` (RF-12) [agent].
- A covered journey is recorded as `passed` with `covered: true`, so every reader of results.json keeps its meaning of `result` [agent].
- NFR-1 is measured by QS-1, not by a test: a test file can't time itself. TC-5 keeps a loose timing check (4 s sleeps, so queueing would show as 8 s or more) [agent].
