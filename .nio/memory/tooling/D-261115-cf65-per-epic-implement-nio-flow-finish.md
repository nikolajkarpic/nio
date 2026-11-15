---
id: D-261115-cf65
type: decision
title: "Per-epic implement: nio flow finish runs the epic's tests; auto lives in the existing skills"
status: proposed          # proposed | human | recorded; jury standing comes from verdicts
answers: why              # why | reuse | jury
date: 2026-11-15
by: "plan / claude-code / opus"                # role / host / model, or human
run: "R-261115-fren"              # run ID; empty when written by hand
serves: [AC-2, AC-18, AC-20]                # AC IDs this decision serves
task: ""                  # task ID, if any
paths: [src/nio/implement.py, skills/implement/SKILL.md, skills/jury/SKILL.md]                 # files or globs it touches
tags: []
supersedes: []            # IDs of records this replaces
---
## Decision
An epic is handed back with `nio flow finish <slug> E-n`, which runs the epic's named tests itself and closes the epic only on a pass; the full-auto driver loop and the one fix agent per jury round are sections of the existing jury and implement skills, run as fresh general-purpose agents.
## Why
FR-5 removes `green`, so the hand-back needs its own name, which the background mod matches. No new skill folder or card keeps the plan inside the existing structure, with no architecture stage (plan skill stop list).
## Rejected alternatives
- Reuse `nio flow green` for the epic: FR-5 says green no longer gates anything, and the name would mislead.
- `skills/auto/` and a `nio-fixer` card (#122's architecture): a new module, not approved for this effort.
## Reuse
When a stage needs an agent loop or a one-off agent, add a section to the skill that already drives that stage before adding a skill or card.
