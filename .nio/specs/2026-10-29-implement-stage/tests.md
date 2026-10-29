---
slug: 2026-10-29-implement-stage
retired: []                      # TC IDs removed from this plan; never reused
---
# Tests: implement stage

Fixtures: every test below lives in `tests/test_implement.py`, a plain script like the others (research RF-20), and uses these
helpers.
- **`impl(modes=None, cfg=None, tasks=None)`** returns a repo at `implementing`.
  - It builds `test_flow.effort("tasks_jury")`, writes `tasks.md` and approves it with `test_flow.approve(root, S, "tasks")`. `tasks.md` is `tasks` when given, else the refunds fixture `tests/fixtures/tasks/tasks.md` with a `- Mode: <mode>: fixture` line added to each task. The mode comes from `modes` (`{"T-1": "split"}`), and defaults to `split`.
  - It commits no test for the tasks. `write_test(root, name="tests/test_refund.py")` writes a unittest module whose `test_refund` fails on an `assertEqual` until `app.py` defines `refund`; tests call it after the claim, as a test phase would.
  - It writes `.nio/config.json` with `tests.suite: "python -m unittest discover -s tests"` merged with `cfg`, commits it all, and writes a `start` line through `test_flow.history`.
  - The TC-1 entry of `tests.md` names `File: tests/test_refund.py:test_refund`.
- **`flow(root, *args)`** is `test_flow.cli` with `--by` added to `claim`, `red`, `green`, `block` and `unblock` too.
- **`lines(root)`** returns the parsed history lines.
- **`state(root)`** returns `flow.load(root, S)[0]`.

## Acceptance tests

### TC-1 the worker pack holds exactly its six parts (AC-1; unit) [default]
- File: `tests/test_implement.py:test_ac1_pack_holds_only_its_parts` (new)
- Covers: CT-6
- Setup: `impl()`; T-1 has `Files: app.py`, `Serves: AC-1`, `Test: TC-1`. Add a second path, `Files: app.py, refunds.py`.
- Action: `implement.worker_pack(root, S, task)` for T-1.
- Assert: the text has exactly five top-level `## ` sections. They hold:
  - the memory pack built with `--task T-1 --path app.py --path refunds.py --ac AC-1`;
  - T-1's `tasks.show` text;
  - AC-1's line and its Observable;
  - every CT-n that TC-1's `Covers:` names;
  - the TC-1 entry.
  No `@nio:remember` text, `Mode` line or handoff format appears.
  No other AC's line, no other TC-n and no `## Build order` from `plan.md` appears.

### TC-2 a worker card is rendered per tier and host (AC-2; integration) [default]
- File: `tests/test_implement.py:test_ac2_worker_card_per_tier` (new)
- Covers: CT-15
- Setup: a repo with `.nio/config.json` `{"agents": {"hosts": ["claude", "codex"], "tiers": {"codex": {"cheap": "c1", "strong": "c2", "max": "c3", "frontier": "c4"}}}}`.
- Action: `agents.sync(root)`.
- Assert: each of these:
  - `.claude/agents/nio-worker-cheap.md`, `-strong.md`, `-max.md` and `-frontier.md` exist, with models `haiku`, `sonnet`, `opus` and `fable`;
  - the four codex files exist with `c1` to `c4`;
  - each body contains `never edit` before `state.json` and `history.jsonl`, and `nio flow` only with `red` and `green` in single mode;
  - no `nio-worker.md` without a tier exists.

### TC-3 the start instruction names the tier's card and the effort (AC-3; unit) [default]
- File: `tests/test_implement.py:test_ac3_claim_names_card_and_effort` (new)
- Covers: CT-5
- Setup: `impl()` with T-1 given `Tier: cheap: fixture` and `Effort: low`; the host is claude.
- Action: `flow(root, "claim", S)`.
- Assert: exit 0; the output has the lines `card: nio-worker-cheap` and `effort: low`.

### TC-4 a claim waits on an unfinished dependency (AC-4; unit) [default]
- File: `tests/test_implement.py:test_ac4_dependency_not_done` (new)
- Covers: CT-4, CT-5
- Setup: `impl()`; T-2 depends on T-1; T-1 is blocked (a `blocked` line written with `test_flow.history`), so nothing else is ready.
- Action: `flow(root, "claim", S)`.
- Assert: exit 1; the output contains `T-2 waits on T-1`; `state(root)["claims"] == {}`.

### TC-5 a second claim is refused (AC-5; unit) [default]
- File: `tests/test_implement.py:test_ac5_one_claim_at_a_time` (new)
- Covers: CT-5
- Setup: `impl()`; `flow(root, "claim", S)` claims T-1.
- Action: `flow(root, "claim", S)` again.
- Assert: exit 1; the output contains `T-1 is claimed`; `state(root)["claims"] == {"task": "T-1"}`.

### TC-6 no approve commit, no claim (AC-6; integration) [default]
- File: `tests/test_implement.py:test_ac6_no_approve_commit` (new)
- Covers: CT-5
- Setup: `impl()` built with `test_flow.approve(root, S, "tasks", commit=False)` and the files committed as `wip`, so the tasks ledger says approved but no commit is named `nio: approve tasks`.
- Action: `flow(root, "claim", S)`.
- Assert: exit 1; the output contains `no "nio: approve tasks" commit`; `len(lines(root))` is unchanged.

### TC-7 uncommitted changes outside the effort refuse a claim (AC-7; integration) [default]
- File: `tests/test_implement.py:test_ac7_dirty_tree` (new)
- Covers: CT-5
- Setup: `impl()`; write `README.md` without committing it.
- Action: `flow(root, "claim", S)`.
- Assert: exit 1; the output lists `README.md`; `state(root)["claims"] == {}`.

### TC-8 tasks come in epic and dependency order (AC-8; unit) [default]
- File: `tests/test_implement.py:test_ac8_order` (new)
- Covers: CT-4
- Setup: `impl(tasks=...)` with E-1 holding T-1 and T-2 (T-2 depends on T-1) and E-2 holding T-3, all in direct mode.
- Action: three times: `flow(root, "claim", S)`, write passing code, then `flow(root, "green", S, "T-n", "--run", "python -m unittest tests/test_refund.py")`.
- Assert: the claimed tasks are `T-1`, `T-2`, `T-3` in that order.

### TC-9 red is accepted on an assertion failure (AC-9; unit) [default]
- File: `tests/test_implement.py:test_ac9_red_accepted` (new)
- Covers: CT-7, CT-2
- Setup: `impl()`; claim T-1; then `write_test(root)`.
- Action: `flow(root, "red", S, "T-1", "--run", "python -m unittest tests/test_refund.py")`.
- Assert: exit 0. The last line has kind `red`, `task: T-1`, `command` equal to the run string, a 64-character `output` hash, `runner: unittest`, and `frozen` with `tests/test_refund.py` mapped to its sha256. `status` gives `red`.

### TC-10 red is refused when the test passes (AC-10; unit) [default]
- File: `tests/test_implement.py:test_ac10_test_passes_first` (new)
- Covers: CT-7
- Setup: `impl()`; claim T-1; `app.py` already defines `refund`, so the test passes.
- Action: red with `python -m unittest tests/test_refund.py`.
- Assert: exit 1; the output contains `the test passes before the code exists`; status `claimed`.

### TC-11 red is refused for an import, collection or syntax error (AC-11; unit) [default]
- File: `tests/test_implement.py:test_ac11_wrong_reason` (new)
- Covers: CT-2, CT-7
- Setup: `impl()`; claim T-1, three times over:
  - (a) the test imports `nosuchmodule`;
  - (b) the test file has a syntax error;
  - (c) `tests/__init__.py` raises, so discovery fails.
- Action: red with `python -m unittest tests/test_refund.py` for each.
- Assert: three exits of 1, each naming `collection, import or syntax error`; status `claimed` after each.

### TC-12 an unknown runner is decided by exit code (AC-12; unit) [default]
- File: `tests/test_implement.py:test_ac12_unknown_runner` (new)
- Covers: CT-2, CT-7
- Setup: `impl()`; claim T-1.
- Action: red with `python tests/test_refund.py` (not a known runner's command), which exits 1.
- Assert: exit 0; the red line has `runner: unknown`.

### TC-13 green on the red command is accepted and review starts (AC-13; unit) [default]
- File: `tests/test_implement.py:test_ac13_green_same_command` (new)
- Covers: CT-8
- Setup: TC-9's red; then add `refund` to `app.py`.
- Action: `flow(root, "green", S, "T-1")`.
- Assert: exit 0. There is a `green` line whose `command` equals the red line's and which has an `output` hash, followed by a `review` line.

### TC-14 green with another command is refused (AC-14; unit) [default]
- File: `tests/test_implement.py:test_ac14_green_other_command` (new)
- Covers: CT-8
- Setup: TC-9's red.
- Action: green with `--run "python -m unittest discover -s tests"`.
- Assert: exit 1; the output contains `the command recorded at red is python -m unittest tests/test_refund.py`; status `red`.

### TC-15 a changed frozen test refuses green until red again (AC-15; unit) [default]
- File: `tests/test_implement.py:test_ac15_frozen_test_changed` (new)
- Covers: CT-7, CT-8
- Setup: TC-9's red; add `refund`; change the assertion in `tests/test_refund.py`.
- Action: each of these:
  1. green;
  2. remove `refund` again, then red;
  3. add `refund`, then green.
- Assert: each of these:
  1. the first green exits 1 naming `tests/test_refund.py`;
  2. the second red line's `frozen` hash differs from the first;
  3. the last green exits 0.

### TC-16 a failed review counts only failures new to the baseline (AC-16; unit) [default]
- File: `tests/test_implement.py:test_ac16_new_failure_only` (new)
- Covers: CT-3, CT-8
- Setup: `impl()` with `tests/test_a.py` failing before the first claim, so the baseline lists `test_a`; claim T-1 and red it. The code makes T-1's test pass but also makes a new `tests/test_b.py` fail.
- Action: green.
- Assert: the `review` line names `test_b` as a new failure and not `test_a`; status `red`; `state(root)["attempts"]["T-1"] == 1`.

### TC-17 files outside the task's list are recorded, not refused (AC-17; unit) [default]
- File: `tests/test_implement.py:test_ac17_outside_files` (new)
- Covers: CT-8
- Setup: TC-9's red; the code changes `app.py` and a new `helpers.py`.
- Action: green.
- Assert: exit 0; the `review` line passes and has `outside: ["helpers.py"]`.

### TC-18 editing the spec fails the review (AC-18; unit) [default]
- File: `tests/test_implement.py:test_ac18_spec_edited` (new)
- Covers: CT-8
- Setup: TC-9's red; add `refund` and also append a line to `.nio/specs/<S>/spec.md`.
- Action: green.
- Assert: exit 1; the output names `spec.md`; status not `done`.

### TC-19 the baseline is recorded before the first claim (AC-19; integration) [default]
- File: `tests/test_implement.py:test_ac19_baseline_first` (new)
- Covers: CT-5, CT-3
- Setup: `impl()` with `tests/test_a.py` and `tests/test_c.py` failing.
- Action: `flow(root, "claim", S)`.
- Assert: the first new line is `baseline`, with `failing` holding `test_a` and `test_c` names and `runner: unittest`. The `claim` line comes after it.

### TC-20 state.json holds no task status (AC-20; unit) [default]
- File: `tests/test_implement.py:test_ac20_status_from_history` (new)
- Covers: CT-4
- Setup: take T-1 through claim, red and green to done (TC-13).
- Action: read `state.json`.
- Assert: its keys are a subset of `flow.STATE_KEYS`. `claims == {}`. No value anywhere in it is `"done"` or `"red"`. `implement.status` gives `{"T-1": "done", ...}` from the lines alone.

### TC-21 a handoff claiming pass doesn't make a task green (AC-21; unit) [default]
- File: `tests/test_implement.py:test_ac21_handoff_ignored` (new)
- Covers: CT-8
- Setup: TC-9's red; write `handoff.md` with `status: done` and the text `all tests pass`.
- Action: `implement.status(...)`, then `flow(root, "status")` and `flow(root, "next", S)`.
- Assert: status `red`; neither output and no history line contains `all tests pass`.

### TC-22 a done task refuses red and green (AC-22; unit) [default]
- File: `tests/test_implement.py:test_ac22_done_refuses` (new)
- Covers: CT-7, CT-8
- Setup: T-1 done (TC-13).
- Action: red and green on T-1.
- Assert: both exit 1 saying `T-1 is done`; `len(lines(root))` is unchanged.

### TC-23 the third failed attempt blocks the task (AC-23; unit) [default]
- File: `tests/test_implement.py:test_ac23_third_attempt_blocks` (new)
- Covers: CT-10
- Setup: TC-9's red, then two greens with failing code, so `attempts["T-1"] == 2`.
- Action: a third green with failing code.
- Assert: each of these:
  - a `blocked` line has `cause: attempts` and `evidence.patch` naming a `.nio/runs/<run>/T-1.patch` that holds the failing code;
  - `git status --porcelain` lists nothing outside the effort folder;
  - `flow(root, "next", S)` contains `waiting_for_human` and `T-1`;
  - `flow(root, "claim", S)` exits 1.

### TC-24 the worker card's spec-problem rules (AC-24; unit) [default]
- File: `tests/test_implement.py:test_ac24_card_rules` (new)
- Covers: CT-15
- Setup: none.
- Action: read `src/nio/agents/worker.md`.
- Assert: it contains `status: blocked`, `change_request:`, `spec_says`, `code_shows` and `smallest_change`, and forbids editing `spec.md`, the plan files and `tasks.md`.

### TC-25 a blocked handoff files a pending change record (AC-25; integration) [default]
- File: `tests/test_implement.py:test_ac25_block_files_change` (new)
- Covers: CT-11
- Setup: claim T-1; write `handoff.md` with `status: blocked` and a `change_request:` holding `spec_says: "refund any order"`, `code_shows: "orders have no paid flag"` and `smallest_change: "add paid to Order"`.
- Action: `flow(root, "block", S, "T-1", "--handoff", "handoff.md")`.
- Assert: exactly one new `.nio/memory/project/C-*.md` with `outcome: pending`, whose body holds the three strings; status `blocked`.

### TC-26 a done task is committed on the effort branch (AC-26; integration) [default]
- File: `tests/test_implement.py:test_ac26_commit` (new)
- Covers: CT-9
- Setup: T-1 titled `Refund a paid order in full`, taken to green (TC-13); note main's HEAD first.
- Action: the green that passes review.
- Assert: `git log -1 --format=%s` is `T-1: Refund a paid order in full`; `git show --name-only HEAD` lists `app.py` and the effort's `history.jsonl`; `git rev-parse main` is unchanged.

### TC-27 the stage works on the effort branch (AC-27; integration) [default]
- File: `tests/test_implement.py:test_ac27_branch` (new)
- Covers: CT-5
- Setup: `impl()` on `main`.
- Action: `flow(root, "claim", S)`.
- Assert: `git branch --show-current` is `nio/<S>`; `main` has no new commit.

### TC-28 the branch is never merged (AC-28; integration) [default]
- File: `tests/test_implement.py:test_ac28_no_merge` (new)
- Covers: CT-9, CT-13
- Setup: `impl(tasks=...)` with one direct task; take it to done.
- Action: read the last output and git.
- Assert: `main`'s HEAD is unchanged; the output contains `nio/<S>` as the branch to merge.

### TC-29 an epic's gate is skipped and the next epic follows (AC-29; integration) [default]
- File: `tests/test_implement.py:test_ac29_epic_skipped` (new)
- Covers: CT-13
- Setup: TC-8's two epics; finish T-1 and T-2.
- Action: the green that finishes T-2.
- Assert: an `epic` line for E-1 with `skipped: not built`; the output contains `notify:` and `E-1`; the next claim is T-3.

### TC-30 the epic report lists baseline failures and outside files (AC-30; unit) [default]
- File: `tests/test_implement.py:test_ac30_epic_report` (new)
- Covers: CT-13
- Setup: one-task epic; the baseline lists `test_a`; the task also changes `helpers.py`.
- Action: the green that finishes the epic.
- Assert: the report names `test_a` as a baseline failure, and `helpers.py` with `T-1`.

### TC-31 the last epic finishes the effort (AC-31; unit) [default]
- File: `tests/test_implement.py:test_ac31_effort_done` (new)
- Covers: CT-13, CT-14
- Setup: TC-28 done.
- Action: `flow(root, "next", S)` and `flow(root, "status")`.
- Assert: both contain `done`; the last line is a `pass` from `implementing` to `done`.

### TC-32 an open fix task holds its epic (AC-32; unit) [default]
- File: `tests/test_implement.py:test_ac32_fix_task_next` (new)
- Covers: CT-4
- Setup: E-1 holds T-1 and T-2; T-1 done; append under `#### Fixes` a T-4 with `From: J-1 (tasks, round 1)`, committed; then take T-2 to done.
- Action: `flow(root, "claim", S)`.
- Assert: after T-2's green, no `epic` line for E-1 exists; the task claimed is T-4.

### TC-33 a shared test file can be frozen by the next task (AC-33; unit) [default]
- File: `tests/test_implement.py:test_ac33_shared_test_file` (new)
- Covers: CT-7
- Setup: T-1 and T-2 both test in `tests/test_refund.py`; T-1 done.
- Action: claim T-2, add its test to the same file, red.
- Assert: exit 0; T-2's red line has a `frozen` hash for `tests/test_refund.py` that differs from T-1's.

### TC-34 no suite command, the stage waits (AC-34; unit) [default]
- File: `tests/test_implement.py:test_ac34_no_suite` (new)
- Covers: CT-5
- Setup: `impl(cfg={"tests": {"suite": None}})`, with the key removed.
- Action: `flow(root, "claim", S)`, then `flow(root, "next", S)`.
- Assert: `next` contains `waiting_for_human` and `tests.suite`; no `baseline` line.

### TC-35 an unknown runner needs a green baseline (AC-35; unit) [default]
- File: `tests/test_implement.py:test_ac35_unknown_runner_baseline` (new)
- Covers: CT-3, CT-5, CT-8
- Setup: (a) `tests.suite: "python check.py"`, with `check.py` exiting 1; (b) the same with `check.py` exiting 0, then T-1 taken to green while `check.py` exits 1.
- Action: claim; then green.
- Assert: (a) `waiting_for_human` naming the failing baseline; (b) the review fails naming a new failure.

### TC-36 the human unblocks a task (AC-36; unit) [default]
- File: `tests/test_implement.py:test_ac36_unblock` (new)
- Covers: CT-12
- Setup: TC-23's blocked T-1.
- Action: `flow(root, "unblock", S, "T-1", "--human", "fixed the fixture")`; claim; green; `write_test(root)` with a different failing assertion; red.
- Assert: each of these:
  - status `ready` before the claim, and `"T-1" not in state(root)["attempts"]`;
  - the green before red exits 1 with `has no failing test first`;
  - the new red's `frozen` hash for `tests/test_refund.py` is the sha256 of the new file and differs from the old red's.

### TC-37 a failed review sends the task back to red with one attempt (AC-37; unit) [default]
- File: `tests/test_implement.py:test_ac37_review_fail_to_red` (new)
- Covers: CT-8, CT-10
- Setup: TC-9's red; code that passes T-1's test but breaks `tests/test_c.py`.
- Action: green.
- Assert: status `red`; `attempts["T-1"] == 1`; the frozen hashes on the last red line are unchanged.

### TC-38 cargo's compile error is refused, mvn is unknown (AC-38; unit) [default]
- File: `tests/test_implement.py:test_ac38_cargo_and_mvn` (new)
- Covers: CT-2
- Setup: fake `cargo` and `mvn` scripts first on `PATH`:
  - `cargo` prints `error[E0308]: mismatched types` and exits 101;
  - `mvn` exits 1.
- Action: `implement.runner` and `wrong_reason` for `cargo test tests/test_refund.py` and `mvn test tests/test_refund.py`; then red through the CLI with each.
- Assert: the cargo red exits 1 naming a compile error, with status `claimed`; the mvn red exits 0, with `runner: unknown`.

### TC-39 a changed done task comes back under a new number (AC-39; integration) [default]
- File: `tests/test_implement.py:test_ac39_changed_task_new_number` (new)
- Covers: CT-4
- Setup: T-1 and T-2 done and committed; a `back` line to `tasking`; a re-approved `tasks.md` with T-2 retired and T-4 holding T-2's changed block.
- Action: `flow(root, "claim", S)`.
- Assert: T-1 and T-2 read `done`; the claim is `T-4`; both `T-1:` and `T-2:` commits are still on `nio/<S>`.

### TC-40 the task's mode, or the forced one (AC-40; unit) [default]
- File: `tests/test_implement.py:test_ac40_mode` (new)
- Covers: CT-4, CT-5
- Setup: `impl(modes={"T-1": "direct"})`; then the same with `cfg={"implement": {"mode": "split"}}`.
- Action: claim.
- Assert: `mode: direct`, then `mode: split`.

### TC-41 direct mode: green with no red, and red refused (AC-41; unit) [default]
- File: `tests/test_implement.py:test_ac41_direct` (new)
- Covers: CT-7, CT-8
- Setup: `impl(modes={"T-1": "direct"})`; claim; add `refund`.
- Action: red with any command, then green with `--run "python -m unittest tests/test_refund.py"`.
- Assert: the red exits 1 naming `direct mode`; the green exits 0; no `red` line for T-1.

### TC-42 single mode: the worker's own red is accepted (AC-42; unit) [default]
- File: `tests/test_implement.py:test_ac42_single` (new)
- Covers: CT-7
- Setup: `impl(modes={"T-1": "single"})`; claim.
- Action: red with `--by "worker / test / test"`.
- Assert: exit 0; the red line has the same fields as TC-9's, with `who.role == "worker"`.

### TC-43 a no-test or non-test command is refused (AC-43; unit) [default]
- File: `tests/test_implement.py:test_ac43_no_test_command` (new)
- Covers: CT-2, CT-7
- Setup: claim T-1 (TC-1 is in `tests/test_refund.py`).
- Action: red with `python -m unittest tests/test_refund.py -k nothing`, then red with `test -e src/new.py`.
- Assert: the first exits 1 with `no tests ran`; the second exits 1 naming `tests/test_refund.py`; status `claimed`.

### TC-44 a broken suite or fewer tests fails the review (AC-44; unit) [default]
- File: `tests/test_implement.py:test_ac44_broken_or_fewer` (new)
- Covers: CT-3, CT-8
- Setup: a baseline of 40 collected, none failing (40 small tests in `tests/test_many.py`). Then two cases: (a) the code makes another module fail to import; (b) the code deletes two tests.
- Action: green in each.
- Assert: (a) the review names the import error; (b) it names `38` against `40`.

### TC-45 editing tests.md fails the review (AC-45; unit) [default]
- File: `tests/test_implement.py:test_ac45_tests_md_edited` (new)
- Covers: CT-8
- Setup: TC-9's red; the code also edits the effort's `tests.md`.
- Action: green.
- Assert: exit 1 naming `tests.md`; status not `done`.

### TC-46 a claim off the effort branch is refused (AC-46; integration) [default]
- File: `tests/test_implement.py:test_ac46_wrong_branch` (new)
- Covers: CT-5
- Setup: T-1 done on `nio/<S>`; `git checkout main`.
- Action: claim.
- Assert: exit 1 naming `nio/<S>`; no `claim` line.

### TC-47 a rejected commit keeps the task green (AC-47; integration) [default]
- File: `tests/test_implement.py:test_ac47_commit_rejected` (new)
- Covers: CT-9
- Setup: `.git/hooks/pre-commit` that prints `hook-says-no-T1` and exits 1; T-1 at red with passing code; keep the bytes of `history.jsonl` and `state.json` before the green.
- Action: green.
- Assert: each of these:
  - no commit starting `T-1:`;
  - no `task_done` line;
  - status `green`;
  - `flow(root, "next", S)` contains `waiting_for_human`, `hook-says-no-T1` and `nio flow green`;
  - `history.jsonl` is its earlier bytes plus the `green`, `review` and `fail` lines only, and `git diff --cached` is empty;
  - after removing the hook, `flow(root, "green", S, "T-1")` exits 0 and makes the `T-1:` commit.

### TC-48 a repeated filing makes one record and waits (AC-48; integration) [default]
- File: `tests/test_implement.py:test_ac48_block_twice` (new)
- Covers: CT-11
- Setup: TC-25's handoff.
- Action: `block` twice.
- Assert: one `C-*` file; the second call prints the same `C-` ID; `next` contains `waiting_for_human`, `T-1` and that ID.

### TC-49 a timed-out or missing command is refused and costs an attempt (AC-49; unit) [default]
- File: `tests/test_implement.py:test_ac49_time_limit` (new)
- Covers: CT-1, CT-7
- Setup: `impl(cfg={"tests": {"timeout": 1}})`; `tests/test_refund.py` sleeps 5 seconds in `setUpClass`; claim T-1.
- Action: red with `python -m unittest tests/test_refund.py`, then red with `nosuchprog tests/test_refund.py`.
- Assert: each of these:
  - the first exits 1 naming `time limit` within 3 seconds;
  - the second exits 1 naming `program not found`;
  - `attempts["T-1"] == 2`;
  - no `python` process started by the test is left running (`os.killpg` on the recorded group raises `ProcessLookupError`).

### TC-50 a direct task's failed review goes back to claimed (AC-50; unit) [default]
- File: `tests/test_implement.py:test_ac50_direct_review_fail` (new)
- Covers: CT-8, CT-10
- Setup: `impl(modes={"T-1": "direct"})`; claim; code that passes T-1's test but breaks `tests/test_c.py`.
- Action: green.
- Assert: status `claimed`; `attempts["T-1"] == 1`; no `red` line for T-1.

## Quality tests

### TC-51 nio's own steps load no model or HTTP client (NFR-1; integration) [default]
- File: `tests/test_implement.py:test_nfr1_no_model_calls` (new)
- Covers: CT-5, CT-7, CT-8, CT-9
- Setup: the TC-13 fixture, whose tests need no network.
- Action: each of these:
  1. Run claim, red and green in one subprocess.
  2. A `sitecustomize` on `PYTHONPATH` blocks `socket.socket.connect` for anything but `AF_UNIX`.
  3. At exit, it prints `sorted(sys.modules)`.
- Assert: each of these:
  - the task is done;
  - no connect was attempted;
  - none of `anthropic`, `openai`, `httpx`, `requests`, `urllib3`, `http.client` or `aiohttp` is in the module list.

## Misuse tests

### TC-52 a worker that weakens the test after red can't get green (UJ-1 misuse; unit) [default]
- File: `tests/test_implement.py:test_uj1_weakened_test` (new)
- Covers: CT-8
- Setup: TC-9's red; replace the assertion with `assertTrue(True)`.
- Action: green.
- Assert: exit 1 naming `tests/test_refund.py`; no `task_done` line.

### TC-53 a worker that edits the spec can't finish the task (UJ-2 misuse; unit) [default]
- File: `tests/test_implement.py:test_uj2_spec_edited` (new)
- Covers: CT-8
- Setup: TC-9's red; the code also rewrites a line of `spec.md` so it matches the code.
- Action: green.
- Assert: the review fails naming `spec.md`; no commit `T-1:`.

### TC-54 an epic with an open fix task never finishes (UJ-3 misuse; unit) [default]
- File: `tests/test_implement.py:test_uj3_open_fix_task` (new)
- Covers: CT-13
- Setup: TC-32's setup, up to T-2's green.
- Action: `implement.epic_end` called for E-1 with T-4 not done.
- Assert: no `epic` line; nothing is printed with `notify:`.
