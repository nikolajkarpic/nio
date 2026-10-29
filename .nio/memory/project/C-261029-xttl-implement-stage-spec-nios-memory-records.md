---
id: C-261029-xttl
type: change
title: "Implement-stage spec: nio's memory records don't count as uncommitted work and stay out of task commits"
answers: why              # why | reuse | jury
date: 2026-10-29
by: "human"                # role / host / model, or human
run: "R-261029-ksbo"              # run ID; empty when written by hand
against: ".nio/specs/2026-10-29-implement-stage/spec.md"               # the spec, plan or record that is wrong
outcome: accepted          # pending | accepted | rejected
paths: [".nio/specs/2026-10-29-implement-stage/spec.md", ".nio/specs/2026-10-29-implement-stage/contracts.md", "src/nio/implement.py"]
tags: [implement-stage, memory, git]
supersedes: []
---
## What is wrong
FR-22 refuses a claim while there are uncommitted changes outside the effort folder, and CT-9 commits every uncommitted path outside it. A spec problem filed with `nio flow block` writes an untracked change record under `.nio/memory/`, so the next claim was refused until the human committed it, and the next task's commit would have swept it in. Found while building E-5 and E-6.
## Proposed change
1. FR-22: "outside the effort folder and nio's own memory records (`.nio/memory/`)".
2. CT-5 and CT-9: the uncommitted-changes check and a task's commit leave out `.nio/memory/`, as they leave out `.nio/runs/` and `.nio/cache/`; memory records are the human's to commit.
## Human decision
Accepted after the build, 2026-10-29: "commit it and do the change requests".
