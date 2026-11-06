---
id: V-261106-oyt3
type: verdict
title: "implementation-E-2 gate for 2026-11-05-parallel-waves: rejected (round 1)"
answers: jury             # why | reuse | jury
date: 2026-11-06
by: "jury"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
subject: "implementation-E-2:2026-11-05-parallel-waves"
outcome: rejected
tier: high
paths: [".nio/specs/2026-11-05-parallel-waves/jury/implementation-E-2.md"]
tags: []
supersedes: []
---
## Ruling
The implementation-E-2 jury ruled **rejected** for `2026-11-05-parallel-waves` in round 1 (6 disposed, 1 open). Ledger: `.nio/specs/2026-11-05-parallel-waves/jury/implementation-E-2.md`.
## Jurors
| Lens | Host | Model | Vote |
| --- | --- | --- | --- |
| conformance | claude-code | claude-sonnet-5-5 | approve |
| consistency | claude-code | claude-haiku-5-5 | block |
| correctness | claude-code | claude-sonnet-5-5 | approve |
| risk-rollback | claude-code | sonnet | block |
## Reasons
- unresolved: J-2, J-3, J-4, J-6
- J-2 [major/risk] The third-attempt or block shelve destroys a wave task's effort-folder edits and overwrites land's fuller patch: disposed fix-task
- J-3 [major/risk] An exception from commit after the apply leaves the applied files in the main tree with no restore: disposed fix-task
- J-4 [major/risk] The snapshot and restore miss git-quoted (non-ASCII) paths, so a failed review or commit leaves those changes applied: disposed fix-task
- J-6 [major/risk] Green on a wave task falls back to the main tree when its worktree is gone: disposed fix-task
- J-1 [minor/gap] The only journey for this epic did not run: open
- J-5 [minor/risk] restore puts back bytes but not file modes: disposed accepted-risk
- J-7 [minor/inconsistency] CT-7 names the default of `tree` as the root, the code uses None: disposed accepted-risk
## What was rejected
Nothing.
