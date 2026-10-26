---
id: D-261026-r52z
type: decision
title: "Jury stop rule: after the first review only confirmed blockers start rounds, plus one final fix check"
status: human            # proposed | human | recorded; jury standing comes from verdicts
answers: why              # why | reuse | jury
date: 2026-10-26
by: "human"                # role / host / model, or human
run: "R-261026-bnld"              # run ID; empty when written by hand
serves: [AC-2, AC-3, AC-5, AC-9, AC-21]                # AC IDs this decision serves
task: ""                  # task ID, if any
paths: [src/nio/jury.py, skills/jury/SKILL.md, src/nio/agents/*.md]                 # files or globs it touches
tags: [jury, convergence, re-review]
supersedes: []            # IDs of records this replaces
---
## Decision
After the first review, only a blocker the refuter confirms starts another round. Majors and minors a re-review finds not fixed go to the human in one list (fix or accept); a new major or minor is only a note. One final fix check, which can raise only blockers, reviews the fixes made from that list, and settling what it flags ends the jury as approved, naming the unreviewed fixes. A re-review is a fix check: the finding, the changed items before and after and their neighbours, and nothing else of the spec.
## Why
On large specs the jury didn't converge. Each round's fixes were new text that the next whole-spec round judged fresh, so every round raised new majors (3 rounds on the grill spec, 4 on grill-checks, both closed by the human; #52). No re-review in the three dogfood juries found a new confirmed blocker.
## Rejected alternatives
- Stop at a quiet round (nothing above minor): every past round had majors, so it would never have stopped.
- Hard cap at 2 rounds: a real late blocker would reach the human without a refuter confirming it.
- Whole spec as context in a re-review: it is the read that produced the new wording findings.
- No check of the list's fixes: the human wanted nothing to go unreviewed (spec 2026-10-26-jury-convergence, Q5).
## Reuse
Any gate whose reviewers re-read artefacts after fixes: check the fixes against their findings, not the whole artefact, and cap with one final check.
