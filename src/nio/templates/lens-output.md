---
lens: <your card's name>                      # your card's name
gate: spec                         # spec | plan | tasks, from the pack
subject: checkout-refunds          # the slug, from the pack
by: "juror / claude-code / sonnet" # role / host / model
context: sufficient                # sufficient | limited | needs-more: was the pack enough to judge?
---
## Reasoning
What you checked and how, in your own words. Write this before the findings.

## Verdicts
Only in a re-review or the final fix check: one line per finding in your fix-check pack, and no other. Leave the
section out in a first review.
- J-2: fixed — FR-7 now names the neighbours

## Findings
### F1 Shipped orders are both refundable and not
- cites: FR-1, FR-2               # IDs, which must exist; a table row is cited as a label (state table row `shipped`) and quoted
- kind: contradiction              # contradiction | gap | ambiguity | untestable | risk | scope | inconsistency
- severity: blocker
- evidence: observed
- quote: "Shipped orders can never be refunded"
- quote: "allowed while the order is paid or shipped"
- situation: an order is shipped and a refund arrives: FR-1 refunds it, FR-2 rejects it
- fix: keep one rule; if FR-2 holds, drop `shipped` from FR-1 and the table row
- gap: missing                    # implementation gate only: missing | partial | contradicts | unrequested
- where: src/app.py               # implementation gate only: the file or area
