---
slug: 2026-11-14-jury-round-cap
route: full
epic: ""                         # "<epic slug>/R-<n>" when this is a slice of an epic
risk: []                         # auth | pii | money | external-input | data-deletion | migration | multi-party | public-api
retired: [OP-1, OP-2, OP-3, OP-4, OP-5, OP-6, OP-7, OP-8, OP-9]  # IDs removed from this spec; never reused
---
<!-- Spec template. WHAT and WHY only, never HOW. Every item ends with its provenance: [human] (the grill
confirmed it), [research: RF-n] (a finding in research.md) or [default] (your proposal; the grill must confirm it).
IDs are permanent: number new items after the highest ever used, never renumber, list removed IDs in `retired`.
Remove a section that doesn't apply; never write N/A. `nio check spec 2026-11-14-jury-round-cap` checks all of this. -->
# Cap jury rounds per gate and let fix tasks land without reopening the tasks gate

## Summary
Jury gates run too many rounds and implementing one feature takes about 8 hours and many tokens. This spec covers two
of four agreed fixes: every jury gate stops after a configurable number of rounds (default 2), runs one automatic third
round only when two or more blockers are still open, skips open minors and hands the rest to the human in one batch
(#129); and an approved tasks.md accepts appended fix tasks and their retirements without reopening the tasks gate,
while findings owned by a later epic never become fix tasks, and glob patterns in a task's Files list reach packs as real paths (#126). The aim is fewer rounds, fewer gate re-entries, and
less wall time and tokens per effort. [human]

## Actors and journeys
- **A-1 Human owner**: runs efforts through nio, rules on findings and overrides gates; wants features done faster and cheaper. [human]
- **A-2 Orchestrating agent**: drives `nio jury next` and `nio flow` through a gate and appends fix tasks. [human]
- **A-3 Jurors** (including escalation jurors, #105): review the judged artefact and raise findings. [human]

**UJ-1 Gate reaches its round cap** (A-1, A-2) [human]
1. The agent runs `nio jury next` for a gate; rounds 1 and 2 run as today.
2. After round 2, if two or more blockers are still open, NIO runs a third round on those blockers' lenses by itself, once.
3. Then `nio jury next` starts no further round: open minors are closed as skipped, and every open major and blocker is printed in one batch.
4. The human rules on each: accept as risk, fix, or one more round.
- Misuse: the agent rules on the batch itself instead of handing it to the human, or keeps calling `nio jury next` hoping for a fourth round.
- Evidence: issue #129; 17 rounds over a cap of 2 across 10 gates of three efforts on 2026-11-08 [research: RF-1].

**UJ-2 Fix task added after the tasks gate is approved** (A-2, A-1) [human]
1. The implementation jury raises a finding; the agent appends a fix task under the epic's `#### Fixes`.
2. The effort stays in implementing; the tasks gate is not reopened.
3. The human retires a fix task; its finding closes as accepted risk and is not re-created next round, and the gate is not reopened.
- Misuse: an agent edits planned (non-fix) tasks and expects it to pass as an append-only fix change.
- Evidence: issue #126 and its 2026-11-14 comment (effort back to `tasks_jury` 2x on #123, 4x on #122).

## User stories

### US-1 Cap every jury gate at the configured round count (P1) [human]
- **Why this priority:** extra rounds are the largest cost measured (17 rounds over target, about 1-2 h per effort).
- **Independent test:** drive a gate through two rounds with one open blocker and one open major left and check that `nio jury next` prints the batch instead of starting round 3.

- **AC-1** (FR-1, FR-2) Given a gate whose round 2 has finished with open majors, at most one open blocker and `jury.max_rounds` unset, when the agent runs `nio jury next`, then no round 3 starts and every open major and blocker is printed in one batch. [human]
  Observable: no round-3 pack exists; output lists every open major and blocker ID of the gate and no minor. Level: integration.
- **AC-2** (FR-3) Given `jury.max_rounds` is 3 in config, when round 2 finishes with open findings, then `nio jury next` starts round 3 as usual. [human]
  Observable: a round-3 pack is written. Level: integration.
- **AC-3** (FR-4) Given round 2 is in progress and escalation jurors (#105) join it, when their outputs are collected, then the round count is still 2 and the cap applies after it. [research: RF-2]
  Observable: the gate ledger's `round` after collecting the two escalation juror outputs `<gate>-<lens>-2.md` and `<gate>-<lens>-3.md` (the `-2`/`-3` suffixes number the escalation jurors, not rounds) is 2; the `next:` line of `nio jury next` names no further escalation juror for that blocker. Level: integration.
- **AC-21** (FR-4) Given a blocker raised in round 1 whose lens already has escalation jurors from round 1, when round 2 collects another juror of that lens, then the escalation count for that blocker includes the round-1 jurors as well. [research: RF-2]
  Observable: the ledger's escalation count for that blocker equals the jurors of that lens since round 1, not only round 2's. Level: integration.
- **AC-4** (FR-5) Given the batch is printed, when the human rules some findings "one more round", then exactly one more round runs, with packs only for the lenses that raised those findings, and the batch is printed again after it if findings remain open; the human may then ask for another. [human]
  Observable: the further round has packs for exactly those findings' lenses; a second `nio jury next` after it prints the batch and starts no round by itself; a second "one more round" ruling starts one more. Level: integration.
- **AC-5** (FR-6) Given the batch is printed, when the human rules a finding "accept as risk" or "fix", then that finding leaves the open list and the gate can close once none remain open. [human]
  Observable: the finding's disposition is set with `--by human`; the gate closes with no open findings. Level: integration.
- **AC-6** (FR-7) Given `jury.max_rounds` is 0, negative or not a whole number, when `nio jury next` runs, then it stops with an error naming the setting and starts no round. [human]
  Observable: non-zero exit; error text names `jury.max_rounds`. Level: unit.
- **AC-7** (FR-1) Given round 2 finished with no open findings, when `nio jury next` runs, then the gate proceeds as today and no batch is printed. [human]
  Observable: no batch output; gate state as before this change. Level: integration.
- **AC-14** (FR-13) Given round 2 (the cap) finished with 2 open blockers and 1 open major, when the agent runs `nio jury next`, then round 3 starts by itself with packs only for the lenses that raised those blockers. [human]
  Observable: round-3 packs exist for exactly the blockers' lenses; no batch is printed yet. Level: integration.
- **AC-15** (FR-14) Given the automatic third round finished with 2 blockers still open, when `nio jury next` runs, then no round 4 starts and the open blockers and majors are printed in one batch. [human]
  Observable: no round-4 pack exists; the batch lists both blockers. Level: integration.
- **AC-16** (FR-15) Given a gate stops at the cap with an open minor, when the batch is printed, then the minor is closed `accepted-risk` by the system with note "minor, skipped at the round cap", is not in the batch, and is listed in the gate summary when the gate closes. [human]
  Observable: the minor's disposition is `accepted-risk`, `by` is the system, note as given; the batch does not name it; the gate summary printed when the gate closes names it. Level: integration.
- **AC-17** (FR-2) Given round 2 finished with exactly one open blocker, when `nio jury next` runs, then no round 3 starts and that blocker is in the batch. [derived: FR-2, FR-13]
  Observable: no round-3 pack exists; the batch lists the blocker. Level: integration.
- **AC-18** (FR-16) Given the spec or plan gate is capped, when the human rules a finding "fix", then the orchestrator edits spec.md or plan.md for it and the gate closes with no juror re-check. [human]
  Observable: the artefact changed after the ruling; no further round or fix-check pack is written; the gate is closed. Level: integration.
- **AC-22** (FR-18) Given a round at or over the cap ends with only minors open, when `nio jury next` runs, then every minor is skipped as in FR-15 and the gate closes with no batch to rule. [human]
  Observable: each minor's disposition is `accepted-risk` by the system; no batch is printed; the gate is closed and its summary names the minors. Level: integration.
- **AC-23** (FR-19) Given round 1 of a gate with a cap of 2 or more ends with open majors or minors and no confirmed blocker, when `nio jury next` runs, then no new round starts and the findings go to the human as today. [human]
  Observable: no round-2 pack is written; the output lists the open findings for the human. Level: integration.
- **AC-24** (FR-20) Given a round of the gate is running, or the gate has not reached the cap, when the human gives a capped-batch ruling (accept as risk, fix, one more round), then it is refused and nothing is recorded. [human]
  Observable: non-zero exit; the finding's disposition is unchanged; no round pack is written. Level: integration.
- **AC-25** (FR-6) Given the batch holds two findings, when the human rules only one of them, then the gate stays capped and the unruled finding is still listed as open. [human]
  Observable: the ruled finding has its disposition; the next `nio jury next` prints the batch with the unruled finding only and the gate is not closed. Level: integration.

### US-2 Fix tasks and their retirements don't reopen the tasks gate (P1) [human]
- **Why this priority:** each reopening cost a juror run, 15-40 orchestrator turns and a commit, about 20-60 min per effort.
- **Independent test:** approve tasks.md, append a fix task under `#### Fixes`, retire it, and check the effort stays in implementing.

- **AC-8** (FR-8) Given an approved tasks.md, when a fix task is appended under an epic's `#### Fixes`, then the effort stays in `implementing` and the tasks gate is not reopened. [human]
  Observable: `nio flow status` state is `implementing`; `nio check tasks --approved` exits 0. Level: integration.
- **AC-9** (FR-9) Given an approved tasks.md with a fix task, when that fix task is retired, then the effort stays in `implementing` and the tasks gate is not reopened. [human]
  Observable: as AC-8, after retirement. Level: integration.
- **AC-10** (FR-10) Given an approved tasks.md, when a planned (non-fix) task is edited, added or retired, then the tasks gate reopens as today. [human]
  Observable: `nio flow status` state is `tasks_jury`. Level: integration.
- **AC-11** (FR-11) Given a fix task with a reason, when that fix task is retired, then the finding it served is closed `accepted-risk` at once, credited to whoever retired the task, with the retirement reason as its note, and the next implementation round creates no new fix task for it. [human]
  Observable: right after retirement the finding's disposition is `accepted-risk`, `by` names the retirer, note is the reason; after the next implementation round no new T- ID cites it in `From:`. Level: integration.
- **AC-12** (FR-12) Given a finding asks for evidence of an AC that tasks.md shows is served by a task in a later epic not yet built, when the finding is routed, then the system disposes it `out-of-scope` with that task's ID logged, makes no fix task, and lists it in the gate summary. [human]
  Observable: finding disposition `out-of-scope`, `by` is the system, note names the serving T- ID; tasks.md unchanged; the gate summary names the finding. Level: integration.
- **AC-13** (FR-12) Given a finding about an AC served by a task in the current or an earlier epic, when it is routed, then it is handled as today. [human]
  Observable: disposition is not `out-of-scope`. Level: integration.
- **AC-26** (FR-12) Given a finding that cites no AC, or cites an AC served both by a task in a later epic and by one in the current or an earlier epic, when it is routed, then it is handled as today. [human]
  Observable: disposition is not `out-of-scope` by the system. Level: integration.
- **AC-27** (FR-10) Given an approved tasks.md, when one change both appends a fix task and edits a planned task, or edits an existing fix task, or adds a task outside `#### Fixes`, then the tasks gate reopens. [human]
  Observable: `nio flow status` state is `tasks_jury` in each case. Level: integration.
- **AC-28** (FR-11) Given an approved tasks.md with a fix task, when that fix task is retired with no reason, then the retirement is refused and the finding stays open. [human]
  Observable: non-zero exit; the fix task is not retired; the finding's disposition is unchanged. Level: integration.

### US-3 Glob patterns in a task's Files list reach packs as real paths (P2) [human]
- **Why this priority:** jurors cite a literal glob as a missing file and raise findings no task can fix (#126, J-2).
- **Independent test:** give a task a Files entry `tests/test_*.py`, build its jury and worker packs, and check they name the matching files.

- **AC-19** (FR-17) Given a task whose Files list holds a glob that matches files, when its jury or worker pack is built, then the pack lists each matching path instead of the pattern. [human]
  Observable: the pack names every matching file and not the pattern text as a path. Level: integration.
- **AC-20** (FR-17) Given a task whose Files list holds a glob that matches nothing, when its pack is built, then the pack shows the pattern marked as matching nothing, never as a literal path. [human]
  Observable: the pack line says the pattern matched no file. Level: integration.

## Functional requirements
- **FR-1** WHEN `nio jury next` runs for a gate whose round count has reached `jury.max_rounds` and findings remain open THE SYSTEM SHALL not start another round, except the one automatic round of FR-13; each implementation epic gate counts its rounds on its own. [human] [research: RF-5]
- **FR-2** WHEN the round cap stops a gate THE SYSTEM SHALL print every still-open major and blocker of that gate in one batch, with the rulings the human can give (accept as risk, fix, one more round). [human]
- **FR-3** THE SYSTEM SHALL read the cap from config `jury.max_rounds`, defaulting to 2 when unset. [human]
- **FR-4** THE SYSTEM SHALL count escalation jurors (#105) as part of the round they join, not as a new round: collecting their outputs leaves the round number unchanged, and the escalation count includes every juror of that lens since the blocker was raised. [research: RF-2]
- **FR-5** WHEN the human rules findings of a capped gate "one more round" THE SYSTEM SHALL run exactly one further round re-checking only the lenses that raised those findings, then stop again with a new batch, on which the human may ask for another; a human-asked round is never followed by an automatic one. [human]
- **FR-6** WHEN the human rules a capped finding "accept as risk" or "fix" THE SYSTEM SHALL record that ruling as the human's disposition of the finding; rulings apply per finding, and the gate stays capped while any finding of the batch is unruled. [human]
- **FR-7** IF `jury.max_rounds` is not a whole number of at least 1 THEN THE SYSTEM SHALL stop with an error naming the setting. [human]
- **FR-8** WHILE tasks.md is approved, WHEN a fix task is appended under an epic's `#### Fixes` THE SYSTEM SHALL keep the tasks gate approved. [human]
- **FR-9** WHILE tasks.md is approved, WHEN a fix task is retired THE SYSTEM SHALL keep the tasks gate approved. [human]
- **FR-10** WHEN a planned task of an approved tasks.md changes, an existing fix task is edited, or a task is added outside an epic's `#### Fixes` THE SYSTEM SHALL reopen the tasks gate; a change that also appends or retires a fix task reopens it too. [human]
- **FR-11** WHEN a fix task is retired THE SYSTEM SHALL refuse the retirement if it gives no reason, and otherwise close the finding it served as `accepted-risk`, credited to whoever retired the task, with the retirement reason as its note, so no later round re-creates a task for it. [human]
- **FR-12** IF the AC ID a finding cites is served in tasks.md only by tasks in a later epic not yet built (its implementation gate not yet closed) THEN THE SYSTEM SHALL dispose the finding `out-of-scope` itself, recording the system as the actor and that task's ID in the note, before any fix task is made, and list it in the gate summary; in every other case (no AC cited, or the AC also served in the current or an earlier epic) the finding is handled as today and `out-of-scope` stays a human-only disposition. [human]
- **FR-13** WHEN a gate reaches `jury.max_rounds` with 2 or more open blockers THE SYSTEM SHALL start one further round by itself, once per gate, re-checking only the lenses that raised those blockers. [human]
- **FR-14** WHEN the automatic round of FR-13 ends with findings open THE SYSTEM SHALL start no further automatic round and print the batch of FR-2. [human]
- **FR-15** WHEN the round cap stops a gate THE SYSTEM SHALL close every open minor as `accepted-risk` with the system as actor and the note "minor, skipped at the round cap", and list each in the gate summary. [human]
- **FR-16** WHEN the human rules a capped finding "fix" at the spec or plan gate THE SYSTEM SHALL let the orchestrator edit spec.md or plan.md for it and close the gate with no juror re-check, the human's ruling being the approval. [human]
- **FR-17** WHEN a jury or worker pack is built THE SYSTEM SHALL expand each glob pattern in a task's Files list to the paths it matches, and show a pattern that matches nothing as matching nothing, never as a literal path. [human]
- **FR-18** WHEN a round at or over the cap ends with only minors open THE SYSTEM SHALL skip them as in FR-15 and close the gate, with no batch. [human]
- **FR-19** WHEN a round below the cap ends with no confirmed blocker open THE SYSTEM SHALL start no new round and hand the open findings to the human as today (the existing stop rule); below the cap only a confirmed blocker starts a round. [human]
- **FR-20** WHILE a round of the gate is running, or before the gate is capped, THE SYSTEM SHALL refuse a capped-batch ruling and record nothing. [human]

## Rules
### State table: gate rounds (start: reviewing; final: closed)
| State | round ends below cap, confirmed blocker open | round ends at or over cap, 2+ blockers open | round ends at or over cap, majors or a lone blocker open | round ends with no findings open, or at or over cap with only minors open | escalation jurors join | human rules every finding | human asks one more round | Src |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| reviewing | → reviewing | → auto round | → capped | → closed | → reviewing | reject: no batch yet | reject: no batch yet | [human] |
| auto round | ignore | → capped | → capped | → closed | → auto round | reject: round running | reject: round running | [human] |
| capped | ignore | ignore | ignore | ignore | ignore | → closed | → extra round | [human] |
| extra round | ignore | → capped | → capped | → closed | → extra round | reject: round running | reject: round running | [human] |
| closed | ignore | ignore | ignore | ignore | ignore | ignore | ignore | [human] |

### Decision table: change to an approved tasks.md
| Change (fix appended, fix retired, planned task changed, mixed, fix edited, outside Fixes, no reason) | → tasks gate | Src |
| --- | --- | --- |
| fix appended | stays approved | [human] |
| fix retired | stays approved; its finding closes as accepted risk | [human] |
| planned task changed | reopens | [human] |
| mixed | reopens (a fix appended or retired together with a planned-task change) | [human] |
| fix edited | reopens (an existing fix task edited) | [human] |
| outside Fixes | reopens (a task added outside `#### Fixes` counts as planned) | [human] |
| no reason | retirement refused (a fix retired with no reason) | [human] |

### Decision table: open finding when a gate reaches its cap
| Open findings (2+ blockers before the automatic round, 2+ blockers after it, 1 blocker, major, minor) | → handling | Src |
| --- | --- | --- |
| 2+ blockers before the automatic round | one automatic round on those blockers' lenses | [human] |
| 2+ blockers after it | human batch | [human] |
| 1 blocker | human batch | [derived: FR-2, FR-13] |
| major | human batch | [human] |
| minor | closed as accepted risk by the system, listed in the gate summary; if only minors are open the gate closes | [human] |

## Key entities
- **Round cap**: `jury.max_rounds` in `.nio/config.json`, default 2; counted per gate ledger, so per epic at the implementation gate. [human] [research: RF-5]
- **Capped batch**: the still-open majors and blockers of one gate printed together after the cap. [human]
- **Automatic round**: the one extra round a gate runs by itself at the cap when 2 or more blockers are open. [human]
- **Gate summary**: the list shown when a gate closes, naming the findings the system closed itself (skipped minors, later-epic dismissals). [human]
- **Fix task**: a task under an epic's `#### Fixes`, appended for a jury finding. [human]

## Success criteria
- **SC-1** Every gate ends in at most 3 jury rounds, the third only when 2 or more blockers are open, unless the human asks for more. [human]
- **SC-2** An effort never returns to `tasks_jury` because of fix tasks or their retirement. [human]
- **SC-3** No retired fix task is re-created by a later round. [human]

## Non-goals
- Fixes #128 and #85 from the same analysis; they get their own spec. [human]
- Running these changes through `nio flow`: this spec is implemented by ordinary agents. [human]

## Glossary
- **Round**: one pass of the jurors over a gate's artefact, including any escalation jurors that join it.
- **Fix task**: a task under `#### Fixes`, created from a jury finding. Never "patch task".
- **Automatic round**: the one round past the cap that NIO starts by itself when 2 or more blockers are open. Never "bonus round".
- **Skipped minor**: an open minor closed as accepted risk by the system at the round cap.

## Decisions
- The cap keeps the existing stop rule (only confirmed blockers start rounds after the first review, plus one final fix check) and bounds it at `jury.max_rounds`: D-261026-r52z (memory, 2026-10-26).
- At the cap: 2+ open blockers start one automatic round on their lenses, majors and a lone blocker go to the human batch, minors are skipped as accepted risk; never a fourth automatic round: the human, Q1.
- A "fix" ruling at a capped spec or plan gate is an edit with no juror re-check; the human's ruling is the approval: the human, Q2.
- The system may set `out-of-scope` only when tasks.md shows a later, unbuilt epic serves the AC: the human, Q3.
- Retiring a fix task closes its finding as accepted risk, credited to the retirer: the human, Q4.
- Glob expansion in task Files lists is in this spec: the human, Q5.
- A human-asked extra round re-checks only the lenses of the findings sent back, and the human may ask again on the next batch: the human, Q6.
- The remaining proposals (A-2, FR-7, AC-6, AC-7, FR-10, AC-10, AC-13, the closed state row, the planned-task-changed row) were confirmed as written: the human, Q7.
- Jury batch rulings: an empty batch closes the gate; below the cap only a confirmed blocker starts a round; rulings are per finding and refused while a round runs; FR-12 matches only the cited AC ID, "built" = the epic's implementation gate is closed; mixed, fix-edit and outside-Fixes changes reopen the tasks gate; a retirement needs a reason: the human, Q8.
- Escalation jurors join their round (collect must not bump the round; the count spans rounds since the blocker was raised): research RF-2 to RF-4.

## Open points
