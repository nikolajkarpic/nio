---
slug: 2026-10-29-implement-stage
route: full
epic: ""                         # "<epic slug>/R-<n>" when this is a slice of an epic
risk: [external-input, multi-party] # auth | pii | money | external-input | data-deletion | migration | multi-party | public-api
retired: [OP-1, OP-2, OP-3, OP-4, OP-5, OP-6, OP-7, OP-8, OP-9, OP-10, OP-11, OP-12, OP-13, OP-14, OP-15, OP-16, OP-17, OP-18, OP-19] # IDs removed from this spec; never reused
---
<!-- Spec template. WHAT and WHY only, never HOW. Every item ends with its provenance: [human] (the grill
confirmed it), [research: RF-n] (a finding in research.md) or [default] (your proposal; the grill must confirm it).
IDs are permanent: number new items after the highest ever used, never renumber, list removed IDs in `retired`.
Remove a section that doesn't apply; never write N/A. `nio check spec 2026-10-29-implement-stage` checks all of this. -->
# Implement stage: work an epic's approved tasks one at a time through a `nio-worker`, with red and green proven by the CLI, a commit per task on an effort branch, and a hand-off to the epic gate

## Summary
Today an effort that passes its tasks gate stops at implementing and waits for the human, because nothing runs its tasks
(#43, #19). This adds the implement stage: each approved task goes to a fresh `nio-worker` subagent that gets only its
pack (the task, its memory pack, the contracts it binds and the planned tests it must pass), on the model its tier names.
The CLI, not the worker, proves red and green by running the worker's test command, freezes the test at red, reviews each
task with checks only, and commits it as `T-n: <title>` on an effort branch the human merges. A worker that finds the
spec wrong stops and files a change request instead of fixing it silently. A task that fails 3 times goes to the human.
When every task of an epic is done with no new test failures, the epic goes to the epic gate (#29), which is skipped and
reported to the human until it is built. [human]

## Actors and journeys
- **A-1 Human**: owns the project; approved the tasks and their estimate, decides change requests, unblocks stuck tasks, and merges the effort branch. [human]
- **A-2 Orchestrator**: the agent session driving the effort with `nio flow`; claims tasks, starts a worker per task, files the change requests workers report. [research: RF-1]
- **A-3 Worker**: a fresh `nio-worker` subagent that works one task, or one phase of it, from its pack alone, in the way the task's `Mode:` names, and reports back in its handoff; it runs `nio flow` only for `red` and `green` on its own task in single mode. [human]

**UJ-1 Work one task in split mode** (A-2, A-3) [human]
1. The orchestrator claims the next ready task and builds its pack.
2. It starts a fresh test-phase worker on the model the task's tier names, with only that pack.
3. The worker writes the planned test and names its command in its handoff; the orchestrator reports red with that command, and the CLI runs it to prove it fails for the right reason.
4. A fresh code-phase worker writes the code; the orchestrator reports green, and the CLI runs the same command to prove it passes, then reviews the task with checks only.
5. The task is done and committed on the effort branch.
- Misuse: the worker weakens the test after red to get green, or reports "tests pass" without the CLI having run them.
- Evidence: issue #43 and its research comment; spec-kit#75 and its `complex-features.md` on implement degrading as context fills.

**UJ-2 A worker finds the spec wrong** (A-3, A-2, A-1) [human]
1. While working a task, the worker finds that the spec or plan doesn't match what the code shows.
2. It stops, and writes its handoff blocked, with what the spec says, what the code shows, and the smallest change needed.
3. The orchestrator files a change request from it and the task is blocked; the human decides the change.
- Misuse: the worker edits the spec, or bends the code to fit it, and says nothing.
- Evidence: NORTH_STAR ("stop and file a change request, never fix silently", #30); spec-kit#4940.

**UJ-3 Finish an epic** (A-2, A-1) [human]
1. Every task of the epic is done and the full test suite has no failure that wasn't in the baseline.
2. The epic goes to the epic gate; while #29 isn't built the gate is recorded as skipped.
3. The human is notified with the epic report, and the effort moves on to the next epic, or to done after the last.
- Misuse: an epic counts as done while a fix task in it is still open, or with a new failing test.
- Evidence: issue #43 point 4; #42 Q5.

## User stories

### US-1 Each task runs in a fresh worker with only its pack (P1) [human]
- **Why this priority:** a worker drowning in the whole spec folder degrades; this is the hand-off the rest of the stage hangs on.
- **Independent test:** claim a task in a fixture effort and read the pack built for it and the worker start it prints.

- **AC-1** (FR-4) Given T-3 with two `Files:` entries, `Serves: AC-2` and `Test: TC-4`, when T-3 is claimed, then its pack holds the `nio pack` output for its title with `--task T-3`, both paths and `--ac AC-2`, the T-3 block from `tasks.md`, the AC-2 text, the CT-n blocks T-3 binds and the TC-4 entry, and nothing else. [human]
  Observable: the pack's parts are exactly those five; no other part of `spec.md`, `plan.md`, `contracts.md` or `tests.md` appears in it. Level: unit.
- **AC-2** (FR-5, FR-6) Given the shipped agent cards, when `nio agents sync` runs, then a `nio-worker-<tier>` card is rendered for each tier and host. [human]
  Observable: a `nio-worker-<tier>` file exists per tier and configured host; its text tells the worker to work its task, or one phase of it, from its pack, never edit `state.json` or `history.jsonl`, and run no `nio flow` command other than `red` and `green` on its own task in single mode. Level: integration.
- **AC-3** (FR-6, FR-7) Given T-3 with `Tier: cheap` and `Effort: low` on Claude Code, when the orchestrator is told how to start its worker, then it names the cheap worker card and low effort. [human]
  Observable: the start instruction names `nio-worker-cheap`, whose rendered model is the one the config maps `cheap` to on that host, and `low`. Level: unit.
- **AC-4** (FR-3) Given T-4 depends on T-1 and T-1 is not done, when T-4 is claimed, then the claim is refused. [human]
  Observable: non-zero exit naming T-1; `state.json` holds no claim. Level: unit.
- **AC-5** (FR-3) Given T-5 is claimed, when another task is claimed, then the claim is refused. [human]
  Observable: non-zero exit naming T-5 as the current claim; the claim in `state.json` is still T-5. Level: unit.
- **AC-6** (FR-2) Given an effort whose tasks gate passed but has no `nio: approve tasks` commit, when a task is claimed, then the claim is refused. [research: RF-9]
  Observable: non-zero exit naming the missing approval; no history line is added. Level: integration.
- **AC-7** (FR-22) Given uncommitted changes outside the effort folder, when a task is claimed, then the claim is refused and names the files. [human]
  Observable: non-zero exit listing the changed files; no claim is recorded. Level: integration.
- **AC-8** (FR-1) Given an effort whose E-1 has T-1 and T-2 (T-2 depends on T-1) and E-2 has T-3, when tasks are claimed in turn, then they come in the order T-1, T-2, T-3. [human]
  Observable: the next ready task the CLI names after each done is T-2, then T-3. Level: unit.

### US-2 Red and green are proven by the CLI, not claimed (P1) [human]
- **Why this priority:** a worker's "tests pass" is a claim; only commands the CLI runs make a task's status trustworthy.
- **Independent test:** drive one fixture task through red and green with commands that pass, fail and error, and read the history after each.

- **AC-9** (FR-8, FR-10) Given a claimed task, when red runs with `--run` and a command whose test fails on an assertion, then red is accepted and the history line carries the command, its output hash and the frozen test file's hash. [human]
  Observable: exit 0; one history line with those three fields; the task's status reads `red`. Level: unit.
- **AC-10** (FR-8) Given a claimed task, when red runs with a command that exits 0, then red is refused. [human]
  Observable: non-zero exit saying the test passes before the code exists; status stays `claimed`. Level: unit.
- **AC-11** (FR-8) Given a claimed task and a known runner, when red runs with a command whose output shows an import error, a collection error or a syntax error, then red is refused for each. [human]
  Observable: three refusals, each naming the matched error kind; status stays `claimed`. Level: unit.
- **AC-12** (FR-9) Given a claimed task, when red runs with a command of a runner not on the known list that exits non-zero, then red is accepted on the exit code alone. [human]
  Observable: exit 0; the history line notes the runner is unknown. Level: unit.
- **AC-13** (FR-12) Given a red task, when green runs and the recorded command exits 0, then green is accepted and review starts. [human]
  Observable: the history line for green carries the same command as red and its output hash. Level: unit.
- **AC-14** (FR-12) Given a red task, when green runs with `--run` and a different command, then it is refused. [human]
  Observable: non-zero exit naming the command recorded at red; status stays `red`. Level: unit.
- **AC-15** (FR-13, FR-11) Given a red task whose frozen test file changed since red, when green runs, then it is refused; after red runs again and the changed test fails, green is accepted. [human]
  Observable: first green: non-zero exit naming the test file; after the second red, a new history line with the new hash, then green exits 0. Level: unit.
- **AC-16** (FR-14, FR-17) Given the baseline lists `test_a` failing, when a task's review finds `test_a` and `test_b` failing, then the review fails on `test_b` only. [human]
  Observable: the review output names `test_b` as a new failure and not `test_a`; status reads `red` and the attempt count rises by 1, as the state table's green row says for a failed review. Level: unit.
- **AC-17** (FR-15) Given T-3 lists `src/a.py` and the task also changed `src/b.py`, when its review runs, then the review passes and `src/b.py` is recorded. [human]
  Observable: the done history line lists `src/b.py` as outside the task's files. Level: unit.
- **AC-18** (FR-25) Given a task that changed the effort's `spec.md`, when its review runs, then the review fails naming `spec.md`. [human]
  Observable: non-zero exit naming `spec.md`; status is not `done`. Level: unit.
- **AC-19** (FR-16) Given an effort reaching implementing with 2 failing tests, when the stage starts, then the baseline is recorded before any claim. [human]
  Observable: a history line holding both failing tests precedes the first claim line. Level: integration.
- **AC-20** (FR-18) Given a task taken through claim, red, green and done, when `state.json` is read, then it holds no task status. [human]
  Observable: `state.json` holds only the current claim and the attempt count; the status comes from history lines. Level: unit.
- **AC-21** (FR-33) Given a worker's handoff that says all tests pass and no green line in history, when the task's status is read, then it is not green. [research: RF-4]
  Observable: status reads `red`; no history line and no `nio flow status` output contains the handoff text. Level: unit.
- **AC-22** (FR-32) Given a task that is `done`, when red or green runs on it, then each is refused. [human]
  Observable: non-zero exits saying the task is done; no history line is added. Level: unit.
- **AC-23** (FR-26) Given a task that has used 2 attempts, when its next attempt (the third) fails, then it is blocked and the effort waits for the human. [human]
  Observable: status `blocked`; `nio flow next` says `waiting_for_human` and names the task; no further claim is accepted. Level: unit.
- **AC-38** (FR-34) Given a claimed task, when red runs `cargo test` whose output holds `error[E0308]` and exits 101, then red is refused; when red runs `mvn test` that exits 1, then red is accepted as an unknown runner. [human]
  Observable: the first exit is non-zero naming a compile error and status stays `claimed`; the second is exit 0 with the unknown runner noted. Level: unit.
- **AC-39** (FR-39) Given T-1 and T-2 done and committed, and a change request that sends the effort back, when the re-approved `tasks.md` changes only T-2's block and the effort returns to implementing, then T-1 and T-2 stay done and T-2's new version, under a new T-n, is the next task. [human]
  Observable: the effort branch still holds T-1's and T-2's commits; T-1 and T-2 read `done`; the next task named has the next free T-n and T-2's new block. Level: integration.
- **AC-40** (FR-40) Given T-3 with `Mode: direct: config only` and a project config with no `implement.mode`, when the orchestrator is told how to work T-3, then it is told direct; with `implement.mode: split` in config, it is told split. [human]
  Observable: the start instruction names `direct`, then `split`. Level: unit.
- **AC-41** (FR-41) Given T-3 claimed in direct mode, when green runs with `--run` and a command that exits 0, then green is accepted with no red line and review starts; red on T-3 is refused. [human]
  Observable: exit 0; the history holds no red line for T-3; a red report exits non-zero naming direct mode. Level: unit.
- **AC-42** (FR-42) Given T-3 claimed in single mode, when its worker runs `nio flow red` with a command that fails on an assertion, then red is accepted as if the orchestrator had reported it. [human]
  Observable: exit 0; the history line is the same as AC-9's. Level: unit.
- **AC-43** (FR-43, FR-8) Given T-3 whose `Test:` names TC-4 in `tests/test_x.py`, when red runs `pytest tests/test_x.py -k nothing` (no tests ran), and when red runs `test -e src/new.py`, then both are refused. [human]
  Observable: the first refusal says no test ran; the second names `tests/test_x.py` as missing from the command; status stays `claimed`. Level: unit.
- **AC-44** (FR-14) Given a baseline of 40 collected tests and none failing, when a review's suite shows a collection error in another module, and when another review collects 38 tests with none failing, then both reviews fail. [human]
  Observable: the first names the collection error; the second names 38 against the baseline's 40. Level: unit.
- **AC-45** (FR-25) Given a task that changed the effort's `tests.md`, when its review runs, then the review fails naming `tests.md`. [human]
  Observable: non-zero exit naming `tests.md`; status is not `done`. Level: unit.
- **AC-46** (FR-20) Given an effort at implementing whose repo was switched to main, when a task is claimed, then the claim is refused. [human]
  Observable: non-zero exit naming `nio/<slug>` as the branch needed; no claim is recorded. Level: integration.
- **AC-47** (FR-19) Given a pre-commit hook that rejects every commit, when T-3's review passes, then T-3 stays green and the effort waits for the human. [human]
  Observable: no `T-3:` commit and no done line; status `green`; `nio flow next` says `waiting_for_human` with the hook's error. Level: integration.
- **AC-48** (FR-24) Given a blocked handoff for T-3, when the orchestrator files it twice, then one change record exists and the effort waits for the human. [human]
  Observable: one `C-*` record naming T-3; `nio flow next` says `waiting_for_human` naming T-3 and that record. Level: integration.
- **AC-49** (FR-44) Given `tests.timeout` of 1 second, when red runs a command that sleeps 5 seconds, and when red runs a program that doesn't exist, then each is refused and uses an attempt. [human]
  Observable: the first names the time limit, the second the missing program; the attempt count rises by 2; no command is left running. Level: unit.
- **AC-50** (FR-45) Given a direct-mode T-3 that is green, when its review finds a new failure, then T-3 is claimed again with 1 attempt used. [human]
  Observable: status `claimed`; attempt count 1; no red line for T-3. Level: unit.
- **AC-33** (FR-10) Given T-1 and T-2 whose tests both live in `tests/test_x.py` and T-1 is done, when T-2's test phase adds its test to that file and red runs, then red is accepted. [human]
  Observable: exit 0; T-2's red history line holds the new hash of `tests/test_x.py`. Level: unit.
- **AC-34** (FR-35) Given a project whose NIO config has no `tests.suite`, when the implement stage starts, then the effort waits for the human. [human]
  Observable: `nio flow next` says `waiting_for_human` naming `tests.suite`; no baseline line is recorded. Level: unit.
- **AC-35** (FR-36) Given `tests.suite` runs an unknown runner, when its baseline run exits 1 the effort waits for the human, and when it exits 0 and a later review's suite exits 1, then that review fails. [human]
  Observable: first: `waiting_for_human` naming the failing baseline; second: the review names a new failure. Level: unit.
- **AC-36** (FR-38) Given T-3 blocked after 3 attempts with frozen files, when the human runs `nio flow unblock <slug> T-3 --human`, then T-3 is ready with 0 attempts and no frozen files. [human]
  Observable: status `ready`; `state.json` attempt count 0; the next claim's red freezes afresh. Level: unit.
- **AC-37** (FR-37) Given T-3 green whose review finds a new failing test, when the review fails, then T-3 is red again and has used 1 attempt. [human]
  Observable: status `red`; `state.json` attempt count 1; T-3's frozen hashes are unchanged. Level: unit.

### US-3 A worker stops on a spec problem and files a change request (P1) [human]
- **Why this priority:** silently fixing the spec in code is what NIO exists to prevent; the change must reach the human.
- **Independent test:** hand a fixture worker handoff with `status: blocked` to the orchestrator and read the change record and the task status.

- **AC-24** (FR-23) Given the `nio-worker` card, when it is read, then it tells the worker to stop on a spec problem, write its handoff with `status: blocked` and a `change_request:` block, and never edit the spec, plan or tasks. [human]
  Observable: the card names `status: blocked`, the `change_request:` block's three parts, and forbids editing `spec.md`, the plan files and `tasks.md`. Level: unit.
- **AC-25** (FR-24) Given a handoff for T-3 with `status: blocked` and a `change_request:` block, when the orchestrator files it, then a `C-*` record with `outcome: pending` exists holding the three parts and T-3 is blocked. [human]
  Observable: one new change record whose body holds what the spec says, what the code shows and the smallest change; T-3's status reads `blocked`. Level: integration.

### US-4 Each done task is committed on the effort branch (P2) [human]
- **Why this priority:** a commit per task gives the human a reviewable, revertable trail, and main stays untouched until they merge.
- **Independent test:** take a fixture task to done in a git repo and read the branch and the commit.

- **AC-26** (FR-19) Given T-3 titled "Add the red guard", when its review passes, then one commit `T-3: Add the red guard` is made on the effort branch. [human]
  Observable: the newest commit's message is exactly that; it holds the task's changes and the effort's history line; main's HEAD is unchanged. Level: integration.
- **AC-27** (FR-20) Given the repo is on main when the implement stage starts, when the first task is claimed, then the work happens on the effort branch. [human]
  Observable: the current branch is `nio/<slug>`; no commit is added to main. Level: integration.
- **AC-28** (FR-21) Given the last epic of an effort is done, when the stage ends, then the effort branch is not merged. [human]
  Observable: main's HEAD is unchanged; the human is told the branch to merge. Level: integration.

### US-5 An epic finishes and the effort moves on (P1) [human]
- **Why this priority:** without a clear end per epic the stage never hands over, and the effort never reaches done.
- **Independent test:** finish every task of a fixture epic and read what `nio flow next` and the history say.

- **AC-29** (FR-27, FR-28) Given every task of E-1 is done with no new failures and the implementation jury is not built, when the last task is done, then the epic gate is recorded as skipped, the human is notified, and E-2's first ready task is next. [human]
  Observable: a history line `skipped: not built` for E-1's gate; a notice to the human naming E-1; the next task named is in E-2. Level: integration.
- **AC-30** (FR-29) Given E-1 finished with `test_a` failing since the baseline and `src/b.py` changed outside its task's files, when the epic report is shown, then it lists both. [human]
  Observable: the report names `test_a` as a baseline failure and `src/b.py` with its task. Level: unit.
- **AC-31** (FR-30) Given the last epic finishes, when `nio flow next` runs, then the effort is done. [human]
  Observable: `next` and `nio flow status` say `done`. Level: unit.
- **AC-32** (FR-31) Given E-1 whose planned tasks are done and a fix task under its `#### Fixes` heading is not, when the next task is asked for, then it is the fix task and E-1 is not finished. [human]
  Observable: the next task named is the fix task; no epic-gate line for E-1 exists. Level: unit.

## Functional requirements
- **FR-1** WHEN an effort is at implementing THE SYSTEM SHALL work the epics in their `tasks.md` order and, within an epic, one task at a time in dependency order. [human]
- **FR-2** IF the effort has no `nio: approve tasks` commit THEN THE SYSTEM SHALL refuse every claim, as the tasks-stage spec's estimate approval requires (its FR-33, FR-44). [research: RF-9]
- **FR-3** IF a task is claimed while a task it depends on is not done, or while another task is claimed, THEN THE SYSTEM SHALL refuse the claim and name the blocking task. [human]
- **FR-4** WHEN a task is claimed THE SYSTEM SHALL build its worker pack from exactly: `nio pack "<task title>" --task T-n` with `--path` for each `Files:` entry and `--ac` for each `Serves:` AC; the task's block from `tasks.md`; the text of each AC it serves from `spec.md`; the CT-n blocks it binds from `contracts.md`; and the TC-n entries it must make pass from `tests.md`. [human]
- **FR-5** THE SYSTEM SHALL ship `nio-worker` agent cards, each run by the orchestrator as a fresh subagent with only the task's pack, as the task's mode says: split, a test-phase worker then a fresh code-phase worker, with the orchestrator reporting red and green; single, one worker that writes the test, reports red, writes the code and reports green; direct, one worker, with the orchestrator reporting green. The card forbids the worker to edit `state.json` or `history.jsonl`, or to run any other `nio flow` command. [human]
- **FR-40** THE SYSTEM SHALL work each task in the mode its `Mode:` line names (`split`, `single` or `direct`), rated with a reason by the tasks evaluator once change request C-261029-4cev has added that line to the tasks stage, unless the project's NIO config sets `implement.mode`, which then applies to every task. [human]
- **FR-41** WHILE a task's mode is direct THE SYSTEM SHALL skip red and freezing, accept green when the command given with `--run` exits 0, and then review the task as for any other mode; in split and single mode it SHALL refuse green on a claimed task, saying no failing test came first, and in direct mode it SHALL refuse red. [human]
- **FR-42** WHILE a task's mode is single THE SYSTEM SHALL accept red and green reported by its worker, deciding them exactly as when the orchestrator reports them. [human]
- **FR-6** WHEN the orchestrator starts a worker THE SYSTEM SHALL name the `nio-worker-<tier>` card for the task's `Tier:`; `nio agents sync` renders one card per tier for each host, carrying the model that tier maps to there. [human]
- **FR-7** WHEN the orchestrator starts a worker on a host that takes an effort per call THE SYSTEM SHALL name the task's `Effort:`; elsewhere the card's effort applies. [human]
- **FR-8** WHEN red is reported for a claimed task with `--run "<command>"` THE SYSTEM SHALL run the command itself and accept red only when it exits non-zero and its output matches none of the known collection, import or syntax error patterns of that command's test runner, nor that runner's report that no tests ran. [human]
- **FR-9** IF the command's test runner is not on the known list THEN THE SYSTEM SHALL decide red on the exit code alone and note the unknown runner in the history line. [human]
- **FR-10** WHEN red is accepted THE SYSTEM SHALL freeze, until the task is done, the files changed between the claim and the first accepted red, leaving out the effort folder, recording the command, a hash of its output and a hash of each frozen file on the history line; a later task may change them again. [human]
- **FR-11** WHEN red is reported again for a red task THE SYSTEM SHALL prove red again under FR-8 and, when accepted, replace the frozen command and re-hash the same frozen files, never adding a file to them. [human]
- **FR-12** WHEN green is reported for a red task THE SYSTEM SHALL run the command recorded at red, refuse any other command, and accept green only when it exits 0. [human]
- **FR-13** IF a frozen test file's hash differs from the one recorded at red THEN THE SYSTEM SHALL refuse green and name the file until red is proven again. [human]
- **FR-14** WHEN green is accepted THE SYSTEM SHALL review the task with checks only, and no model run: the files changed since the claim, the frozen test files unchanged, and the full test suite with no failure missing from the baseline, no collection or import error, and no fewer tests than the baseline collected. [human]
- **FR-15** WHEN a review finds changed files outside the task's `Files:` list THE SYSTEM SHALL allow them, record each on the task's history line, and list them for the epic gate. [human]
- **FR-16** WHEN the implement stage starts on an effort, before its first claim, THE SYSTEM SHALL run the full test suite and record its failing tests as the baseline on a history line. [human]
- **FR-17** IF a review finds a failing test that the baseline doesn't list THEN THE SYSTEM SHALL fail the review and name each new failure. [human]
- **FR-18** THE SYSTEM SHALL derive each task's status from history lines and keep in `state.json` only the current claim and the attempt count. [human]
- **FR-19** WHEN a task's review passes THE SYSTEM SHALL mark it done and make one commit with the message `T-n: <title>` on the effort branch, the done history line and the commit together; IF the commit fails THEN the task SHALL stay green, with no done line, and the effort SHALL wait for the human, naming git's error. [human]
- **FR-20** WHEN the implement stage starts THE SYSTEM SHALL create or switch to the effort branch `nio/<slug>`; at every claim and before every commit it SHALL refuse unless the current branch is `nio/<slug>`, and SHALL never commit a task on the default branch. [human]
- **FR-21** THE SYSTEM SHALL never merge the effort branch; the human merges it. [human]
- **FR-22** IF a task is claimed while there are uncommitted changes outside the effort folder THEN THE SYSTEM SHALL refuse the claim and list them, so each task's commit holds only its own work. [human]
- **FR-23** WHEN a worker finds that the spec, plan or tasks don't match what the code shows THE SYSTEM SHALL have it stop and write its handoff with `status: blocked` and a `change_request:` block (what the spec or plan says, what the code shows, the smallest change it would need), and never edit the spec, plan or tasks. [human]
- **FR-24** WHEN the orchestrator files a blocked handoff's change request as a `C-*` record THE SYSTEM SHALL set the task to blocked and the effort waiting for the human, naming the task and the record; filing the same handoff again SHALL create no second record. [human]
- **FR-25** IF a task's changes touch the effort's `spec.md`, any plan-stage file (`contracts.md` and `tests.md` included) or `tasks.md` THEN THE SYSTEM SHALL fail its review and name the file. [human]
- **FR-26** WHEN a task has failed 3 attempts THE SYSTEM SHALL set it to blocked and set the effort waiting for the human, naming the task. [human]
- **FR-27** WHEN every task of an epic, fix tasks included, is done and the full suite has no failure missing from the baseline THE SYSTEM SHALL hand the epic to the epic gate. [human]
- **FR-28** WHILE the implementation jury (#29) is not built, WHEN an epic is handed to the epic gate THE SYSTEM SHALL record the gate as `skipped: not built`, notify the human, and move on to the next epic. [human]
- **FR-29** WHEN an epic finishes THE SYSTEM SHALL show the human an epic report listing its done tasks with their commits, the files changed outside each task's list, and the baseline failures still failing. [human]
- **FR-30** WHEN the last epic of an effort finishes THE SYSTEM SHALL move the effort from implementing to done, replacing the flow-state spec's "implement not built" wait (its FR-22). [human]
- **FR-31** THE SYSTEM SHALL work a fix task under an epic's `#### Fixes` heading like any other task of that epic. [human]
- **FR-32** IF red, green or a claim is reported for a task whose state doesn't allow it THEN THE SYSTEM SHALL refuse it, name the task's state, and record nothing, as the state table "Task" says. [human]
- **FR-33** THE SYSTEM SHALL decide red, green and review only from the commands it runs and the files, never from a worker's handoff text. [research: RF-4]
- **FR-34** THE SYSTEM SHALL ship the collection, import, syntax and compile error markers of pytest, unittest, jest, vitest, mocha, go test, cargo test and rspec as its known runners, telling the runner from the command; Maven and Gradle are unknown runners. [human]
- **FR-35** THE SYSTEM SHALL run the full test suite with the command the project's NIO config names as `tests.suite`, and IF it isn't set THEN set the effort waiting for the human, naming that setting, before recording a baseline. [human]
- **FR-36** IF the full suite's runner is unknown THEN THE SYSTEM SHALL require a baseline run that exits 0, set the effort waiting for the human when it doesn't, and treat any non-zero suite exit at review as a new failure. [human]
- **FR-37** THE SYSTEM SHALL count one attempt for the claimed task each time its guard refuses red or green and each time its review fails; a task blocked by a spec problem uses no attempt. [human]
- **FR-39** WHEN a change request sends the effort back from implementing THE SYSTEM SHALL keep its done tasks and their commits on the effort branch; when the effort returns to implementing, only tasks the re-approved `tasks.md` adds or changes run, a changed done task coming back under the next free T-n while the old one stays done. [human]
- **FR-43** WHEN red is reported THE SYSTEM SHALL refuse a command that doesn't name a test file from the TC-n entries of the task's `Test:` line. [human]
- **FR-44** WHEN a command it runs passes the time limit (`tests.timeout` in the project's NIO config, 10 minutes when unset) or its program isn't found THE SYSTEM SHALL stop it and treat it as a refused red or green, or as a failed review for the full suite, naming the cause. [human]
- **FR-45** WHEN a direct-mode task's review fails THE SYSTEM SHALL set it back to claimed, so its next worker reports green again. [human]
- **FR-38** WHEN the human runs `nio flow unblock <slug> T-n --human` THE SYSTEM SHALL set the task ready, reset its attempt count to 0 and drop its frozen files, so its next claim starts at the test phase. [human]

## Rules

### State table: Task (start: pending; final: done)
| State | dependencies done | claim | red accepted | green accepted | review passes | review fails | spec problem filed | attempts used up | human unblocks | direct review fails | commit fails | Src |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| pending | → ready | reject: dependencies not done | reject: not claimed | reject: not claimed | ignore | ignore | reject: not claimed | ignore | ignore | ignore | ignore | [human] |
| ready | ignore | → claimed | reject: not claimed | reject: not claimed | ignore | ignore | reject: not claimed | ignore | ignore | ignore | ignore | [human] |
| claimed | ignore | reject: already claimed | → red | → green | ignore | ignore | → blocked | → blocked | ignore | ignore | ignore | [human] |
| red | ignore | reject: already claimed | → red | → green | ignore | ignore | → blocked | → blocked | ignore | ignore | ignore | [human] |
| green | ignore | reject: already claimed | reject: review pending | ignore | → done | → red | → blocked | → blocked | ignore | → claimed | → green | [human] |
| done | ignore | reject: task is done | reject: task is done | reject: task is done | ignore | ignore | reject: task is done | ignore | ignore | ignore | ignore | [human] |
| blocked | ignore | reject: task is blocked | reject: task is blocked | reject: task is blocked | ignore | ignore | ignore | ignore | → ready | ignore | ignore | [human] |

Modes (FR-41): `red accepted` never happens in direct mode, and `green accepted` on a claimed task happens only in direct mode; `review fails` is the split and single event, `direct review fails` the direct one. [human]

### Decision table: Red
| exit code (zero, non-zero) | runner (known, unknown) | output shows a collection, import or syntax error, or that no tests ran (yes, no) | → red | Src |
| --- | --- | --- | --- | --- |
| zero | - | - | refused: the test passes before the code exists | [human] |
| non-zero | known | yes | refused: the test fails for the wrong reason, or no test ran | [human] |
| non-zero | known | no | accepted | [human] |
| non-zero | unknown | - | accepted on the exit code alone | [human] |

### Decision table: Review
| touches spec, plan files or tasks (yes, no) | frozen test files unchanged (yes, no) | a failure missing from the baseline, a collection or import error, or fewer tests than the baseline (yes, no) | → review | Src |
| --- | --- | --- | --- | --- |
| yes | - | - | fails: the worker edited the spec, plan or tasks | [human] |
| no | no | - | fails: the test changed after red | [human] |
| no | yes | yes | fails: new failures, a broken suite or missing tests | [human] |
| no | yes | no | passes | [human] |

## Key entities
- **Worker pack**: what one worker gets for one task: its memory pack, its `tasks.md` block, the text of the ACs it serves, the CT-n blocks it binds and the TC-n entries it must pass; nothing else. [human]
- **Handoff**: what a worker writes back: its status (`red-ready` with its test command after the test phase, `done` after the code phase, or `blocked`), its evidence, and a `change_request:` block when blocked. [human]
- **Baseline**: the tests failing before the first task of the effort, recorded on a history line. [human]
- **Frozen test file**: a file changed between the claim and the first accepted red, outside the effort folder, kept as a hash on the history line until the task is done. [human]
- **Attempt**: one refused red or green, or one failed review, of a task, counted in `state.json`; the third blocks the task. [human]
- **Effort branch**: `nio/<slug>`, where each done task is committed; the human merges it. [human]
- **Epic report**: what the human gets when an epic finishes: done tasks and commits, files outside each task's list, baseline failures still failing. [human]

## Non-functional requirements
- **NFR-1** THE SYSTEM SHALL claim, prove red and green, review and commit a task with zero model calls of its own, checked by running those steps on fixture tests that need no network, with network access blocked, and by asserting that no model or HTTP client module is loaded in the nio process while they run. [human]

## Success criteria
- **SC-1** Every task marked done traces to history lines with an accepted red (none in direct mode), an accepted green on the same command, a passed review, and its `T-n` commit. [human]
- **SC-2** No worker pack holds anything beyond its task's memory pack, task block, served AC text, CT-n blocks and TC-n entries. [human]
- **SC-3** Every spec problem a worker meets during implementing ends as a change record for the human, never as an edit to the spec, plan or tasks. [human]

## Non-goals
- The implementation jury and evaluation of each epic (#29): the next effort; until then the epic gate is skipped (FR-28). [human]
- The workers' own methods (TDD, builder, test writer, adversarial tester, swarm): an effort of their own later. [human]
- Frontend implementation and browser end-to-end testing (a script opens the app and clicks through it, with screenshots or video as evidence): its own issue (#61), built next. [human]
- Isolated git worktrees per worker, parallel tasks, and cross-host workers (`codex exec`, `agy -p`, #4): tasks run one at a time here. [human]
- Changing the `tasks.md` format beyond the `Mode:` line (C-261029-4cev): the red and green command comes from the worker, not from the task. [human]
- Merging the effort branch into main. [human]
- Building the notify hook (#7); this spec only says when the human is notified, and the orchestrator's message carries the notice until it exists. [research: RF-3]
- Driving the bug-fix (`lite`) and multi-slice (`epic`) routes, which `nio flow` doesn't drive yet. [research: RF-10]

## Glossary
- **Red**: a task's test proven failing, for the right reason, by a command the CLI ran. Never "failing state".
- **Green**: the same command, run by the CLI, exiting 0.
- **Review**: the CLI's checks on a green task; no model reads it.
- **Baseline**: the tests already failing before the stage's first task.
- **Worker**: the `nio-worker` subagent that works one phase of one task. Never "implementer".
- **Test phase**: a worker's run that writes a task's failing test and names the command that runs it.
- **Mode**: how a task is worked: `split` (two workers, test first), `single` (one worker, test first) or `direct` (one worker, no test first).
- **Code phase**: a fresh worker's run that writes the code that makes a red task's test pass.
- **Effort branch**: the branch an effort's task commits go on.
- **Epic gate**: the check an epic passes after its tasks are done; the implementation jury (#29) once built.

## Risks and evidence against
- The CLI runs a shell command a model wrote (`--run`), so a bad or hostile command runs with the human's rights; accepted, since the worker's code already runs with those rights whenever tests run, and every command is recorded in history. [human]
- A worker has a shell, so it could append to `history.jsonl` or run `nio flow unblock --human` itself, and nio can't tell it from the human; accepted, since the human reviews the effort branch's commits before merging. [human]
- With an unknown test runner, red falls back to the exit code, so an import error can pass as red. [human]
- NIO commits per task on its own, where CLAUDE.md says never commit without the human asking; the effort branch and the human's merge are what keep that safe. [human]
- Evidence for small packs: Chroma's "context rot" study (2025) measured accuracy falling as input grows across 18 models; spec-kit's `complex-features.md` splits implementation for the same reason. [human]
- Skipping the epic gate until #29 is built means epics finish on CLI checks alone, with no judgment of the code. [human]

## Decisions
- A task's status is derived from history lines the CLI writes, the same way the flow stage is derived from files: D-261028-4kji (memory, 2026-10-28).
- The task machine (claims, attempts, red and green guards, picking the next task) is built here, not in #45: C-261028-xcg6 (memory, 2026-10-28).
- A task's tier and effort pick the worker's model through each host's config: D-261027-vi67 (memory, 2026-10-27).
- A task's `Test:` line cites the plan's TC-n, which the worker pack carries: D-261028-scwb (memory, 2026-10-28).
- A task is worked in the mode the evaluator rates (split, single or direct), a project setting can force one, and a single-mode worker reports its own red and green: D-261029-rkpb (memory, 2026-10-29); change requests C-261029-4cev (tasks-stage spec) and C-261029-rmbs (flow-state spec).
- Red freezes every file the test phase changed until the task is done, since planned tests share one file (grill Q2, agent, 2026-10-29).
- One `nio-worker-<tier>` card per tier and host, because only Claude Code picks a model per call: D-261029-ti54 (memory, 2026-10-29).
- A failed review sends the task back to red, settling the tasks-stage spec's DF-1 (grill Q10, agent, 2026-10-29).
- Done tasks and their commits survive a change request; only tasks the re-approved `tasks.md` adds or changes run again: D-261029-nayw (memory, 2026-10-29).
- The 3-attempt cap applies whether or not the effort's auto flag is on, unlike the flow's stop list (grill Q9, agent, 2026-10-29).

## Open points
