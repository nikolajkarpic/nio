---
id: D-261107-xzn3
type: decision
title: "Lite routing (#11): lite only for a defect with an obvious expected behaviour, one-module scope and no auth/money/data-deletion/migration/pii flag; escalation rewrites the spec on the full route"
status: recorded          # proposed | human | recorded; jury standing comes from verdicts
answers: why              # why | reuse | jury
date: 2026-11-07
by: "orchestrator / claude-code / claude-opus-5-5"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
serves: [AC-9, AC-11, AC-13, AC-14]
task: ""                  # task ID, if any
paths: [skills/spec/SKILL.md, src/nio/tasks.py]
tags: []
supersedes: []            # IDs of records this replaces
---
## Decision
The spec skill routes lite only when all four hold: a defect, an expected behaviour stated or obvious, a likely one-module scope, and no auth, money, data-deletion, migration or pii flag; else full. A lite effort escalates on non-test files in more than one folder (an `escalate:` note from `nio check tasks`), a new dependency, or a change to an interface used outside the bug's folder or to stored data: the same spec is rewritten on the full template with tags kept, and the flow places it at spec_jury or grilling. A declined switch continues on lite, logged in grill.md.
## Why
#11's recommended default: rules an agent and the CLI can check and explain; a wrong call is caught by escalation, so no model router is needed before mis-route data exists (#31).
## Rejected alternatives
- A CLI check refusing a lite spec with a risky flag: breaks today's bugfix fixtures carrying `money`.
- A new full spec plus abandoning the lite one: a second folder and branch, and a human-only abandon.
## Reuse
Revisit the criteria once #31 has mis-route data.
