---
id: V-261026-6hdg
type: verdict
title: "spec gate for grill-checks: human (round 4)"
answers: jury             # why | reuse | jury
date: 2026-10-26
by: "jury"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
subject: "spec:grill-checks"
outcome: human
tier: low
paths: [".nio/specs/grill-checks/jury/spec.md"]
tags: []
supersedes: []
---
## Ruling
The spec jury ruled **human** for `grill-checks` in round 4 (11 disposed, 31 fixed, 8 merged, 1 refuted). Ledger: `.nio/specs/grill-checks/jury/spec.md`.
## Jurors
| Lens | Host | Model | Vote |
| --- | --- | --- | --- |
| consistency | claude-code | sonnet | block |
| logic | claude-code | sonnet | approve |
| scope | claude-code | sonnet | block |
| testability | claude-code | sonnet | block |
## Reasons
- the human closed the gate: Four rounds; every fix held and all 51 findings are disposed. Round 4's fixes are wording and ACs over code unchanged since round 1, with tests. Closing rather than a fifth round (convergence: #52).
- (the jury said rerun: the spec changed since round 4 judged it: re-review what changed (`nio jury changed`))
- J-40 [major/contradiction] SC-1 says the human can only close a deferred finding as a spec fix: disposed spec-fix
- J-41 [minor/inconsistency] Deferred-finding ACs sit under the wrong user story: disposed spec-fix
- J-42 [minor/ambiguity] SC-1 can be read to forbid the closure AC-17 requires: disposed spec-fix
- J-43 [minor/gap] The closing table has one input but the outcome depends on three: disposed spec-fix
- J-44 [minor/ambiguity] FR-15 and FR-12 depend on telling a deferred finding from a lens finding, but nothing says how: disposed spec-fix
- J-45 [minor/gap] A `[derived: DF-n]` source is covered by neither FR-4 nor the source table: disposed spec-fix
- J-46 [minor/risk] The "only the human closes" invariant is stated as enforced but is spoofable by design: disposed spec-fix
- J-48 [minor/scope] FR-16 lets the human close a deferred finding as a spec fix with `--by human`, which no answer asked for: disposed spec-fix
## What was rejected
- J-38 FR-15's suppression is tested only for a disposed finding, and "deferred finding" is not identified: refuted (FR-15 now defines a deferred finding as "one that collect made from a DF, not a lens finding that cites it", and AC-15 covers the case "either still open or disposed as accepted risk", so the open case is tested and the recognition rule is stated. What's left is that no AC has a lens finding citing a DF, which is J-44's point.)
