---
id: V-261114-bjmy
type: verdict
title: "spec gate for 2026-11-14-short-lived-drivers: human (round 3)"
answers: jury             # why | reuse | jury
date: 2026-11-14
by: "jury"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
subject: "spec:2026-11-14-short-lived-drivers"
outcome: human
tier: low
paths: [".nio/specs/2026-11-14-short-lived-drivers/jury/spec.md"]
tags: []
supersedes: []
---
## Ruling
The spec jury ruled **human** for `2026-11-14-short-lived-drivers` in round 3 (7 disposed, 1 dropped, 11 fixed, 6 merged). Ledger: `.nio/specs/2026-11-14-short-lived-drivers/jury/spec.md`.
## Jurors
| Lens | Host | Model | Vote |
| --- | --- | --- | --- |
| consistency | claude-code | claude-haiku-5-5 | block |
| consistency | claude-code | claude-haiku-5-5 | block |
| consistency | claude-code | claude-haiku-5-5 | block |
| logic | claude-code | claude-sonnet-5-5 | block |
| scope | claude-code | claude-haiku-5-5 | approve |
| testability | claude-code | claude-sonnet-5-5 | block |
## Reasons
- the human closed the gate: fix ruled by the human (J-10); spec-gate fixes close without re-check per the jury-round-cap spec
- (the jury said rerun: the spec changed since round 3 judged it: re-review what changed (`nio jury changed`))
- J-1 [blocker/contradiction] Drivers must write juror output, against D-261107-pdq4: disposed spec-fix
- J-5 [major/inconsistency] The wait table has a foreground row that FR-9 does not allow: disposed spec-fix
- J-16 [blocker/contradiction] AC-10 forbids a check between waits that AC-11 requires: disposed spec-fix
- J-3 [minor/inconsistency] The spec calls C-261108-mplt pending while the record says it is accepted: disposed spec-fix
- J-15 [minor/scope] Two separable features in one spec: disposed accepted-risk
- J-24 [minor/inconsistency] The C-261108-mplt status is called pending in the spec, but the pack records it as accepted: disposed spec-fix
- J-25 [minor/inconsistency] FR-8 covers a long `nio` command, but the glossary's long command also covers suite runs: disposed spec-fix
## What was rejected
- J-4 A "blocked handoff" saved by the driver may be the note that grill Q2 rules out: dropped (a cited ID or quote is not in the artefact)
