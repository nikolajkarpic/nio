---
id: D-261024-ujcn
type: decision
title: "Context packs show every standing with a weight; the agent decides"
status: human
answers: why              # why | reuse | jury
date: 2026-10-24
by: "human"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
serves: []                # AC IDs this decision serves
task: ""                  # task ID, if any
paths: ["src/nio/pack.py", "skills/recall/SKILL.md"]
tags: ["pack", "standing", "recall"]
supersedes: []            # IDs of records this replaces
---
## Decision
A pack shows every record's standing, warned ones included, and any of them may be printed in full. It ends with a map from standing to weight (approved binding, current strong, uncommitted tentative, drifted verify, challenged disputed, escalated undecided, conflict blocked), listing only the standings it contains. Standing never changes the order. A superseded record gives way to what replaced it; a rejected one drops out. The recall skill's table uses the same weights.
## Why
The agent is the one who decides whether to act on a record; the pack's job is to give it what it needs to weigh it. A drifted record on the exact file is very relevant, and the agent needs its full text to check it against the code. Sorting by standing would quietly push such a record below a loosely related approved one. Printing only the standings present saves lines in the usual pack, which holds just approved and current.
## Rejected alternatives
- Hiding warned records, or showing them as lines only: the agent then has to look them up, which it may skip.
- Binding records first: favours what is safe to follow over what is relevant.
- Always printing the whole map: mostly rows the agent does not need.
## Reuse
Keep the weights in `pack.py` and the recall skill in sync.
