---
id: D-261107-pdq4
type: decision
title: "nio jury next drives a gate step; jurors write their own output"
status: recorded          # proposed | human | recorded; jury standing comes from verdicts
answers: why              # why | reuse | jury
date: 2026-11-07
by: "orchestrator / claude-code / claude-opus-5-5 (delegated by human)"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
serves: [AC-1, AC-2, AC-3, AC-4, AC-5, AC-11, AC-12]                # AC IDs this decision serves
task: "T-3"                  # task ID, if any
paths: [src/nio/jury.py, src/nio/cli.py, skills/jury/SKILL.md]                 # files or globs it touches
tags: []
supersedes: []            # IDs of records this replaces
---
## Decision
A jury gate is driven by `nio jury next <slug> <gate> [--run <run>]`: it plans, renders the agents, writes every lens's pack (first review or fix check) under `.nio/runs/<run>/jury/packs/`, collects, writes the refuter batch to a file, composes and records the outcome, starts a re-review's run itself, and ends with one `next:` line. Its own state is `packs/step.json` in the run, not a ledger field.
## Why
#76: the orchestrator's own calls were most of a gate's time and cost. Scenario A (research RF-2) took 31 orchestrator tool calls with the separate commands; the skill's steps now take 14 (15 with the fixture's fourth lens), measured by `test_ac11_scenario_a_in_at_most_15_calls`, which follows the step's own `next:` lines.
## Rejected alternatives
- Only collect + check in one call (#76's minimum): about half the calls, no margin (grill Q8).
- Ledger field for the step's state: a schema change for scratch state.
- The step writing escalation packs: rare; the skill keeps them (spec non-goal).
## Reuse
When a skill strings several CLI calls whose order never changes, fold them into one command that prints only the next action.
