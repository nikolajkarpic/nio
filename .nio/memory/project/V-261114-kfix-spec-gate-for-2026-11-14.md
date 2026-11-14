---
id: V-261114-kfix
type: verdict
title: "spec gate for 2026-11-14-effort-jury: rejected (round 1)"
answers: jury             # why | reuse | jury
date: 2026-11-14
by: "jury"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
subject: "spec:2026-11-14-effort-jury"
outcome: rejected
tier: high
paths: [".nio/specs/2026-11-14-effort-jury/jury/spec.md"]
tags: []
supersedes: []
---
## Ruling
The spec jury ruled **rejected** for `2026-11-14-effort-jury` in round 1 (1 dropped, 4 merged, 17 open, 5 refuted). Ledger: `.nio/specs/2026-11-14-effort-jury/jury/spec.md`.
## Jurors
| Lens | Host | Model | Vote |
| --- | --- | --- | --- |
| adversary | claude-code | sonnet | block |
| consistency | claude-code | claude-haiku-5-5 | block |
| consistency | claude-code | claude-haiku-5-5 | block |
| consistency | claude-code | claude-haiku-5-5 | block |
| logic | claude-code | sonnet | block |
| scope | claude-code | claude-haiku-5-5 | approve |
| testability | claude-code | sonnet | block |
## Reasons
- unresolved: J-1, J-2, J-3, J-4, J-5, J-6, J-9, J-10, J-11, J-12, J-13, J-15, J-16, J-18, J-24, J-26, J-27
- J-1 [major/gap] Nothing says how a human is told from an agent at the approve call: open
- J-2 [major/gap] Push, PR creation and the comment have no failure or replay behaviour: open
- J-3 [major/risk] The verdict isn't tied to a commit, and a merge by an agent has no AC that contains it: open
- J-4 [major/gap] In-flight efforts with open findings on an epic can lose them silently: open
- J-6 [blocker/contradiction] Spec removes the per-epic suite-at-end rule of a current decision without a change request: open
- J-11 [major/contradiction] One verdict comment, but the gate runs several rounds: open
- J-12 [major/contradiction] Out-of-flow commits can fall outside every split pack: open
- J-18 [major/untestable] Fresh-driver independence is checked only by skill text: open
- J-5 [minor/gap] An epic can close on a missing or vacuous suite: open
- J-9 [minor/gap] State table has no row for a failing suite on an epic's last task: open
- J-10 [minor/inconsistency] Provenance tags on FR-7 and AC-6 do not match the template's allowed tags: open
- J-13 [minor/inconsistency] The human's approval is unconditional in one table and conditional in the other: open
- J-15 [minor/scope] FR-7 applies jury rules that the grill never confirmed: open
- J-16 [minor/scope] FR-11 adds a "system closed" outcome bucket that no answer asked for: open
- J-26 [minor/ambiguity] Undefined setting `jury.max_runs` next to `jury.max_rounds`: open
- J-27 [minor/ambiguity] "closing task's review" versus "no reviewers": open
## What was rejected
- J-7 Spec replaces the per-epic implementation juries that approved verdicts gated, without a change request: refuted (V-261030-67dz is a spec-gate verdict on another effort's spec, and V-261031-ag5f approved one epic's gate of that effort. Neither binds a later effort's spec. The replacement is the human's own direction (Summary, #77 and #100, Q1 and Q6), and the spec's non-goals and Decisions state it plainly.)
- J-8 Spec does not say what replaces the epic line that an accepted change relies on: refuted (C-261030-abpr is a build-order fix against the old effort's spec, about where tasks T-4 and T-27 sit in that plan. The epic line and the claim wait rule are implementation (HOW). AC-1 already says what the spec requires: `nio flow status` names E-2's next task after E-1 closes on the suite.)
- J-14 Fix tasks re-trigger the transition to the pr gate: dropped (a cited ID or quote is not in the artefact)
- J-20 AC-13 and AC-6 depend on undefined numbers and rules: refuted (FR-7, FR-10 and the Decisions deliberately defer to the existing jury rules (D-261026-r52z, "same rulings as any capped gate"), and the human confirmed this in Q7. The round-cap values and rulings are defined there, so a tester can read them.)
- J-22 The epic line that the claim rule waits for has no home in the spec: refuted (The epic line and the claim wait rule are HOW. C-261030-abpr (accepted) is a build-order fix against the old effort's task plan (it moves T-4 and T-27), not a spec rule that binds this spec. AC-1 already fixes the observable: `nio flow status` names E-2's next task after E-1 closes on the suite.)
- J-25 Accepted epic-line rule (C-261030-abpr) is not carried into the new epic close: refuted (It is the same point as J-8 and J-22. The epic line is HOW, and C-261030-abpr is a build-order change against another effort's plan. AC-1 and FR-1 give the observable: `nio flow status` names the next epic's task. The spec need not say what writes an internal line. The finding itself says it is inferred, not read from the spec or code.)
