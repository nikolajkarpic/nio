---
id: D-261024-6tkp
type: decision
title: "Record paths may name unstaged files unless gitignored"
status: human             # proposed | human | recorded; jury standing comes from verdicts
answers: why              # why | reuse | jury
date: 2026-10-24
by: "human"               # role / host / model, or human
run: ""                   # run ID; empty when written by hand
serves: []                # AC IDs this decision serves
task: ""                  # task ID, if any
paths: ["src/nio/records.py"]
tags: ["lint"]
supersedes: ["D-261024-aqpe"]
---
## Decision
When a record is written, `nio check` accepts a `paths` glob that matches a tracked file or an untracked file that is not gitignored (`git ls-files --cached --others --exclude-standard`). Afterwards, an unmatched path is still only a warning, as in D-261024-aqpe.
## Why
Matching only `git ls-files` meant a decision about code written in the same change failed `nio check` until that code was `git add`ed. Agents record decisions right after writing the code, and the failure looks like a broken record, not a missing `git add`. Gitignored files stay rejected because a record must point at something that will be committed.
## Rejected alternatives
- Tell agents to `git add` first: agents forget, and the error misleads them about the cause.
- Always rejecting unmatched paths later: records can't be edited, so a rename would fail CI forever (kept from D-261024-aqpe).
## Reuse
Treat a stale-path warning as a hint that a superseding record may be due.
