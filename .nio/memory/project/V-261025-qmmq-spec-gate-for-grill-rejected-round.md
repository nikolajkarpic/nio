---
id: V-261025-qmmq
type: verdict
title: "spec gate for grill: rejected (round 1)"
answers: jury             # why | reuse | jury
date: 2026-10-25
by: "jury"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
subject: "spec:grill"
outcome: rejected
tier: low
paths: [".nio/specs/grill/jury/spec.md"]
tags: []
supersedes: []
---
## Ruling
The spec jury ruled **rejected** for `grill` in round 1 (2 merged, 15 open). Ledger: `.nio/specs/grill/jury/spec.md`.
## Jurors
| Lens | Host | Model | Vote |
| --- | --- | --- | --- |
| consistency | claude-code | haiku | approve |
| logic | claude-code | sonnet | block |
| scope | claude-code | haiku | block |
| scope | claude-code | haiku | block |
| scope | claude-code | haiku | block |
| testability | claude-code | sonnet | block |
## Reasons
- unresolved: J-1, J-2, J-3, J-4, J-5, J-6, J-7, J-9, J-10, J-12, J-13, J-14, J-15, J-16, J-17
- J-1 [major/contradiction] The contradiction state rejects both asking and answering the resolution question: open
- J-2 [major/contradiction] The decision table lets money and breaking-change decisions fall below the bar: open
- J-3 [minor/contradiction] The state table forbids the rounds mode that FR-3 and AC-3 allow: open
- J-4 [blocker/contradiction] Rounds mode contradicts the non-goal against asking several questions in one message: open
- J-5 [minor/scope] The configurable 15 and the epic-split suggestion were never asked: open
- J-6 [minor/scope] Money and breaking changes are added to the always-asked set: open
- J-7 [minor/contradiction] The guessing non-goal is contradicted by FR-16, and the non-goal was not updated: open
- J-9 [minor/scope] Threshold of "more than three" that no answer set: open
## What was rejected
Nothing.
