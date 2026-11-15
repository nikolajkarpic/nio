---
slug: 2026-11-15-faster-flow
route: full
epic: ""                         # "<epic slug>/R-<n>" when this is a slice of an epic
risk: [migration]          # auth | pii | money | external-input | data-deletion | migration | multi-party | public-api
retired: [FR-20, FR-21, AC-21, AC-22, OP-1, OP-2, OP-3, OP-4, OP-5, OP-6, OP-7, OP-8, OP-9, OP-10, OP-11, OP-12, OP-13, OP-14, OP-15, OP-16, OP-17, OP-18, OP-19, OP-20, OP-21, OP-22, OP-23]  # IDs removed from this spec; never reused
---
<!-- Spec template. WHAT and WHY only, never HOW. Every item ends with its provenance: [human] (the grill
confirmed it), [research: RF-n] (a finding in research.md) or [agent] (your proposal; the grill must confirm it).
IDs are permanent: number new items after the highest ever used, never renumber, list removed IDs in `retired`.
Remove a section that doesn't apply; never write N/A. `nio check spec 2026-11-15-faster-flow` checks all of this. -->
# Faster flow: per-epic implementation, background long commands, jury gates that don't stall, and the full-auto run

## Summary
The NIO flow is slow where it should not be. Effort #142's first epic spent ~39 min of agent time, ~8 min of shell and
~66 min waiting on the human, much of it on per-task red/green gates, wait loops and gate stops (#151). This effort
speeds the whole flow up in one spec: the implement stage moves to one agent per epic with one test run at its end and
no red/green, a task can no longer depend on a later epic, long commands run in the background in every effort session,
the jury gates stop dropping or re-sending findings, the claim and hand-off bugs go, and the full-auto run (#122) drives
every stage and gate itself, with one agent fixing all of a round's confirmed findings. [human]

## Actors and journeys
- **A-1 Effort owner**: the developer who writes the spec and drives the effort; wants an effort from spec to PR in less wall-clock time, with fewer stops that need them. P-1. [research: RF-1]
- **A-2 Maintainer**: whoever installs NIO in the repo; wants long commands backgrounded for everyone without a per-person opt-in. P-3. [research: RF-1]
- **A-3 Driver**: the agent that runs the flow for the effort owner (`nio flow next`, the stage's skill, `nio flow done`), by hand or under auto. [research: RF-2]
- **A-4 Implementation agent**: the one agent that implements a claimed epic from its pack (its tasks, tests and code). [human]
- **A-5 Fix agent**: the one agent that settles all confirmed findings of a jury round. [human]
- **A-6 Jury**: the jurors, escalation jurors and refuter that judge a gate. [research: RF-2]

**UJ-1 Implement an epic** (A-3, A-4) [research: RF-3]
1. The driver claims the next epic and gets one pack for the whole epic.
2. The implementation agent writes the epic's tests and code and hands the epic back.
3. `nio flow` runs the epic's tests itself; the epic closes if they pass, and stays open with the failing output if not.
4. After the last epic, the pr gate's jury reviews the whole effort diff once.
- Misuse: the agent reports "tests pass" without the flow running them; the agent leaves an epic's tests trivially passing; a second driver claims the same epic.
- Evidence: #151 (effort #142, C-261115-duou, C-261115-svvm).

**UJ-2 A full-auto run** (A-1, A-3, A-5, A-6) [research: RF-22]
1. The effort owner approves the spec and grants auto.
2. The driver runs every stage and gate in turn; a gate whose jury approves is committed by the flow, except the pr gate, which only the human approves.
3. When a round confirms findings, one fix agent settles all of them and the next round starts.
4. The run approves every gate but the pr gate itself, risky spec or not, and does the steps that need `--by human` today; it stops for the human only on the stop list and at the pr gate.
- Misuse: an agent grants itself auto; the fix agent overrides the human's own words; the run loops on a gate without closing findings.
- Evidence: #122, D-261108-txqj.

**UJ-3 Waiting on a long command** (A-2, A-3) [research: RF-9]
1. The driver starts `nio jury evidence`, the end-of-epic test run or the test suite.
2. The background mod runs it in the background; the host wakes the driver when it exits.
- Misuse: the mod isn't loaded and the driver falls back to a sleep/poll loop.
- Evidence: #130, #151 ("the session that drove #142 didn't have it on").

## User stories

### US-1 One agent implements a whole epic, and the flow runs its tests at the end (P1) [human]
- **Why this priority:** per-task red/green caused most of the agent cold starts, repeated test runs and stops on #142; it is the largest agent-side saving (#151).
- **Independent test:** run a two-task epic through the new implement stage; one claim, one agent, one test run by `nio flow`, no red/green.

- **AC-1** (FR-1, FR-2) Given an effort whose tasks are approved, when the driver claims work, then it gets the next whole epic and one pack holding its tasks, the spec items and contracts they cite, and the tests they name. [human]
  Observable: the claim names the epic, not a task; the pack lists every undone task of that epic and the tests they name. Level: integration.
- **AC-2** (FR-3) Given a claimed epic whose named tests pass, when the agent hands it back as done, then the flow runs those tests itself and closes the epic. [human]
  Observable: the effort's history shows a test run by the flow for that epic, followed by the epic's close; no close without that run. Level: integration.
- **AC-3** (FR-3, FR-4) Given a claimed epic with one failing named test, when the agent hands it back as done, then the epic stays open and the failing test and the tail of the run's output are recorded. [agent]
  Observable: the epic is not closed; the recorded result names the failing test and holds the output tail. Level: integration.
- **AC-4** (FR-3) Given an agent hand-back that says all tests passed, when the flow's own run fails, then the epic stays open. [human]
  Observable: the epic is open after the hand-back; the agent's claim is not recorded as the result. Level: integration.
- **AC-5** (FR-5) Given an effort at the implement stage, when the driver follows the implement skill, then no red or green step is asked for, and no task carries a mode. [human]
  Observable: the implement skill and `nio flow` name no per-task red or green step; `nio check tasks` accepts tasks with no mode. Level: integration.
- **AC-6** (FR-6) Given an epic that closed on its tests, when the flow moves on, then no jury runs for that epic, and the pr gate is the only jury of the implementation. [human]
  Observable: no implementation-E-n gate or ledger exists for the effort; one pr gate ledger exists after the last epic. Level: integration.
- **AC-7** (FR-7) Given an approved tasks.md, when its epics are listed, then each task still names its ACs and tests and each epic carries one tier. [human]
  Observable: `nio check tasks` passes a tasks.md with tier per epic and fails one with a task missing its AC → test map. Level: unit.
- **AC-8** (FR-8) Given the repo after this change, when NORTH_STAR's "Implement" section and the implement skill are read, then they describe per-epic implementation and no TDD red/green step. [human]
  Observable: neither file names a test writer, builder or red/green gate for the implement stage. Level: unit.
- **AC-9** (FR-9) Given an epic already claimed, when a second driver claims work on the same effort, then the claim of that epic is refused and names it. [agent]
  Observable: the second claim exits non-zero with the epic's ID; the first claim is unchanged. Level: integration.
- **AC-10** (FR-10) Given an epic whose tasks name no test, when the agent hands it back as done, then the flow refuses to close it and says it has no test to run. [agent]
  Observable: the epic stays open; the message says the epic has no test to run. Level: integration.
- **AC-11** (FR-11) Given an untracked file outside the epic's files in the working tree, when the epic closes, then the epic's commit leaves that file out. [agent]
  Observable: the untracked file is still untracked after the close; the commit lists only the epic's files and the flow files. Level: integration.

### US-2 A task can't depend on a later epic (P1) [human]
- **Why this priority:** a cross-epic dependency deadlocked #142's claim and passed every check and jury (#152, #69); with one claim per epic it would stall a whole epic.
- **Independent test:** run `nio check tasks` on a tasks.md where a task waits on a later epic's task.

- **AC-12** (FR-12) Given a tasks.md where T-10 in E-5 depends on T-11 in E-6, when `nio check tasks` runs, then it fails with a message naming T-10, T-11 and both epics. [human]
  Observable: exit code non-zero; the message holds both task IDs and both epic IDs. Level: unit.
- **AC-13** (FR-12) Given a tasks.md whose dependencies only point to the same or earlier epics, when `nio check tasks` runs, then it raises no cross-epic error. [agent]
  Observable: no error line about a later epic. Level: unit.

### US-3 Long commands run in the background in every effort session (P2) [human]
- **Why this priority:** wait loops around long commands took ~267 min on 2026-11-08 (#130), and #142 saved none of it because the mod was off.
- **Independent test:** in a fresh effort session, run a jury and an epic's test run; the transcript has no sleep/poll loop.

- **AC-14** (FR-13) Given the background mod loaded, when a session runs `nio jury evidence` or the end-of-epic test command (also as `uv run nio …` and after `cd <dir> &&`), then the mod runs it in the background. [research: RF-6]
  Observable: the mod's hook rewrites each command to a background run; its long-command list holds no `nio jury run`. Level: unit.
- **AC-15** (FR-14) Given the NIO repo after `@nio:install`, and a session that drives an effort started with no `--plugin-dir` or `CLAUDE_CODE_PLUGIN_DIRS`, when it runs `nio jury evidence`, then the command runs in the background. [agent]
  Observable: the session's transcript shows the command backgrounded and no sleep/poll loop. Level: e2e.
- **AC-16** (FR-15) Given a Claude Code session driving an effort without the background mod loaded, when the driver starts, then it is told the mod is off. [agent]
  Observable: the start-up output names the missing mod. Level: integration.

### US-4 The full-auto run drives the effort to the end, with one agent fixing all findings (P1) [human]
- **Why this priority:** human waits were ~66 of ~87 min on #142, the largest share; the human asked to finish the half-built full-auto run here.
- **Independent test:** grant auto on an effort with an approved spec, risky or not; it runs to the pr gate with no human approval between, and each round's confirmed findings go to one fix agent.

- **AC-17** (FR-16) Given an effort, when the human grants auto with `--by human`, then the flag is on and the grant is in the effort's history; when anyone else tries to grant or revoke it, then it is refused. [research: RF-22]
  Observable: history holds the grant line with `human`; a grant without `--by human` exits non-zero and the flag is unchanged. Level: integration.
- **AC-18** (FR-17) Given an effort with auto on and an approved spec, when the driver runs, then it loops next stage → its skill → done until the effort pauses or ends, each stage in a fresh agent where the host allows. [research: RF-13]
  Observable: a run transcript shows each stage started by a fresh agent and no human approval between stages. Level: e2e.
- **AC-19** (FR-18) Given an effort with auto on at the implement stage, when the driver runs it, then it implements per epic and runs the pr gate once, with no epic jury. [human]
  Observable: history shows epic claims and closes, then one pr gate; no implementation-E-n ledger. Level: e2e.
- **AC-20** (FR-19) Given a jury round that confirmed three findings, when the round is collected, then all three go to one fix agent in one batch, and the next round starts after its edits. [human]
  Observable: one fix-agent run per round, whose input lists every confirmed finding of that round; a next round follows. Level: e2e.
- **AC-23** (FR-22) Given an effort with auto on, when the run pauses, then the human is told the reason and the resume command; when it reaches the end, then a pull request with the run report is open, unmerged, and the pr gate waits for the human. [research: RF-22]
  Observable: the pause message names the reason and a command; the PR exists, is not merged, and the pr gate is not approved by the flow. Level: integration.

### US-5 Jury gates don't drop, re-send or blow up findings (P2) [human]
- **Why this priority:** each of these stops cost a re-run, extra refuter batches or human repair at a gate (#124, #138, #94, #96, #95); under auto they would stall the run or approve unread work.
- **Independent test:** replay each issue's case through `nio jury` and see the gate go on without a manual fix.

- **AC-24** (FR-23) Given a finding whose quote ends with a source note such as `(tasks.md, T-11)`, when the jury grounds it, then it is grounded on the quote without the note. [agent]
  Observable: the finding is not dropped as ungrounded. Level: unit.
- **AC-25** (FR-24) Given a lens whose every finding is dropped as ungrounded, when the gate composes, then the juror's output is marked invalid with a re-run asked, and the gate is not approved. [agent]
  Observable: the verdict is not `approved`; the lens is listed for re-run. Level: integration.
- **AC-26** (FR-25) Given a finding dropped as ungrounded, when the human records a ruling on it, then the ruling is accepted and the finding is open again. [agent]
  Observable: `nio jury dispose` exits zero; the ledger shows the finding open with the ruling. Level: integration.
- **AC-27** (FR-26) Given two escalation jurors judging blocker J-6, when their outputs are collected, then they count as votes on J-6, and anything else they raise is recorded as a note with no new finding ID. [agent]
  Observable: the ledger gains no new J- IDs from them; J-6 carries their votes. Level: integration.
- **AC-28** (FR-27) Given a gate with two refuter passes, when the second pass is collected, then the first pass's output is still on disk under its own number. [agent]
  Observable: both pass files exist with their own content. Level: integration.
- **AC-29** (FR-28) Given the refuter merges a confirmed major into a minor, when the merge raises the kept finding's severity, then the kept finding stays confirmed and no second refuter batch is printed. [agent]
  Observable: `nio jury collect` prints no refuter batch for the kept finding. Level: integration.
- **AC-30** (FR-29) Given a blocker fixed in the artefact while its escalation round was running, when the fix is checked, then the check compares against the version the finding was raised on and passes. [agent]
  Observable: no "fix without a change" error for that finding. Level: integration.
- **AC-31** (FR-30) Given plan edits to CT-1 and two TCs, when `nio jury changed` runs on the plan, then it lists those IDs as changed and the fix-check pack carries only them and their neighbours. [agent]
  Observable: the output names CT-1 and the two TCs, not whole sections. Level: unit.

### US-6 Claims, indexes and hand-offs don't break the run (P3) [human]
- **Why this priority:** each is a crash or a dead end that stops an unattended run (#107, #106, #64).
- **Independent test:** run a claim while the index rebuilds, a jury from a worktree session, and a hand-off without the plugin.

- **AC-32** (FR-31) Given an index rebuild under way, when a claim builds a pack, then it reads either the old or the new index and does not crash on a missing record. [agent]
  Observable: with a record the index names deleted before the pack is built, the claim exits zero and the pack leaves that record out; a reader opening the index while a rebuild is stopped half-way sees the whole old index (the rebuild replaces the file in one step). [agent] Level: integration.
- **AC-33** (FR-32) Given a claim that creates a worktree and then fails, when it exits, then no worktree it created is left. [agent]
  Observable: `git worktree list` is the same before and after the failed claim. Level: integration.
- **AC-34** (FR-33) Given a host session started in a different checkout from the worktree the agents were rendered into, when `nio jury next` renders them, then it warns that the host loads other agents. [agent]
  Observable: the output names both roots in a warning. Level: integration.
- **AC-35** (FR-34) Given the NIO plugin is not installed, when `nio flow next` or `nio flow done` prints the next step, then the step names the skill file as well as the `/nio:*` command. [agent]
  Observable: the `next:` line holds `skills/<stage>/SKILL.md`. Level: integration.

### US-7 What the closed issues still need keeps working (P3) [human]
- **Why this priority:** per-epic implementation closes #97, #108, #115, #82, #78, #80, #98 and #83, but some of their behaviours must survive the change.
- **Independent test:** replay each surviving case on the new flow.

- **AC-36** (FR-35) Given a tasks.md with fix tasks T-6 to T-9 and T-10 retired, when `nio check tasks` runs, then it accepts T-6 to T-9 and T-10 stays unused. [agent]
  Observable: no "a fix task takes the next free ID" error; reusing T-10 fails. Level: unit.
- **AC-37** (FR-36) Given an approved tasks gate and a fix task whose finding was accepted as risk, when that fix task is retired, then the effort stays past the tasks gate. [agent]
  Observable: `nio flow status` stage is unchanged after the retire. Level: integration.
- **AC-38** (FR-37) Given an AC proved by an existing passing test, when the evidence for the pr gate is collected, then that test counts as the AC's evidence and no fix task is filed for it. [agent]
  Observable: the evidence lists the existing test against the AC; no "no passing evidence" finding for it. Level: integration.
- **AC-39** (FR-38) Given the flow writes a change request, when `nio check` runs on it, then it passes. [agent]
  Observable: `nio check` exits zero on the freshly written record. Level: integration.
- **AC-40** (FR-39) Given a confirmed pr-gate finding rooted in a plan file, when it is recorded, then it goes to a plan change, not a code fix task. [agent]
  Observable: no fix task is appended for it; a plan change is asked for. Level: integration.
- **AC-41** (FR-40) Given a task listing a file it reuses unchanged, when the pr gate checks the diff, then no "isn't in the diff" finding is raised for that file. [agent]
  Observable: the gate's findings hold no such line for that file. Level: integration.

- **AC-42** (FR-41) Given a pr gate on an effort that added tests, when its jury is listed, then the test-proof lens is among its lenses. [agent]
  Observable: `nio jury next <slug> pr` names `test-proof`. Level: integration.
- **AC-43** (FR-42) Given an epic whose test run failed, when it is claimed again, then the pack carries the failing tests and output tail; after its third failed run, then it is blocked for the human. [agent]
  Observable: the second claim's pack holds the failure; after three failures the epic's state is blocked and the claim is refused. Level: integration.
- **AC-44** (FR-43) Given E-2 and E-3 with no dependency between them, when the driver claims work, then both can be claimed at once, each in its own worktree. [agent]
  Observable: two claims succeed and `git worktree list` shows one worktree per epic. Level: integration.
- **AC-45** (FR-44) Given an effort at implementing with E-1 done and E-2 half done under the per-task flow, when it is claimed after the change, then E-2 is claimed whole with only its undone tasks. [agent]
  Observable: the claim names E-2; its pack lists only E-2's undone tasks; done tasks keep their commits; history shows a flow test run for E-1 before E-1's close. [agent] Level: integration.
- **AC-46** (FR-45) Given a tasks.md where E-1's task adds a check that only E-3's task can satisfy, when the tasks gate's executability juror reads it, then it raises a finding naming both tasks. [agent]
  Observable: the juror's output holds a finding citing both task IDs. Level: e2e.
- **AC-47** (FR-4, FR-42) Given a claimed epic whose named test hangs, or whose test file doesn't import, when the agent hands it back as done, then the flow's run ends as failed and counts as one of the 3 failed runs. [agent]
  Observable: the hung run is stopped at 30 minutes (a test lowers the limit); the epic is `failed`, not `testing`; its failed-run count rose by one; the recorded output is at most 50 lines. Level: integration.

- **AC-48** (FR-46) Given an effort with auto on whose spec carries the migration flag, when its plan gate's jury approves, then the flow commits `nio: approve plan` itself and history records an auto approval naming the grant. [human]
  Observable: the approval commit exists with no human command; the history line says auto and cites the grant line. Level: integration.
- **AC-49** (FR-47) Given an effort with auto on, when the driver unblocks a task blocked on a change request, overrides a failing guard, runs `seen` and rules a capped batch, then each succeeds and is recorded as auto; when the driver tries to approve the pr gate, revoke auto, or unblock an epic blocked by its 3 failed test runs, then it is refused and the run pauses for the human. [human]
  Observable: the four allowed steps exit zero with auto history lines; the three refused ones exit non-zero, change nothing, and the effort is paused naming the reason. Level: integration.

## Functional requirements
- **FR-1** WHEN a driver claims work in an effort whose tasks are approved, THE SYSTEM SHALL hand it one whole epic (every undone task of the first epic that is waiting or failed and whose dependencies are closed) instead of one task; one agent per epic, not one for the whole effort. [agent]
- **FR-2** WHEN an epic is claimed, THE SYSTEM SHALL build one pack for it holding the epic's tasks, the spec items and contracts they cite, and the tests they name. [agent]
- **FR-3** WHEN the implementation agent hands an epic back as done, THE SYSTEM SHALL run the tests the epic's tasks name itself and close the epic only if every one passes; the agent's report never counts. [human]
- **FR-4** IF an epic's test run fails, errors (a test file that doesn't import, a command not found), collects no test, or runs past 30 minutes (then stopped), THEN THE SYSTEM SHALL keep the epic open, record the failing tests and the last 50 lines of the run's output, and count it as one failed run toward FR-42's 3. [agent]
- **FR-5** THE SYSTEM SHALL have no per-task red or green step in the implement stage: `nio flow red` and `nio flow green` no longer gate a task, and task modes (split, single, direct) and the tests-frozen-at-red rule are gone. [human]
- **FR-6** THE SYSTEM SHALL run no jury per epic; the pr gate's one jury on the whole effort diff SHALL stay the only review of the implementation. [human]
- **FR-7** THE SYSTEM SHALL keep each task in tasks.md as an item of its epic's checklist and its task → AC → test map, with the tier rated per epic. [human]
- **FR-8** THE SYSTEM SHALL describe the implement stage as per-epic implementation in NORTH_STAR's "Implement" section and in the implement skill. [human]
- **FR-9** IF a driver claims an epic by name that is already claimed, or no epic is left to claim, THEN THE SYSTEM SHALL refuse the claim and name the epic or say none is left. [agent]
- **FR-10** IF the tasks of an epic name no test, THEN THE SYSTEM SHALL refuse to close the epic and say it has no test to run. [research: RF-19]
- **FR-11** WHEN an epic closes, THE SYSTEM SHALL commit only the epic's files and the flow files, leaving other untracked paths out. [agent]
- **FR-12** IF a task depends on a task in a later epic, THEN THE SYSTEM SHALL fail `nio check tasks` with a message naming both tasks and their epics. [human]
- **FR-13** WHEN a session runs `nio jury evidence`, the end-of-epic test command or the test suite, THE SYSTEM SHALL have the background mod run it in the background, and SHALL drop the mod's match on `nio jury run`, which no longer exists. [research: RF-6]
- **FR-14** WHEN `@nio:install` has installed the Claude Code mods in the NIO repo (#142), THE SYSTEM SHALL have the background mod on in every session that drives an effort there, with no per-person opt-in. [agent]
- **FR-15** IF a Claude Code session drives an effort without the background mod loaded, THEN THE SYSTEM SHALL say so when the driver starts. [agent]
- **FR-16** WHEN the human grants auto for an effort with `--by human`, at the done that closes drafting or at any later stage, THE SYSTEM SHALL turn the flag on and record the grant in the effort's history, and SHALL refuse a grant or revoke by anyone else, as #122's approved spec says (its FR-1 to FR-3, FR-30 to FR-32). [research: RF-22]
- **FR-17** WHILE an effort's auto flag is on, THE SYSTEM SHALL drive it stage after stage (next stage, its skill, done) until it pauses or ends, each stage in a fresh agent where the host allows, carrying over the grant, the `[auto]` tag and the driver claim already built on #122's branch. [research: RF-11]
- **FR-18** WHILE an effort's auto flag is on, THE SYSTEM SHALL drive the implement stage per epic (FR-1 to FR-3) and run the pr gate once per effort, with no epic jury. [human]
- **FR-19** WHILE an effort's auto flag is on, WHEN a jury round confirms blocker or major findings, THE SYSTEM SHALL hand all of them to one fix agent in one batch, which pauses for the human on a `[human]` line, a scope cut or a risk-flag change, accepts minors and refuted findings as the gate's risk, and start the next round after its edits, as #122's approved spec says (its FR-9 to FR-12, FR-17, FR-36, FR-37). [human]
- **FR-22** WHEN an auto run pauses, THE SYSTEM SHALL tell the human the reason and the command that resumes it; WHEN it reaches the end, it SHALL open the pull request with the run report as its body and stop, never merging, and the pr gate stays approved only by the human. [research: RF-22]
- **FR-23** WHEN the jury grounds a finding's quote, THE SYSTEM SHALL ignore a trailing source note of the form `(file, ID)`. [agent]
- **FR-24** IF every finding of a lens is dropped as ungrounded, THEN THE SYSTEM SHALL mark that juror's output invalid, ask for a re-run, and not compose the gate as approved. [agent]
- **FR-25** WHEN the human records a ruling on a finding dropped as ungrounded, THE SYSTEM SHALL accept it and reopen the finding. [agent]
- **FR-26** WHEN escalation jurors judge a blocker, THE SYSTEM SHALL count their outputs as votes on that blocker and record anything else they raise as notes, not new findings. [agent]
- **FR-27** THE SYSTEM SHALL keep each refuter pass's output under its own number, never overwriting an earlier pass. [agent]
- **FR-28** WHEN the refuter merges a confirmed finding into another and the kept finding's severity rises, THE SYSTEM SHALL keep the kept finding confirmed and send no second refuter batch for it. [agent]
- **FR-29** IF the artefact was fixed while an escalation round was running, THEN THE SYSTEM SHALL check the fix against the version the finding was raised on. [agent]
- **FR-30** WHEN plan versions are compared, THE SYSTEM SHALL treat a `### <ID>` heading and its lines as one item, so a fix-check pack carries only the changed contracts and tests and their neighbours. [agent]
- **FR-31** WHILE the memory index is being rebuilt, THE SYSTEM SHALL let a reader see either the old or the new index, never a half-built one, and SHALL skip a record missing from it rather than crash. [agent]
- **FR-32** IF a claim fails, THEN THE SYSTEM SHALL remove every worktree that claim created. [agent]
- **FR-33** WHEN `nio jury next` renders agents and the host session's root differs from the repo root it rendered into, THE SYSTEM SHALL warn that the host loads other agents. [agent]
- **FR-34** WHEN `nio flow next` or `nio flow done` prints the next step, THE SYSTEM SHALL name both the `/nio:<stage>` command and the skill's file `skills/<stage>/SKILL.md`, so the human can act on it whether or not the NIO plugin is installed. [agent]
- **FR-35** IF a fix task is retired, THEN THE SYSTEM SHALL accept the remaining fix tasks' IDs in `nio check tasks` and keep the retired ID unused. [research: RF-15]
- **FR-36** WHEN a fix task whose finding was accepted as risk is retired, THE SYSTEM SHALL keep the tasks approval and not move the effort back to tasks. [research: RF-15]
- **FR-37** WHEN an AC is proved by an existing test that passes, THE SYSTEM SHALL count that test as the AC's evidence and file no fix task for it. [agent]
- **FR-38** WHEN the flow writes a change request, THE SYSTEM SHALL write one that `nio check` accepts. [agent]
- **FR-39** IF a confirmed pr-gate finding is rooted in a spec or plan file, THEN THE SYSTEM SHALL route it to a spec or plan change, not a code fix task. [research: RF-15]
- **FR-40** IF a task lists a file it reuses unchanged, THEN THE SYSTEM SHALL raise no "isn't in the diff" finding for that file. [research: RF-17]
- **FR-41** WHEN the pr gate's jury runs, THE SYSTEM SHALL include the test-proof lens, judging for each test the effort added whether it would still pass with the code it proves left out; this replaces the proof red gave. [agent]
- **FR-42** WHEN a failed epic is claimed again, THE SYSTEM SHALL give a fresh implementation agent the epic's pack plus the failing tests and the output tail; IF an epic's test run has failed 3 times, THEN THE SYSTEM SHALL block the epic and wait for the human. [agent]
- **FR-43** WHEN two or more epics have no dependency between them, THE SYSTEM SHALL let them be claimed at once, each in its own worktree, through the existing waves. [agent]
- **FR-44** WHEN an effort that is already at implementing is claimed after this change, THE SYSTEM SHALL keep its done tasks done, run an epic whose tasks are all done through the flow's epic test run (FR-3) and close it only if that run passes, and claim the next epic whole with its undone tasks. [agent]
- **FR-45** WHEN the tasks gate's jury runs, THE SYSTEM SHALL have the executability lens flag a task blocked until a later epic: a guard or a suite check an early epic adds that only a later epic's task can satisfy. [agent]
- **FR-46** WHILE an effort's auto flag is on, WHEN a gate other than the pr gate has its jury approve, THE SYSTEM SHALL commit its approval itself, whatever the spec's risk flags, recording it in history as an auto approval that names the grant. [human]
- **FR-47** WHILE an effort's auto flag is on, THE SYSTEM SHALL let the driver run the steps that need `--by human` today (unblock, override of a failing guard, `seen`, a ruling on a capped batch), each recorded in history as auto with the grant it rests on; granting or revoking auto, approving the pr gate, and unblocking an epic blocked by its own 3 failed test runs stay the human's alone, and such a block pauses the auto run. [human]

## Rules
### State table: Epic (start: waiting; final: closed)
| State | claim | agent hands back done | hand-back, tasks name no test | flow's test run passes | test run fails, 1st or 2nd | test run fails, 3rd | human unblocks | Src |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| waiting | → claimed | reject: not claimed | reject: not claimed | reject: no run without a hand-back | reject: no run without a hand-back | reject: no run without a hand-back | reject: not blocked | [agent] |
| claimed | reject: already claimed | → testing | reject: no test to run (FR-10) | reject: no run without a hand-back | reject: no run without a hand-back | reject: no run without a hand-back | reject: not blocked | [agent] |
| testing | reject: tests running | ignore | ignore | → closed | → failed | → blocked | reject: not blocked | [agent] |
| failed | → claimed | reject: not claimed | reject: not claimed | reject: no run without a hand-back | reject: no run without a hand-back | reject: no run without a hand-back | reject: not blocked | [agent] |
| blocked | reject: blocked for the human | reject: not claimed | reject: not claimed | reject: no run without a hand-back | reject: no run without a hand-back | reject: no run without a hand-back | → waiting | [agent] |
| closed | reject: epic closed | reject: epic closed | reject: epic closed | ignore | ignore | ignore | reject: not blocked | [agent] |

A run that errors, collects no test or runs past 30 minutes counts as "flow's test run fails" (FR-4). Unblocking resets the failed-run count. An in-flight epic whose tasks were all done under the per-task flow enters at `testing` (FR-44). A closed epic that gains an undone task (a later pr round's fix task) is `waiting` again. [agent]

### Decision table: Gate outcome
| gate (pr, other) | auto (on, off) | risk flag (risky, none) | jury (approved, findings) | → outcome | Src |
| --- | --- | --- | --- | --- | --- |
| pr | - | - | approved | waits for the human's approval; the flow never approves it | [agent] |
| other | off | - | approved | waits for the human's approval | [agent] |
| - | off | - | findings | findings go to the human | [agent] |
| other | on | - | approved | the flow commits the approval, recorded as auto, and notifies the human | [human] |
| - | on | - | findings | one fix agent takes all confirmed findings, then the next round (stop list applies) | [agent] |

## Key entities
- **Epic claim**: which epic is claimed, by which driver, and its state (waiting, claimed, testing, failed, blocked, closed) and its failed-run count. [agent]
- **Epic pack**: the one input the implementation agent gets: the epic's tasks, the spec items and contracts they cite, the tests they name. [agent]
- **Epic test result**: the tests the flow ran for an epic, pass or fail, and the tail of the output. [agent]
- **Auto grant**: the auto flag with the history line recording who granted or revoked it and when. [agent]
- **Fix batch**: all confirmed findings of one jury round, handed to one fix agent. [human]

## Non-functional requirements
- **NFR-1** THE SYSTEM SHALL run an epic's named tests once per hand-back, not once per task. [agent]
- **NFR-2** THE SYSTEM SHALL start at most one implementation agent per epic attempt. [agent]

## Success criteria
- **SC-1** Replaying #142's first epic (its tasks.md and tests unchanged) through the new implement stage takes at most 29 min of agent time and 6 min of shell time, as the effort's usage record counts them: a quarter less than #142's ~39 min agent and ~8 min shell. [agent]
- **SC-2** A jury run during an effort finishes with no sleep/poll loop in the transcript. [human]
- **SC-3** An effort with auto on, risky or not, goes from approved spec to the pr gate with no human approval in between. [agent]
- **SC-4** No epic of a new effort stops for a red refusal, a can't-go-red task or a frozen test. [agent]

## Non-goals
- #133, #86, #104 and #92: left out of this effort. [agent]
- Making long commands themselves faster: the background mod removes wait loops, not run time. [human]
- A jury per epic: dropped in 373b3ee (#77, #100) and not brought back. [human]
- A separate fix for #97 (a task can't update older tests that pin behaviour it changes): with no red step, tests are never frozen, so it closes with this change. [human]
- Separate fixes for the per-task red/green parts of #108, #115, #82, #78, #80, #98 and #83 (red refusing a passing regression test, frozen files in the commit, per-task block cycles): they close with this change; what must survive is FR-11 and FR-35 to FR-40. [human]
- The background mod on hosts other than Claude Code: it is Claude-only dev tooling. [human]

## Glossary
- **Epic test run**: the run `nio flow` itself makes of the tests an epic's tasks name, after the agent hands the epic back.
- **Fix agent**: the one agent that settles all confirmed findings of a jury round.
- **Background mod**: the Claude Code hook in `tools/claude-mods/background-nio-commands/` that runs long nio commands in the background.
- **Auto**: the effort flag under which the flow approves every gate but the pr gate and does the `--by human` steps itself.

## Risks and evidence against
- With no red step, a test that passes with no code looks the same as one that checks something (#151); the test-proof lens at the pr gate (FR-41) is the check that replaces red. [agent]
- A large epic may overflow one agent's context (#151); epics have no size cap, the tasks drafter keeps them to one user story. [agent]
- #122's approved spec requires an epic jury after every epic (its FR-16, AC-20), which contradicts FR-6 and FR-18; its branch is 194 commits behind `main` (#151); this spec replaces those two items, and the branch's built work is carried over (FR-17). [research: RF-11]
- One spec covering this many issues is large; the jury's scope lens will weigh splitting it. [agent]

## Decisions
- Only the human grants or revokes auto mode, with `--by human`, recorded in history and revocable: D-261108-txqj (grill, 2026-11-08).
- Under auto the flow approves every gate but the pr gate, risky specs included, and the driver does the `--by human` steps itself; this replaces #122's risky-spec stop (its FR-28) and the risky-commit rule on `main` (FR-46, FR-47; the human, 2026-11-15).
- #122's approved spec is the contract for how auto behaves, except its epic jury (FR-16, AC-20 there), which FR-6 and FR-18 here replace; its built work is carried over, not rebuilt (Q-calls OP-12 to OP-16, OP-18).
- Red's proof is replaced by the test-proof lens at the pr gate (FR-41): an agent call under the delegated grill (grill.md, OP-2), for the human's review at this gate. [agent]
- One agent per epic; independent epics run in parallel; a failed epic gets a fresh agent, 3 tries (FR-1, FR-42, FR-43).
- Efforts already at implementing convert to per-epic at their next claim instead of finishing on the old flow, so no per-task code path survives FR-5 (FR-44): an agent call under the delegated grill (grill.md, OP-6), for the human's review at this gate; rollback is reverting the change. [agent]

