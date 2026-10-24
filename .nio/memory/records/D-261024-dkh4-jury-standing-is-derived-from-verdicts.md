---
id: D-261024-dkh4
type: decision
title: "Jury standing is derived from verdicts, never stored"
status: human             # proposed | human | recorded
answers: why              # why | reuse | jury
date: 2026-10-24
by: "writer / claude-code / claude-opus-5-5"
run: ""                   # run ID; empty when written by hand
serves: []                # AC IDs this decision serves
task: ""                  # task ID, if any
paths: ["src/nio/records.py", "src/nio/templates/*.md", "MEMORY_NORTH_STAR.md"]
tags: ["record-format", "jury"]
supersedes: []            # IDs of records this replaces
---
## Decision
`status` on decisions and lessons only says how the record entered memory: `proposed`, `human` or `recorded`. Whether the jury approved or rejected it is read from verdicts whose `subject` names it; `nio check` rejects `approved` and `rejected` as a status.
## Why
Records are never edited, and a decision is usually written before the jury rules on it. A stored `approved` could only be right when the verdict came first, so most decisions would show `proposed` forever while a verdict said otherwise. The verdict already holds the ruling; storing it twice lets the two disagree.
## Rejected alternatives
- Keep `approved` and `rejected` in `status`: it goes stale the moment a later verdict lands.
- Write a superseding record after every verdict: doubles the records for no new information.
## Reuse
Any fact that can change after a record is written belongs in a later record that points back, not in a field of the earlier one.
