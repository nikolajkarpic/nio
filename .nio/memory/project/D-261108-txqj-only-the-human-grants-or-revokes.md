---
id: D-261108-txqj
type: decision
title: "Only the human grants or revokes auto mode"
status: human            # proposed | human | recorded; jury standing comes from verdicts
answers: why              # why | reuse | jury
date: 2026-11-08
by: "human"                # role / host / model, or human
run: "R-261108-lfjo"              # run ID; empty when written by hand
serves: ["AC-29", "AC-30", "AC-31"]                # AC IDs this decision serves
task: ""                  # task ID, if any
paths: ["src/nio/flow.py"]                 # files or globs it touches
tags: ["flow", "jury", "auto"]
supersedes: []            # IDs of records this replaces
---
## Decision
Only the human switches an effort's auto flag on (`nio flow start <slug> --auto --by human`), at any stage from the end of drafting on, and only the human switches it off. A fix under way when auto is switched off finishes its edits, and the next jury round waits for the human. Spec 2026-11-08-full-auto-run FR-1, FR-30–FR-32.
## Why
With auto on, the jury approves gates in the human's place and the run commits without asking. NORTH_STAR says autonomy is earned through the jury, never assumed, so an agent must never be able to grant itself autonomy. An orchestrator's claim that the human asked is no proof.
## Rejected alternatives
- An orchestrator the human delegated to may grant: the only proof is the agent's own word.
- A `nio:auto` issue label grants: anyone who can label the issue grants autonomy.
- Grant only when the draft is written: an effort the human started by hand could never go auto.
- Off switch stops at once, even mid-fix: can leave half-edited files.
## Reuse
Any new way to hand a decision from the human to agents (a new grant or flag) follows the same rule: `--by human` only, recorded in history, revocable.
