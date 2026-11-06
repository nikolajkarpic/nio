# Research: 2026-11-05-parallel-waves

Facts the grill looked up instead of asking.

- **RF-1** Issue #59 (deferred from #45, Q15) names the actors and the journey: the orchestrator claims, workers work in their own worktree, the orchestrator runs each task's guards and calls `nio flow done`; the human resolves conflicts. Today one ready task runs at a time. Source: https://github.com/nikolajkarpic/nio/issues/59: "`nio flow run` runs one ready task at a time, and `budgets.parallel` stays at 1 until this exists."
- **RF-2** `nio` finds its root with `git rev-parse --show-toplevel`, which inside a linked worktree names the worktree, not the project: today a worker in a worktree would write the worktree's own committed copy of `state.json`. Source: src/nio/records.py:53: "return Path(git(".", "rev-parse", "--show-toplevel")[0])"
- **RF-3** The review lists a task's changed paths as the diff from its claim's commit to the working tree; on the main tree after siblings landed, that diff also holds the siblings' commits. Source: src/nio/implement.py:473: "paths = changed(root, mine[0]["evidence"].get("commit") or "HEAD")"
- **RF-4** The guards (red, green and the review's suite) run inside the effort lock, and a second caller gets Busy with "try again". Source: src/nio/flow.py:180: "is being written by another nio flow call (pid {pid} on {host}); try again"
- **RF-5** Claim already refuses on uncommitted changes outside the effort folder. Source: src/nio/implement.py:268: "raise ValueError("uncommitted changes outside the effort folder:""
