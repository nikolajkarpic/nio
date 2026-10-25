---
slug: checkout-refunds
route: full                      # full | lite
epic: ""                         # epic slug and slice, e.g. "checkout/R-2"; empty when standalone
risk: [money, external-input]    # auth | pii | money | external-input | data-deletion | migration | multi-party | public-api; [] when none
retired: []                      # IDs removed from this spec; never reused
---
# Refunds for paid orders

## Summary
What this delivers and why, for whom, in 3–5 lines. WHAT and WHY only, never HOW. [human]

## Actors and journeys
- **A-1 Customer**: buys online, expects money back within days. [research: RF-2]
- **A-2 Support agent**: refunds on the customer's behalf. [research: RF-4]

**UJ-1 Customer refunds a paid order** (A-1) [research: RF-2]
1. Opens the order, picks "Refund".
2. Sees the amount, confirms.
- Misuse: requests the refund twice in quick succession.
- Evidence: RF-2 (support tickets #212, #240).

## User stories

### US-1 Customer refunds a paid order (P1) [human]
- **Why this priority:** the most common refund; support handles it by hand today.
- **Independent test:** refund one paid order end to end and see the money and the order state.

- **AC-1** (FR-1) Given a paid order, when the customer requests a refund, then the order is refunded in full. [human]
  Observable: order state is `refunded`; refund amount equals the order total. Level: integration.
- **AC-2** (FR-2) Given a refunded order, when the customer requests a refund again, then it is rejected. [human]
  Observable: response says "already refunded"; no second payment is created. Level: integration.

## Functional requirements
- **FR-1** WHEN a customer requests a refund on a paid order THE SYSTEM SHALL refund the full order amount. [human]
- **FR-2** IF the order is already refunded THEN THE SYSTEM SHALL reject the refund request. [human]

## Rules
### State table: order (start: paid; final: shipped, refunded)
| State | ship | refund | Src |
| --- | --- | --- | --- |
| paid | → shipped | → refunded | [human] |
| shipped | ignore | reject: return it first | [human] |
| refunded | reject: refunded | reject: already refunded | [human] |

### Decision table: refund amount
| order state (paid, returned) | items returned (all, some) | → refund | Src |
| --- | --- | --- | --- |
| paid | - | full | [human] |
| returned | all | full | [human] |
| returned | some | returned items only | [human] |

## Key entities
- **Refund**: amount, order, created at, by (customer or support). [human]

## Non-functional requirements
- **NFR-1** THE SYSTEM SHALL confirm a refund request within 2 s at the 95th percentile. [human]

## Success criteria
- **SC-1** Support handles 50% fewer refund tickets within a month of release. [human]

## Non-goals
- Partial refunds of paid (not returned) orders. [human]
- Refunds to a different payment method. [human]

## Glossary
- **Refund**: money returned to the original payment method. Never "reimbursement" or "chargeback".

## Risks and evidence against
- Double refunds under concurrent requests (RF-5: race in the payments client). [research: RF-5]

## Decisions
- Full refunds only for paid orders: D-261025-k2m4 (grill, 2026-10-25).

## Open points
- (drafting only; empty at the gate) OP-1: Can support refund after 30 days? [default]
