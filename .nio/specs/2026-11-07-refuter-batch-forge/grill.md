# Grill: 2026-11-07-refuter-batch-forge

Session 1 (2026-11-07): delegated to the agent (orchestrator / claude-code / claude-opus-5-5, delegated by human). Lite spec: only decisions over the bar.

## Lookup · OP-3 · 2026-11-07
Found: RF-1, RF-2. Retired OP-3.

## Lookup · OP-4 · 2026-11-07
Found: RF-3. Retired OP-4; it raised Q3.

## Asked · Q1 · OP-1 · 2026-11-07
Question: Which fix stops a refuter file from answering a finding no outstanding batch lists?
Context: The batch is kept per run and never cleared, so any later writer in the run can answer it (RF-1); a batch is recorded only through one function (RF-2).
Options: 1. Clear the run's batch once a refuter output is applied (recommended): one line; a refuter file counts only while a printed batch is outstanding, and the still-pending findings are asked again when the next batch prints. 2. Key the batch by a counter or hash the refuter must echo: also changes the refuter card and its output format. 3. Also refuse a refuter file that changes in the same collect as new lens outputs: not needed once the batch is cleared, and it would refuse a legitimate refuter answer collected together with a retry juror.
Refs: OP-1 · EB-1 · RF-1, RF-2 · src/nio/jury.py:658

## Q1 · OP-1 · 2026-11-07
Question: Which fix stops a refuter file from answering a finding no outstanding batch lists?
Options:
1. Clear the run's batch once applied (recommended)
2. Key the batch by an echoed counter or hash
3. Also refuse a refuter file new in the same collect as lens outputs
Answer: 1. Clear the run's batch once a refuter output is applied. [agent]
Patched: EB-1; retired OP-1

## Asked · Q2 · OP-2 · 2026-11-07
Question: When a refuter file changes with no batch outstanding, should the collect be refused or the file skipped?
Context: Skipping must still mark the file read, or the next printed batch would apply it (RF-2).
Options: 1. Refuse the call, as today for a refuter output before its batch (recommended): nothing is merged until the file is removed; no new message. 2. Skip the file and print the new batch: friendlier, but a forged file stays on disk looking answered. 3. Skip silently: the forger's write goes unnoticed.
Refs: OP-2 · EB-1, UB-2 · src/nio/jury.py:660

## Q2 · OP-2 · 2026-11-07
Question: When a refuter file changes with no batch outstanding, should the collect be refused or the file skipped?
Options:
1. Refuse the call (recommended)
2. Skip and print the new batch
3. Skip silently
Answer: 1. Refuse the call with "refuter output before its batch"; a finding the batch still lists is answered as before. [agent]
Patched: EB-1, AC-1; retired OP-2

## Asked · Q3 · OP-4 · 2026-11-07
Question: Should a failed `git diff` in `land` raise, or come back as git's error so the task is blocked?
Context: The caller blocks the task on a returned error and cleans up; an exception would leave the claim and worktree (RF-3).
Options: 1. Return git's error, so the task is blocked with its worktree removed (recommended): the same path as a failed apply. 2. Raise as `shelve` does: the claim and worktree stay, `green` crashes. 3. Leave it: a failed diff still reads as landed.
Refs: OP-4 · EB-2, AC-2 · RF-3

## Q3 · OP-4 · 2026-11-07
Question: Should a failed `git diff` in `land` raise, or come back as git's error so the task is blocked?
Options:
1. Return git's error (recommended)
2. Raise
3. Leave it
Answer: 1. Return git's error, main tree untouched, so the caller blocks the task. [agent]
Patched: EB-2, AC-2

## Call · UB-1 to UB-6, AC-3 to AC-8, Decisions · 2026-11-07
Below the bar: each keeps today's behaviour as a regression guard, or names a fact the memory pack holds (D-261107-pdq4, D-261107-ldro, C-261107-bff2). No to all five: what a user can do, what a user sees, who may do it, what data is kept or changed, what it costs.
Answer: confirmed as drafted. [agent]
