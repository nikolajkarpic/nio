---
id: C-261028-dclz
type: change
title: "Flow-state architecture note: git exit-code mode and two jury functions"
answers: why              # why | reuse | jury
date: 2026-10-28
by: "agent / claude-code / opus"                # role / host / model, or human
run: "R-261028-stif"              # run ID; empty when written by hand
against: ".nio/specs/2026-10-28-flow-state/architecture.md"# the spec, plan or record that is wrong
outcome: accepted         # pending | accepted | rejected
paths: [".nio/specs/2026-10-28-flow-state/architecture.md", "src/nio/records.py"]
tags: [flow-state, architecture]
supersedes: []
---
## What is wrong
The flow-state architecture note says `nio flow` reaches git only through `records.git` and lists the jury functions it reads. `records.git` returns stdout lines only, but the gate commit must report git's error when it fails (spec FR-20), and finding an edited approved file needs `jury.blob` and `jury.artefact`, which the note doesn't list. Plan jury finding J-1 (architecture-fit).
## Proposed change
1. `records.git` gains an optional mode that returns the exit code and stderr as well; every current caller keeps today's behaviour.
2. The note's list of functions `nio flow` reads adds `jury.blob` and `jury.artefact`.
## Human decision
Accepted by the human (2026-10-28, flow-state grill Q25).
