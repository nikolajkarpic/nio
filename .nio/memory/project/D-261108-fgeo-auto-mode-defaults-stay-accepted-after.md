---
id: D-261108-fgeo
type: decision
title: "Auto-mode defaults stay accepted after auto is switched off"
status: human            # proposed | human | recorded; jury standing comes from verdicts
answers: why              # why | reuse | jury
date: 2026-11-08
by: "human"                # role / host / model, or human
run: "R-261108-lfjo"              # run ID; empty when written by hand
serves: ["AC-17", "AC-18"]                # AC IDs this decision serves
task: ""                  # task ID, if any
paths: ["src/nio/spec.py"]                 # files or globs it touches
tags: ["spec", "grill", "auto"]
supersedes: []            # IDs of records this replaces
---
## Decision
Under auto, the run turns open points and `[default]` items into `[auto]` defaults, which the spec jury judges. Once the spec jury has approved them they pass the spec gate whether auto is on or off: switching auto off reopens none of them. Spec 2026-11-08-full-auto-run FR-7, FR-8, FR-14.
## Why
The human chose this over making them unconfirmed again (Q10): the jury already judged them, and re-asking costs the human questions. Accepted trade-off: choices the human never saw stay in force. The run report lists every `[auto]` default with the record that allowed it (FR-22, FR-23), so the human can still find them.
## Rejected alternatives
- Count them as unconfirmed when auto is off, so the spec gate refuses them: the human reviews every choice, at the cost of extra questions.
- Drop them back to open points: the jury's work on them is lost.
## Reuse
When an agent-made choice has passed the jury, it keeps its standing after the human takes back control, unless the human reopens it explicitly.
