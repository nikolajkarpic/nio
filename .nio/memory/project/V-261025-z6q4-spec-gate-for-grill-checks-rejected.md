---
id: V-261025-z6q4
type: verdict
title: "spec gate for grill-checks: rejected (round 4)"
answers: jury             # why | reuse | jury
date: 2026-10-25
by: "jury"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
subject: "spec:grill-checks"
outcome: rejected
tier: low
paths: [".nio/specs/grill-checks/jury/spec.md"]
tags: []
supersedes: []
---
## Ruling
The spec jury ruled **rejected** for `grill-checks` in round 4 (31 fixed, 8 merged, 11 open, 1 refuted). Ledger: `.nio/specs/grill-checks/jury/spec.md`.
## Jurors
| Lens | Host | Model | Vote |
| --- | --- | --- | --- |
| consistency | claude-code | sonnet | block |
| logic | claude-code | sonnet | approve |
| scope | claude-code | sonnet | block |
| testability | claude-code | sonnet | block |
## Reasons
- unresolved: J-40, J-41, J-42, J-43, J-44, J-45, J-46, J-48, J-49, J-50, J-51
- J-40 [major/contradiction] SC-1 says the human can only close a deferred finding as a spec fix: open
- J-41 [minor/inconsistency] Deferred-finding ACs sit under the wrong user story: open
- J-42 [minor/ambiguity] SC-1 can be read to forbid the closure AC-17 requires: open
- J-43 [minor/gap] The closing table has one input but the outcome depends on three: open
- J-44 [minor/ambiguity] FR-15 and FR-12 depend on telling a deferred finding from a lens finding, but nothing says how: open
- J-45 [minor/gap] A `[derived: DF-n]` source is covered by neither FR-4 nor the source table: open
- J-46 [minor/risk] The "only the human closes" invariant is stated as enforced but is spoofable by design: open
- J-48 [minor/scope] FR-16 lets the human close a deferred finding as a spec fix with `--by human`, which no answer asked for: open
## What was rejected
- J-38 FR-15's suppression is tested only for a disposed finding, and "deferred finding" is not identified: refuted (FR-15 now defines a deferred finding as "one that collect made from a DF, not a lens finding that cites it", and AC-15 covers the case "either still open or disposed as accepted risk", so the open case is tested and the recognition rule is stated. What's left is that no AC has a lens finding citing a DF, which is J-44's point.)
