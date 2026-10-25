---
id: V-261025-kdsv
type: verdict
title: "spec gate for grill: human (round 3)"
answers: jury             # why | reuse | jury
date: 2026-10-25
by: "jury"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
subject: "spec:grill"
outcome: human
tier: low
paths: [".nio/specs/grill/jury/spec.md"]
tags: []
supersedes: []
---
## Ruling
The spec jury ruled **human** for `grill` in round 3 (17 disposed, 4 dropped, 11 fixed, 2 merged, 1 refuted). Ledger: `.nio/specs/grill/jury/spec.md`.
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
- the human closed the gate: fixed the logic contradictions over three rounds; the remaining edge cases are accepted as risk in #51 rather than run more rounds (#52)
- (the jury said rerun: the spec changed since round 3 judged it: re-review what changed (`nio jury changed`))
- J-2 [major/contradiction] The decision table lets money and breaking-change decisions fall below the bar: disposed spec-fix
- J-4 [blocker/contradiction] Rounds mode contradicts the non-goal against asking several questions in one message: disposed spec-fix
- J-5 [minor/scope] The configurable 15 and the epic-split suggestion were never asked: disposed spec-fix
- J-6 [minor/scope] Money and breaking changes are added to the always-asked set: disposed spec-fix
- J-7 [minor/contradiction] The guessing non-goal is contradicted by FR-16, and the non-goal was not updated: disposed spec-fix
- J-9 [minor/scope] Threshold of "more than three" that no answer set: disposed spec-fix
- J-10 [minor/scope] One spec carrying several features, including changes to nio check spec: disposed spec-fix
- J-21 [major/gap] The state table leaves out pause, delegation, finish-gate steps and partial round answers: disposed accepted-risk
## What was rejected
- J-17 AC-4 "verified facts" cannot be checked from the message: refuted (AC-4 and FR-4 already require each fact to carry a source (an RF-n, a file:line or a spec ID), and the Observable says the message "has each of those parts", which includes the `?` ending, the one-line why and the recommendation's reason. The filler rule is the only judgement left, and it is a stated "never filler" requirement, not a gap in the AC.)
- J-23 Recording five bar answers for every unasked point is labelled as the human's decision: dropped (a cited ID or quote is not in the artefact)
- J-24 The glossary check still sits in this slice, though the split moved the checker to grill-checks: dropped (a cited ID or quote is not in the artefact)
- J-25 The epic suggestion is limited to the first pause, which no answer says: dropped (a cited ID or quote is not in the artefact)
- J-26 The follow-up options are built from the human's words, which no answer asks for: dropped (a cited ID or quote is not in the artefact)
