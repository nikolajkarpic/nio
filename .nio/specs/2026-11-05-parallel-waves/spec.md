---
slug: 2026-11-05-parallel-waves
route: full
epic: ""                         # "<epic slug>/R-<n>" when this is a slice of an epic
risk: [data-deletion]            # a failed review puts the main tree back
retired: [OP-1, OP-2, OP-3, OP-4, OP-5]  # IDs removed from this spec; never reused
---
<!-- Spec template. WHAT and WHY only, never HOW. Every item ends with its provenance: [human] (the grill
confirmed it), [research: RF-n] (a finding in research.md) or [default] (your proposal; the grill must confirm it).
IDs are permanent: number new items after the highest ever used, never renumber, list removed IDs in `retired`.
Remove a section that doesn't apply; never write N/A. `nio check spec 2026-11-05-parallel-waves` checks all of this. -->
# Parallel waves: run `Parallel: yes` ready tasks together, one worktree each

## Summary
Today `nio flow claim` takes one ready task at a time and `budgets.parallel` stays at 1. This lets `nio flow` and the
implement skill run a wave of `Parallel: yes` ready tasks of one epic at once, up to `budgets.parallel`, each worker in
its own git worktree, while `nio flow` stays the single writer of `state.json`. Each task still lands as one commit
`T-n: <title>` on the main tree. It is the smallest change that does this (YAGNI). [human]

## Actors and journeys
- **A-1 Human**: runs an effort and wants independent tasks done sooner; resolves a task that is blocked. [research: RF-1]
- **A-2 Orchestrator**: the implement skill driving `nio flow`; claims waves, dispatches workers, runs guards, calls `nio flow done`. [human]
- **A-3 Worker**: an agent working one task in that task's worktree; never writes `state.json`. [human]

**UJ-1 Run a wave** (A-2, A-3) [research: RF-1]
1. The orchestrator claims; the epic's next ready task and at least one more are `Parallel: yes`, so a wave is claimed.
2. Each worker works its task in its own worktree; red and green run there.
3. As each green arrives, its diff is applied to the main tree, reviewed and committed.
4. When every wave task is done (a blocked one first unblocked by the human), the next claim may open a new wave.
- Misuse: a worker edits a file outside its task's list, or two `Parallel: yes` tasks touch the same file anyway.
- Evidence: #59, #45 (Q15).

## User stories

### US-1 Claim and work a wave in worktrees (P1) [human]
- **Why this priority:** without the wave claim and one worktree per worker nothing runs in parallel.
- **Independent test:** an effort with three ready `Parallel: yes` tasks in one epic and `budgets.parallel` 2: claim
  returns two tasks, each with its own worktree, and red/green for each run in that worktree.

- **AC-1** (FR-1, FR-3) Given an epic whose next ready task and two more ready tasks are `Parallel: yes` and `.nio/config.json` sets no `budgets.parallel`, when the orchestrator claims, then two tasks are claimed as one wave. [human]
  Observable: with ready `Parallel: yes` tasks T-1, T-2, T-3 in that `tasks.md` order, the claim names exactly T-1 and T-2, each with its own mode, and `state.json` marks both as claimed. Level: integration.
- **AC-2** (FR-2) Given `budgets.parallel` is 1, or the epic's next ready task is `Parallel: no`, or it is the only ready `Parallel: yes` task in its epic, when the orchestrator claims, then one task is claimed as today. [human]
  Observable: the claim names one task ID and no worktree exists. Level: integration.
- **AC-3** (FR-4, FR-5) Given a claimed wave, when red and green run for one of its tasks, then each runs the task's command in that task's worktree, made from the effort branch's HEAD at claim time. [human]
  Observable: the worktree exists at `.nio/runs/<run>/worktree`, is detached at the claim-time HEAD, and the command's working directory is that worktree. Level: integration.
- **AC-4** (FR-9) Given a wave with one task done and one still in progress, when the orchestrator claims, then no new wave is claimed. [human]
  Observable: the claim returns no task and `state.json` is unchanged. Level: integration.
- **AC-5** (FR-10) Given a worker in a task's worktree, when it runs `nio flow red` or `nio flow green`, then the project's one `state.json` is written. [human]
  Observable: the project root's `state.json` records the result and no `state.json` appears under the worktree. Level: integration.
- **AC-6** (FR-11) Given one wave task's guard is running, when a second wave task's guard is called, then the second caller gets "try again". [human]
  Observable: while the effort lock is held, the second call exits 1 at once with output containing `is being written by another nio flow call` and `try again`, and its command never runs. Level: integration.
- **AC-11** (FR-12) Given a claimed wave of two tasks, when the implement skill dispatches, then two workers run at once, each in its own task's worktree. [human]
  Observable: the implement skill's steps tell the orchestrator to start one worker per claimed wave task at the same time, each given its task's worktree as its working directory, and to report red and green for each task by its own ID. Level: unit.

### US-2 Land each wave task as one commit (P1) [human]
- **Why this priority:** the work is useless until it is back on the main tree, reviewed, one commit per task.
- **Independent test:** finish green on two wave tasks; the main tree gets two commits `T-n: <title>` in green order.

- **AC-7** (FR-6) Given two wave tasks, when their greens arrive one after the other, then each task's diff, untracked files included, is applied to the main tree, reviewed there and committed as `T-n: <title>`, in green order. [human]
  Observable: `git log` shows one commit per task, titled `T-n: <title>`, in the order the greens arrived, containing the worktree's new and changed files. Level: integration.
- **AC-8** (FR-7) Given a wave task whose diff does not apply to the main tree, when its green arrives, then that task is blocked with its patch kept and the other wave tasks still land. [human]
  Observable: `state.json` shows that task blocked and the effort waiting for the human, its patch file exists, the main tree is unchanged by it, and a sibling's later green still commits. Level: integration.
- **AC-9** (FR-8) Given a wave task whose diff applies but whose review fails, when the review ends, then the main tree is as before the apply and the work stays in the task's worktree. [human]
  Observable: `git status` of the main tree matches the pre-apply state and the worktree still holds the changes. Level: integration.
- **AC-15** (FR-6, FR-7) Given a wave task whose worker also edits a file outside its task's list, or a sibling that changed the same file, when its green arrives, then an outside file is reviewed as today (recorded as outside the task's files) and a clash on the same file is a diff that does not apply (AC-8). [human]
  Observable: the review line's `outside` names the extra file; with a same-file clash the second task is blocked as in AC-8. Level: integration.
- **AC-16** (FR-17) Given a worktree cannot be created for a wave task, when the orchestrator claims, then the claim is refused, nothing is recorded, and no worktree of that claim is left. [agent]
  Observable: exit 1 naming git's error, `history.jsonl` unchanged, `git worktree list` as before. Level: integration.
- **AC-17** (FR-15) Given `budgets.parallel` is 0 or `"two"`, when the orchestrator claims, then the claim is refused naming the value. [agent]
  Observable: exit 1, output naming `budgets.parallel` and the value, `history.jsonl` unchanged. Level: integration.
- **AC-12** (FR-13) Given a wave task, when it is committed or blocked, then its worktree is removed and, when blocked, its patch is kept in its run folder. [human]
  Observable: after the commit or the block, `git worktree list` no longer names the task's worktree and the folder is gone; a blocked task's patch file exists. Level: integration.
- **AC-13** (FR-14) Given the main tree has uncommitted changes outside the effort folder, when a wave task's green arrives, then green is refused before anything is applied and nothing is recorded. [human]
  Observable: the call exits non-zero naming the uncommitted paths, the main tree's files are byte-identical, and `history.jsonl` gains no line. Level: integration.
- **AC-14** (FR-6) Given a sibling wave task landed after this task was claimed, when this task's review runs, then it judges only this task's own changes. [derived: FR-6, RF-3]
  Observable: the review line's `outside` list names none of the sibling's files. Level: integration.
- **AC-10** (FR-16) Given a wave of two tasks that are the last two of their epic, when the first lands, then no epic suite runs; when the second lands, the epic suite runs in the main tree. [human]
  Observable: the first green's review runs no suite; the second green's suite runs at a HEAD that holds the first task's commit and with the second task's changes applied. Level: integration.

## Functional requirements
- **FR-1** WHEN the orchestrator claims AND `budgets.parallel` is above 1 AND the epic's next ready task is `Parallel: yes` AND at least one more ready `Parallel: yes` task is in the same epic THE SYSTEM SHALL claim as one wave the next ready task and the epic's following ready `Parallel: yes` tasks in `tasks.md` order, at most `budgets.parallel` of them, each worked in the mode it is rated (split, single or direct) as today. [human]
- **FR-2** IF the conditions of FR-1 do not all hold THEN THE SYSTEM SHALL claim one task as it does today. [human]
- **FR-3** THE SYSTEM SHALL treat `budgets.parallel` as 2 when `.nio/config.json` does not set it. [human]
- **FR-15** IF `budgets.parallel` is set to anything but a whole number of at least 1 THEN THE SYSTEM SHALL refuse the claim, naming the value, and record nothing. [agent]
- **FR-4** WHEN a wave task is claimed THE SYSTEM SHALL create a detached git worktree for it at `.nio/runs/<run>/worktree` from the effort branch's HEAD at claim time. [human]
- **FR-5** WHEN red or green runs for a wave task THE SYSTEM SHALL run the task's command in that task's worktree. [human]
- **FR-6** WHEN a wave task's green passes THE SYSTEM SHALL apply its worktree diff, untracked files included, to the main tree, run the review there, and commit it as `T-n: <title>`. [human]
- **FR-7** IF a wave task's diff does not apply to the main tree THEN THE SYSTEM SHALL block that task only, keep its patch, and let the rest of the wave go on. [human]
- **FR-8** IF a wave task's review fails THEN THE SYSTEM SHALL put the main tree back as before the apply and leave the work in the task's worktree for the next attempt, the task back at red (direct mode: claimed) as today; at the third attempt the task is blocked and its worktree's changes kept as its patch (FR-13). [human]
- **FR-9** WHILE any task of the last wave is claimed, red or green, or the effort waits for the human on a blocked task, THE SYSTEM SHALL claim nothing new; the other wave tasks' red and green still run. [human]
- **FR-10** WHEN `nio` runs inside a task's worktree THE SYSTEM SHALL resolve to the project root, so `state.json` has one writer. [human]
- **FR-11** THE SYSTEM SHALL run each red, and each green with its apply, review and commit, whole under the effort lock, one at a time, so the main tree holds no task's uncommitted apply once the lock is released; a concurrent caller exits 1 at once, without waiting, with the message `<slug> is being written by another nio flow call (pid <pid> on <host>); try again`. [human]
- **FR-12** WHEN a wave is claimed THE SYSTEM SHALL have the implement skill work every wave task at once, each in its rated mode as today (split: a test-phase then a code-phase worker; single or direct: one worker), every one of its workers in its task's worktree. [human]
- **FR-13** WHEN a wave task is committed or blocked THE SYSTEM SHALL remove its worktree, keeping a blocked task's patch in its run folder. [human]
- **FR-17** IF a wave task's worktree cannot be created THEN THE SYSTEM SHALL refuse the claim, record nothing and remove any worktree that claim made. [agent]
- **FR-16** THE SYSTEM SHALL run the epic suite only for the task whose landing leaves every other task of its epic done, in the main tree after its apply, so the suite sees every task of the epic. [human]
- **FR-14** IF the main tree has uncommitted changes outside the effort folder when a wave task's green arrives THEN THE SYSTEM SHALL refuse the green before applying anything and record nothing. [human]

## Rules
### Decision table: what claim returns
| budgets.parallel (1, >1) | next ready task parallel (yes, no) | other ready parallel tasks in epic (0, ≥1) | last wave open: a task claimed, red or green, or waiting on a blocked one (yes, no) | → claim | Src |
| --- | --- | --- | --- | --- | --- |
| - | - | - | yes | → nothing new | [human] |
| 1 | - | - | no | → one task, as today | [human] |
| >1 | no | - | no | → one task, as today | [human] |
| >1 | yes | 0 | no | → one task, as today | [human] |
| >1 | yes | ≥1 | no | → a wave of up to `budgets.parallel` tasks | [human] |

## Key entities
- **Wave**: the set of `Parallel: yes` tasks of one epic claimed together; open until each is done or blocked. [human]
- **Task worktree**: a detached git worktree per wave task, made from the effort branch's HEAD at claim time. [human]

## Non-goals
- No 3-way merge and no automatic conflict resolution. [human]
- No port or cache isolation for workers' own runs (deferred until it bites). [human]
- No wave across epics. [human]
- No recovery for a wave worker that crashes or times out beyond today's: its task stays claimed until the orchestrator starts a fresh worker for it. [human]

## Glossary
- **Wave**: see Key entities. Never "batch".
- **Main tree**: the project's own working tree on the effort branch, where commits land. Never "parent checkout".

## Decisions
- Worktrees are removed at commit and at block, the patch kept: the recommended option, taken under the human's standing grant in intake.md (grill call Q-A), now FR-13 (2026-11-05).
- Green refuses on a dirty main tree before applying, so the restore never touches the human's changes: the recommended option, taken under the human's standing grant in intake.md (grill call Q-B), now FR-14 (2026-11-05).
- Single-mode workers run red and green themselves through `nio flow`: C-261029-rmbs (change, 2026-10-29).
- Done tasks and their commits survive a change request: D-261029-nayw (decision, 2026-10-29).
- Workers run as one nio-worker card per tier and host: D-261029-ti54 (decision, 2026-10-29).

