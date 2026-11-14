---
id: C-261108-czgp
type: change
title: "Spec problem in T-30: T-30 / TC-28: `test_skip_needs_reason` must fail first, then pass once the code is written (fix for J-1: T-2 names src/nio/templates/project/product.md, which is not in the repo at 7b81c93c)"
answers: why              # why | reuse | jury
date: 2026-11-08
by: "orchestrator / claude-code / claude-opus-5-5 (delegated by human)"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
against: ".nio/specs/2026-11-08-project-onboarding/spec.md"
outcome: accepted          # pending | accepted | rejected
paths: []
tags: []
supersedes: []
---
## What is wrong
The spec says: T-30 / TC-28: `test_skip_needs_reason` must fail first, then pass once the code is written (fix for J-1: T-2 names src/nio/templates/project/product.md, which is not in the repo at 7b81c93c)

The code shows: The finding is that the template files were never committed. src/nio/onboard.py:act already refuses a blank skip reason (it raises ValueError, so exit 1, and writes nothing). It already reads templates/project/{n}.md for --empty. The six templates (product, personas, stack, architecture, infra, principles) are on disk in /home/work/nio-49/src/nio/templates/project/, but they are untracked. So TC-28 passes before any code is written, and `nio flow red` refuses it.
## Proposed change
Drop the red/green requirement for T-30 (run it as direct), or mark TC-28 as already covered. The fix itself is only to commit the untracked src/nio/templates/project/*.md files together with the src/nio/onboard.py change.

Handoff: 6b19cef51093cd5440df8bef31e11dbd75a8296e0c7b0aaab5955a2bc9477c69
## Human decision
Accepted (human, 2026-11-08): the round-5 fix tasks were attached unrelated, already-passing tests. Duplicates removed; the remaining fix tasks (T-30, T-36, T-37, T-38, T-41, T-45) each name a new test that fails while the defect exists. T-39 is unchanged, awaiting the human's ruling.
