---
slug: 2026-11-05-implement-followups
route: full
epic: ""                         # "<epic slug>/R-<n>" when this is a slice of an epic
risk: [external-input]           # auth | pii | money | external-input | data-deletion | migration | multi-party | public-api
retired: [FR-12, FR-13, FR-14, AC-13, AC-16, AC-17, AC-19, OP-1, OP-2, OP-3, OP-4, OP-5, OP-6, OP-7, OP-8, OP-9, OP-10, OP-11, OP-12, OP-13]                      # IDs removed from this spec; never reused
---
<!-- Spec template. WHAT and WHY only, never HOW. Every item ends with its provenance: [human] (the grill
confirmed it), [research: RF-n] (a finding in research.md) or [default] (your proposal; the grill must confirm it).
IDs are permanent: number new items after the highest ever used, never renumber, list removed IDs in `retired`.
Remove a section that doesn't apply; never write N/A. `nio check spec 2026-11-05-implement-followups` checks all of this. -->
# Implement follow-ups: fix five defects found while building #29

## Summary
Building #29 turned up small defects in the implement stage and its juries (#65). This fixes the five that are bugs:
the change record `nio flow block` files fails the memory check, `nio flow red` asks for test files of TC IDs a later
task proves, the tasks-gate fix check and `nio jury changed` leave out tasks added under `#### Fixes`, the evaluator
can rewrite `tasks.md` whole, and a wall-clock test can fail a task's review under load. Each one cost a hand edit,
a lost attempt or a false blocker; none adds a feature. [human] They stay one spec: each is a task or two, and the tasks
stage gives each story its own epic. [agent]

## Actors and journeys
- **A-1 Human**: owns the project; decides change requests and gates, and pays for every lost attempt and hand edit. [research: RF-16]
- **A-2 Orchestrator**: the agent session that drives an effort with `nio flow`, reports red and green, and files a worker's blocked handoff with `nio flow block`. [research: RF-16]
- **A-3 Worker**: a `nio-worker` that works one task from its pack and names the test command red and green run. [research: RF-16]
- **A-4 Juror**: a jury lens judging a fix-check pack at the tasks gate. [research: RF-16]
- **A-5 Evaluator**: the `nio-evaluator` agent that rates each task's tier, effort and mode in `tasks.md`. [research: RF-16]

**UJ-1 A blocked task reaches the next gate commit** (A-3, A-2, A-1) [research: RF-16]
1. The worker finds the spec wrong and hands off blocked with a change request; the orchestrator runs `nio flow block`; the human decides the record and the next gate commit goes through.
- Misuse: the orchestrator hand-edits the record's headings to get the commit through.
- Evidence: #65 item 1; C-261030-abpr.

**UJ-2 Red on a task whose Test line defers a TC** (A-3, A-2) [research: RF-16]
1. The worker writes the task's own test; the orchestrator reports red with a command naming that test's file; the CLI accepts it.
- Misuse: the command names an unrelated file only to get past the check.
- Evidence: #65 item 2; T-2 of 2026-10-27-implementation-jury.

**UJ-3 A juror checks a fix that moved work into Fixes** (A-4) [research: RF-16]
1. The juror reads the fix-check pack, sees the removed task and the fix task that took its work, and judges the fix.
- Misuse: the juror raises a blocker that the moved work has no task because it never saw the fix task.
- Evidence: #65 item 3.

**UJ-4 The evaluator rates tasks** (A-5) [research: RF-16]
1. The evaluator reads every task and fills its rating lines; nothing else in `tasks.md` changes.
- Misuse: the evaluator writes the whole file back and drops or reorders lines.
- Evidence: #65 item 5.

**UJ-5 A task's review runs the full suite on a loaded machine** (A-2, A-1) [research: RF-16]
1. The review runs the suite while other work loads the machine; it passes or fails on the code, not on timing.
- Misuse: a slow run reads as the task's failure and spends one of its three attempts.
- Evidence: #65 item 9; T-19 of the #29 build.

## User stories

### US-1 A blocked task's change record passes the memory check (P1) [human]
- **Why this priority:** today every `nio flow block` leaves a record that stops the next gate commit until the human edits it by hand.
- **Independent test:** run `nio flow block` on a fixture task with a blocked handoff, then run the memory check on the record it filed.

- **AC-1** (FR-1) Given a claimed task and a blocked handoff with a `change_request`, when `nio flow block` runs, then the memory check passes on the change record it files. [human]
  Observable: `nio check` reports no error for the new record, and the pre-commit memory check exits 0 with it staged. Level: integration.
- **AC-2** (FR-2) Given a handoff whose `change_request` holds distinct texts for what the spec says, what the code shows and the smallest change, when `nio flow block` files the record, then the spec's and the code's texts appear under `## What is wrong` and the smallest change under `## Proposed change`. [agent]
  Observable: each of the three texts appears verbatim under its section. Level: unit.
- **AC-3** (FR-1, FR-2) Given `nio flow block` already ran for a handoff, when it runs again for the same handoff, then the same pending record is reused and still passes the memory check. [agent]
  Observable: one change record holds that handoff's hash; `nio check` reports no error for it. Level: integration.
- **AC-20** (FR-16) Given a handoff whose smallest-change text holds the line `## Human decision`, or a line `---`, when `nio flow block` runs, then it refuses the handoff naming that line, and files no record. [agent]
  Observable: non-zero exit naming the line; no new `C-` record under `.nio/memory/`; the task's status is unchanged. Level: unit.
- **AC-21** (FR-16) Given a handoff whose what-the-code-shows text is empty or only spaces, when `nio flow block` runs, then it refuses the handoff and files no record. [research: RF-17]
  Observable: non-zero exit saying the handoff is not blocked with a `change_request`; no new `C-` record. Level: unit.

### US-2 Red asks only for the test files of the TC IDs the task proves itself (P1) [human]
- **Why this priority:** a refused red spends one of the task's three attempts; T-2 lost one to a file a later task writes.
- **Independent test:** run `nio flow red` on a fixture task whose `Test:` line defers a TC ID to a later task, with commands naming each file.

- **AC-4** (FR-3) Given a task whose `Test:` line cites TC-10 and says TC-38 is proved later by T-11, and the two have different files, when red runs with a command naming only TC-10's file that fails on an assertion, then red is accepted. [human]
  Observable: exit 0; the task's status reads `red`. Level: unit.
- **AC-5** (FR-3, FR-4) Given the same task, when red runs with a command naming only TC-38's file, then red is refused for not naming TC-10's file. [agent]
  Observable: non-zero exit; the refusal names TC-10's file and not TC-38's; a `refused` line is recorded. Level: unit.
- **AC-6** (FR-3) Given a task whose `Test:` line is exactly ``a direct unit check calling `load`; TC-6 and TC-7 proved later by T-8``, when red runs with a command that names no TC file and fails on an assertion, then red is accepted: a task with no own TC ID has no file to name. [human]
  Observable: exit 0; the task's status reads `red`. Level: unit.
- **AC-7** (FR-5) Given the later task whose own `Test:` line cites TC-38 with no deferral, when red runs with a command that doesn't name TC-38's file, then red is refused. [agent]
  Observable: non-zero exit naming TC-38's file; status stays `claimed`. Level: unit.
- **AC-22** (FR-3, FR-4) Given a task whose `Test:` line cites TC-10 and TC-12 as its own, with different files, when red runs with a command naming only TC-10's file that fails on an assertion, then red is accepted. [agent]
  Observable: exit 0; the task's status reads `red`. Level: unit.
- **AC-23** (FR-3) Given a task whose `Test:` line is `TC-38, plus a direct check; TC-38 proved later by T-11`, when red runs with a command that doesn't name TC-38's file, then red is refused: a TC ID cited outside the deferral part is the task's own. [agent]
  Observable: non-zero exit naming TC-38's file. Level: unit.

### US-3 The tasks-gate fix check shows tasks added under Fixes (P2) [human]
- **Why this priority:** a missing fix task reads as missing work; the refuter caught two false blockers, but each one costs a round.
- **Independent test:** build a fix-check pack and the `nio jury changed` output for a fixture tasks gate where a task moved into `#### Fixes`.

- **AC-8** (FR-6) Given a tasks gate whose last round judged T-4, and T-4 was since removed and its work added as T-30 under an epic's `#### Fixes`, when `nio jury fixcheck` builds a lens's pack, then the pack shows T-4 as removed and T-30 as added, with T-30's text. [human]
  Observable: the pack holds T-4's text as before and T-30's full block as after. Level: unit.
- **AC-9** (FR-7) Given the same gate, when `nio jury changed` runs, then T-30 is among the changed IDs it reports. [human]
  Observable: the output lists T-30 next to T-4. Level: unit.
- **AC-10** (FR-8) Given an approved tasks gate, when a fix task is added under `#### Fixes` during implementation, then the tasks gate stays approved. [research: RF-9]
  Observable: the tasks gate's status is still approved. Level: integration.
- **AC-11** (FR-6, FR-7) Given a tasks gate where nothing was added under `#### Fixes` since the last round, when `nio jury fixcheck` and `nio jury changed` run, then their output is the same as before this change. [agent]
  Observable: output equals the output of the current code on the same fixture. Level: unit.
- **AC-24** (FR-7) Given a tasks gate whose only change since the last round is T-30 added under `#### Fixes`, when `nio jury changed` runs, then it lists T-30 and names no lens to re-run. [agent]
  Observable: T-30 is in the changed list; the lenses-to-re-run list is empty. Level: unit.
- **AC-25** (FR-8) Given an approved tasks gate, when a planned task outside `#### Fixes` is edited or removed, then the approval is withdrawn as it is today. [research: RF-9]
  Observable: `nio check tasks --approved` fails for the effort. Level: integration.

### US-4 The evaluator edits only the rating lines (P2) [human]
- **Why this priority:** the tasks check caught the lost epic headings, but a rewrite that keeps the structure could change a task's text unseen.
- **Independent test:** copy a fixture `tasks.md`, change lines in it, and run `nio check tasks` against the copy.

- **AC-12** (FR-10) Given the shipped agent cards, when `nio agents sync` renders the evaluator card, then it tells the evaluator to edit each task's `Tier:`, `Effort:` and `Mode:` lines in place and never write `tasks.md` whole, and gives it a tool that edits in place but none that writes a whole file. [agent]
  Observable: the rendered card's text says both, and its tool list holds Edit and not Write. Level: unit.
- **AC-26** (FR-9) Given a copy of `tasks.md` taken before rating and a `tasks.md` where one task's `Files:` line also changed, when `nio check tasks <slug> --rated-from <copy>` runs, then it fails naming the changed line. [agent]
  Observable: non-zero exit; the error quotes the `Files:` line. Level: unit.
- **AC-27** (FR-9) Given a copy taken before rating and a `tasks.md` where only `Tier:`, `Effort:` and `Mode:` lines changed and none still reads `to be rated`, when the same check runs, then it passes. [agent]
  Observable: exit 0. Level: unit.
- **AC-28** (FR-17) Given the tasks skill, when it runs the evaluator, then it copies `tasks.md` before and runs `nio check tasks <slug> --rated-from <copy>` after. [agent]
  Observable: `skills/tasks/SKILL.md` names both steps around the evaluator. Level: unit.

### US-5 A wall-clock limit can't fail a task's review (P1) [human]
- **Why this priority:** a timing failure spends one of a task's three attempts for nothing; T-19 lost one.
- **Independent test:** run a task's review with `NIO_PERF=1` in the caller's environment and the status-speed test made to read 3 seconds.

- **AC-14** (FR-11) Given `NIO_PERF=1` in the orchestrator's environment and a suite whose only test fails when `NIO_PERF` is set, when a task's review runs the suite, then the review passes. [human]
  Observable: the review records no failure; the task's attempt count is unchanged. Level: integration.
- **AC-15** (FR-11) Given a task whose change breaks a test's assertion, when the task's review runs the full suite, then the review fails as it does today. [agent]
  Observable: the review records the failing test and uses an attempt. Level: integration.
- **AC-18** (FR-15) Given `test_nfr3_status_speed` with its clock made to read 3 seconds for the status run, when it runs with `NIO_PERF` unset, then it passes on status's output (one line per effort, 20 lines); with `NIO_PERF=1`, it fails naming the 2-second limit. [agent]
  Observable: exit 0 without `NIO_PERF`; non-zero naming "2 seconds" with `NIO_PERF=1`. Level: unit.
- **AC-29** (FR-18) Given the repo's agent instructions, when a reader looks for the self-checks, then `NIO_PERF=1 uv run python tests/test_flow.py` is listed, to run after a change to `nio flow status`. [agent]
  Observable: `CLAUDE.md` holds that command and the words "nio flow status". Level: unit.

## Functional requirements
- **FR-1** WHEN `nio flow block` files a change record THE SYSTEM SHALL write it with the sections the memory check requires of a change record. [human]
- **FR-2** WHEN `nio flow block` files a change record THE SYSTEM SHALL carry the handoff's what-the-spec-says, what-the-code-shows and smallest-change texts into it: the first two under `## What is wrong`, the third under `## Proposed change`. [agent]
- **FR-3** WHEN `nio flow red` checks that its command names the task's test files THE SYSTEM SHALL require it to name at least one file of the task's own TC IDs, where a TC ID is the task's own unless it appears only in the part of the `Test:` line that says a later task proves it; a task with no own TC ID has no file to name. [human]
- **FR-4** IF `nio flow red` refuses a command for naming none of the files of the task's own TC IDs THEN THE SYSTEM SHALL name only those files in the refusal. [agent]
- **FR-5** WHEN `nio flow red` checks the command of the task that proves a deferred TC ID THE SYSTEM SHALL require that TC ID's file. [agent]
- **FR-6** WHEN `nio jury fixcheck` builds a pack at the tasks gate THE SYSTEM SHALL show the tasks added under `#### Fixes` since the version the lens judged, with their text. [human]
- **FR-7** WHEN `nio jury changed` reports the changes at the tasks gate THE SYSTEM SHALL list the tasks added under `#### Fixes` since the version the last round judged, without naming a lens to re-run for them. [agent]
- **FR-8** WHILE a tasks gate is approved THE SYSTEM SHALL keep it approved when a task is added under `#### Fixes`, and withdraw it, as today, when a planned task outside `#### Fixes` is edited or removed. [research: RF-9]
- **FR-9** WHEN `nio check tasks <slug> --rated-from <copy>` runs THE SYSTEM SHALL fail for any line that differs from the copy other than a `Tier:`, `Effort:` or `Mode:` line, and for any rating line still reading `to be rated`. [agent]
- **FR-10** THE SYSTEM SHALL ship an evaluator card that tells the evaluator to edit the rating lines in place and never write `tasks.md` whole, with an edit tool and no whole-file write tool. [agent]
- **FR-11** WHEN a task's review runs the test suite THE SYSTEM SHALL run it with `NIO_PERF` removed from its environment. [human]
- **FR-15** WHEN `test_nfr3_status_speed` runs THE SYSTEM SHALL check status's output for the 20 efforts, and assert the 2-second limit only when `NIO_PERF=1` is set. [agent]
- **FR-16** IF a handoff's `change_request` text holds a line that starts with `## ` or is `---`, or one of its three texts is empty THEN `nio flow block` SHALL refuse the handoff, name the line or the empty text, and file no record. [agent]
- **FR-17** WHEN the tasks skill runs the evaluator THE SYSTEM SHALL copy `tasks.md` first and run `nio check tasks <slug> --rated-from <copy>` after. [agent]
- **FR-18** THE SYSTEM SHALL list `NIO_PERF=1 uv run python tests/test_flow.py` among the repo's self-checks in `CLAUDE.md`, to run after a change to `nio flow status`. [agent]

## Rules
### Decision table: files a red command must name
| The task's own TC IDs (none, some) | Command names a file of one of them (yes, no) | → | Src |
| --- | --- | --- | --- |
| some | yes | → the command runs and red is judged on its result | [research: RF-5] |
| some | no | → refused, naming the own TC IDs' files; an attempt is used | [research: RF-5] |
| none | - | → no file required; the command runs and red is judged on its result | [human] |

### Decision table: what the tasks-gate fix check and `changed` show
| Task change since the judged version (removed, added outside Fixes, added under Fixes) | → shown in the fix-check pack and listed by `changed` | → names a lens to re-run | Src |
| --- | --- | --- | --- |
| removed | → yes | → yes | [research: RF-9] |
| added outside Fixes | → yes | → yes | [research: RF-9] |
| added under Fixes | → yes | → no | [agent] |

## Key entities
- **Change record**: a `C-` memory record with the sections the memory check requires; `nio flow block` files one per blocked handoff. [agent]
- **Handoff**: a worker's report; when blocked it carries a `change_request` with what the spec says, what the code shows and the smallest change. [agent]
- **Test line**: a task's `Test:` field, citing the TC IDs it proves and, in one `;`-separated part holding "proved later", any it defers to a later task. [research: RF-7]
- **Fix-check pack**: what one lens reads in a re-review or final fix check: its findings and the changed items, before and after. [agent]
- **Rating lines**: a task's `Tier:`, `Effort:` and `Mode:` lines, the only ones the evaluator writes. [agent]

## Success criteria
- **SC-1** A task blocked with `nio flow block` reaches its next gate commit with no hand edit to its change record. [agent]
- **SC-2** No red is refused for a test file that only a later task writes. [agent]
- **SC-3** At the tasks gate, no finding says moved work has no task when that work sits under `#### Fixes`. [agent]
- **SC-4** After the evaluator runs, every changed line of `tasks.md` is a rating line, or `nio check tasks --rated-from` fails. [agent]
- **SC-5** No task attempt is spent on the status-speed limit. [agent]

## Non-goals
- Catching a task that blocks the build itself, a rule from an early epic cleared only in a later one (#65 item 4): it has its own issue, #69. [human]
- Real parallel work through separate worktrees (#65 item 6): it belongs to #59. [human]
- One test file per story from the tasks drafter (#65 item 7): it moves to #59. [human]
- Running only the task's own tests in its review and the full suite at the epic's end (#65 item 8): done in #66. [human]
- Editing change records already fixed by hand, such as C-261030-abpr: none is pending with the old sections. [research: RF-4]
- Checking that a deferral names a later task that proves the TC ID, and changing what the worker pack shows: neither is in #65; the first joins #69's checks across tasks. [agent]
- The drift test's 2-second limit (plain-talk NFR-1) and the tests that prove a time limit stopped a run: #65 names only the status-speed test. [agent]

## Glossary
- **Deferred TC ID**: a TC ID that appears only in the part of a task's `Test:` line that says a later task proves it ("proved later by T-n"). Never "skipped test".
- **Rating lines**: a task's `Tier:`, `Effort:` and `Mode:` lines.
- **Fix task**: a task under an epic's `#### Fixes` heading, added after the tasks gate judged the list.

## Risks and evidence against
- US-5 changes how flow-state's NFR-3 (status in under 2 seconds, [human] in an approved spec) is checked: C-261105-6rme records it, and FR-18 names where the limit is still checked. [agent]
- A task may defer every TC ID it cites and so need no file at red, as a task citing no TC ID does today; the tasks jury reads each `Test:` line and is where such a task is caught. [agent]
- A worker's handoff file has no size limit; it is a local file the worker wrote, and the human reads the record before deciding it. [agent]

## Decisions
- A task's `Test:` line cites the plan's TC-n, so red reads a task's test files from those entries: D-261028-scwb (memory, 2026-10-28).
- A blocked handoff's record is fixed in what `nio flow block` writes, not in the memory check: the spec's and the code's texts go under `## What is wrong`, the smallest change under `## Proposed change`; a text that would forge a section is refused (OP-2, J-1, [agent]).
- A deferral keeps the shape every `tasks.md` already uses ("TC-n proved later by T-m" in its own `;` part). A TC ID cited anywhere else on the line is the task's own; a red command must name a file of at least one own TC ID, as today (OP-6, J-2, J-6, [agent]).
- A fix task under `#### Fixes` is shown to the juror but doesn't make a lens re-run or withdraw an approval (OP-8, [agent]).
- The evaluator gets an edit tool and no whole-file write tool, and `nio check tasks --rated-from` checks its diff (US-4, RF-10, J-18, [agent]).
- A task's review strips `NIO_PERF`, and the status-speed test asserts its limit only with `NIO_PERF=1`, run by hand after a change to status (OP-11, J-8, J-9, [agent]): C-261105-6rme (memory, 2026-11-05).
