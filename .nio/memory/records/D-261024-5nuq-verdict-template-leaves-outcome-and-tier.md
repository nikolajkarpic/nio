---
id: D-261024-5nuq
type: decision
title: "Verdict template leaves outcome and tier empty"
status: proposed          # proposed | human | recorded; jury standing comes from verdicts
answers: why              # why | reuse | jury
date: 2026-10-24
by: "writer / claude-code / claude-opus-5-5"
run: "R-261024-nyzf"      # run ID; empty when written by hand
serves: []                # AC IDs this decision serves
task: ""                  # task ID, if any
paths: ["src/nio/templates/verdict.md"]
tags: ["jury", "lint"]
supersedes: []            # IDs of records this replaces
---
## Decision
`nio new verdict` writes `outcome: ""` and `tier: ""`, with no default, so `nio check` fails until the writer picks a value for both.
## Why
Every jury ruling is recorded and verdicts are never edited afterwards. With `approved` / `low` as defaults, a writer who forgot to fill them in would pass lint and permanently record a low-tier approval the jury never gave. An empty field fails loudly at write time, when it is still cheap to fix.
## Rejected alternatives
- Defaulting to `approved` / `low`: a forgotten field becomes a false approval that can't be corrected in place.
## Reuse
In any template for an immutable record, leave fields that carry a judgment empty so lint forces a choice; only default fields whose default is always true.
