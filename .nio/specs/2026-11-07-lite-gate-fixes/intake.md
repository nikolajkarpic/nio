# Intake

## The human's words (via the delegating orchestrator session)

Found dogfooding the lite path (#44) on #91; both block every lite effort, so fix them in the #44 PR.

## Source: https://github.com/nikolajkarpic/nio/issues/111

# nio check tasks treats a bug fix's one epic as foundational unless it is headed (US-n)

## Problem
Found dogfooding the lite path (#44) on #91: the tasks drafter wrote the bug fix's one epic as `## E-1 <title>` (the template and card say "a bug-fix spec: one epic, E-1" and give no suffix). `nio check tasks` then failed every AC with "T-1 serves AC-n, which no task depending on it serves": `tasks.check` applies the foundational-epic rule (#42 FR-45) to any epic whose story is empty, and the last task of an epic has no dependents. Every lite effort hits this; the tests passed only because their fixtures head the epic `(US-1)`.

Workaround used: head the epic `(US-1)`.

## Proposal
Apply the foundational rule only to `(Foundation)` epics, or skip it on a lite spec; add a test with a bug-fix epic that has no suffix.

Refs: src/nio/tasks.py:257 · #44 · #91

Also from the same dogfood: on a lite spec (no tests.md) `nio jury evidence` lists no tests (`results.json` `tests: []`), so every AC of the implementation gate reads 'no passing evidence' and files a pointless fix task. Fixing both in the #44 PR through a second lite effort.
