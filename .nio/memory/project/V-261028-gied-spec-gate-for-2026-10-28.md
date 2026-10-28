---
id: V-261028-gied
type: verdict
title: "spec gate for 2026-10-28-plan-jury: rejected (round 1)"
answers: jury             # why | reuse | jury
date: 2026-10-28
by: "jury"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
subject: "spec:2026-10-28-plan-jury"
outcome: rejected
tier: low
paths: [".nio/specs/2026-10-28-plan-jury/jury/spec.md"]
tags: []
supersedes: []
---
## Ruling
The spec jury ruled **rejected** for `2026-10-28-plan-jury` in round 1 (1 dropped, 1 merged, 14 open, 1 refuted). Ledger: `.nio/specs/2026-10-28-plan-jury/jury/spec.md`.
## Jurors
| Lens | Host | Model | Vote |
| --- | --- | --- | --- |
| consistency | claude-code | haiku | block |
| logic | claude-code | sonnet | block |
| scope | claude-code | haiku | approve |
| testability | claude-code | sonnet | block |
## Reasons
- unresolved: J-1, J-2, J-3, J-4, J-5, J-6, J-7, J-8, J-12, J-13, J-14, J-15, J-16, J-17
- J-1 [major/inconsistency] FR-12 states a different stop rule from the current decision it borrows: open
- J-2 [major/inconsistency] The risk lens is named two ways: open
- J-3 [minor/gap] AC-1 does not exclude the Data model trigger it says to ignore: open
- J-4 [minor/ambiguity] The spec never says what happens to the existing testability lens at the plan gate: open
- J-5 [major/gap] A plan gate waiting on the spec has no exit if the spec change fails, and a second spec-rooted finding is dropped: open
- J-6 [major/inconsistency] "Handed to the human but not closed" is not a state in the table: open
- J-7 [major/gap] A spec with no plan.md can start the tasks stage: open
- J-8 [major/gap] A plan that is approved stays approved after the spec changes under it: open
## What was rejected
- J-10 A human can close a plan gate with a reason, which nobody asked for: refuted (The premise that the research says nothing about closing a gate is wrong. `research.md` RF-9 records that the approved tasks-stage spec counts a gate the human closed as approved, and a gate handed over but not closed as not approved (tasks-stage spec line 205). The grill (grill.md line 101) surfaced RF-9. So FR-39's `[research: RF-9]` tag is backed, and the closed-by-human path is existing precedent, not something invented.)
- J-11 One spec bundles the plan gate and the tasks-stage refusal, with a P2 slice: dropped (a cited ID or quote is not in the artefact)
