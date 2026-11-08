---
id: V-261107-6pfb
type: verdict
title: "implementation-E-1 gate for 2026-11-07-refuter-batch-forge: rejected (round 1)"
answers: jury             # why | reuse | jury
date: 2026-11-07
by: "jury"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
subject: "implementation-E-1:2026-11-07-refuter-batch-forge"
outcome: rejected
tier: medium
paths: [".nio/specs/2026-11-07-refuter-batch-forge/jury/implementation-E-1.md"]
tags: []
supersedes: []
---
## Ruling
The implementation-E-1 jury ruled **rejected** for `2026-11-07-refuter-batch-forge` in round 1 (3 disposed, 5 open). Ledger: `.nio/specs/2026-11-07-refuter-batch-forge/jury/implementation-E-1.md`.
## Jurors
| Lens | Host | Model | Vote |
| --- | --- | --- | --- |
| adversary | claude-code | opus | block |
| conformance | claude-code | opus | approve |
| consistency | claude-code | claude-opus-5-5 | block |
| correctness | claude-code | opus | approve |
## Reasons
- unresolved: J-1, J-7, J-8
- J-1 [major/risk] A failed git diff force-removes the worktree with no patch saved: disposed fix-task
- J-7 [blocker/gap] AC-4 has no passing evidence: disposed fix-task
- J-8 [blocker/gap] AC-5 has no passing evidence: disposed fix-task
- J-2 [minor/risk] land still ignores errors from git add and the name-only diff: open
- J-3 [minor/risk] A byte-identical refuter answer to a new batch is never read: open
- J-4 [minor/risk] A forged refuter file is still accepted while a batch is outstanding: open
- J-5 [minor/gap] AC-8's test doesn't check that the returned error is git's own: open
- J-6 [minor/gap] The batch check passes on the stale pack from the first batch: open
## What was rejected
Nothing.
