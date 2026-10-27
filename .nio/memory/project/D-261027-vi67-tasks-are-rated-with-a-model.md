---
id: D-261027-vi67
type: decision
title: "Tasks are rated with a model tier and an effort; a frontier tier sits above max"
status: human            # proposed | human | recorded; jury standing comes from verdicts
answers: why              # why | reuse | jury
date: 2026-10-27
by: "human"                # role / host / model, or human
run: "R-261027-65by"              # run ID; empty when written by hand
serves: [AC-14, AC-25, AC-26]                # AC IDs this decision serves
task: ""                  # task ID, if any
paths: [src/nio/agents.py]                 # files or globs it touches
tags: [tasks, tiers, effort, agents]
supersedes: []            # IDs of records this replaces
---
## Decision
Each task states `Tier: <cheap|strong|max|frontier>: <reason>` and `Effort: <low|med|high>`, the same values agent cards use. A fourth tier, `frontier`, sits above `max` for agent cards and tasks alike. Each coding agent maps tiers to its own models in config (Claude: Haiku, Sonnet, Opus, Fable), and a host with no frontier model falls back to its max model.
## Why
There are several coding agents, and the human wants both the model and the effort judged, with Claude's Fable available (spec 2026-10-27-tasks-stage, grill Q1, Q2). The #42 decision "low/medium/high mapped to cheap/medium/strong" rested on a misstated tier list: the real tiers were cheap, strong and max.
## Rejected alternatives
- low/medium/high mapped to cheap/strong/max: one axis only, and the names clash with the jury's risk tier.
- Fable replaces Opus as max: no way to choose Opus over Fable.
- Naming the exact model per task: ties tasks.md to one coding agent.
## Reuse
Anything that picks a model for an agent or a worker: rate it with a host-neutral tier and an effort, and let config map them per host.
