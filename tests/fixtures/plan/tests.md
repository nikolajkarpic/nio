---
slug: checkout-refunds
retired: []
---
# Tests: Refunds for paid orders

## Acceptance tests

### TC-1 A paid order is refunded in full (AC-1; integration) [default]
- File: `tests/test_refunds.py:test_full_refund` (new)
- Covers: CT-1, CT-2
- Setup: a paid order of 40.00
- Action: `POST /orders/o1/refund`
- Assert: order state is `refunded`; refund amount is 40.00

### TC-2 A second refund is rejected (AC-2; integration) [default]
- File: `tests/test_refunds.py:test_second_refund` (new)
- Covers: CT-1, CT-2
- Setup: an order already refunded
- Action: `POST /orders/o1/refund`
- Assert: 409 "already refunded"; one payment only

## Quality tests
### TC-3 Refunds confirm fast (NFR-1; integration) [default]
- File: `tests/test_refunds.py:test_refund_p95` (new)
- Covers: CT-2
- Setup: 1,000 paid orders
- Action: refund each over HTTP
- Assert: p95 ≤ 2 s

## Misuse tests
### TC-4 Two refunds at once pay once (UJ-1 misuse; integration) [research: RF-5]
- File: `tests/test_refunds.py:test_concurrent_refunds` (new)
- Covers: CT-1
- Setup: a paid order
- Action: two refund requests at the same time
- Assert: one succeeds, one gets 409; one payment only
