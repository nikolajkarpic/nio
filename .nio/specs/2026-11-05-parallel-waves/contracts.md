---
slug: 2026-11-05-parallel-waves
retired: []                      # CT IDs removed from this plan; never reused
---
# Contracts: parallel waves

## Contracts

### CT-1 Claim a wave (FR-1, FR-2, FR-3, FR-9, FR-15) [default]
- Binding: `src/nio/implement.py:claim` (existing)
- Kind: cli
- Shape: `nio flow claim <slug> --by "<role> / <host> / <model>"`; a new helper `wave(root, slug, lines, first) -> [task, ...]` in the same file, and `tasks_of` gains `parallel: bool`
- Accepts: `budgets.parallel` from the merged NIO config, 2 when unset (FR-3); each task's `Parallel:` field, read as `parallel: True` only for `yes` [research: RF-7]
- Returns:
  - one task: the five lines printed today (`task:`, `mode:`, `card:`, `effort:`, `pack:`), one `claim` line, `claims: {"task": "T-n"}`;
  - a wave: the same five lines per task, in `tasks.md` order, each followed by `worktree: .nio/runs/<run>/worktree`; one `claim` line per task, each with `evidence.worktree` naming its worktree; `claims: {"task": <first>, "wave": [<ids in order>]}` [agent]
- Fails: `budgets.parallel` is not an int of at least 1 (a bool counts as not an int) → exit 1, `budgets.parallel must be a whole number of at least 1, not <value>`, nothing written (FR-15); `claims` not empty → exit 1, `<T-n> is claimed`, as today (FR-9)
- Rules: "claim as one wave the next ready task and the epic's following ready `Parallel: yes` tasks in `tasks.md` order, at most `budgets.parallel` of them, each worked in the mode it is rated (split, single or direct) as today" (FR-1)
- Rules: "IF the conditions of FR-1 do not all hold THEN THE SYSTEM SHALL claim one task as it does today." (FR-2)
- Rules: a wave task leaves `claims` only when it is committed or blocked, through a new `release(claims, tid) -> claims` in the same file: `tid` is dropped from `wave`, `task` moves to the first ID left, and `{}` is returned once none is left or when `claims` has no `wave` (today's single claim). `commit`, `attempt` and `block` call it where they write `"claims": {}` today, so a sibling's claim survives (FR-9) [derived: FR-9]
- Rules: while any task of the effort is `blocked`, claim refuses with exit 1, `<T-n> is blocked: nio flow unblock <slug> <T-n> --human "<reason>" --by human`, nothing written, so a second blocked sibling still holds the next claim after the first is unblocked (FR-9) [derived: FR-9]
- Rules: the wave skips a `Parallel: no` task that sits between `Parallel: yes` ones: "the epic's following ready `Parallel: yes` tasks" (FR-1) [derived: FR-1]
- State: follows the spec's decision table "what claim returns"

### CT-2 A worktree per wave task (FR-4, FR-13, FR-17) [default]
- Binding: `src/nio/implement.py:worktree` (new)
- Like: `src/nio/implement.py:run_of`
- Kind: function
- Shape: at claim, `git worktree add --detach .nio/runs/<run>/worktree <HEAD at claim>` per wave task, `<run>` being that task's own run; `worktree(root, lines, tid) -> Path | None`, the absolute worktree its latest claim line names, None when it names none or the folder is gone; removal is `git worktree remove --force <path>`
- Accepts: the claim-time HEAD of the effort branch (the `commit` the claim line already records)
- Returns: a detached worktree at that HEAD; `.nio/runs/` is gitignored, so the main tree's `git status` doesn't list it [research: RF-9]
- Fails: `git worktree add` fails for any wave task → the worktrees made so far by this claim are removed, exit 1 with `can't create a worktree for <T-n>: <git's error>`, no line written (FR-17)
- Rules: "WHEN a wave task is committed or blocked THE SYSTEM SHALL remove its worktree, keeping a blocked task's patch in its run folder." (FR-13); the patch goes to the run its worktree lives in [agent]
- Rules: the run folders and packs a refused claim made before the failing worktree stay as scratch (`.nio/runs/` is never committed), and a first claim's switch to `nio/<slug>` stays; only worktrees are removed (FR-17) [agent]
- Rules: removal is forced: files the worktree's `.gitignore` hides (build output, caches) are not in the patch and are lost with it [agent]

### CT-3 Red and green run in the task's worktree (FR-5, FR-11) [default]
- Binding: `src/nio/implement.py:red` (existing)
- Kind: cli
- Shape: `green` in the same file changes likewise; `nio flow red <slug> T-n --run "<command>" --by ...`, `nio flow green <slug> T-n [--run "<command>"] --by ...`, unchanged
- Accepts: a task whose latest claim names a worktree: the command runs with that worktree as its working directory, and red's frozen files and their hashes, and green's frozen check, are read there; a task without one runs in the main tree as today
- Returns: as today
- Fails: as today; a concurrent call exits 1 at once with "`<slug> is being written by another nio flow call (pid <pid> on <host>); try again`" [research: RF-4]
- Rules: "THE SYSTEM SHALL run each red, and each green with its apply, review and commit, whole under the effort lock, one at a time, so the main tree holds no task's uncommitted apply once the lock is released" (FR-11)

### CT-4 Land a wave task's green on the main tree (FR-6, FR-7, FR-8, FR-14, FR-16) [default]
- Binding: `src/nio/implement.py:land` (new)
- Like: `src/nio/implement.py:shelve`
- Kind: function
- Shape: `land(root, slug, tid, tree, since) -> (patch path, {path: bytes or None}, git's error or "")`, called by `green`; the dict is a snapshot of each path the patch touches, taken in the main tree just before the apply (None: the file didn't exist); `restore(root, saved)` writes each back (deleting a None one)
- Accepts: a wave task's worktree and its claim commit `since`
- Returns: in the worktree, `git add -A` then `git diff --cached --binary <since>` saved as `.nio/runs/<run>/T-n.patch`; `git apply --binary` of it in the main tree, leaving out the effort's `state.json` and `history.jsonl` (they are never in the snapshot either); the snapshot
- Fails:
  - the main tree has uncommitted changes outside the effort folder → exit 1 `uncommitted changes outside the effort folder:` and the paths, before the command runs, nothing written (FR-14);
  - `git apply` fails → a `blocked` line `cause: apply` with the patch, the task released from `claims`, `waiting` set to `<T-n> blocked: its changes don't apply`, its worktree removed, the main tree untouched (FR-7);
  - the review fails → `restore(root, saved)` puts each path back to its bytes before the apply, so an uncommitted edit in the effort folder survives, then the attempt is counted as today with the worktree as the tree to shelve (CT-7) (FR-8);
  - the commit fails → `commit` puts history, state and the index back as today, then `restore(root, saved)`; the task stays green as today and a retry applies again;
  - `nio flow` itself dies between the apply and the commit → the applied files stay uncommitted in the main tree and the next green is refused by the dirty-tree check naming them; the patch is still in `.nio/runs/<run>/T-n.patch`, and the human puts the tree back with `git apply -R <that patch>` (the spec's non-goal on crashes) [agent]
- Rules: "WHEN a wave task's green passes THE SYSTEM SHALL apply its worktree diff, untracked files included, to the main tree, run the review there, and commit it as `T-n: <title>`." (FR-6)
- Rules: "THE SYSTEM SHALL run the epic suite only for the task whose landing leaves every other task of its epic done, in the main tree after its apply, so the suite sees every task of the epic." (FR-16): `closes` already decides this from task states, and the review runs after the apply
- Rules: on success the worktree is removed and the task released from `claims` (FR-13, CT-1)
- Rules: only overlapping edits fail to apply: two tasks editing different hunks of one file both land, the second's review recording that file as outside its list (AC-15) [derived: AC-15, FR-7]

### CT-5 The review judges only the task's own changes (FR-6) [default]
- Binding: `src/nio/implement.py:review` (existing)
- Kind: function
- Shape: `review(root, slug, task, lines)`, unchanged
- Accepts: for a wave task, its changed paths are those between HEAD and the main tree after the apply, not those since its claim commit, so a sibling's landed commit is not in them [research: RF-3]
- Returns: the review line as today; its `outside` names no sibling file

### CT-6 nio inside a task's worktree resolves to the project root (FR-10) [default]
- Binding: `src/nio/records.py:repo_root` (existing)
- Kind: function
- Shape: `repo_root() -> Path`
- Returns: git's top level, except when that is `<root>/.nio/runs/<run>/worktree`: then `<root>` [research: RF-2]
- Rules: any other linked worktree (the human's own) stays its own root [agent]

### CT-7 Attempts and blocks shelve from the worktree (FR-8, FR-13) [default]
- Binding: `src/nio/implement.py:shelve` (existing)
- Kind: function
- Shape: `shelve(root, slug, run, tid, tree=root)`; `attempt` and `block` pass the task's worktree when it has one
- Accepts: for a wave task, its worktree as `tree`: the patch is that tree's changes, saved in the main tree's run folder [research: RF-8]
- Returns: at the third attempt, or on `nio flow block`, the patch kept, the task released from `claims` (its siblings stay), its worktree removed
- Rules: "at the third attempt the task is blocked and its worktree's changes kept as its patch (FR-13)" (FR-8)

### CT-8 The implement skill dispatches a wave at once (FR-12) [default]
- Binding: `skills/implement/SKILL.md` (existing)
- Kind: file
- Shape: the opening lines, steps 1, 2, 5 and 6 and "When to stop" of the skill; and the worker card `src/nio/agents/worker.md` (existing), whose single-mode lines tell the worker to run `nio flow red`/`green` again after a few seconds on `try again`, not to report it as a refusal
- Rules: while a wave is open, a claim refused with `is claimed` means wait for the other wave workers, not stop; the orchestrator claims again only once every wave task is done or blocked [derived: FR-9]
- Rules: "WHEN a wave is claimed THE SYSTEM SHALL have the implement skill work every wave task at once, each in its rated mode as today (split: a test-phase then a code-phase worker; single or direct: one worker), every one of its workers in its task's worktree." (FR-12); a `try again` from `nio flow` is retried, not counted as a refusal [derived: FR-11]
