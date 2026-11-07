---
slug: 2026-11-07-lite-path
architecture: none               # approved | none (follows the existing code's structure)
retired: []                      # OP IDs removed from this plan; never reused
---
# Plan: lite path of the NIO flow for small bug fixes

## Build order
### US-1 Run a small fix through the lite route
- Delivers: CT-1, CT-2, CT-3, CT-6, CT-10, CT-11
- Tests: TC-1, TC-2, TC-4, TC-5
- Scenario: QS-1

### US-2 Write a mini bugfix spec
- Depends on: US-1
- Delivers: CT-8, CT-9, CT-14
- Tests: TC-6, TC-7, TC-8

### US-3 Escalate a lite effort that turns out bigger
- Depends on: US-1
- Delivers: CT-4, CT-7, CT-12, CT-13
- Tests: TC-9, TC-11, TC-12
- Scenario: QS-2

### US-4 Pick lite or full at intake
- Depends on: US-3
- Delivers: CT-5
- Tests: TC-13, TC-14, TC-15, TC-16

## Coverage
| Spec ID | Contracts | Tests |
| --- | --- | --- |
| FR-1 | CT-1, CT-3 | TC-1 |
| FR-2 | CT-1 | TC-1 |
| FR-3 | CT-6 | TC-2 |
| FR-4 | CT-9 | TC-6 |
| FR-5 | CT-9 | TC-7 |
| FR-6 | CT-10 | TC-4 |
| FR-7 | CT-8, CT-14 | TC-8 |
| FR-8 | CT-4, CT-6, CT-7, CT-8, CT-12, CT-13 | TC-9, TC-16 |
| FR-10 | CT-1, CT-13 | TC-11 |
| FR-11 | CT-13 | TC-12 |
| FR-12 | CT-5 | TC-13, TC-14 |
| FR-13 | CT-11 | TC-5 |
| FR-14 | CT-5 | TC-15 |
| FR-15 | CT-2 | TC-1 |
| AC-1 | CT-1, CT-2, CT-3 | TC-1 |
| AC-2 | CT-6 | TC-2 |
| AC-4 | CT-10 | TC-4 |
| AC-5 | CT-11 | TC-5 |
| AC-6 | CT-9 | TC-6 |
| AC-7 | CT-9 | TC-7 |
| AC-8 | CT-8, CT-14 | TC-8 |
| AC-9 | CT-4, CT-6, CT-7, CT-8, CT-12, CT-13 | TC-9 |
| AC-11 | CT-1, CT-13 | TC-11 |
| AC-12 | CT-13 | TC-12 |
| AC-13 | CT-5 | TC-13 |
| AC-14 | CT-5 | TC-14 |
| AC-15 | CT-5 | TC-15 |
| AC-16 | CT-4, CT-6, CT-7, CT-8, CT-12, CT-13 | TC-16 |
| NFR-1 | none | none |
| NFR-2 | none | none |
