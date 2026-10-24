---
id: D-261024-7m4l
type: decision
title: "Near-duplicate warning at similarity 0.92 on shared paths"
status: proposed          # proposed | human | recorded; jury standing comes from verdicts
answers: why              # why | reuse | jury
date: 2026-10-24
by: "builder / claude-code / opus"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
serves: []                # AC IDs this decision serves
task: ""                  # task ID, if any
paths: ["src/nio/index.py"]
tags: ["index", "conflicts", "vectors"]
supersedes: []            # IDs of records this replaces
---
## Decision
`nio index --check` warns when two records share a touched file, neither supersedes the other, and their int8 bge-small embeddings have cosine similarity of 0.92 or more. Any pair counts, not just records new on a branch.
## Why
On the first 21 records, the most similar distinct pair scored 0.84, and a real revision (D-261024-6tkp superseding D-261024-aqpe) scored 0.85. Near-identical records score above 0.95. 0.92 catches the same decision written twice without flagging revisions or related decisions. The index cannot tell which records are new on a branch, and a duplicate that is already merged should still warn until a supersede resolves it.
## Rejected alternatives
- Restricting the check to records added since the merge base: needs a base branch in config, and it hides duplicates that are already merged.
- A lower threshold such as 0.85: it would flag ordinary revisions and related decisions on the same file.
## Reuse
Re-tune `DUP_SIMILARITY` in `src/nio/index.py` once there are about 30 real records, or whenever the embedding model changes.
