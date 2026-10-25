---
id: V-261025-wrsv
type: verdict
title: "spec gate for grill-checks: rejected (round 1)"
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
The spec jury ruled **rejected** for `grill-checks` in round 1 (1 merged, 13 open). Ledger: `.nio/specs/grill-checks/jury/spec.md`.
## Jurors
| Lens | Host | Model | Vote |
| --- | --- | --- | --- |
| consistency | claude-code | sonnet | approve |
| logic | claude-code | sonnet | block |
| scope | claude-code | sonnet | block |
| testability | claude-code | sonnet | block |
## Reasons
- unresolved: J-1, J-2, J-3, J-4, J-5, J-6, J-7, J-8, J-9, J-11, J-12, J-13, J-14
- J-1 [minor/inconsistency] Dedup rule is wider than what the code does: open
- J-2 [minor/gap] Severity table sets the finding's kind, but the requirements do not: open
- J-3 [major/contradiction] A grill-closed finding is both refused (agent) and allowed (grill), though the grill is an agent: open
- J-4 [major/contradiction] "Whole word" and "reimbursement-free" cannot both hold: open
- J-5 [minor/gap] The closing table has no outcome for a human who disposes as a spec fix: open
- J-6 [minor/risk] A reused DF number would be silently skipped on the next collect: open
- J-7 [major/scope] Deferred-point bookkeeping validators go beyond the ask: open
- J-8 [minor/scope] Counting untagged lines in the notes is unrequested: open
## What was rejected
Nothing.
