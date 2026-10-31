---
id: C-261031-rvfx
type: change
title: "Implementation-jury: fix the ten findings of the branch code review before E-2's re-review"
answers: why              # why | reuse | jury
date: 2026-10-31
by: "human"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
against: ".nio/specs/2026-10-27-implementation-jury/tasks.md"
outcome: accepted          # pending | accepted | rejected
paths: []
tags: []
supersedes: []
---
## What is wrong
A code review of the branch found: `nio jury template` and `nio jury files` crash at the implementation gate; the epic check blocks disposing of a finding once fix tasks exist; a failed suite can read as passing or as a crash; a fix check can loop or keep stale evidence; CLI findings stay open after a good re-run; a stale results file leaves conformance collected but never joined; only Python and JS tests are recognised; `.nio/` text counts as using a symbol.
## Proposed change
Only `plan` and `collect` need a finished epic. Evidence is re-judged every review round, carrying a test matched earlier. On a failed suite, a test the summary doesn't name is run alone; a runner that can't run one reads as didn't run. Built as T-46, under E-2's Fixes.
## Human decision
Accepted 2026-10-31: "Yes please fix it and finish up".
