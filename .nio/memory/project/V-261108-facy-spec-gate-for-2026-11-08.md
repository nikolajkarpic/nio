---
id: V-261108-facy
type: verdict
title: "spec gate for 2026-11-08-explainer: rejected (round 1)"
answers: jury             # why | reuse | jury
date: 2026-11-08
by: "jury"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
subject: "spec:2026-11-08-explainer"
outcome: rejected
tier: medium
paths: [".nio/specs/2026-11-08-explainer/jury/spec.md"]
tags: []
supersedes: []
---
## Ruling
The spec jury ruled **rejected** for `2026-11-08-explainer` in round 1 (3 merged, 19 open, 1 refuted). Ledger: `.nio/specs/2026-11-08-explainer/jury/spec.md`.
## Jurors
| Lens | Host | Model | Vote |
| --- | --- | --- | --- |
| adversary | claude-code | sonnet | block |
| consistency | claude-code | claude-haiku-5-5 | block |
| logic | claude-code | sonnet | block |
| scope | claude-code | haiku-5.5 | approve |
| testability | claude-code | sonnet | block |
## Reasons
- unresolved: J-1, J-2, J-4, J-5, J-6, J-7, J-8, J-9, J-10, J-11, J-13, J-14, J-16, J-17, J-18, J-20, J-21, J-22, J-23
- J-1 [major/risk] Deleting "the SVGs the previous run listed" trusts a file anyone can edit: open
- J-2 [major/gap] Topic name goes straight into a file path: open
- J-4 [major/gap] The 20-node cap is a rule nothing enforces: open
- J-5 [major/risk] Rendering runs an unpinned fetched package on text derived from untrusted input: open
- J-6 [major/inconsistency] Host-skill format may skip the contract-ID check that FR-8 requires: open
- J-7 [major/inconsistency] Core-diagram check may fail every topic explainer: open
- J-10 [major/contradiction] Flow output "same with and without the explainer" conflicts with suggesting explain: open
- J-11 [major/contradiction] Re-run keeps drill-down sections but deletes the SVGs they show: open
- J-8 [minor/inconsistency] Staleness is said to follow the plan, but FR-16 also fires on spec.md and contracts.md: open
- J-9 [minor/inconsistency] The drill-down marker is worded differently in Decisions and FR-25: open
- J-14 [minor/ambiguity] Re-run marks drill-down sections "earlier plan" even when the plan did not change: open
- J-16 [minor/scope] The other-format branch is an unconfirmed agent default under a [human] story: open
- J-17 [minor/inconsistency] FR-16 flags "plan changed" for a change to spec.md, which the human never confirmed: open
- J-18 [minor/gap] The human's wish to pair with nio:research is dropped by a non-goal with no FR behind it: open
- J-21 [minor/untestable] SC-1 depends on a reader's judgement: open
- J-23 [minor/gap] "Source gone" and spec.md changes in FR-16 have no AC: open
## What was rejected
- J-15 One spec bundles several separable features: refuted (Template permits a single spec (epic field is optional), and the stories already carry P1/P2/P3 priorities and an Independent test each, which is the slicing the spec uses; no rule or grill answer demands a split, so this is a preference, not a defect.)
