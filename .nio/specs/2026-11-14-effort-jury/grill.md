# Grill: 2026-11-14-effort-jury

Session 1 (2026-11-14): the human answered Q1-Q6; an agent recorded them and looked up the facts.

## Lookup · OP-1, OP-2, OP-6, OP-8, OP-10, OP-12, OP-13, OP-14 · 2026-11-14
Facet: actors and permissions, change from today, effect on data and state, verification
Found: RF-1, RF-2 (OP-1: the builder closed 39 of 41 epic gates; hand fixes on two of three 2026-11-08 branches), RF-3, RF-4 (OP-2: what depends on per-epic gates), RF-5, RF-6 (OP-6: no base branch recorded; three-dot diff starts at the merge base), RF-7 (OP-8: history names role, host and model only, no session), RF-8 (OP-10: per-epic evidence and what is collected once), RF-9 (OP-12: #101-#104), RF-10 (OP-13: lens cap), RF-11 (OP-14: today the epic's builder also juries it), RF-12 (GitHub refuses an author's own approval), RF-13 (lite still runs epic juries). Retired OP-1, OP-2, OP-6, OP-8, OP-10, OP-12, OP-13, OP-14.
Patched: UJ-1 evidence, Decisions, Key entities

## Q1 · OP-3 · 2026-11-14
Question: When an epic's tasks are done, does its end keep any check at all, or nothing until the `pr` gate?
Context: Today the closing task's review runs `tests.epic` for a non-last epic and the full suite at the last (RF-4); then an epic jury runs.
Options:
1. Full suite must pass: an epic closes only when the whole test suite passes; no reviewers, no rounds.
2. Suite + one conformance check: the suite, plus one conformance juror on the epic.
3. Nothing: the epic closes when its tasks are done; everything waits for the `pr` gate.
Answer: 1. Full suite must pass: an epic closes only when the whole test suite passes; no reviewers, no rounds. [human]
Patched: Summary, FR-1, AC-1, AC-16 (new), state table header; retired OP-3

## Q2 · OP-4 · 2026-11-14
Question: Where do fix tasks from `pr` gate findings go in tasks.md?
Options:
1. New final 'PR fixes' epic: the pr gate's fix tasks go into one closing epic created automatically; run through the normal implement steps, then the suite, then the gate's fix check.
2. Under the epic they touch: each fix task under the `#### Fixes` of the epic whose code the finding is about.
3. Fixed directly, no tasks: the driver fixes findings itself with no task.
Answer: 1. New final 'PR fixes' epic: the pr gate's fix tasks go into one closing epic created automatically; run through the normal implement steps, then the suite, then the gate's fix check. [human]
Patched: FR-15 (new), AC-6, UJ-1, state table, Key entities, Glossary; retired OP-4

## Q3 · OP-5 · 2026-11-14
Question: When the `pr` gate is reached, does the run stop before the pull request, or open it and wait for the human there?
Options:
1. Open PR, wait there: open the pull request with the verdict in its body and wait.
2. Stop before the PR: the run stops; the human opens the pull request.
3. Draft PR, wait: open a draft pull request and wait.
Answer: free-form: "open pr and run independent evaluator to comment APPROVED or REQUEST_CHANGES in the pr and leave it there". Written as: when the `pr` gate is reached, auto or not, the run pushes the branch and opens the pull request; an independent evaluator, the `pr` gate's fresh driver and never the builder, posts one pull request comment whose first word is `APPROVED` or `REQUEST_CHANGES`, followed by the verdict and findings; the run then stops and waits; nio never merges. The human approves by merging or recording the gate. A GitHub review approval is not used, since GitHub refuses one from the account that opened the pull request (RF-12). [human]
Patched: Summary, A-1, UJ-1, US-3 test, FR-16 (new), AC-19 (new), FR-2, FR-8 and AC-10 (derived), SC-2, non-goals 3 and 4, Key entities, Glossary; retired OP-5

## Q4 · OP-7 · 2026-11-14
Question: When the effort diff is too large for one juror to read whole, how is it split among jurors?
Options:
1. Split by epic, plus one whole-view: over a size limit, each requirement-checking lens gets one epic's diff, in parallel, and the integration lens alone sees the whole change at summary level.
2. Split by file group: jurors get groups of files.
3. No split, warn: one juror per lens reads the whole diff; a warning names its size.
Answer: 1. Split by epic, plus one whole-view: over a size limit (1,500 changed lines by default), each requirement-checking lens gets one epic's diff, in parallel, and the integration lens alone sees the whole change at summary level. [human]
Patched: FR-13 (new), AC-17 (new), Risks; retired OP-7

## Q5 · OP-9 · 2026-11-14
Question: What happens to efforts already implementing when this lands, with some epic gates closed?
Options:
1. Switch at next epic: in-flight efforts keep already-closed epic gates; remaining epics close on suite-only; the pr gate covers the whole diff including already-juried epics.
2. Finish on the old rule: they keep per-epic juries to the end.
3. Ask per effort: the human picks for each effort.
Answer: 1. Switch at next epic: in-flight efforts keep already-closed epic gates; remaining epics close on suite-only; the pr gate covers the whole diff including already-juried epics. [human]
Patched: US-4, FR-12, AC-15; retired OP-9

## Q6 · OP-11 · 2026-11-14
Question: Does a lite-route effort get the `pr` gate too, or keep what it has today?
Context: The lite route skips only the spec jury and planning; it still runs per-epic implementation juries (RF-13).
Options:
1. Final jury replaces it: lite-route efforts get only the pr gate (PR + verdict comment) instead of their implementation jury.
2. Keep the lite jury only: lite efforts keep their per-epic implementation jury and get no `pr` gate.
3. Both: per-epic juries and the `pr` gate.
Answer: 1. Final jury replaces it: lite-route efforts get only the pr gate (PR + verdict comment) instead of their implementation jury. [human]
Patched: FR-14 (new), AC-18 (new); retired OP-11

## Call · FR-13 · 2026-11-14
The size limit's setting is `jury.split_lines`, default 1,500 changed lines (the number the human gave in Q4), counted on the effort diff. [agent]
Five no's: changes what a user can do: no; sees: no (the human set the behaviour and the number); who may do it: no; data: no; cost: no (the default is the human's).
Patched: FR-13, AC-17

## Call · OP-13, FR-4, FR-5 · 2026-11-14
The `pr` gate's own default `jury.max_runs` is 7, so its five core lenses plus the two risk lenses the table can add (security, risk-rollback) all run without asking (RF-10); a configured `jury.max_runs` still wins, and over it the existing rule applies (the human picks; core lenses can't be dropped). [agent]
Five no's: changes what a user can do: no; sees: no (one gate fewer asks the human to pick, only for a spec flagged for both security and rollback); who may do it: no; data: no; cost: no (at most one more lens run on one gate per effort, while every per-epic gate, 2 to 7 rounds each, goes away).
Patched: Decisions; retired OP-13

## Call · OP-6, Effort diff · 2026-11-14
`main` in the effort diff is the remote's default branch, found as the pre-push hook finds it (RF-5); the three-dot diff starts at the merge base, so commits that land on main after the branch began are not judged (RF-6). The pull request is opened against the same branch. [agent]
Five no's: changes what a user can do: no; sees: no (on this repo it is `main`); who may do it: no; data: no; cost: no.
Patched: Key entities (Effort diff), Glossary, Decisions

## Call · FR-7 · 2026-11-14
The `pr` gate keeps today's jury rules: the stop rule (D-261026-r52z), the round cap `jury.max_rounds`, the automatic round, the capped batch and fix tasks for confirmed findings, as the merged round-cap spec set them; only where the fix tasks go changes (Q2). Taken as drafted. [agent]
Five no's: changes what a user can do: no; sees: no; who may do it: no; data: no; cost: no (today's rules).
Patched: FR-7

## Derived · FR-8, AC-10 · 2026-11-14
From: FR-16 (Q3: an independent evaluator, the gate's fresh driver, not the builder), RF-7 (nio can't tell sessions apart, so it can't refuse the builder by identity) and RF-11 (today the epic's builder also juries it; a gate that is its own unit gets a driver started from the brief alone, which built nothing). So the `pr` gate is its own unit in a fresh driver; the earlier draft's "refuse the builder when it tries" is dropped, as nothing can recognise it.
Patched: FR-8, AC-10, Fresh gate driver entity, Decisions

## Derived · UJ-1, AC-6 · 2026-11-14
From: UJ-1 from FR-1, FR-2, FR-3, FR-11, FR-15 and FR-16; AC-6 from FR-7 and FR-15 (Q2).
Patched: UJ-1, AC-6

## Q7 · defaults · 2026-11-14
Question: Confirm the remaining proposals and the agent calls as written?
Options:
1. Confirm all.
2. Change the 7-reviewer limit.
3. Go through each.
Answer: 1. Confirm all: FR-5 and AC-5 (risk flags add at the `pr` gate the lenses they add at a gate today), AC-9 (a clean diff gets no integration finding), FR-10 and AC-13 (capped `pr` gate closes under the round-cap rulings), the `done` state-table row; and the agent calls: the `pr` gate runs in a fresh driver started from the brief alone (FR-8, AC-10), its default `jury.max_runs` is 7, `main` is the remote's default branch (Effort diff), `jury.split_lines` defaults to 1,500. [human]
Refs: FR-5, AC-5, AC-9, FR-10, AC-13, FR-8, AC-10, FR-13, Effort diff
Patched: those items to [human]; Decisions

## Q8 · J-6, J-5, J-9 · 2026-11-14
Question: Closing every epic on the whole suite goes against a current decision (epic check runs the epic's own tests, the full suite only at the end). Which way?
Context: D-261106-ltsr (memory, current); spec jury round 1 confirmed the contradiction 3 of 3.
Options:
1. Keep the full suite at every epic and file a change request against the old decision.
2. Follow the old decision: an epic closes on its tasks' own tests; the full suite runs once, at the `pr` gate.
3. Full suite every few epics.
Answer: "whichever would be faster" → 2. Follow D-261106-ltsr: an epic closes when its tasks' own tests have passed (already proved at each task's green); the full suite runs once, at the `pr` gate; no change request. A failed test at an epic's last task goes back to `implementing`. Supersedes Q1. [human]
Refs: J-6, J-23, J-5, J-9, FR-1, AC-1, AC-16, D-261106-ltsr
Patched: Summary, UJ-1, US-1, AC-1, AC-16, AC-2, FR-1, FR-2, state table, Decisions (Q1 line, evidence line)

## Q9 · spec jury round 1 batch · 2026-11-14
Question: The remaining round-1 findings, each with a recommended ruling: take all as recommended?
Options:
1. All as recommended.
2. Change some of them.
3. Go through each.
Answer: 1. All as recommended. [human]
- Fix (J-24, J-4): an epic part-way through closes on the new rule; an epic already in its old implementation jury (capped or with open fix tasks) finishes that jury first.
- Fix (J-1, J-17, J-13): the `pr` gate's approval is recorded only through a human-only command; no agent can record it, auto on or off; a merge without that record doesn't count; approval only with no unruled finding; both tables aligned.
- Fix (J-2, J-21, J-11): an open pull request is reused; one verdict comment, edited in place each round; a failed push, pull request or comment stops with a clear message; the real-model lens ACs get a fixed pass rule.
- Fix (J-3): the verdict names the head commit judged and is stale if HEAD moves.
- Fix (J-12, J-19): with a split diff, commits outside any epic (the `PR fixes` epic included) get one extra pack.
- Fix (J-14): after the `PR fixes` epic's tasks are done, the push updates the pull request and the gate runs its fix check.
- Accept as risk: J-18 (NIO can't tell sessions apart; skill text only), J-16 (keep the system-closed list).
- Confirm FR-7 as written (J-10, J-15).
Refs: J-1, J-2, J-3, J-4, J-10, J-11, J-12, J-13, J-14, J-15, J-16, J-17, J-18, J-19, J-21, J-24
Patched: Summary, UJ-1, US-3, US-4, AC-6, AC-7, AC-8, AC-9, AC-11, AC-12, AC-15, AC-17, AC-19, AC-20 (new), AC-21 (new), AC-22 (new), AC-23 (new), AC-24 (new), AC-25 (new), AC-26 (new), AC-27 (new), AC-28 (new), FR-7 (retagged [human]), FR-9, FR-12, FR-13, FR-16, FR-17 (new), state table, decision table, Verdict comment entity, Decisions
