---
id: V-261025-wasi
type: verdict
title: "spec gate for grill-checks: rejected (round 3)"
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
The spec jury ruled **rejected** for `grill-checks` in round 3 (22 fixed, 7 merged, 10 open). Ledger: `.nio/specs/grill-checks/jury/spec.md`.
## Jurors
| Lens | Host | Model | Vote |
| --- | --- | --- | --- |
| consistency | claude-code | sonnet | block |
| logic | claude-code | sonnet | block |
| scope | claude-code | sonnet | block |
| testability | claude-code | sonnet | block |
## Reasons
- unresolved: J-28, J-30, J-31, J-32, J-33, J-34, J-35, J-37, J-38, J-39
- J-28 [major/inconsistency] "Only the human closes" and SC-1 contradict the `--by grill` closing path: open
- J-30 [minor/ambiguity] Collect rule says "one open finding per deferred point" without an exception for existing findings: open
- J-31 [minor/inconsistency] Accepted-tag list in FR-6 is narrower than the sources FR-3 allows: open
- J-32 [minor/gap] A contradiction finding is a blocker, but the human can close it as easily as a gap: open
- J-33 [minor/scope] Verdict-blocking rule is an agent call nobody confirmed: open
- J-34 [minor/gap] Key entity adds a retirement rule that no requirement states: open
- J-35 [major/ambiguity] AC-27 gives the wrong reason for one of its two failures, and "section" is undefined: open
- J-37 [major/gap] No test stops `--by grill` from closing a deferred finding as accepted risk or out of scope: open
## What was rejected
Nothing.
