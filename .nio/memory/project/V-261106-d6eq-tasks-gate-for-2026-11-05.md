---
id: V-261106-d6eq
type: verdict
title: "tasks gate for 2026-11-05-parallel-waves: approved (round 2)"
answers: jury             # why | reuse | jury
date: 2026-11-06
by: "jury"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
subject: "tasks:2026-11-05-parallel-waves"
outcome: approved
tier: high
paths: [".nio/specs/2026-11-05-parallel-waves/jury/tasks.md"]
tags: []
supersedes: []
---
## Ruling
The tasks jury ruled **approved** for `2026-11-05-parallel-waves` in round 2 (1 fixed, 4 refuted). Ledger: `.nio/specs/2026-11-05-parallel-waves/jury/tasks.md`.
## Jurors
| Lens | Host | Model | Vote |
| --- | --- | --- | --- |
| executability | claude-code | haiku | approve |
## Reasons
- Every lens approved and no finding is open.
## What was rejected
- J-1 release() has no owning task: refuted (Serves lists ACs, not functions. `release` is the CT-1 rule behind FR-9, and its first caller is `commit` in T-4. TC-7 is in T-4's Test and lands T-2 before T-1, so it fails if `"claims": {}` is kept. TC-8, also in T-4, covers the apply-block release. T-5's callers (`attempt`, `block`) are covered by TC-4/TC-12 in T-5.)
- J-2 TC-16 leaves the baseline line open: refuted (tests.md TC-16 asserts "the history's line count is unchanged". That count includes a `baseline` line, so a worker who writes the baseline before the worktrees fails the test, and the order is forced by the assertion. The parenthetical only restates this, so there is no real room for two valid builds.)
- J-3 T-4 is max-tier work rated med effort, too large for one pack: refuted (The finding's risk is a worker stopping after the happy path. Every case it lists has its own TC in T-4's Test (TC-8 apply block, TC-13/TC-14 dirty tree and scoping, TC-10 suite gating, TC-15), and T-4 is not done until they pass. Nothing in the artefact sets a rule on tier versus effort or a size cap that T-4 breaks, so this is a preference about effort rating rather than a defect.)
- J-4 T-4 contract includes a review-failure restore that only T-5 proves: refuted (tasks.md gives the review-failure and commit-failure restore to T-5, in its title and in Serves AC-9 with TC-9. T-4's title and Serves cover landing and review scoping only. T-5 depends on T-4, so the gap exists only between two tasks of the same unshipped spec, and ownership is stated.)
