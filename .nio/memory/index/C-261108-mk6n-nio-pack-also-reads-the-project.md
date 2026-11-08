---
id: C-261108-mk6n
type: change
title: "nio pack also reads the project docs and hashes their recorded source files"
answers: why              # why | reuse | jury
date: 2026-11-08
by: "orchestrator / claude-code / claude-opus-5-5 (delegated by human)"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
against: "D-261024-bygj"               # the spec, plan or record that is wrong
outcome: accepted          # pending | accepted | rejected
paths: ["src/nio/pack.py", ".nio/specs/2026-11-08-project-onboarding/spec.md"]
tags: ["pack", "onboarding", "project-docs"]
supersedes: []
---
## What is wrong
D-261024-bygj says `nio pack` only reads memory and never researches the code. The onboarding spec (2026-11-08-project-onboarding, FR-17, FR-25) has the pack also carry the project docs under `.nio/project/` and mark one stale by hashing the files that doc records as its sources. The spec jury (J-9) found that this goes beyond the decision as written.
## Proposed change
`nio pack` may also read `.nio/project/` and hash the source files the project docs record, nothing else. This keeps the decision's reasons: no model, no search of the code to find scope, the same result every time, cheap. Scope still comes from the caller.
## Human decision
Accepted 2026-11-08 by the orchestrator under the human's standing grant (orchestrator / claude-code / claude-opus-5-5, delegated by human) to take the recommended option; the human can reject it.
