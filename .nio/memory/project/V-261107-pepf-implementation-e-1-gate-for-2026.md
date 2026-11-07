---
id: V-261107-pepf
type: verdict
title: "implementation-E-1 gate for 2026-11-07-review-fixes: rejected (round 1)"
answers: jury             # why | reuse | jury
date: 2026-11-07
by: "jury"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
subject: "implementation-E-1:2026-11-07-review-fixes"
outcome: rejected
tier: high
paths: [".nio/specs/2026-11-07-review-fixes/jury/implementation-E-1.md"]
tags: []
supersedes: []
---
## Ruling
The implementation-E-1 jury ruled **rejected** for `2026-11-07-review-fixes` in round 1 (2 disposed, 1 merged, 5 open). Ledger: `.nio/specs/2026-11-07-review-fixes/jury/implementation-E-1.md`.
## Jurors
| Lens | Host | Model | Vote |
| --- | --- | --- | --- |
| adversary | claude-code | sonnet | block |
| conformance | claude-code | sonnet | approve |
| consistency | claude-code | claude-haiku-5-5 | block |
| correctness | claude-code | sonnet | approve |
| risk-rollback | claude-code | opus-5.5 | block |
## Reasons
- unresolved: J-1, J-6
- J-1 [major/risk] A failed `git diff` in `shelve` writes an empty patch, then the work is restored away: disposed fix-task
- J-6 [major/contradiction] Implementation rerun with no lens to re-run opens a run instead of showing the human: disposed fix-task
- J-2 [minor/risk] Every edit after any rejected round re-runs all voting lenses, with no bound on spend: open
- J-3 [minor/risk] The moved-artefact guard is bypassed by the actor it is meant to stop: open
- J-4 [minor/risk] Patch byte-exactness is only shown with default git config: open
- J-5 [minor/risk] `land` and `shelve` decode file names as text, so a non-UTF-8 name crashes after the patch is half done: open
- J-8 [minor/ambiguity] "restore it" at the implementation gate invites undoing a commit: open
## What was rejected
Nothing.
