# Grill log: 2026-11-05-parallel-waves

Append-only. One entry per question, below-the-bar call or derived item.

## Session 1 · 2026-11-05 · @nio:grill, delegated to an agent (the human's standing autonomy grant)

The brainstorm decisions on #59 (intake) settled meaning, actors, data and state, failure and conflict, and the change from today.

## Facts · OP-1, OP-4, OP-5 · 2026-11-05
Facet: actors (OP-1), change (OP-4), verification (OP-5)
Found: RF-1 to RF-5 (research.md).
Patched: A-1, UJ-1 to [research: RF-1]; AC-14 derived from FR-6 and RF-3; retired OP-1, OP-4, OP-5

## Call · OP-2 · 2026-11-05
Question: When is a task's worktree removed?
Options:
1. At commit and at block, the patch kept in the run folder (recommended)
2. Never by nio: the human prunes
3. At abandon too
Answer: 1. At commit and at block, the patch kept in the run folder: no stale worktrees pile up and a blocked task's work survives as its patch, as the attempt cap already does. [agent]
Below the bar: changes what a user can do: no; sees: no; who may: no; data kept or changed: no (the patch keeps the work); cost: no.
Patched: FR-13, AC-12; retired OP-2

## Call · OP-3 · 2026-11-05
Question: If the main tree has uncommitted changes when a wave task's green arrives, may the restore touch them?
Options:
1. Refuse the green before applying, record nothing (recommended)
2. Apply anyway and restore only the task's paths
3. Stash the human's changes
Answer: 1. Refuse the green before applying, record nothing: the human's changes are never touched, like claim already refuses (RF-5). [agent]
Below the bar: changes what a user can do: no; sees: no; who may: no; data kept or changed: no (it protects it); cost: no.
Patched: FR-14, AC-13; retired OP-3

## Session 2 · 2026-11-06 · spec jury round 1 fixes, delegated to an agent (the human's standing autonomy grant)

Q-A is the call logged above on OP-2 (now FR-13), Q-B the call on OP-3 (now FR-14).

## Call · J-4, J-9 · FR-9 · 2026-11-06
Question: Does a blocked wave task hold the next claim?
Options:
1. Yes: the effort waits for the human; the other wave tasks' red and green still run (recommended)
2. No: a new wave opens over it
Answer: 1. Yes: the effort waits for the human until they unblock it, as a block does today; the rest of the wave still lands. [agent]
Patched: FR-9, UJ-1 step 4, decision table header; non-goal on crashed workers

## Call · J-5 · FR-11 · 2026-11-06
Question: What does the effort lock cover in a wave?
Options:
1. Each red, and each green with its apply, review and commit, whole (recommended): no task's apply is left uncommitted when the lock is released, so FR-14 sees only the human's changes
2. Only the guard commands
Answer: 1. As today's `nio flow green` already does (RF-4). [agent]
Patched: FR-11, AC-6

## Call · J-6 · FR-16 · 2026-11-06
Question: Which green runs the epic suite in a wave?
Options:
1. The one whose landing leaves every other task of the epic done (recommended): it lands last, so the suite sees every task
2. Keep epic-closing tasks out of waves
Answer: 1. The last to land runs it, after its apply, in the main tree. [agent]
Patched: FR-16, AC-10

## Call · J-2, J-12 · FR-1, FR-15 · 2026-11-06
Question: Which tasks form a wave, in which mode, and what does a bad `budgets.parallel` do?
Options:
1. The next ready task, then the epic's following ready `Parallel: yes` tasks in tasks.md order, each in its rated mode; a value that isn't a whole number of at least 1 is refused (recommended)
2. Only split-mode tasks join a wave; a bad value counts as 1
Answer: 1. [agent]
Patched: FR-1, FR-15, AC-1, AC-17

## Call · J-9 · AC-15, FR-17 · 2026-11-06
Question: What happens on the journey's misuse and when a worktree can't be made?
Options:
1. Outside files are reviewed as today; a same-file clash is a diff that doesn't apply (FR-7); a worktree git can't make refuses the claim and records nothing (recommended)
2. Leave them unstated
Answer: 1. [agent]
Patched: AC-15, AC-16, FR-17

## Call · J-7 · FR-8 · 2026-11-06
Question: What does a failed wave review leave, and at the third attempt?
Options:
1. The task back at red (direct: claimed) with its worktree; the third attempt blocks it and keeps the worktree's changes as its patch (recommended)
Answer: 1. As the attempt cap does today. [agent]
Patched: FR-8

## Call · J-13, J-14 · FR-13, FR-14 · 2026-11-06
Question: Keep the dirty-tree refusal and the worktree removal the grill added?
Options:
1. Keep both (recommended): the refusal is the only thing stopping a failed review's restore from touching the human's own uncommitted work (the spec's data-deletion risk); removal keeps `git worktree list` from filling with finished tasks
2. Cut both: less to build; the human's uncommitted changes can be lost on a failed review, and worktrees pile up
Answer: 1. Keep both, under the human's standing autonomy grant to take the recommended option. [agent]
Patched: none
