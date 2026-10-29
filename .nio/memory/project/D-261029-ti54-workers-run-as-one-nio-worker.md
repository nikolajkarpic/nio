---
id: D-261029-ti54
type: decision
title: "Workers run as one nio-worker card per tier and host"
status: proposed          # proposed | human | recorded; jury standing comes from verdicts
answers: why              # why | reuse | jury
date: 2026-10-29
by: "grill agent / claude-code / claude-opus-5-5"                # role / host / model, or human
run: "R-261029-ksbo"              # run ID; empty when written by hand
serves: ["AC-2", "AC-3"]                # AC IDs this decision serves
task: ""                  # task ID, if any
paths: ["src/nio/agents.py", "src/nio/agents/*.md"]                 # files or globs it touches
tags: ["agents", "implement"]
supersedes: []            # IDs of records this replaces
---
## Decision
`nio agents sync` renders one `nio-worker-<tier>` card per tier (cheap, strong, max, frontier) for each host, each carrying the model that tier maps to there. The orchestrator starts the card for the task's `Tier:`; the task's `Effort:` is passed per call only where the host takes it.
## Why
Only Claude Code lets a caller pick a subagent's model per call; in Codex the agent file's model wins and per-spawn choice is reported broken, and Gemini CLI fixes the model per agent (research RF-7). NIO already writes the model into each rendered card (RF-8), so a card per tier honours the task's tier on every host.
## Rejected alternatives
- Pass the model per call: one card, but Codex and Gemini CLI would ignore the tier.
- One model for every worker: drops the tier rating the tasks stage does (D-261027-vi67).
## Reuse
Any shipped card whose model must vary per task. Grill Q4 of 2026-10-29-implement-stage (delegated, agent answer).
