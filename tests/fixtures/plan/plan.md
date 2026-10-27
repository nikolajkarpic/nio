---
slug: checkout-refunds
architecture: none
retired: []
---
# Plan: Refunds for paid orders

## Build order
### US-1 Customer refunds a paid order
- Delivers: CT-1, CT-2
- Tests: TC-1, TC-2, TC-3, TC-4
- Scenario: QS-1

## Coverage
| Spec ID | Contracts | Tests |
| --- | --- | --- |
| FR-1 | CT-1, CT-2 | TC-1 |
| FR-2 | CT-1, CT-2 | TC-2 |
| AC-1 | CT-1, CT-2 | TC-1 |
| AC-2 | CT-1, CT-2 | TC-2 |
| NFR-1 | CT-2 | TC-3 |

## Decisions
- Reuse the payments client's idempotency key against double refunds: D-261027-a1b2 (research, 2026-10-27).
