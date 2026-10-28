---
id: C-261028-i36m
type: change
title: "Plan jury: lenses that must search the repo can only read the listed files"
answers: why              # why | reuse | jury
date: 2026-10-28
by: "agent / claude-code / opus"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
against: ".nio/specs/2026-10-28-plan-jury/spec.md"
outcome: pending          # pending | accepted | rejected
paths: ["src/nio/jury.py", "src/nio/agents/architecture-fit.md", "src/nio/agents/test-proof.md"]
tags: [plan-jury, grounding, e2e]
supersedes: []
---
## What is wrong
The end-to-end run of `tests/test_lenses.py` (2026-10-28) showed the plan-jury spec asking for two things that can't both hold:
- FR-46 has architecture-fit flag a `Like: none` reason when similar code exists. FR-20 has test-proof search the repo before saying a test is missing.
- FR-42 and FR-43 give a juror only the listed files (the plan files, the spec, CLAUDE.md, and the files contracts bind or name on `Like:`), and accept quotes only from them.
So a parser elsewhere in the repo is never in architecture-fit's files. In `test_ac50` it never mentioned `parsers.py`, and a quote from that file would be dropped anyway. The pack also tells jurors to read nothing else, which undercuts FR-20.

## Proposed change
Let test-proof and architecture-fit search the whole repo (their cards already have Read, Grep and Glob). Accept a quote from any repo file that a finding names in its cites, so grounding stays checkable. The listed files stay the pack every juror starts from. This reopens grill Q2 of 2026-10-28-plan-jury ("the plan files plus what the juror was given"); the human decides.

## Human decision
Pending.
