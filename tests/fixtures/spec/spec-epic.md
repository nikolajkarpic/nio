---
slug: checkout
route: epic
risk: [money, pii, external-input]
retired: []
---
# Checkout

## Summary
What the whole effort delivers and why, in 3–5 lines. [human]

## Actors and journeys
(as in a slice spec; slices inherit these and cite them)

## Roadmap
| ID | Slice | Intent | Scope boundary | Depends on | Status | Spec |
| --- | --- | --- | --- | --- | --- | --- |
| R-1 | Cart | Hold items and totals | in: cart; deferred: discounts → R-3 | — | planned | — |
| R-2 | Refunds | Refund paid orders | in: full refunds; deferred: partial → R-4 | R-1 | in-progress | checkout-refunds |

## Non-goals
- Marketplace sellers. [human]

## Glossary
(shared by every slice)

## Decisions
- Effort-wide decisions, as links to D- records.
