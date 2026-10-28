---
slug: 2026-10-28-flow-state
route: full
epic: ""                         # "<epic slug>/R-<n>" when this is a slice of an epic
risk: [multi-party]              # auth | pii | money | external-input | data-deletion | migration | multi-party | public-api
retired: [OP-1, OP-2, OP-3, OP-4, OP-5, OP-6, OP-7, OP-11, OP-8, OP-9, OP-10, OP-12, OP-13]                      # IDs removed from this spec; never reused
---
<!-- Spec template. WHAT and WHY only, never HOW. Every item ends with its provenance: [human] (the grill
confirmed it), [research: RF-n] (a finding in research.md) or [default] (your proposal; the grill must confirm it).
IDs are permanent: number new items after the highest ever used, never renumber, list removed IDs in `retired`.
Remove a section that doesn't apply; never write N/A. `nio check spec 2026-10-28-flow-state` checks all of this. -->
# Flow state: `nio flow` tells any agent where an effort is and moves it on only when deterministic guards pass

## Summary
Today no file says where an effort stands, so an agent keeps "where am I" in its context and loses it on a compaction,
a new session or a host switch, and the human can't tell what a run is doing without watching it (#45, #19). This adds
`nio flow`: `next` prints the current stage and what to do, `done` runs the stage's guards and moves on only when they
pass, `status` shows every effort on one line, and `park` marks an idle one. State is read from the files that already
hold it (spec, grill log, jury ledgers, change records); `state.json` keeps only what no file holds, and every transition
is appended to `history.jsonl`. The human can push a check through with a reason, a change request or a changed approved
file sends the effort back to the stage that owns the file, and the stop list pauses an effort that must not go on. The
`[guess]` tag, the auto switch and `nio flow run` come in later specs. [human]

## Actors and journeys
- **A-1 Human**: owns the project and its efforts; approves gates, answers grill questions, pushes a check through with a reason, parks idle efforts, and wants to see what every effort is doing without watching it. [human]
- **A-2 Orchestrator**: the agent session that drives one effort; the only caller of `nio flow done`, so the only writer of flow state. Skilled with NIO's skills and CLI, but its context can be compacted or replaced at any time. [human]
- **A-3 Worker**: an agent working one task in a worktree or on another host; writes its handoff (result, evidence, test output) and never touches flow state. [human]

**UJ-1 Carry on after a compaction** (A-2) [human]
1. The orchestrator's context is compacted, or a new session or another host takes over.
2. It runs `nio flow next` and reads the stage, the skill to run, the input files, the exit criteria and the done command.
3. It runs the skill, then `nio flow done` with the stage.
4. The guards pass and the effort moves on, or `done` prints what is still missing and the orchestrator works on that.
- Misuse: the orchestrator edits `state.json` by hand, or reports a stage done on its own say-so, to get past a guard.
- Evidence: issue #45 ("After a compaction, a new session or a host switch, the agent runs `nio flow next` and carries on"); no recorded case of a lost place, but idle efforts, unlinked runs and skills that name no next command [research: RF-1].

**UJ-2 See what every effort is doing** (A-1) [human]
1. The human runs `nio flow status`.
2. They read one line per effort: its stage, whether it runs in auto mode, what it is doing or waiting on, and when it last moved.
3. They park an effort they've stopped working on, with a reason, and resume it later with `nio flow start` or `nio flow next`.
- Misuse: an effort sits idle for days and looks like it is still running.
- Evidence: issue #45 Brainstorm Q13; implementation-jury idle since 2026-10-27 with nothing marking it.

**UJ-3 Push a stuck check through** (A-1) [human]
1. A guard fails for a reason the human judges wrong, for example a jury tooling bug.
2. The human runs `nio flow done` with `--human` and a reason.
3. The effort moves on, and its history keeps the failing guard output and the reason as a record of its own.
- Misuse: an agent uses the override to skip a guard it can't pass.
- Evidence: issue #45 Brainstorm Q12; #55 (an override that produced no record of its own).

**UJ-4 A change sends the effort back** (A-1, A-2) [human]
1. A change request is filed against one of the effort's files, or an approved file is edited after its gate judged it.
2. The next `nio flow` call moves the effort back to the stage that owns the file and names the change in its history.
3. The orchestrator works that stage again and the effort moves forward through the guards as before.
- Misuse: work carries on against a spec or plan that no longer matches what was approved.
- Evidence: issue #45 Brainstorm Q14; C-261028-7njg reopened the tasks-stage spec after the plan jury landed.

## User stories

### US-1 Any agent picks up where the effort is (P1) [human]
- **Why this priority:** this is why the machine exists; without it nothing else here has a stage to guard, show or reopen.
- **Independent test:** set up an effort folder at a known stage, run `nio flow next` in a fresh shell with no other context, and compare what it prints with the stage the files show.

- **AC-1** (FR-7, FR-2) Given an effort whose spec gate is approved and which has no plan yet, when `nio flow next` runs, then it names the planning stage, the plan skill, its input files, its exit criteria and the done command. [agent]
  Observable: the output names `planning`, `@nio:plan`, `spec.md`, and the command `nio flow done planning` with the slug. Level: unit.
- **AC-2** (FR-8) Given an effort whose `grill.md` ends with an `## Asked · Q4` entry and no answer, when `nio flow next` runs, then it reports the effort waiting for the human on Q4. [human]
  Observable: the output says `waiting_for_human` and names Q4; no skill other than the grill is named. Level: unit.
- **AC-3** (FR-9, FR-10) Given two efforts with history, when `nio flow start` runs on the older one and then `nio flow next` runs with no slug, then it reports on the one just started, and no pointer file exists. [human]
  Observable: the output names the started slug; no file outside the effort folders was written. Level: integration.
- **AC-4** (FR-11) Given no current effort and no slug, when `nio flow next` runs, then it fails and lists the efforts it could start. [agent]
  Observable: non-zero exit; the message names each non-legacy effort and the `nio flow start` command. Level: unit.
- **AC-5** (FR-11) Given a slug with no folder under `.nio/specs/`, when `nio flow start` runs on it, then it fails and writes nothing. [agent]
  Observable: non-zero exit naming the slug; no folder, `state.json` or `history.jsonl` is created. Level: unit.
- **AC-6** (FR-10, FR-4, FR-5) Given an effort folder with no `state.json`, when `nio flow start` runs on it, then it creates `state.json` and `history.jsonl` with one start line carrying who, when and the run. [agent]
  Observable: both files exist; `history.jsonl` has one line with the role, host, model, timestamp and run ID fields. Level: unit.
- **AC-7** (FR-3) Given an effort that has passed its spec gate, when `state.json` is read, then it holds no gate outcome, round, judged version, pending question or change request. [human]
  Observable: the keys of `state.json` are within the auto flag, pause reason, abandon reason, waiting-on, task claims and attempts, and current run. Level: unit.
- **AC-8** (FR-2) Given the spec ledger says `approved` and `spec.md` is unchanged since its last round, when the ledger is edited to `rejected` and `nio flow next` runs, then the stage reflects the rejection without any `nio flow` write in between. [human]
  Observable: `next` names `grilling`; `state.json` is byte-identical before and after. Level: unit.
- **AC-9** (FR-6) Given `state.json` holds a key `stage`, which is not one of the stored fields, when any `nio flow` command runs, then it refuses and names the file and the key. [agent]
  Observable: non-zero exit; the message names `state.json` and `stage`. Level: unit.
- **AC-10** (FR-6, FR-60) Given line 3 of a 5-line `history.jsonl` is not valid JSON, when `nio flow next` and `nio flow status` run, then `next` refuses naming the file and line 3, and `status` shows that effort as broken and lists the others. [human]
  Observable: `next` exits non-zero naming `history.jsonl` and line 3; the status line says `broken: history.jsonl, line 3`; other efforts are listed. Level: unit.
- **AC-58** (FR-58, FR-6) Given an effort whose `state.json` was edited by hand to set the auto flag, when `nio flow next` runs, then it refuses and names `state.json`. [human]
  Observable: non-zero exit; the message names `state.json` and the hash mismatch; nothing is written. Level: unit.
- **AC-59** (FR-59) Given `history.jsonl` whose last line has no line ending, when `nio flow park` runs, then the torn line is cut off, the park is recorded, and a line notes the cut. [human]
  Observable: exit 0; the file ends with a line ending; it holds a `repair` line naming the cut and a `park` line; the torn text is gone. Level: unit.
- **AC-11** (FR-1) Given the shipped skills and agent cards, when they are searched, then none tells an agent to write `state.json` or `history.jsonl`. [human]
  Observable: no file under `skills/` or `src/nio/agents/` instructs an edit of either file; every mention goes through a `nio flow` command. Level: unit.
- **AC-12** (FR-45, FR-54) Given one `nio flow done` call on an effort is still writing, when a second `nio flow` call tries to write the same effort, then the second is refused and the first completes. [human]
  Observable: the second exits non-zero saying the effort is being written; `history.jsonl` has exactly one new line. Level: integration.
- **AC-56** (FR-54) Given a lock file in the effort folder 2 minutes old and no call running, when `nio flow park` runs, then it takes the lock over and parks the effort; the lock file is never listed by `git status`. [human]
  Observable: exit 0; one `park` history line; `git status --porcelain` doesn't list the lock. Level: integration.

### US-2 The effort moves on only when its guards pass (P1) [human]
- **Why this priority:** the guards are what makes the state trustworthy: no stage counts as done because an agent says so.
- **Independent test:** run `nio flow done` on fixture efforts whose guards pass and fail, and read the state and history after each.

- **AC-13** (FR-12, FR-15, FR-4) Given an effort in grilling whose `nio check spec --gate` passes, when `nio flow done grilling` runs, then the effort moves to spec_jury and one history line records it. [human]
  Observable: exit 0; `next` names `spec_jury`; one new line in `history.jsonl` with from `grilling`, to `spec_jury` and the check as evidence. Level: unit.
- **AC-14** (FR-13, FR-15) Given an effort in grilling whose spec still has OP-3 and one unconfirmed `[default]`, when `nio flow done grilling` runs, then it fails and names both. [human]
  Observable: non-zero exit; the output names OP-3 and the default item; `next` still names `grilling`; no history line is added. Level: unit.
- **AC-15** (FR-14) Given a worker's handoff file says "all tests pass" and the spec jury's ledger is not approved, when `nio flow done spec_jury` runs, then it fails. [human]
  Observable: non-zero exit; the output names the ledger's outcome; the handoff text is not cited as evidence. Level: unit.
- **AC-16** (FR-15) Given an effort in tasking whose `tasks.md` leaves AC-4 with no task, when `nio flow done tasking` runs, then it fails naming AC-4. [human]
  Observable: non-zero exit; the output carries `nio check tasks`'s error for AC-4. Level: unit.
- **AC-17** (FR-16) Given an effort in drafting, when `nio flow done planning` runs, then it refuses and names drafting as the current stage. [agent]
  Observable: non-zero exit; the message names `drafting`; no history line is added. Level: unit.
- **AC-18** (FR-17) Given an effort that already passed drafting, when `nio flow done drafting` runs again, then nothing changes. [agent]
  Observable: exit 0; `history.jsonl` and `state.json` are byte-identical before and after. Level: unit.
- **AC-19** (FR-18) Given the spec jury's ledger says `approved` with `unresolved: 0`, when `nio flow done spec_jury --commit` runs, then one commit `nio: approve spec` holds the effort's files. [human]
  Observable: the latest commit's message is `nio: approve spec`; it touches `history.jsonl` and the spec ledger and no file outside the effort folder. Level: integration.
- **AC-52** (FR-48, FR-49) Given the same approved ledger, uncommitted, and the auto flag off, when `nio flow done spec_jury` runs without `--commit`, then nothing is committed or recorded, and both it and `nio flow next` print the `--commit` command. [human]
  Observable: `HEAD` unchanged; no new history line; each output contains `nio flow done spec_jury --commit`. Level: integration.
- **AC-20** (FR-19) Given an effort in drafting whose guard passes, when `nio flow done drafting` runs, then no commit is made. [human]
  Observable: `HEAD` is unchanged; the history line is in the working tree, uncommitted. Level: integration.
- **AC-21** (FR-20) Given a gate passes and the commit fails (for example a pre-commit hook rejects it), when `nio flow done` runs, then it reports git's error and records nothing. [agent]
  Observable: non-zero exit carrying git's message; `history.jsonl` has no new line; `next` names the same stage. Level: integration.
- **AC-22** (FR-21) Given drafting passes and researching and advocate_walking are not built, when `nio flow done drafting` runs, then the history records both as `skipped: not built` and the effort moves to grilling. [human]
  Observable: three new lines: the drafting pass, then `skipped: not built` for `researching` and for `advocate_walking`; `next` names `grilling` and mentions the skipped stages. Level: unit.
- **AC-23** (FR-22) Given the tasks gate passes and the implement stage is not built, when the effort reaches implementing, then it waits for the human. [human]
  Observable: `next` says `waiting_for_human: implement not built` and names no skill. Level: unit.
- **AC-24** (FR-23) Given an effort in spec_jury whose ledger turns `rejected`, when `nio flow next` runs, then the effort is back in grilling. [human]
  Observable: `next` names `grilling` and the rejected round. Level: unit.
- **AC-63** (FR-56) Given an effort sent back to grilling by a rejected spec ledger, when `spec.md` is edited after that round, then `nio flow next` names `spec_jury` for its re-review. [human]
  Observable: `next` names `spec_jury`. Level: unit.
- **AC-25** (FR-23) Given an effort in tasks_jury whose ledger turns `rejected`, when `nio flow next` runs, then the effort is back in tasking. [human]
  Observable: `next` names `tasking`. Level: unit.
- **AC-64** (FR-55) Given an effort whose spec ledger is approved and a `nio: approve spec` commit touched its folder, with no `history.jsonl`, when `nio flow next` runs, then it is past spec_jury; without that commit it waits on the approval. [human]
  Observable: with the commit, `next` names `planning`; without it, `waiting_for_human` with `nio flow done spec_jury --commit`. Level: integration.
- **AC-51** (FR-47) Given an effort with an approved spec gate, no plan files and no `history.jsonl`, when `nio flow next` runs, then it names planning, and nothing is written. [human]
  Observable: `next` names `planning`; no `state.json` or `history.jsonl` is created. Level: unit.

### US-3 The human can push a check through, on the record (P2) [human]
- **Why this priority:** without it a broken guard or jury tool blocks an effort for good; with it, every push is still traceable.
- **Independent test:** run `nio flow done --human` on a fixture whose guard fails and read the history line.

- **AC-26** (FR-24, FR-25) Given an effort in grilling whose `nio check spec --gate` fails on OP-3, when `nio flow done grilling --human "OP-3 is settled in Q5"` runs, then the effort moves to spec_jury and its own history line holds the guard output and the reason. [human]
  Observable: `next` names `spec_jury`; one new line with kind `override`, the failing output naming OP-3, and the reason text. Level: unit.
- **AC-27** (FR-25) Given the same override is given twice on two efforts' identical failures, when both history files are read, then each holds its own override line. [human]
  Observable: each `history.jsonl` has exactly one override line; neither is merged or deduplicated. Level: unit.
- **AC-28** (FR-26) Given a failing guard, when `nio flow done grilling --human ""` runs, then it refuses. [human]
  Observable: non-zero exit; the message says a reason is required; no history line is added. Level: unit.
- **AC-29** (FR-27) Given the human closed the spec gate with `nio jury check --human "pack bug"`, when `nio flow done spec_jury` runs, then the gate passes as a human override carrying that reason. [human]
  Observable: exit 0; the history line has kind `override` and the reason `pack bug`. Level: unit.
- **AC-57** (FR-57) Given an override on grilling, when `nio flow status` runs before and after `nio flow seen <slug>`, then the override shows before and not after, and history records the seen. [human]
  Observable: before, the line names the override and its reason; after, it doesn't; one history line with kind `seen`. Level: unit.
- **AC-30** (FR-24) Given every guard of grilling passes, when `nio flow done grilling --human "just in case"` runs, then the transition is recorded as a normal pass with the reason noted. [agent]
  Observable: one history line with kind `pass` and the reason; no override line. Level: unit.

### US-4 The human sees every effort at a glance (P2) [human]
- **Why this priority:** several efforts run at once and idle ones look alive; this is how the human finds out what needs them.
- **Independent test:** run `nio flow status` on a repo with a working, a waiting, a parked, a done and a legacy effort.

- **AC-31** (FR-28, FR-46) Given five efforts (working, waiting on Q4, parked, waiting at implementing, and one with no history), when `nio flow status` runs, then it prints one line per effort, newest activity first, each with its state, auto or not, its status word and last activity. [human]
  Observable: five lines in order of last activity; the status words are `working`, `waiting_for_human: Q4`, `parked: <why>`, `waiting_for_human: implement not built`; the effort with no history shows the time of its newest commit. Level: integration.
- **AC-32** (FR-29) Given `.nio/specs/grilling/`, a folder without the layout, when `nio flow status` runs, then it shows it as `legacy`, and no `nio flow` command writes into it. [human]
  Observable: the line says `legacy`; `nio flow start grilling` exits non-zero; the folder is byte-identical after. Level: unit.
- **AC-53** (FR-50) Given a dated effort whose spec has `route: lite`, when `nio flow status` and `nio flow next` run on it, then both say `unsupported: lite` and nothing is written. [human]
  Observable: the status line says `unsupported: lite`; `next` names no skill; no `state.json` or `history.jsonl` appears. Level: unit.
- **AC-33** (FR-30) Given a working effort, when `nio flow park` runs with the reason "waiting on #43", then status shows it parked with that reason and history records it. [human]
  Observable: status line `parked: waiting on #43`; one history line with kind `park` and the reason. Level: unit.
- **AC-34** (FR-31) Given a parked effort, when `nio flow next` runs on it, then it is no longer parked and history records the resume. [human]
  Observable: status shows `working`; one history line with kind `resume`. Level: unit.
- **AC-35** (FR-32) Given an effort, when `nio flow park` runs with an empty reason, or on an effort that is done, then it refuses. [agent]
  Observable: non-zero exit for each; no history line is added. Level: unit.
- **AC-55** (FR-52, FR-53) Given a parked effort, when `nio flow abandon` runs with "superseded by #60" and a pending change record is then filed against its `plan.md`, then status lists it last as abandoned and it doesn't move; after `nio flow start` it is working again. [human]
  Observable: last status line `abandoned: superseded by #60` with the stage unchanged; history has kind `abandon`, then `resume` after start. Level: unit.
- **AC-61** (FR-54) Given a lock held for 2 minutes by a process on this host that is still running, when `nio flow park` runs, then it is refused. [agent]
  Observable: non-zero exit saying the effort is being written; no history line. Level: integration.
- **AC-62** (FR-61) Given an effort, when `nio flow abandon` runs with an empty reason, on `.nio/specs/grilling/`, on a dated effort with `route: lite`, or on a done effort, then it refuses. [human]
  Observable: non-zero exit for each; no history line; the folder is byte-identical. Level: unit.
- **AC-36** (FR-33, FR-5) Given `nio run 2026-10-28-flow-state planning` started run R-1, when `nio flow done planning` runs during it, then the run folder names the effort and stage and the history line carries R-1. [human]
  Observable: the run folder holds the slug and `planning`; the history line's run field is R-1. Level: integration.
- **AC-37** (FR-34) Given no arguments, when `nio run` runs, then it creates a run as it does today. [agent]
  Observable: exit 0; it prints a run ID and creates `.nio/runs/<run>/promote.md`. Level: integration.

### US-5 A change sends the effort back to the stage that owns the file (P1) [human]
- **Why this priority:** carrying on against a stale spec or plan builds the wrong thing; C-261028-7njg showed it happens.
- **Independent test:** take a fixture effort at tasking, add a pending change record against its `plan.md`, and run `nio flow next`.

- **AC-38** (FR-35, FR-37) Given an effort in tasking and a `C-*` record with `outcome: pending` and `against:` its `plan.md`, when `nio flow next` runs, then it reports the effort `waiting_for_human` on the change record, names planning as the stage it goes back to, and history records the move once. [human]
  Observable: `next` says `waiting_for_human` with the C ID and `planning`; one history line with from `tasking`, to `planning` and the C ID; a second `next` adds no line. Level: unit.
- **AC-39** (FR-36, FR-37) Given an effort at implementing whose `tasks.md` was edited after the tasks gate judged it, when `nio flow next` runs, then the effort is back in tasks_jury and history names the file and both versions. [human]
  Observable: `next` names `tasks_jury`; the history line holds `tasks.md`, the judged version and the current one. Level: unit.
- **AC-40** (FR-35) Given a `C-*` record with `outcome: rejected` against the effort's `plan.md`, when `nio flow next` runs, then nothing moves. [human]
  Observable: `next` names the same stage as before; no history line is added. Level: unit.
- **AC-41** (FR-38) Given a pending change record against `plan.md` and the effort back in planning, when `nio flow done planning` runs with the plan check passing, then it refuses while the record is pending. [human]
  Observable: non-zero exit naming the C ID and its `outcome: pending`. Level: unit.
- **AC-42** (FR-35) Given a parked effort at tasking and a pending change record against its `research.md`, when `nio flow status` runs, then the effort is in grilling and still parked. [agent]
  Observable: the status line shows `grilling` and `parked: <why>`. Level: unit.

### US-6 The stop list pauses an auto effort that must not go on (P3) [human]
- **Why this priority:** it only bites once an effort runs in auto mode, which a later spec switches on; this spec builds the list so the switch has something to stop on.
- **Independent test:** set the auto flag in a fixture `state.json` and drive each stop condition.

- **AC-43** (FR-39) Given an auto effort whose plan gate has run 3 jury rounds without approval, when `nio flow next` runs, then it pauses the effort for the human and lists the open findings. [human]
  Observable: `next` names no skill; it prints the pause reason and every open finding ID of the plan ledger. Level: unit.
- **AC-44** (FR-39) Given an auto effort whose spec gate's round 2 closed no finding of round 1, when `nio flow next` runs, then it pauses the same way after 2 rounds. [human]
  Observable: as AC-43, after round 2. Level: unit.
- **AC-60** (FR-39) Given an auto effort whose spec gate has finished round 1 with open findings, when `nio flow next` runs, then it does not pause. [human]
  Observable: `next` names the gate's skill as usual. Level: unit.
- **AC-45** (FR-40) Given an auto effort and `budgets` allowing 4 juries, when the fifth jury would start, then the effort is suspended and the report lists what it used. [human]
  Observable: status `suspended: cap`; `next` prints the jury and subagent run counts used. Level: unit.
- **AC-46** (FR-41) Given an auto effort, when `nio flow done tasking` fails 3 times with the same guard output, then the effort is suspended as stuck. [human]
  Observable: status `suspended: stuck`; a fourth `done` names no skill until resumed. Level: unit.
- **AC-47** (FR-41) Given an auto effort, when `nio flow done tasking` fails 3 times with different guard output each time, then it is not suspended. [human]
  Observable: status stays `working`. Level: unit.
- **AC-48** (FR-42) Given an auto effort at tasking and a new pending change record against `plan.md`, when `nio flow next` runs, then the effort waits for the human before moving back. [human]
  Observable: `waiting_for_human` naming the C ID; `next` still names `tasking` until the human resumes it, then names `planning`. Level: unit.
- **AC-54** (FR-51) Given an auto effort whose spec has `risk: [money]` and an approved spec ledger, when `nio flow done spec_jury` runs, then nothing is committed and it waits for the human's `--commit`. [human]
  Observable: `HEAD` unchanged; status `waiting_for_human` naming the approval; the output prints `nio flow done spec_jury --commit`. Level: unit.
- **AC-49** (FR-43, FR-44) Given a suspended effort, when `nio flow next` runs, then it prints the reason in the "Talking to the human" shape and names no skill, until `nio flow start` resumes it. [agent]
  Observable: the output has the shape's parts and no skill name; after `nio flow start`, `next` names a skill again. Level: unit.
- **AC-50** (FR-39) Given an effort with the auto flag off whose gate has run 3 rounds, when `nio flow next` runs, then the stop list doesn't pause it. [human]
  Observable: `next` names the gate's skill as usual. Level: unit.

## Functional requirements
- **FR-1** THE SYSTEM SHALL write an effort's `state.json` and `history.jsonl` only through `nio flow` commands, and no skill or agent card SHALL tell an agent to edit them. [human]
- **FR-2** WHEN any `nio flow` command runs THE SYSTEM SHALL read gate outcomes, rounds and judged versions from `jury/<gate>.json`, the pending question from `grill.md`, and pending change requests from `C-*` records, and SHALL keep no copy of them. [human]
- **FR-3** THE SYSTEM SHALL store in `.nio/specs/<slug>/state.json` only the auto flag, the pause reason, the abandon reason, what the effort waits on, task claims and attempts, and the current run. [human]
- **FR-4** WHEN a transition happens THE SYSTEM SHALL append one line to `.nio/specs/<slug>/history.jsonl` and never rewrite an earlier line. [human]
- **FR-5** THE SYSTEM SHALL record on every history line who (role, host, model), when, from, to, the evidence (paths, verdict ID, test output hash) and the current run ID. [human]
- **FR-6** IF `state.json` or a line of `history.jsonl` other than a torn last line (FR-59) can't be read, or `state.json` holds a key outside FR-3's list, or its hash differs from the one the last history line recorded (FR-58), THEN THE SYSTEM SHALL refuse every `nio flow` command on that effort and name the file and the key or line. [human]
- **FR-58** THE SYSTEM SHALL record on every history line a hash of `state.json` as the command left it. [human]
- **FR-59** IF the last line of `history.jsonl` has no line ending THEN THE SYSTEM SHALL ignore it, cut it off on the next write, and record that it did. [human]
- **FR-60** WHEN `nio flow status` meets an effort that FR-6 refuses THE SYSTEM SHALL show it as `broken: <file, line or key>` and list the other efforts as usual. [human]
- **FR-7** WHEN `nio flow next` runs THE SYSTEM SHALL print the current state, the skill to run, the input files, the exit criteria and the `nio flow done` command that reports it. [human]
- **FR-8** WHEN `grill.md` has an `## Asked` entry with no answer THE SYSTEM SHALL report the effort as `waiting_for_human` with that question's ID. [human]
- **FR-9** WHEN a `nio flow` command runs with no slug THE SYSTEM SHALL act on the effort with the newest history line, keeping no pointer of its own. [human]
- **FR-10** WHEN `nio flow start <slug>` runs THE SYSTEM SHALL create its `state.json` and `history.jsonl` if missing and record a start line, which makes it the effort with the newest history line. [human]
- **FR-11** IF no slug is given and no effort has a history line, or the slug has no folder under `.nio/specs/`, THEN THE SYSTEM SHALL refuse, list the efforts it can act on, and write nothing. [agent]
- **FR-12** WHEN `nio flow done <stage>` runs THE SYSTEM SHALL run that stage's guards itself and, when all pass, move the effort to the next state. [human]
- **FR-13** IF a guard fails THEN THE SYSTEM SHALL leave the state unchanged, print each failing guard with what is still missing, and exit non-zero; it writes no history line except FR-41's `fail` line in auto mode. [human]
- **FR-14** THE SYSTEM SHALL decide a guard only from files and the results of commands it runs, never from an agent's claim or a worker's handoff text. [human]
- **FR-15** THE SYSTEM SHALL use the guards in the decision table "Guards" to leave each stage. [human]
- **FR-16** IF `nio flow done` names a stage the effort hasn't reached THEN THE SYSTEM SHALL refuse and name the current stage. [agent]
- **FR-17** WHEN `nio flow done` names a stage the effort has already passed THE SYSTEM SHALL change nothing, add no history line and exit 0. [agent]
- **FR-18** WHEN a gate's guard passes and either `nio flow done <gate> --commit` was run or the auto flag is on, THE SYSTEM SHALL commit the effort's files with the message `nio: approve <stage>` and record the pass. [human]
- **FR-48** WHEN a gate's guard passes, the auto flag is off and `--commit` is not given, THE SYSTEM SHALL make no commit, record nothing, and print the exact `nio flow done <gate> --commit` command for the human to approve. [human]
- **FR-49** WHILE a gate's guard passes but neither its approval commit nor an override exists, WHEN `nio flow next` or `nio flow status` runs THE SYSTEM SHALL report the effort `waiting_for_human` on that gate's approval and print the `nio flow done <gate> --commit` command. [derived: FR-48, FR-55]
- **FR-19** WHEN a transition that is not a gate happens THE SYSTEM SHALL make no commit, leaving it to ride along with the next normal commit. [human]
- **FR-20** IF the gate commit fails THEN THE SYSTEM SHALL print git's error, record no transition and leave the state unchanged. [agent]
- **FR-21** WHEN the next stage is not built THE SYSTEM SHALL record it in history as `skipped: not built`, say so in `nio flow next`, and move to the next built stage; today researching, advocate_walking and arch_grilling are not built (RF-2). [human]
- **FR-22** WHILE the implement stage is not built, WHEN an effort reaches implementing THE SYSTEM SHALL set it waiting for the human with the reason `implement not built`. [human]
- **FR-23** WHEN a gate's jury ledger says `rejected` THE SYSTEM SHALL move the effort back as the state table "Flow" says. [human]
- **FR-24** WHEN `nio flow done <stage> --human "<reason>"` runs and a guard fails THE SYSTEM SHALL pass the stage and append a history line holding the failing guard output and the reason. [human]
- **FR-25** THE SYSTEM SHALL write each human override as its own history line and never merge or deduplicate it with another line. [human]
- **FR-26** IF `--human` is given with an empty reason THEN THE SYSTEM SHALL refuse and record nothing. [human]
- **FR-57** THE SYSTEM SHALL show each override in `nio flow status` and `nio flow next` as an override not yet seen, with its stage and reason, until `nio flow seen <slug>` records that the human saw it; every skill and agent card SHALL say that only the human gives `--human` or runs `nio flow seen`. [human]
- **FR-27** WHEN a jury gate was closed by the human with a reason (`nio jury check --human`) THE SYSTEM SHALL treat its guard as passed by a human override and record that reason. [human]
- **FR-28** WHEN `nio flow status` runs THE SYSTEM SHALL print one line per effort, newest activity first, with its state, auto or not, one of `working`, `waiting_for_human: <why>`, `suspended: <cap|stuck>`, `parked: <why>`, `unsupported: <route>`, `abandoned: <why>` or `done`, and its last activity, with abandoned efforts listed last. [human]
- **FR-29** IF an effort folder's name doesn't start with a `YYYY-MM-DD-` date THEN THE SYSTEM SHALL show it as `legacy` and write nothing in it. [research: RF-4]
- **FR-30** WHEN `nio flow park <slug> "<why>"` runs THE SYSTEM SHALL mark the effort parked with that reason and record it in history. [human]
- **FR-31** WHEN `nio flow start` or `nio flow next` runs on a parked effort THE SYSTEM SHALL resume it and record the resume in history. [human]
- **FR-32** IF `nio flow park` is given an empty reason, or the effort is done, THEN THE SYSTEM SHALL refuse and record nothing. [agent]
- **FR-33** WHEN `nio run <slug> <stage|T-n>` runs THE SYSTEM SHALL write the effort and the stage or task into the run folder. [human]
- **FR-34** WHEN `nio run` runs with no arguments THE SYSTEM SHALL create a run as it does today. [agent]
- **FR-35** WHEN a `C-*` record with `outcome: pending` has `against:` one of the effort's files THE SYSTEM SHALL move the effort, from any state, back to the stage the decision table "Owning stage" gives for a pending change request. [human]
- **FR-36** WHEN an approved file's content no longer matches the version its gate judged THE SYSTEM SHALL move the effort, from any state, back to the stage the decision table "Owning stage" gives for an edited approved file. [human]
- **FR-37** WHEN a change moves the effort back THE SYSTEM SHALL record the move once, not on every later call, and name the change in the history line: the C ID, or the file with its judged and current versions. [human]
- **FR-38** IF a pending `C-*` record is against one of the effort's files THEN THE SYSTEM SHALL refuse `nio flow done` for the owning stage and every later stage until the record is no longer pending, and `nio flow next` SHALL report the effort `waiting_for_human` on that record. [human]
- **FR-39** WHILE the effort's auto flag is on, WHEN a gate has spent 3 jury rounds, or, from round 2 on, a round closed none of the previous round's open findings, THE SYSTEM SHALL pause the effort for the human and list the gate's open findings. [human]
- **FR-40** WHILE the effort's auto flag is on, WHEN a per-effort count cap from a new `budgets` key in config (`budgets.juries`, `budgets.subagents`: per effort, unlike `jury.max_runs`, which caps lens runs per gate; neither is counted per effort today, RF-5) is used up THE SYSTEM SHALL suspend it as `suspended: cap` and report what it used. [human]
- **FR-41** WHILE the effort's auto flag is on, WHEN `nio flow done` fails THE SYSTEM SHALL append a `fail` history line with the guard and a hash of its output with timestamps and paths removed, and WHEN the last 3 history lines are `fail` lines with the same guard and hash it SHALL suspend the effort as `suspended: stuck`. [human]
- **FR-42** WHILE the effort's auto flag is on, WHEN a change would move it back (FR-35, FR-36) THE SYSTEM SHALL pause for the human before moving it. [human]
- **FR-51** WHILE the effort's auto flag is on and its spec's `risk:` holds `money`, `data-deletion`, `migration` or `auth`, WHEN a gate's guard passes THE SYSTEM SHALL wait for the human's `--commit` instead of committing, as with the auto flag off. [human]
- **FR-43** WHILE an effort waits for the human or is suspended, WHEN `nio flow next` runs THE SYSTEM SHALL print the reason in the "Talking to the human" shape and name no skill. [agent]
- **FR-44** WHEN `nio flow start` runs on a suspended effort THE SYSTEM SHALL resume it and record the resume in history. [agent]
- **FR-45** IF another `nio flow` call holds the effort's lock file THEN THE SYSTEM SHALL refuse to write, say the effort is being written, and change nothing. [human]
- **FR-54** WHEN a `nio flow` call writes an effort THE SYSTEM SHALL create a lock file in the effort folder that git ignores, atomically, naming its process and host, and SHALL take it over only when it is older than one minute and its process on this host is gone, or its host is another one. [human]
- **FR-47** WHEN any `nio flow` command runs THE SYSTEM SHALL take the effort's stage to be the first stage in the state table "Flow" that has not passed, whether or not `nio flow done` recorded the stages before it; `done` runs the same guards and records the passing. A stage that is not a gate has passed when its guard passes on the files, when it is not built (FR-21), or when history holds an override line for it. [human]
- **FR-55** THE SYSTEM SHALL count a gate as passed only when its guard passes on the files and either a commit `nio: approve <gate>` touched the effort folder or history holds an override line for it. [human]
- **FR-56** WHILE a gate's ledger says `rejected` and the gate's files are unchanged since the round that rejected them, THE SYSTEM SHALL take the effort's stage to be the state table's "jury rejects" target; once those files change, the stage is the gate again, for its re-review. [human]
- **FR-50** IF an effort's spec has a route other than `full` THEN THE SYSTEM SHALL show it as `unsupported: <route>` in `nio flow status`, say so in `nio flow next`, and write nothing in it. [human]
- **FR-52** WHEN `nio flow abandon <slug> "<why>"` runs with a non-empty reason THE SYSTEM SHALL mark the effort abandoned, record it in history, and stop moving it on changes (FR-35, FR-36) until `nio flow start` resumes it; no skill or agent card SHALL tell an agent to abandon an effort unless the human asked for it. [human]
- **FR-61** IF `nio flow abandon` is given an empty reason, or the effort is legacy, unsupported or done, THEN THE SYSTEM SHALL refuse and record nothing. [human]
- **FR-53** WHEN `nio flow start` runs on an abandoned effort THE SYSTEM SHALL resume it and record the resume in history. [human]
- **FR-46** THE SYSTEM SHALL take an effort's last activity from its newest history line, or, when it has none, from the newest commit that touched its folder. [agent]

## Rules

### State table: Flow (start: intake; final: done)
| State | guard passes | jury rejects | Src |
| --- | --- | --- | --- |
| intake | → drafting | ignore | [human] |
| drafting | → researching | ignore | [human] |
| researching | → advocate_walking | ignore | [human] |
| advocate_walking | → grilling | ignore | [human] |
| grilling | → spec_jury | ignore | [human] |
| spec_jury | → arch_grilling | → grilling | [human] |
| arch_grilling | → planning | ignore | [human] |
| planning | → plan_jury | ignore | [human] |
| plan_jury | → tasking | → planning | [research: RF-3] |
| tasking | → tasks_jury | ignore | [human] |
| tasks_jury | → implementing | → tasking | [human] |
| implementing | → done | ignore | [human] |
| done | ignore | ignore | [human] |

### Decision table: Guards
| Stage left (intake, drafting, researching, advocate_walking, grilling, spec_jury, arch_grilling, planning, plan_jury, tasking, tasks_jury, implementing) | → Guard | Src |
| --- | --- | --- |
| intake | `intake.md` exists | [agent] |
| drafting | `spec.md` exists and every template section is filled or has an open point | [human] |
| researching | `research.md` exists and no `fact` open point is left in `spec.md`; not built today, since the grill does research inside its own stage, so it is skipped | [research: RF-2] |
| advocate_walking | not built today: skipped (FR-21) | [research: RF-2] |
| grilling | `nio check spec --gate` passes: no open point, no unconfirmed `[default]` | [human] |
| spec_jury | the spec ledger says approved with `unresolved: 0`, or the human closed it with a reason | [human] |
| arch_grilling | not built today: skipped (FR-21) | [research: RF-2] |
| planning | `nio check plan --gate` passes | [research: RF-6] |
| plan_jury | `nio check plan --approved` exits 0 | [research: RF-6] |
| tasking | `nio check tasks` passes: every AC has a task and every task an AC | [human] |
| tasks_jury | `nio check tasks --approved` exits 0 (the tasks ledger approved, or the human closed it with a reason) | [research: RF-6] |
| implementing | not built today: waits for the human (FR-22) | [human] |

### Decision table: Owning stage
| Changed file (intake.md, research.md, spec.md, architecture.md, plan files, tasks.md) | → Pending change request against it sends the effort to | → Edited after its gate approved it sends the effort to | Src |
| --- | --- | --- | --- |
| intake.md | drafting | ignore | [agent] |
| research.md | grilling | grilling | [research: RF-2] |
| spec.md | grilling | spec_jury | [human] |
| architecture.md | arch_grilling | ignore | [agent] |
| plan files | planning | plan_jury | [human] |
| tasks.md | tasking | tasks_jury | [human] |

## Key entities
- **Effort**: one folder `.nio/specs/<slug>/` and the work on it, from intake to done. [human]
- **state.json**: the committed store of what no other file holds: auto flag, pause reason, waiting-on, task claims and attempts, current run. [human]
- **History line**: one appended line in `history.jsonl` per transition, override, skip, park or resume: who, when, from, to, evidence, run ID, and a reason when the human gave one. [human]
- **Guard**: a deterministic check on files or command results that must pass to leave a stage. [human]

## Non-functional requirements
- **NFR-1** THE SYSTEM SHALL print `nio flow next` in at most 12 lines when the effort is not paused. [agent]
- **NFR-2** THE SYSTEM SHALL answer `nio flow next`, `nio flow status` and `nio flow park` with no model or network call, checked by running them with network access blocked. [human]
- **NFR-3** THE SYSTEM SHALL print `nio flow status` for 20 efforts of 50 history lines each in under 2 seconds, from process start, on the machine that runs the tests. [human]

## Success criteria
- **SC-1** A fresh session with no prior context resumes any non-legacy effort from `nio flow next` alone, without asking the human where things stand. [human]
- **SC-2** Every stage an effort passed can be traced to a history line naming who moved it and on what evidence. [human]
- **SC-3** Each of the four dated past efforts (plan-jury, tasks-stage, implementation-jury, jury-convergence) shows its real stage in `nio flow status` without any hand edit. [derived: FR-47]

## Non-goals
- The `[guess]` tag for defaults the drafter invents for open points, and its harder jury check (Brainstorm Q4). [human]
- Switching auto mode on: `nio flow start --auto`, the `nio:auto` label, and the history line recording the grant (Q8); this spec only reads the flag. [human]
- `nio flow run`, the headless driver loop (Q10), with its refusal of `--human` inside a run (Q12), one-task-at-a-time scheduling (Q15) and the end-of-run report (Q9, Q11). [human]
- Auto-mode jury confirmation of defaults, turning open points into defaults, and the lens for planned-test changes (Q2, Q3, Q7). [human]
- The notify hook (#7); this spec records the waits, stops and done it will fire on. [human]
- The task machine: claims, attempts, the red and green test guards and picking the next ready task ship with the implement stage (#43); `state.json` only keeps room for claims and attempts (Q4). Change request C-261028-xcg6 moves the tasks-stage spec's "#45" to #43 to match (Q17). [human]
- Driving the bug-fix (`lite`) and multi-slice (`epic`) routes; they come with #44 and the epic work (Q5). [human]
- Worktree-based parallel waves and `budgets.parallel` above 1 (Q15). [human]
- Converting legacy effort folders to the layout. [agent]
- Fixing jury gate convergence (#55, #58), done before this spec. [human]

## Glossary
- **Effort**: one spec folder and the work on it, tracked by one flow.
- **Gate**: a stage closed by a jury verdict or the human's approval (spec_jury, plan_jury, tasks_jury); only gates commit.
- **Guard**: a deterministic check that must pass to leave a stage.
- **Override**: the human passing a failing guard with `--human` and a reason.
- **Owning stage**: the stage that writes a file, and the one a change to that file sends the effort back to.
- **Stop list**: the conditions that pause or suspend an auto effort.
- **Legacy**: an effort folder without the layout, shown but never written.

## Risks and evidence against
- Derived state is only as good as the readers of `grill.md`, the ledgers and the change records; a format change in any of them silently changes the stage (issue #45 research comment 2, point F). [agent]
- Every recorded human gate closure so far came from a broken jury tool (#55, #58), so overrides may become routine rather than rare (issue #45 research comment 2, finding 2). [agent]

- An always-human item the drafter didn't flag in `risk:` isn't caught by the flow (Q6). [human]

- The stop list (FR-39 to FR-42, FR-51) is proven only with a fixture auto flag until the auto switch's spec; its first live use is an unattended run. [agent]

## Decisions
- Flow state lives in committed files and anything faster is derived from them: D-261024-ifge (memory, 2026-10-24).
- The stage is derived from the files; `nio flow done` records it (Q1, FR-47): D-261028-4kji.
- A gate commits only when the human asks (`--commit`), or when the auto grant stands in for asking; CLAUDE.md's rule holds (Q2, FR-18, FR-48).
- The round cap, count caps and stuck rule apply only with the auto flag on; manual runs keep the human as the brake (Q3, FR-39 to FR-41).
- The task machine ships with the implement stage (#43), not here (Q4).
- `nio flow` drives full-route specs only; other routes show as unsupported (Q5).
- The always-human list is recognised by the spec's risk flags (money, data-deletion, migration, auth): an auto run waits for the human at every gate (Q6, FR-51).
- A pending change request sends the effort to the stage that writes the file; an approved file edited after its gate sends it to that gate's jury, which re-checks what changed (Q7).
- Abandoned is a separate, human-only, reversible mark: listed last, never moved by changes, resumed by `nio flow start` (Q8).
- Writes to an effort take a lock file (git-ignored); a second writer is refused, a lock older than a minute is taken over (Q9, FR-45, FR-54).
- An approved file edited after its gate goes back to that gate's jury, for the spec, plan and tasks alike (Q7, Q12).
- A gate counts as passed only with its `nio: approve` commit or an override; other stages are read from the files; a rejected round sends the effort back until the files change (Q13, FR-47, FR-55, FR-56).
- Only the human gives `--human`; each override shows until `nio flow seen` (Q14, FR-57).
- History lines carry a hash of `state.json`; a hand edit stops every command (Q15, FR-58).
- In auto mode a failed `done` writes a `fail` line; three matching ones suspend the effort (Q16, FR-41).
- The task machine moves to #43 through change request C-261028-xcg6 on the tasks-stage spec (Q17).
- No slug means the effort with the newest history line; there is no local pointer (Q18, FR-9).
- A torn last history line is cut off and noted; any other damage stops the effort and shows as broken (Q19, FR-59, FR-60).

## Open points
