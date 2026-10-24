---
id: D-261024-ehmq
type: decision
title: "Writer dedup marks hits at similarity 0.85"
status: proposed          # proposed | human | recorded; jury standing comes from verdicts
answers: why              # why | reuse | jury
date: 2026-10-24
by: "builder / claude-code / opus"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
serves: []                # AC IDs this decision serves
task: ""                  # task ID, if any
paths: ["src/nio/query.py", "skills/remember/SKILL.md"]
tags: ["dedup", "vectors", "query"]
supersedes: []            # IDs of records this replaces
---
## Decision
`nio query` marks a hit with `≈` when its cosine similarity to the query is 0.85 or more. The writer's dedup step passes the candidate's title, Decision and Why as whole sentences.
## Why
On this repo, paraphrased duplicates of D-261024-hkog and D-261024-easj scored 0.88 and 0.89, related decisions 0.75 to 0.80, and unrelated ones about 0.67. Short questions score 0.6 to 0.8 even against the right record, so the mark only works on full candidate text. It is looser than the 0.92 CI warning (D-261024-7m4l): a false alarm before writing costs one read, but a duplicate stays in memory forever.
## Rejected alternatives
- Reusing 0.92: it would miss paraphrased duplicates at about 0.88.
- Hiding the score and only showing the mark: the writer could not judge near misses.
## Reuse
Re-tune this together with `DUP_SIMILARITY` on the first ~30 records, or after a model change.
