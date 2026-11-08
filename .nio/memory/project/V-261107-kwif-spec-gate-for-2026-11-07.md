---
id: V-261107-kwif
type: verdict
title: "spec gate for 2026-11-07-review-fixes: rejected (round 1)"
answers: jury             # why | reuse | jury
date: 2026-11-07
by: "jury"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
subject: "spec:2026-11-07-review-fixes"
outcome: rejected
tier: high
paths: [".nio/specs/2026-11-07-review-fixes/jury/spec.md"]
tags: []
supersedes: []
---
## Ruling
The spec jury ruled **rejected** for `2026-11-07-review-fixes` in round 1 (1 dropped, 2 merged, 7 open, 2 refuted). Ledger: `.nio/specs/2026-11-07-review-fixes/jury/spec.md`.
## Jurors
| Lens | Host | Model | Vote |
| --- | --- | --- | --- |
| adversary | claude-code | sonnet | block |
| logic | claude-code | sonnet | block |
| testability | claude-code | sonnet | block |
## Reasons
- unresolved: J-1, J-2, J-4, J-5, J-9, J-11, J-12
- J-1 [major/gap] A refuter file planted before the batch is printed can still count: open
- J-2 [major/gap] A refused run after an artefact change has no recovery path: open
- J-9 [major/gap] FR-9 covers four judged artefacts but only the spec has a test: open
- J-4 [minor/gap] Duplicate or conflicting verdicts for one ID in a refuter output: open
- J-5 [minor/ambiguity] "Items or sections changed" is undefined, so a real change can go unreviewed: open
- J-11 [minor/untestable] AC-3, AC-6 and AC-9 point at test suites, not at an observable: open
- J-12 [minor/untestable] AC-13 and AC-7 Observables lack exact, checkable text: open
## What was rejected
- J-3 Binary and mode-only changes in a patch are not covered: refuted (FR-3 and FR-4 respond to #102, which is about CRLF and non-UTF-8 text decoding. The non-goals exclude "Any refactor beyond the lines each fix needs", and the summary scopes the effort to minimal fixes. Binary, mode-only and quoted-path handling is existing behaviour that this spec neither allows nor changes.)
- J-7 FR-5 and FR-10 both govern a rerun with no fix to check: refuted (FR-5 applies only when "no lens is named to re-run". When items changed, FR-10 names every voting lens, so FR-5's condition is false. AC-7 (FR-10) and AC-8 (FR-5) split the cases by whether an item changed. The rules are consistent, and a literal contradiction is not shown.)
- J-8 FR-10 and AC-7 re-run a lens for a finding that has no fix: dropped (a cited ID or quote is not in the artefact)
