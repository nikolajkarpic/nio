---
id: D-261107-ldro
type: decision
title: "Juror cards get a write tool limited to their output file by instruction"
status: recorded          # proposed | human | recorded; jury standing comes from verdicts
answers: why              # why | reuse | jury
date: 2026-11-07
by: "orchestrator / claude-code / claude-opus-5-5 (delegated by human)"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
serves: [AC-8, AC-9]                # AC IDs this decision serves
task: "T-4"                  # task ID, if any
paths: [src/nio/agents.py, src/nio/agents/*.md, src/nio/jury.py]                 # files or globs it touches
tags: []
supersedes: []            # IDs of records this replaces
---
## Decision
The 13 juror cards (lenses and refuter) get `tools: [read, write]`; each card's Output format says to write the whole output to the file the pack names and no other file. Collect takes a lens output's lens from its file name, printing one line when the front matter names another (#90).
## Why
Saving each juror's answer cost the orchestrator a call and a copy of the answer in its context. No host limits a subagent's writes to one path (RF-3), so the limit is the card's instruction, as `read` already is on Codex. The file name rule removes the re-emits #90 measured.
## Rejected alternatives
- Keep the orchestrator saving outputs: one more call and the answer in context per juror.
- Refuse a mismatched front matter: a re-emit each time.
## Reuse
A subagent whose only output is one file writes it itself; name the file in its pack and let the file name carry identity.
