---
slug: 2026-11-05-parallel-waves
retired: []                      # TC IDs removed from this plan; never reused
---
# Tests: parallel waves

Fixtures: every test below lives in a new plain script `tests/test_waves.py` (run by `tests.suite` like the others,
research RF-10). It imports `impl`, `flow`, `lines`, `state`, `commit_all` and `git` from `tests/test_implement.py` and
adds:
- **`waves(n=2, modes=None, parallel=None, cfg=None)`** returns a repo at implementing, built with `impl(tasks=..., cfg=cfg)`.
  - Its `tasks.md` has epic `## E-1 Wave (US-1)` with tasks T-1 to T-n, then epic `## E-2 Later (US-2)` with one task T-9 (`Depends on: T-1`, `Parallel: no`, `Files: z.py`).
  - Task T-k has `Files: `mk.py`, `mk_new.py``, `Serves: AC-1`, `Test: TC-1`, `Depends on: none`, `Tier: cheap: x`, `Effort: low`, `Parallel: <parallel.get("T-k", "yes")>`, `Mode: <modes.get("T-k", "direct")>: x`.
  - Before the tasks are approved it commits an empty `app.py`, `shared.py` holding `x = 0\n`, and `mk.py` holding `v = 0\n` for each k.
- **`wt(out, tid)`** returns the absolute `Path` of the `worktree:` line that follows `task: <tid> ` in a claim's output.
- **`work(root, out, tid)`** stands for a direct worker: in `wt(out, tid)` it writes `mk.py` as `v = 1\n` and a new `mk_new.py` as `w = 1\n` (k is the task's number).
- **`land(root, tid)`** is `flow(root, "green", S, tid, "--run", "true")`.

## Acceptance tests

### TC-1 a wave of two is claimed by default (AC-1; integration) [default]
- File: `tests/test_waves.py:test_ac1_claims_a_wave_of_two` (new)
- Covers: CT-1
- Setup: `waves(n=3, modes={"T-1": "split"})`; the config sets no `budgets.parallel`.
- Action: `flow(root, "claim", S)`.
- Assert: exit 0; the output has exactly two `task:` lines, `task: T-1 ` then `task: T-2 `, and none for T-3; the `mode:` line after T-1's is `mode: split` and after T-2's is `mode: direct`; each task's block has a `worktree: .nio/runs/` line; `state(root)["claims"] == {"task": "T-1", "wave": ["T-1", "T-2"]}`; the history's last two lines are `claim` lines for T-1 and T-2. In a second fresh repo, `waves(n=3, parallel={"T-2": "no"})`, the claim's `task:` lines are `T-1` then `T-3` (a `Parallel: no` task in between is skipped) and `claims["wave"] == ["T-1", "T-3"]`.

### TC-2 one task is claimed when a wave can't form (AC-2; integration) [default]
- File: `tests/test_waves.py:test_ac2_one_task_when_no_wave` (new)
- Covers: CT-1
- Setup: three fresh repos: `waves(n=3, cfg={"budgets": {"parallel": 1}})`; `waves(n=3, parallel={"T-1": "no"})`; `waves(n=3, parallel={"T-2": "no", "T-3": "no"})`.
- Action: `flow(root, "claim", S)` in each.
- Assert: in each, exit 0, exactly one `task:` line, `task: T-1 `, no `worktree:` line, `state(root)["claims"] == {"task": "T-1"}`, and `git worktree list` prints one line (the main tree).

### TC-3 red and green run in the task's worktree (AC-3; integration) [default]
- File: `tests/test_waves.py:test_ac3_red_and_green_run_in_the_worktree` (new)
- Covers: CT-2, CT-3
- Setup: `waves(modes={"T-1": "split"})`; `head` is `git rev-parse HEAD`; claim; `w1 = wt(out, "T-1")`, `w2 = wt(out, "T-2")`; `log` is a temp file outside the repo. In `w1` write `tests/test_refund.py` as `test_implement.write_test` writes it.
- Action: `flow(root, "red", S, "T-1", "--run", f"pwd >> {log}; python -m unittest tests/test_refund.py")`; then `work(root, out, "T-2")` and `flow(root, "green", S, "T-2", "--run", f"pwd > {log}2")`.
- Then: in `w1` append `# edited\n` to `tests/test_refund.py` and run `flow(root, "green", S, "T-1")`.
- Assert: red exits 0 with `red: T-1 accepted` and its output lists `  tests/test_refund.py` after `frozen:`; the history's `red` line has `frozen` with the key `tests/test_refund.py` and that file's sha256 in `w1`; the green after the edit exits 1 with `tests/test_refund.py changed since red`; the first line of `log` is `w1` (resolved); the main tree has no `tests/test_refund.py`; `w1` is under `.nio/runs/` and ends in `/worktree`; `git -C w1 rev-parse HEAD` equals `head` and `git -C w1 symbolic-ref -q HEAD` exits non-zero (detached); `log2` holds `w2` (resolved).

### TC-4 no new claim while a wave task is open (AC-4; integration) [default]
- File: `tests/test_waves.py:test_ac4_no_claim_while_the_wave_is_open` (new)
- Covers: CT-1
- Setup: `waves(n=3, cfg={"budgets": {"parallel": 2}})`; claim; `work(root, out, "T-1")`; `land(root, "T-1")` exits 0. Save `state.json`'s bytes and the history's line count.
- Action: `flow(root, "claim", S)`.
- Assert: exit 1; the output contains `T-2 is claimed` and no `task:` line; `state.json`'s bytes and the history's line count are unchanged; `state(root)["claims"] == {"task": "T-2", "wave": ["T-2"]}`.

### TC-5 nio in a worktree writes the project's one state (AC-5; integration) [default]
- File: `tests/test_waves.py:test_ac5_nio_in_a_worktree_writes_the_root_state` (new)
- Covers: CT-6, CT-3
- Setup: `waves(modes={"T-1": "single"})`; claim; `w1 = wt(out, "T-1")`; write the failing test into `w1` as in TC-3.
- Action: `test_flow.cli(w1, "red", S, "T-1", "--run", "python -m unittest tests/test_refund.py", "--by", "worker / test / test")`, run with `w1` as its working directory.
- Assert: exit 0; the root's history ends with a `red` line for T-1; `git -C w1 status --porcelain -- .nio/specs` prints nothing (no `state.json` or `history.jsonl` written under the worktree); `records.repo_root()` called with the working directory set to `w1` returns the root (resolved), and called in a plain linked worktree made with `git worktree add <tmp>/other` returns `<tmp>/other`.

### TC-6 a second guard while one runs gets "try again" (AC-6; integration) [default]
- File: `tests/test_waves.py:test_ac6_second_guard_is_told_to_try_again` (new)
- Covers: CT-3
- Setup: `waves()`; claim; `work(root, out, "T-2")`; `marker` is a temp path outside the repo.
- Action: inside `with nio_flow.lock(root, S):` (the first guard holding the lock), time `flow(root, "green", S, "T-2", "--run", f"touch {marker}")`.
- Assert: exit 1 in under 5 seconds; the output contains `is being written by another nio flow call` and `try again`; `marker` does not exist; the history's line count is unchanged. A regression guard: today's lock already does this, and the wave must keep it.

### TC-7 wave tasks land one commit each, in green order (AC-7; integration) [default]
- File: `tests/test_waves.py:test_ac7_each_task_lands_as_one_commit_in_green_order` (new)
- Covers: CT-4
- Setup: `waves()`; claim; `work(root, out, "T-1")`; `work(root, out, "T-2")`.
- Action: `land(root, "T-2")`, then `land(root, "T-1")`.
- Assert: both exit 0 with `done: T-2` and `done: T-1`; `git log -2 --format=%s` is `T-1: <T-1's title>` then `T-2: <T-2's title>` (newest first); `git show --name-only --format= HEAD~1` lists `m2.py` and `m2_new.py` and not `m1.py`; `HEAD` lists `m1.py` and `m1_new.py`; the main tree's `m2_new.py` reads `w = 1\n`.

### TC-8 a diff that doesn't apply blocks only its task (AC-8; integration) [default]
- File: `tests/test_waves.py:test_ac8_a_clash_blocks_only_its_task` (new)
- Covers: CT-4, CT-2
- Setup: `waves(n=3, cfg={"budgets": {"parallel": 3}})`; claim; `work` each of T-1, T-2, T-3; in `wt(out, "T-1")` write `shared.py` as `x = 1\n`, in `wt(out, "T-2")` as `x = 2\n`; `land(root, "T-1")` exits 0.
- Action: `land(root, "T-2")`, then `land(root, "T-3")`.
- Assert: T-2's call exits 1 and its output contains `T-2 blocked: its changes don't apply`; `implement.status(root, S, lines(root))["T-2"] == "blocked"`; `state(root)["waiting"]["task"] == "T-2"`; the history's `blocked` line for T-2 has `cause: apply` and a `patch` naming a file that exists and contains `x = 2`; the main tree's `shared.py` reads `x = 1\n` and `m2_new.py` doesn't exist; T-3's call exits 0 with `done: T-3`, and `git log -1 --format=%s` starts `T-3: `; `git worktree list` names neither `wt(out, "T-2")` nor `wt(out, "T-3")`, and neither folder exists.

### TC-9 a failed review puts the main tree back (AC-9; integration) [default]
- File: `tests/test_waves.py:test_ac9_failed_review_restores_the_main_tree` (new)
- Covers: CT-4
- Setup: `waves()`; claim; `work(root, out, "T-1")`; in `wt(out, "T-1")` append `x\n` to `.nio/specs/<S>/spec.md`; in the main tree, uncommitted, put `# mine\n` before the first line of the same `spec.md` (an edit the patch's hunk doesn't overlap). Save `git status --porcelain` of the main tree and the bytes of its `spec.md` and `m1.py`.
- Action: `land(root, "T-1")`.
- Assert: exit 1; the output contains `review: failed` and `the task edited spec.md`; the main tree's `git status --porcelain` lines outside `.nio/specs/<S>/state.json` and `history.jsonl` equal the saved ones, and its `spec.md` and `m1.py` bytes are unchanged; `m1_new.py` is absent from the main tree; the worktree still holds `m1_new.py` and the appended `spec.md`; `implement.status(...)["T-1"] == "claimed"` (direct mode).

### TC-10 the epic suite runs only for the last task to land (AC-10; integration) [default]
- File: `tests/test_waves.py:test_ac10_suite_runs_for_the_last_task_only` (new)
- Covers: CT-4
- Setup: `log` a temp file outside the repo; `waves(cfg={"tests": {"suite": f"git log --format=%s >> {log}; ls >> {log}; echo END >> {log}; python -m unittest discover -s tests"}})`; claim (the baseline writes one `END` block); `work` T-1 and T-2.
- Action: `land(root, "T-1")`, count `END` lines; `land(root, "T-2")`, count again.
- Assert: after T-1 the count is still 1; after T-2 it is 2, and the second block holds a `T-1: ` subject and lists `m2_new.py`.

### TC-11 the implement skill starts a worker per wave task at once (AC-11; unit) [default]
- File: `tests/test_waves.py:test_ac11_skill_dispatches_a_wave` (new)
- Covers: CT-8
- Setup: the text of `skills/implement/SKILL.md`.
- Action: read it.
- Assert: it contains `one worker per claimed task at the same time`, `the task's worktree as its working directory`, `by its own ID`, `try again` and `while a wave is open, \`is claimed\` means wait`; and `src/nio/agents/worker.md` contains `try again` in its single-mode lines.

### TC-12 a task's worktree goes at commit and at block, the patch kept (AC-12; integration) [default]
- File: `tests/test_waves.py:test_ac12_worktree_removed_at_commit_and_block` (new)
- Covers: CT-2, CT-7
- Setup: `waves()`; claim; `w1, w2 = wt(out, "T-1"), wt(out, "T-2")`; `work` both.
- Action: `land(root, "T-1")`; then `flow(root, "green", S, "T-2", "--run", "false")` three times.
- Assert: after the land, `git worktree list` doesn't name `w1` and `w1` doesn't exist; after the third refusal, the output contains `blocked: T-2 after 3 attempts`, `git worktree list` doesn't name `w2`, `w2` doesn't exist, and `w2.parent / "T-2.patch"` exists and contains `m2_new.py`.

### TC-13 green refuses on a dirty main tree (AC-13; integration) [default]
- File: `tests/test_waves.py:test_ac13_green_refuses_on_a_dirty_main_tree` (new)
- Covers: CT-4
- Setup: `waves()`; claim; `work(root, out, "T-1")`; in the main tree write `stray.txt` as `mine\n`; `marker` a temp path outside the repo. Save the history's line count and the bytes of `stray.txt` and `m1.py`.
- Action: `flow(root, "green", S, "T-1", "--run", f"touch {marker}")`.
- Assert: exit 1; the output contains `uncommitted changes outside the effort folder` and `stray.txt`; `marker` does not exist; the line count and both files' bytes are unchanged; `m1_new.py` is absent from the main tree.

### TC-14 the review judges only the task's own changes (AC-14; integration) [default]
- File: `tests/test_waves.py:test_ac14_review_ignores_a_landed_sibling` (new)
- Covers: CT-5
- Setup: `waves()`; claim; `work` T-1 and T-2; `land(root, "T-2")` exits 0.
- Action: `land(root, "T-1")`.
- Assert: exit 0; the last `review` line for T-1 has `passed: true` and an `outside` list naming neither `m2.py` nor `m2_new.py` (it is `[]`).

### TC-15 a worker edits a file outside its list, or a sibling's file (UJ-1 misuse) (AC-15; integration) [default]
- File: `tests/test_waves.py:test_ac15_outside_file_is_recorded_and_a_clash_blocks` (new)
- Covers: CT-4, CT-5
- Setup: `waves()`; claim; `work` T-1 and T-2; in `wt(out, "T-1")` also write `extra.txt` as `e\n`; in both worktrees write `shared.py`, `x = 1\n` in T-1's and `x = 2\n` in T-2's.
- Action: `land(root, "T-1")`, then `land(root, "T-2")`.
- Assert: T-1's call exits 0, its output contains `outside the task's files: extra.txt` and `outside the task's files: shared.py`, and its review line's `outside` is `["extra.txt", "shared.py"]` in any order; T-2's call exits 1 and T-2 is `blocked` with a `blocked` line `cause: apply`, as in TC-8.

### TC-16 a worktree git can't make refuses the claim (AC-16; integration) [default]
- File: `tests/test_waves.py:test_ac16_worktree_failure_refuses_the_claim` (new)
- Covers: CT-2
- Setup: `waves()`; save the history's line count and `git worktree list`; wrap `implement.records.git` in the test process so that its second call whose arguments start with `worktree`, `add` returns `(128, "", "fatal: boom")` with `full=True` (and the plain call's lines otherwise), calling the real one for everything else.
- Action: `implement.claim(root, S, by=BY)` in process.
- Assert: it raises `ValueError` whose text contains `can't create a worktree for T-2` and `fatal: boom`; the history's line count is unchanged (no `claim` line; a first claim's `baseline` line may not be written either); `git worktree list` equals the saved list.

### TC-17 a bad budgets.parallel refuses the claim (AC-17; integration) [default]
- File: `tests/test_waves.py:test_ac17_bad_parallel_budget_is_refused` (new)
- Covers: CT-1
- Setup: three fresh repos, `waves(cfg={"budgets": {"parallel": v}})` for `v` in `0`, `"two"` and `True`; save each one's history line count.
- Action: `flow(root, "claim", S)`.
- Assert: exit 1; the output contains `budgets.parallel` and the value as Python's `repr` shows it (`0`, `'two'`, `True`); the line count is unchanged.

### TC-18 a second blocked sibling still holds the claim (AC-4; integration) [default]
- File: `tests/test_waves.py:test_ac4_two_blocked_siblings_hold_the_claim` (new)
- Covers: CT-1
- Setup: `waves(n=3)`; claim; `work` T-1 and T-2; `flow(root, "green", S, tid, "--run", "false")` three times for T-1, then three times for T-2, so both are blocked; then `flow(root, "unblock", S, "T-2", "--human", "x", "--by", "human")`.
- Action: `flow(root, "claim", S)`.
- Assert: exit 1; the output contains `T-1 is blocked` and `nio flow unblock`; no `claim` line was added.

### TC-19 a failed commit puts the main tree back and a retry lands (AC-9; integration) [default]
- File: `tests/test_waves.py:test_ac9_failed_commit_restores_and_retry_lands` (new)
- Covers: CT-4
- Setup: `waves()`; claim; `work(root, out, "T-1")`; save the main tree's `git status --porcelain` (outside state.json and history.jsonl) and `m1.py`'s bytes; wrap `implement.records.git` in the test process so a call whose first argument is `commit` returns `(1, "", "hook said no")` with `full=True`.
- Action: `implement.green(root, S, "T-1", "true", BY)` in process; then unwrap and `land(root, "T-1")`.
- Assert: the first call returns code 1 and its lines contain `stays green`; the main tree's porcelain and `m1.py` bytes equal the saved ones and `m1_new.py` is absent; `implement.status(...)["T-1"] == "green"`; `wt(out, "T-1")` still holds `m1_new.py`; the retry exits 0 with `done: T-1` and `git log -1 --format=%s` starts `T-1: `.

