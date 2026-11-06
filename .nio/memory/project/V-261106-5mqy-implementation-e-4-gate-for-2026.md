---
id: V-261106-5mqy
type: verdict
title: "implementation-E-4 gate for 2026-11-05-implement-followups: rejected (round 1)"
answers: jury             # why | reuse | jury
date: 2026-11-06
by: "jury"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
subject: "implementation-E-4:2026-11-05-implement-followups"
outcome: rejected
tier: medium
paths: [".nio/specs/2026-11-05-implement-followups/jury/implementation-E-4.md"]
tags: []
supersedes: []
---
## Ruling
The implementation-E-4 jury ruled **rejected** for `2026-11-05-implement-followups` in round 1 (1 disposed, 1 merged, 7 open, 2 refuted). Ledger: `.nio/specs/2026-11-05-implement-followups/jury/implementation-E-4.md`.
## Jurors
| Lens | Host | Model | Vote |
| --- | --- | --- | --- |
| adversary | claude-code | claude-sonnet-5-5 | approve |
| conformance | claude-code | claude-sonnet-5-5 | block |
| consistency | claude-code | claude-haiku-5-5 | block |
| correctness | claude-code | claude-sonnet-5-5 | approve |
## Reasons
- unresolved: J-8
- J-8 [major/inconsistency] AC-9 calls T-30 a changed ID, but the code and CT-6 keep it out of the changed line: disposed fix-task
- J-3 [minor/contradiction] `changed` leaves T-30 out of the changed IDs, but AC-9 says to list it there: open
- J-4 [minor/risk] The misuse test for fixcheck duplicates the happy path and attacks nothing: open
- J-6 [minor/gap] AC-25 covers editing or removing a planned task, but only editing is tested: open
- J-7 [minor/gap] AC-11 requires output equal to the current code's output, but the test only checks absence and line count: open
- J-9 [minor/inconsistency] fix_ids reads the `#### Fixes` heading differently from the approval path: open
- J-10 [minor/inconsistency] AC-9 says changed lists T-30 next to T-4, but the code prints it on a separate line: open
- J-11 [minor/gap] The AC-8 misuse test asserts only a subset of the main test: open
## What was rejected
- J-1 A fix task edited after it was first shown is never shown again: refuted (FR-6, FR-7 and FR-8 (spec.md:137-139) cover tasks "added under #### Fixes", not later edits to a fix task. FR-8 deliberately exempts the Fixes section from approval (`planned()` strips it, jury.py:183). Reviewing edits to an existing fix task is a new requirement, not a gap in this spec.)
- J-2 A duplicate task ID under Fixes can mark a planned task as a fix: refuted (Approval and `changed` read the artefact through `planned()` (jury.py:183-191). That function strips `#### Fixes` sections by regex and never calls `fix_ids`. An edited planned T-4 therefore still shows up as changed and still withdraws approval, whatever `fix_ids` returns. Also, `tasks.check` rejects a repeated ID outright (tasks.py:187, "is defined N times"), so the duplicate cannot pass the tasks check.)
