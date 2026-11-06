# Research: 2026-11-05-parallel-waves

Facts the grill looked up instead of asking.

- **RF-1** Issue #59 (deferred from #45, Q15) names the actors and the journey: the orchestrator claims, workers work in their own worktree, the orchestrator runs each task's guards and calls `nio flow done`; the human resolves conflicts. Today one ready task runs at a time. Source: https://github.com/nikolajkarpic/nio/issues/59: "`nio flow run` runs one ready task at a time, and `budgets.parallel` stays at 1 until this exists."
- **RF-2** `nio` finds its root with `git rev-parse --show-toplevel`, which inside a linked worktree names the worktree, not the project: today a worker in a worktree would write the worktree's own committed copy of `state.json`. Source: src/nio/records.py:53: "return Path(git(".", "rev-parse", "--show-toplevel")[0])"
- **RF-3** The review lists a task's changed paths as the diff from its claim's commit to the working tree; on the main tree after siblings landed, that diff also holds the siblings' commits. Source: src/nio/implement.py:473: "paths = changed(root, mine[0]["evidence"].get("commit") or "HEAD")"
- **RF-4** The guards (red, green and the review's suite) run inside the effort lock, and a second caller gets Busy with "try again". Source: src/nio/flow.py:180: "is being written by another nio flow call (pid {pid} on {host}); try again"
- **RF-5** Claim already refuses on uncommitted changes outside the effort folder. Source: src/nio/implement.py:268: "raise ValueError("uncommitted changes outside the effort folder:""
- **RF-6** The claimed task is kept only in `state.json`'s `claims`, read by the claim guard and by `nio flow next`'s status line. Source: src/nio/flow.py:664: "tid = state["claims"].get("task")"
- **RF-7** `nio check tasks` already refuses two `Parallel: yes` tasks naming the same file unless one depends on the other. Source: src/nio/tasks.py:239: "errs.append(f"parallel clash: {a} and {b} both name `{f}`")"
- **RF-8** A blocked task's changes are saved as `.nio/runs/<run>/T-n.patch` and the paths restored to HEAD by one helper, used by the attempt cap and by `nio flow block`. Source: src/nio/implement.py:357: "def shelve(root, slug, run, tid):"
- **RF-9** A history line's run is the newest run naming the effort, so the claim line of a wave would carry one run for all its tasks. Source: src/nio/flow.py:699: "the newest run whose flow.json names this effort and the stage being left"
- **RF-10** Tests are plain scripts run by `tests.suite`, one `tests/test_*.py` per area; the implement stage's helpers (`impl`, `flow`, `lines`, `state`, `write_test`) live in tests/test_implement.py. Source: .nio/config.json:13: "for f in tests/test_*.py; do uv run python \"$f\" || exit 1; done"
- **RF-11** `budgets.parallel` is read nowhere in the code today. Source: src/nio/implement.py:101: "forced = (records.config(root).get("implement") or {}).get("mode")"
