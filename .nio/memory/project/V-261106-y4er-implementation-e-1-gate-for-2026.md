---
id: V-261106-y4er
type: verdict
title: "implementation-E-1 gate for 2026-11-06-faster-checks: approved (round 1)"
answers: jury             # why | reuse | jury
date: 2026-11-06
by: "jury"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
subject: "implementation-E-1:2026-11-06-faster-checks"
outcome: approved
tier: medium
paths: [".nio/specs/2026-11-06-faster-checks/jury/implementation-E-1.md"]
tags: []
supersedes: []
---
## Ruling
The implementation-E-1 jury ruled **approved** for `2026-11-06-faster-checks` in round 1 (5 open, 2 refuted). Ledger: `.nio/specs/2026-11-06-faster-checks/jury/implementation-E-1.md`.
## Jurors
| Lens | Host | Model | Vote |
| --- | --- | --- | --- |
| adversary | claude-code | sonnet | approve |
| conformance | claude-code | sonnet | approve |
| consistency | claude-code | claude-haiku-5-5 | approve |
| correctness | claude-code | sonnet | approve |
## Reasons
- J-2 [minor/contradiction] `none` followed by any number of `.` or `!` is accepted: open
- J-3 [minor/risk] Labels that differ only in case merge, and the first one silently wins: open
- J-4 [minor/inconsistency] Trailing-mark rule is looser than AC-12: open
- J-6 [minor/contradiction] Several trailing marks are accepted as no findings: open
- J-7 [minor/contradiction] Trailing punctuation is stripped without a limit, so `none!!` and `none.!.` read as no findings: open
## What was rejected
- J-1 An empty `where` passes as present: refuted (Line 117 does accept `- where:` with an empty value, because `blocks` stores `[""]`, which is a truthy list. The user's note says an empty `where` was accepted before this epic too. AC-14 and FR-11 say "reject as before" and name only a missing `gap` or `where`. This epic's change (case folding of labels) did not cause it. I could not run `git show 19c8e09` here, so the pre-epic behaviour is taken from the caller's note.)
- J-5 Prose before findings is not rejected: refuted (`None, but see F1` or `none yet` with no `###` finding is rejected, because line 144 fires when `findings` is empty. When valid `### F1` blocks follow, the findings are all present and parsed. Line 142 rejects the `None.` plus finding case that AC-14 lists as a contradiction. Prose ahead of valid findings loses nothing, and the spec does not say it must be rejected.)
