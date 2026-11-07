---
id: V-261107-ehcv
type: verdict
title: "plan gate for 2026-11-07-review-fixes: human (round 3)"
answers: jury             # why | reuse | jury
date: 2026-11-07
by: "jury"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
subject: "plan:2026-11-07-review-fixes"
outcome: human
tier: high
paths: [".nio/specs/2026-11-07-review-fixes/jury/plan.md"]
tags: []
supersedes: []
---
## Ruling
The plan jury ruled **human** for `2026-11-07-review-fixes` in round 3 (15 fixed, 1 open, 2 refuted). Ledger: `.nio/specs/2026-11-07-review-fixes/jury/plan.md`.
## Jurors
| Lens | Host | Model | Vote |
| --- | --- | --- | --- |
| architecture-fit | claude-code | opus-5.5 | approve |
| architecture-fit | claude-code | opus-5.5 | approve |
| architecture-fit | claude-code | opus-5.5 | approve |
| risk-rollback | claude-code | opus-5.5 | approve |
| test-proof | claude-code | opus-5.5 | approve |
## Reasons
- one list for the human; fix or accept each as risk: J-8
- J-8 [minor/risk] shelve with no changed paths writes a str through write_bytes: open
## What was rejected
- J-5 No test proves a failed land's patch restores the work after the worktree is deleted: refuted (`land` writes the patch and then applies that same file (implement.py 368-373). TC-4 and TC-14 apply the saved patch successfully with CRLF, latin-1 and binary files, and TC-6 shows its bytes equal git's. TC-5 re-applies shelve's patch with `git apply --binary`. A failed apply doesn't change how the patch is written, so a failure test adds no proof of the byte path.)
- J-6 A failed `git diff` still lets shelve delete the work after saving an empty or partial patch: refuted (Ignoring `git diff`'s exit code is the code as it stands today (implement.py 368, 454, "as today" in CT-5). The spec asks only for byte-exact patches (FR-3, FR-4), and its non-goals exclude "Any refactor beyond the lines each fix needs". Nothing in the spec requires handling a failed diff, so this is a new requirement, not a flaw in the plan.)
