---
slug: refund-double-charge
route: lite
risk: [money]
retired: []
---
# Double refund on fast double click

## Summary
What is broken, who hits it, and how it was found. [human]
Repro: open a paid order, click "Refund" twice within 1 s; two refunds are created.

## Current behaviour
- **CB-1** WHEN a customer requests a refund twice within 1 s THEN the system creates two refunds. [research: RF-1]

## Expected behaviour
- **EB-1** WHEN a customer requests a refund twice within 1 s THE SYSTEM SHALL create exactly one refund. [human]

## Unchanged behaviour
- **UB-1** WHEN a customer requests one refund on a paid order THE SYSTEM SHALL CONTINUE TO refund the full amount. [human]

## Acceptance criteria
- **AC-1** (EB-1) Given a paid order, when two refund requests arrive within 1 s, then one refund exists. [human]
  Observable: exactly one refund row for the order. Level: integration. (written first; fails before the fix)
- **AC-2** (UB-1) Given a paid order, when one refund request arrives, then it is refunded in full. [human]
  Observable: order state `refunded`, amount equals total. Level: integration.
