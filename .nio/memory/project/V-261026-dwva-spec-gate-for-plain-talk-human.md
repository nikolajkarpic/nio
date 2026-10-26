---
id: V-261026-dwva
type: verdict
title: "spec gate for plain-talk: human (round 3)"
answers: jury             # why | reuse | jury
date: 2026-10-26
by: "jury"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
subject: "spec:plain-talk"
outcome: human
tier: low
paths: [".nio/specs/plain-talk/jury/spec.md"]
tags: []
supersedes: []
---
## Ruling
The spec jury ruled **human** for `plain-talk` in round 3 (17 disposed, 11 fixed, 4 merged). Ledger: `.nio/specs/plain-talk/jury/spec.md`.
## Jurors
| Lens | Host | Model | Vote |
| --- | --- | --- | --- |
| consistency | claude-code | opus-5.5 | block |
| consistency | claude-code | opus-5.5 | block |
| consistency | claude-code | opus-5.5 | block |
| logic | claude-code | opus-5.5 | block |
| scope | claude-code | opus-5.5 | block |
| testability | claude-code | opus-5.5 | block |
## Reasons
- the human closed the gate: Close the gate now: go to the plan and implementation, with round 2's fixes (all wording or test details) unverified by a third round.
- (the jury said rerun: the spec changed since round 3 judged it: re-review what changed (`nio jury changed`))
- J-2 [blocker/contradiction] Facts' sources move from the question body to `Refs:`, against an approved grill requirement: disposed spec-fix
- J-3 [major/contradiction] `nio jury answers` does not keep working unchanged with the labelled lines: disposed spec-fix
- J-10 [minor/scope] One bundle where the spec could be split into slices: disposed out-of-scope
- J-16 [minor/inconsistency] The entry header is named differently in FR-13 and in the spec's own Non-goals, and differently again in the grill skill: disposed spec-fix
- J-17 [minor/ambiguity] A round of questions is specified without saying it is opt-in, so it reads as the default the grill spec forbids: disposed spec-fix
- J-18 [minor/inconsistency] The grill log header is given two different ways: disposed spec-fix
- J-19 [minor/gap] Timing of the log entry against the shown message: disposed spec-fix
- J-21 [minor/inconsistency] The behaviour-change test in FR-7 is narrower than the grill's bar it cites: disposed spec-fix
## What was rejected
Nothing.
