# Intake

## Source: https://github.com/nikolajkarpic/nio/issues/59

### Flow: run parallel tasks in waves, one git worktree per worker

### What needs designing

Deferred from #45 (brainstorm Q15, 2026-10-28): `nio flow run` runs one ready task at a time, and `budgets.parallel` stays at 1 until this exists.

- **Waves:** every ready task marked `Parallel: yes` (no shared files, which `nio check tasks` enforces) runs together, up to `budgets.parallel`, as Kiro does.
- **Worktree adapter:** each worker gets its own git worktree (NORTH_STAR, Cross-host runs). Open: how its diff is merged back, and who resolves a conflict.
- **Single writer:** workers still never touch `state.json`. The orchestrator runs each task's guards in that task's worktree, then calls `nio flow done T-n`.
- **Build pressure:** parallel test runs share caches and ports (a reported Ralph-loop failure). Open: run each wave's tests one at a time, or isolate them.

### Open questions: brainstorm all of these before implementing
- Merge strategy and conflict handling for worktree diffs.
- Whether the guards run in the worktree or after the merge.
- Default `budgets.parallel` on the $100 Claude and $20 Antigravity plans.

Refs: #45 (Q15, research comments 1 and 3) · #43

## Source: https://github.com/nikolajkarpic/nio/issues/59#issuecomment-6670875417 (the human's decisions, taken under their autonomy grant)

Brainstorm decisions (taken under the human's standing autonomy grant: the recommended, simplest option each time).

1. **Merge strategy and conflicts.** Each wave task works in its own detached git worktree at `.nio/runs/<run>/worktree`, made from the effort branch's HEAD at claim time. At green, `nio flow` applies the worktree's diff (`git diff HEAD --binary`, untracked files included) to the main tree with `git apply`, then reviews and commits it as `T-n: <title>` as today, so tasks land one commit each, in the order their greens arrive (the effort lock serialises them). A diff that doesn't apply blocks that task only (its patch kept, like the attempt cap does) and the effort waits for the human; the rest of the wave goes on. No 3-way merge, no auto-resolve: `Parallel: yes` tasks already share no files (`nio check tasks`), so a conflict means something went wrong.
2. **Where the guards run.** Red and green run the task's command in the task's worktree. The review (plan-file edits, frozen test files, files outside the list, the epic suite) runs in the main tree after the apply, so the epic-closing task's suite sees every sibling's commit. A failed review puts the main tree back and leaves the work in the worktree for the next attempt.
3. **Default `budgets.parallel`: 2.** Small enough for the $100 Claude and $20 Antigravity plans (two workers at once), raise it in `.nio/config.json`. `1` turns waves off. A wave is claimed only when the epic's next ready task is `Parallel: yes` and at least one more ready `Parallel: yes` task sits in the same epic; otherwise `claim` works as today.
4. **Build pressure.** The guard commands (red, green, the epic suite) already run inside the effort lock, so a wave's guards run one at a time; a second caller gets "try again". No port or cache isolation for the workers' own runs (deferred until it bites).

Also: `nio` run from inside a task's worktree resolves to the project root, so a single-mode worker's `nio flow red/green` still writes the one `state.json` (single writer). A new wave is claimed only once every task of the last one is done or blocked.

## Human, 2026-11-05

> Keep it lean (YAGNI): smallest change that lets `nio flow` + the implement skill run a wave of `Parallel: yes` ready tasks concurrently, each worker in its own worktree, single writer of state preserved.

## Human, 2026-11-05 (the standing grant, relayed by the orchestrator)

> The human has given full autonomy: never ask them anything; whenever a decision is open, take the recommended option and record it.
