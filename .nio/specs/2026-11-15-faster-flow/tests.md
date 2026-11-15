---
slug: 2026-11-15-faster-flow
retired: []                      # TC IDs removed from this plan; never reused
---
# Tests: Faster flow

Shared setup, named below. `impl()` is `tests/test_implement.py`'s fixture (a repo at implementing), given here a
tasks.md of two epics: E-1 (T-1, T-2, each naming a self-check TC in `tests/test_app.py`) and E-2 (T-3, no dependency
on E-1), tier per epic; `BY` is `"orchestrator / test / test"`. `effort(stage)` and `auto_on(root, stage)` are
`tests/test_flow.py`'s; `grant(root)` is `flow.start(root, S, "human", auto=True)`. `repo()`/`errs()` are
`tests/test_tasks.py`'s, `plan_repo()`/`lens()`/`first_review()` `tests/test_jury.py`'s. The e2e tests live in
`tests/test_auto_e2e.py` and run only with `NIO_E2E=1`, on a copy of the refunds fixture, with `gh` replaced on `PATH`
by a stub that logs its argv and prints `https://example.test/pr/1` and a bare local repo as `origin`.

## Acceptance tests

### TC-1 The claim hands a whole epic (AC-1; integration) [agent]
- File: `tests/test_implement.py:test_claim_hands_the_whole_epic` (new)
- Covers: CT-1
- Setup: `impl()` with E-1's T-2 `Depends on: T-1`, neither done.
- Action: `nio flow claim S --by BY`.
- Assert: exit 0; output has `epic: E-1`, `tasks: T-1, T-2` and no `task:` line; the pack file holds T-1 and T-2, their ACs, CTs and TCs, and no T-3; history's last line is `claim` with `epic: E-1`.

### TC-2 A passing hand-back is run by the flow and closes the epic (AC-2; integration) [agent]
- File: `tests/test_implement.py:test_finish_runs_the_tests_and_closes` (new)
- Covers: CT-2, CT-3
- Setup: TC-1's claim of E-1 (both tasks undone); write passing tests for T-1 and T-2 and their code.
- Action: `nio flow finish S E-1 --by BY`.
- Assert: exit 0; history holds an `epic_test` line `epic: E-1, passed: true` and after it `task_done` for T-1 and T-2; `git log -1 --format=%s` is `E-1: <heading>`; with no `epic_test` line written (a run made to crash before it) no `task_done` exists; on a copy where the agent also edited `.nio/specs/S/spec.md`, `finish` exits non-zero naming `spec.md` and writes no `task_done`.

### TC-3 A failing named test keeps the epic open with the tail (AC-3; integration) [agent]
- File: `tests/test_implement.py:test_finish_failing_test_keeps_the_epic_open` (new)
- Covers: CT-2, CT-4
- Setup: E-1 claimed; T-2's test asserts `1 == 2`; the test prints 80 numbered lines first.
- Action: `nio flow finish S E-1 --by BY`.
- Assert: exit non-zero; `epics()["E-1"]` is `("failed", 1)`; the `epic_test` line has `passed: false`, `failing` holding T-2's test name, and `tail` of exactly 50 lines ending with the runner's `ran 2 tests, 1 failed`; no `task_done` line.

### TC-4 The agent's word doesn't close the epic (AC-4; integration) [agent]
- File: `tests/test_implement.py:test_finish_ignores_the_agents_claim` (new)
- Covers: CT-2
- Setup: E-1 claimed; T-1's test fails; a hand-off file saying `status: done, tests pass`.
- Action: `nio flow finish S E-1 --by BY` (the CLI takes no word from the agent).
- Assert: exit non-zero; `epics()["E-1"][0] == "failed"`; no history line holds the hand-off text.

### TC-5 No red, green or mode remains (AC-5; integration) [agent]
- File: `tests/test_implement.py:test_no_red_green_or_mode` (new)
- Covers: CT-5, CT-8
- Setup: `repo()` with no `Mode:` line in any task.
- Action: `nio check tasks S`; `nio flow red S T-1 --run x --by BY`; read `skills/implement/SKILL.md` and `src/nio/cli.py`'s `nio flow` choices.
- Assert: check exits 0 with no `Mode` error; `nio flow red` exits 2 with `invalid choice`; the skill names none of `nio flow red`, `nio flow green`, `split`, `single mode`, `direct`.

### TC-6 No jury runs per epic (AC-6; integration) [agent]
- File: `tests/test_effort.py:test_epics_close_without_a_jury_then_one_pr_gate` (new)
- Covers: CT-2
- Setup: `impl()`; both epics finished with passing tests.
- Action: `nio flow next S`.
- Assert: no `.nio/specs/S/jury/implementation-E-*` file exists; history's last line is `pass` implementing → pr; after `nio jury next S pr` (stubbed `gh`) only `jury/pr.json` exists. Then a rejected pr round with one confirmed major: tasks.md gains `## E-3 PR fixes` with `- Tier: strong` and `- Effort: med` lines, `nio check tasks S` exits 0, and `nio flow claim S --by BY` names E-3.

### TC-7 Tier per epic and the task map are checked (AC-7; unit) [agent]
- File: `tests/test_tasks.py:test_tier_per_epic_and_the_task_map` (new)
- Covers: CT-6
- Setup: `repo()` with `- Tier: strong: x` and `- Effort: med` under each `## E-n` and none on tasks; a copy with T-2's `Test:` removed; a copy with E-2's Tier removed.
- Action: `errs(root)` on each.
- Assert: the first has no error; the second has `T-2: needs \`- Test:\``; the third has `E-2: needs \`- Tier:\``.

### TC-8 NORTH_STAR and the skill describe per-epic work (AC-8; unit) [agent]
- File: `tests/test_talk.py:test_implement_is_per_epic` (new)
- Covers: CT-8, CT-10
- Setup: the repo files.
- Action: read `NORTH_STAR.md`'s `### Implement` section and `skills/implement/SKILL.md`.
- Assert: both contain `one agent per epic`; neither contains `TDD`, `test writer`, `builder`, `red` as a word, or `green` as a word.

### TC-9 A claimed epic can't be claimed again (AC-9; integration) [agent]
- File: `tests/test_implement.py:test_second_claim_of_an_epic_is_refused` (new)
- Covers: CT-1
- Setup: E-1 claimed by driver A.
- Action: `nio flow claim S E-1 --by "driver-b / test / test"`.
- Assert: exit non-zero; output holds `E-1 is claimed`; `state.json` `claims` and history are byte-identical to before.

### TC-10 An epic with no test can't close (AC-10; integration) [agent]
- File: `tests/test_implement.py:test_finish_refuses_an_epic_with_no_test` (new)
- Covers: CT-2
- Setup: a lite spec whose E-1 tasks say `Test: none`; E-1 claimed.
- Action: `nio flow finish S E-1 --by BY`.
- Assert: exit non-zero; output holds `E-1 has no test to run`; no `epic_test` line; `epics()["E-1"][0] == "claimed"`.

### TC-11 The epic's commit leaves a stray file out (AC-11; integration) [agent]
- File: `tests/test_implement.py:test_epic_commit_leaves_untracked_files_out` (new)
- Covers: CT-3
- Setup: E-1 claimed, its tests and code written; an untracked `notes/scratch.txt` that no task lists.
- Action: `nio flow finish S E-1 --by BY`.
- Assert: `git status --porcelain` still shows `?? notes/`; `git show --name-only HEAD` lists E-1's `Files:` paths, the untracked test file its TCs name (`tests/test_app.py`, listed in no `Files:`), `history.jsonl` and `state.json`, and nothing else.

### TC-12 A dependency on a later epic fails the check (AC-12; unit) [agent]
- File: `tests/test_tasks.py:test_dependency_on_a_later_epic_fails` (new)
- Covers: CT-7
- Setup: `repo()` with T-10 in E-5 `Depends on: T-11` and T-11 in E-6.
- Action: `nio check tasks S`.
- Assert: exit non-zero; one error line holds `T-10`, `T-11`, `E-5` and `E-6`.

### TC-13 Earlier-epic dependencies pass (AC-13; unit) [agent]
- File: `tests/test_tasks.py:test_dependency_on_an_earlier_epic_passes` (new)
- Covers: CT-7
- Setup: `repo()` with T-3 in E-2 `Depends on: T-1` (E-1) and T-2 in E-1 `Depends on: T-1`.
- Action: `errs(root)`.
- Assert: no error line contains `a later epic`.

### TC-14 The mod backgrounds the new long commands (AC-14; unit) [agent]
- File: `tools/claude-mods/background-nio-commands/hooks/register.test.ts:AC-1..AC-5: long commands are backgrounded, nothing else changes` (existing)
- Covers: CT-11
- Setup: the test's `setup()` stub, no config.
- Action: send `nio jury evidence S pr --run R`, `uv run nio flow finish S E-1 --by x`, `cd /w && nio jury evidence S pr`, `nio jury run S spec`, `nio flow green S T-1`.
- Assert: the test's cases for `nio jury run` and `nio flow green` are replaced: the first three commands come back with `run_in_background: true`; the last two come back unchanged; `register.ts` source holds no `jury\s+run`.

### TC-15 After install, a fresh session backgrounds jury evidence (AC-15; e2e) [agent]
- File: `tests/test_auto_e2e.py:test_installed_mod_backgrounds_evidence` (new)
- Covers: CT-11, CT-12
- Setup: a copy of the NIO repo; `nio mods install` run there; no `--plugin-dir`, `CLAUDE_CODE_PLUGIN_DIRS` unset.
- Action: `claude -p "run uv run nio jury evidence --help and report its first line" --output-format stream-json`.
- Assert: the transcript's Bash tool call for `nio jury evidence` has `run_in_background: true`; no tool call holds `sleep`.

### TC-16 The brief says the mod is off (AC-16; integration) [agent]
- File: `tests/test_flow.py:test_brief_warns_when_the_mod_is_off` (new)
- Covers: CT-13
- Setup: `effort("implementing")`; `CLAUDECODE=1`; no `.claude/settings*.json`; then a copy with `.claude/settings.local.json` `{"enabledPlugins": {"background-nio-commands@nio-mods": true}}`; then `CLAUDECODE` unset.
- Action: `nio flow brief S` in each.
- Assert: the first output's first line starts `warning: the background mod is off`; the second and third hold no `background mod`.

### TC-17 Only the human grants or revokes auto (AC-17; integration) [agent]
- File: `tests/test_flow.py:test_only_the_human_grants_and_revokes_auto` (new)
- Covers: CT-33, CT-34
- Setup: `effort("grilling")`.
- Action: `nio flow start S --auto --by BY`; `nio flow start S --auto --by human`; `nio flow manual S --by BY`; `nio flow manual S --by human`.
- Assert: 1st exits non-zero, `auto: false`, no line added; 2nd exits 0, `auto: true`, last line `kind: grant`, `who.role: human`; 3rd exits non-zero, `auto` still true, no line added; 4th exits 0, last line `kind: switch_off`, `auto: false`.

### TC-18 The driver runs each stage in a fresh agent (AC-18; e2e) [agent]
- File: `tests/test_auto_e2e.py:test_driver_runs_every_stage` (new)
- Covers: CT-39, CT-34, CT-35
- Setup: refunds fixture at spec_jury with a spec the lenses approve, granted, usage hook installed.
- Action: `claude -p "drive <S> under auto from nio flow next (skills/jury/SKILL.md)"`.
- Assert: history after the `grant` has `pass` lines for spec_jury, planning, plan_jury, tasking, tasks_jury in order with no `who.role: human`; `usage.report` shows one `agent_called` per stage, each a separate agent.

### TC-19 Under auto the implement stage runs per epic and one pr gate (AC-19; e2e) [agent]
- File: `tests/test_auto_e2e.py:test_auto_implements_per_epic` (new)
- Covers: CT-1, CT-2, CT-39
- Setup: TC-18's run continued to implementing.
- Action: the driver goes on until it stops.
- Assert: history holds a `claim` and a passing `epic_test` per epic, then `pass` implementing → pr; `jury/` holds `pr.json` and no `implementation-E-*` file.

### TC-20 One fix agent takes all three confirmed findings (AC-20; e2e) [agent]
- File: `tests/test_auto_e2e.py:test_one_fix_agent_per_round` (new)
- Covers: CT-37, CT-39
- Setup: refunds fixture at plan_jury, granted; a plan with three seeded faults the lenses confirm (a TC without an Assert, a CT with no binding, a coverage row missing).
- Action: the driver runs the plan gate.
- Assert: `usage.report` shows one fix-agent call in round 1 whose prompt lists all three J- IDs; the ledger's round 2 exists after that call's edits; the three findings are disposed `by: auto`.

### TC-21 The pause names the reason and the end opens an unmerged PR (AC-23; integration) [agent]
- File: `tests/test_flow.py:test_auto_pause_and_end` (new)
- Covers: CT-40, CT-41, CT-35
- Setup: `auto_on(root, "plan_jury")` with the plan ledger at round 3, rejected; a copy at `pr` with the pr ledger approved and `gh` stubbed.
- Action: `nio flow next S`; on the copy `nio jury next S pr` then `nio flow done pr S --by BY`.
- Assert: the first output holds `plan jury ran 3 rounds` and `nio flow start S --by human`; on the copy the `gh` log holds `pr create` (or `pr edit`) with `--body-file` whose text starts `# Run report: S`, no `pr merge`, and `done pr` exits non-zero with `only the human approves the pr gate`.

### TC-22 A trailing source note doesn't unground a quote (AC-24; unit) [agent]
- File: `tests/test_jury.py:test_trailing_source_note_still_grounds` (new)
- Covers: CT-14
- Setup: `setup()`; a lens finding with `- quote: "Refund an order" (tasks.md, T-11)`.
- Action: `nio jury collect`.
- Assert: the finding's status is `open`, validation not `ungrounded`.

### TC-23 A lens with every finding ungrounded is re-run (AC-25; integration) [agent]
- File: `tests/test_jury.py:test_all_ungrounded_lens_is_rerun` (new)
- Covers: CT-15
- Setup: `setup()`; logic lens with two findings quoting text absent from the spec; testability lens `none`.
- Action: `nio jury check S spec`.
- Assert: outcome is not `approved`; output names `logic` for re-run; the logic juror is `valid: false` with `every finding is ungrounded`.

### TC-24 The human reopens a dropped finding (AC-26; integration) [agent]
- File: `tests/test_jury.py:test_human_reopens_a_dropped_finding` (new)
- Covers: CT-16
- Setup: a ledger with J-2 `dropped` (ungrounded).
- Action: `nio jury dispose S spec J-2 reopen --by human --note "it is in the intake"`; then the same with `--by agent` on J-3 dropped.
- Assert: first exits 0, J-2 `status: open`, `ruling: it is in the intake`; second exits non-zero, J-3 unchanged.

### TC-25 Escalation outputs are votes, not new findings (AC-27; integration) [agent]
- File: `tests/test_jury.py:test_escalation_jurors_vote_on_the_blocker` (new)
- Covers: CT-17
- Setup: J-6 a confirmed blocker of logic, escalated; `spec-logic-2.md` re-raises J-6's cites plus one other finding; `spec-logic-3.md` re-raises J-6 only.
- Action: `nio jury collect`.
- Assert: the ledger's highest J- ID is unchanged; J-6's sources include both escalation jurors; `notes` holds one entry with the other finding's title.

### TC-26 Two refuter passes keep two files (AC-28; integration) [agent]
- File: `tests/test_jury.py:test_refuter_passes_keep_their_own_files` (new)
- Covers: CT-18
- Setup: one run with a first refuter batch answered, then a second batch asked.
- Action: write the second pass's output; `nio jury collect`.
- Assert: `spec-refuter-1.md` and `spec-refuter-2.md` both exist with their own text; the first pass's verdicts are still in the ledger.

### TC-27 A severity-raising merge keeps the kept finding confirmed (AC-29; integration) [agent]
- File: `tests/test_jury.py:test_merge_raising_severity_keeps_confirmation` (new)
- Covers: CT-19
- Setup: J-1 a minor `confirmed`, J-2 a major `confirmed`.
- Action: a refuter output `J-2: same-as J-1`; `nio jury collect`.
- Assert: J-1 is `major`, validation `confirmed`; the output has no `## Refuter batch`.

### TC-28 A fix made during escalation passes the fix check (AC-30; integration) [agent]
- File: `tests/test_jury.py:test_fix_during_escalation_checks_the_raised_version` (new)
- Covers: CT-20
- Setup: blocker J-1 raised in round 1 on FR-3; FR-3 edited and J-1 disposed `spec-fix` while round 2 (escalation) runs, round 2 storing the edited version.
- Action: `nio jury check S spec`.
- Assert: no line `spec-fix without a change`.

### TC-29 Changed plan items are named by ID (AC-31; unit) [agent]
- File: `tests/test_jury.py:test_changed_names_plan_items` (new)
- Covers: CT-21
- Setup: `plan_repo()` with a judged version; edit CT-1's `- Shape:` line and two TCs' `- Assert:` lines.
- Action: `nio jury changed S plan`.
- Assert: output names `CT-1` and the two TC IDs, and no `## Contracts` or `## Acceptance tests` section.

### TC-30 A claim during a rebuild doesn't crash (AC-32; integration) [agent]
- File: `tests/test_pack.py:test_missing_record_and_whole_old_index` (new)
- Covers: CT-23
- Setup: a memory with records A and B indexed; B's file deleted after `index.build`; a copy where `index.build` is stopped (patched to raise) before its replace.
- Action: `pack.build` on the first; `query.search` on the copy.
- Assert: the first returns without error and holds no B; the copy's `index.db` has the same row count as before the stopped rebuild and no `index.db.new` is read.

### TC-31 A failed claim leaves no worktree (AC-33; integration) [agent]
- File: `tests/test_waves.py:test_failed_claim_removes_its_worktrees` (new)
- Covers: CT-24
- Setup: E-1 claimed; E-2 independent; `flow.write` patched to raise.
- Action: `nio flow claim S --by BY`.
- Assert: exit non-zero; `git worktree list` is the same text before and after.

### TC-32 Rendering into another root warns (AC-34; integration) [agent]
- File: `tests/test_jury.py:test_jury_next_warns_on_another_root` (new)
- Covers: CT-22
- Setup: `setup()`; `CLAUDE_PROJECT_DIR` set to a temp dir.
- Action: `nio jury next S spec`.
- Assert: output has a `warning:` line holding both the repo root and the temp dir.

### TC-33 The hand-off names the skill file (AC-35; integration) [agent]
- File: `tests/test_flow.py:test_ac1_next_names_planning` (existing)
- Covers: CT-25
- Setup: as today, with and without `CLAUDECODE`.
- Action: `nio flow next S`.
- Assert: the two asserts at lines 544-548 are replaced: `next: run /nio:plan (skills/plan/SKILL.md)` and `next: run the nio:plan skill (skills/plan/SKILL.md)`; the asserts in `test_ac13_done_grilling_passes`, `test_ac22_skips_not_built` and `test_lite_route_stages` gain the same `(skills/<stage>/SKILL.md)` tail.

### TC-34 Fix tasks around a retired one pass the check (AC-36; unit) [agent]
- File: `tests/test_tasks.py:test_retired_fix_id_stays_unused` (new)
- Covers: CT-26
- Setup: approved tasks.md with fix tasks T-6 to T-9 and `retired: [T-10]`; a copy adding a fix task `T-10`.
- Action: `errs(root)` on each.
- Assert: the first has no `next free ID` error; the second has an error naming `T-10`.

### TC-35 Retiring an accepted-risk fix task keeps the tasks approval (AC-37; integration) [agent]
- File: `tests/test_flow.py:test_ac9_retired_fix_task_keeps_implementing` (existing)
- Covers: CT-26
- Setup: as today: tasks gate approved, fix task whose finding was accepted as risk.
- Action: `nio task retire S T-n`.
- Assert: `nio flow status` stage is `implementing` before and after.

### TC-36 An existing passing test is the AC's evidence (AC-38; integration) [agent]
- File: `tests/test_evidence.py:test_existing_passing_test_is_evidence` (new)
- Covers: CT-27
- Setup: tests.md entry `File: tests/test_app.py:test_old (existing)` for AC-1; the test passes and the diff doesn't touch the file; a conformance output whose `## Matches` maps AC-1 to `tests/test_app.py:<line of def test_old>`.
- Action: `nio jury evidence S pr --run R`, then `nio jury collect S pr --run R` (which runs `evidence.join`); a copy without the change where `test_old` fails.
- Assert: the evidence lists `test_old` against AC-1; the ledger has no finding `AC-1 has no passing evidence` and tasks.md gains no task; on the failing copy that finding exists.

### TC-37 A change request the flow writes lints clean (AC-39; integration) [agent]
- File: `tests/test_jury.py:test_raised_change_request_passes_check` (new)
- Covers: CT-28
- Setup: `plan_repo()`; `jury.raise_change` on a finding; `implement.block` with a handoff on another.
- Action: `nio check` on the repo.
- Assert: exit 0; no error line names either new record.

### TC-38 A plan-rooted pr finding asks for a plan change (AC-40; integration) [agent]
- File: `tests/test_evidence.py:test_plan_rooted_pr_finding_is_no_fix_task` (new)
- Covers: CT-29
- Setup: a pr ledger with a confirmed major citing `.nio/specs/S/tests.md` TC-3.
- Action: `nio jury check S pr --record`.
- Assert: tasks.md gains no task; a change record against `tests.md` exists; output holds `change asked: J-n`.

### TC-39 A reused file raises no phantom (AC-41; integration) [agent]
- File: `tests/test_evidence.py:test_unchanged_file_is_no_phantom` (new)
- Covers: CT-30
- Setup: T-2 `Files: \`app.py\`, \`lib/util.py\` (unchanged)`; the diff touches only `app.py`.
- Action: `nio jury evidence S pr`.
- Assert: no finding text holds `lib/util.py isn't in the epic's diff`.

### TC-40 The pr gate runs the test-proof lens (AC-42; integration) [agent]
- File: `tests/test_evidence.py:test_pr_gate_plans_test_proof` (new)
- Covers: CT-31
- Setup: an effort at pr whose diff adds a test, `gh` stubbed.
- Action: `nio jury next S pr` (the pr gate, not an `implementation-E-n` one).
- Assert: the lens line names `test-proof`; `src/nio/agents/test-proof.md` has `## At the pr gate`.

### TC-41 A failed epic's re-claim carries the failure; the third blocks it (AC-43; integration) [agent]
- File: `tests/test_implement.py:test_failed_epic_reclaim_and_block` (new)
- Covers: CT-1, CT-2, CT-4
- Setup: E-1 claimed, T-2's test failing.
- Action: finish; claim; finish; claim; finish; claim.
- Assert: the 2nd claim's pack holds T-2's test name and the tail; after the 3rd finish `epics()["E-1"] == ("blocked", 3)` and `waiting.why` is `E-1 blocked after 3 failed test runs`; the last claim exits non-zero with `E-1 is blocked`.

### TC-42 Two independent epics claim at once in their own trees (AC-44; integration) [agent]
- File: `tests/test_waves.py:test_two_independent_epics_claim_at_once` (new)
- Covers: CT-1
- Setup: `impl()` (E-2 independent of E-1), `budgets.parallel` 2.
- Action: `nio flow claim S --by A`; `nio flow claim S --by B`.
- Assert: both exit 0, naming E-1 and E-2; the second prints `worktree:`; `git worktree list` has two lines (the checkout and E-2's tree). Then E-2's code and test are written in its worktree only and `nio flow finish S E-2 --by B` exits 0, and `git show --name-only HEAD` holds E-2's files; a second `finish` started while the first runs (`running.json` naming it) exits non-zero with `E-2's tests are running`.

### TC-43 An in-flight effort converts at its next claim (AC-45; integration) [agent]
- File: `tests/test_implement.py:test_in_flight_effort_converts_per_epic` (new)
- Covers: CT-1, CT-2, CT-4
- Setup: `impl()` with history: E-1's T-1, T-2 `task_done` under the old flow (their commits made); E-2 of three tasks with T-3 done.
- Action: `nio flow claim S --by BY` → it names E-1 at testing; `nio flow finish S E-1 --by BY` (passing); `nio flow claim S --by BY`.
- Assert: history holds a passing `epic_test` for E-1 before any later `claim`; T-1, T-2, T-3 commits are unchanged; the last claim names E-2 and its pack lists T-4, T-5 only.

### TC-44 The executability juror flags a task blocked until a later epic (AC-46; e2e) [agent]
- File: `tests/test_lenses.py:test_executability_flags_a_later_epic_guard` (new)
- Covers: CT-32
- Setup: `NIO_E2E=1`; a tasks.md where E-1's T-2 adds a check that every TC file exists, and only E-3's T-7 writes the file.
- Action: run the executability card on its pack.
- Assert: the output holds a finding citing both `T-2` and `T-7`.

### TC-45 A hung or broken run is one failed run (AC-47; integration) [agent]
- File: `tests/test_implement.py:test_hung_or_broken_run_counts_as_failed` (new)
- Covers: CT-2
- Setup: E-1 claimed; `implement.EPIC_LIMIT` set to 2 seconds; T-1's test sleeps 10 s and prints 80 lines; a copy whose test file has a syntax error.
- Action: `nio flow finish S E-1 --by BY` on each.
- Assert: both exit non-zero; first's `epic_test` `cause` is the time limit and the run ended within 5 s; second's `cause` names a collection error; each epic reads `("failed", 1)`, not `testing`; each `tail` has at most 50 lines.

### TC-46 A risky plan gate approves itself under auto (AC-48; integration) [agent]
- File: `tests/test_flow.py:test_auto_approves_a_risky_gate` (new)
- Covers: CT-35
- Setup: `effort("plan_jury", risk="[migration]")`, granted; the plan ledger approved.
- Action: `nio flow done plan_jury S --by BY`.
- Assert: exit 0; `git log -1 --format=%s` is `nio: approve plan`; the `pass` line's evidence `auto.grant` equals the grant line's 1-based number.

### TC-47 The `--by human` steps under auto: four allowed, three refused (AC-49; integration) [agent]
- File: `tests/test_flow.py:test_auto_human_steps` (new)
- Covers: CT-36, CT-4, CT-33
- Setup: an auto effort at implementing with: a task blocked on a change request, a failing guard to override, unseen overrides, a capped batch; a copy with E-1 blocked by 3 failed runs; a copy at pr with an approved ledger.
- Action: as `BY`: `nio flow unblock`, `nio flow done … --human "x"`, `nio flow seen`, `nio jury rule … --by BY`; then `nio flow approve S`, `nio flow manual S`, `nio flow unblock S E-1 --human x`.
- Assert: the first four exit 0 and each new history line has `who.auto` equal to the grant line (the rule's `ruling` line too, and the ledger `by: auto`); the last three exit non-zero, history and state.json are byte-identical, and `nio flow status` shows the effort waiting with the reason.

### TC-57 A live old wave claim converts and its work is kept (AC-45; integration) [agent]
- File: `tests/test_implement.py:test_live_old_wave_claim_converts` (new)
- Covers: CT-1, CT-2
- Setup: a history and state written by the old flow: `claims` `{"task": "T-1", "wave": ["T-1", "T-2"]}` with T-2's worktree holding uncommitted code and its test; E-1's tests pass once both trees are combined.
- Action: `nio flow claim S --by BY`; `nio flow finish S E-1 --by BY`.
- Assert: the claim names E-1 as already claimed with T-2's worktree; `finish` exits 0; `git show --name-only HEAD` holds T-2's files; the worktree is gone from `git worktree list`.

### TC-58 The old flow reads an effort the new flow closed (AC-45; integration) [agent]
- File: `tests/test_implement.py:test_rollback_old_status_reads_new_history` (new)
- Covers: CT-2, CT-4
- Setup: an effort whose E-1 closed under the new flow (`claim` with `epic`, `epic_test`, `task_done` lines), no live claim; the old module loaded from `git show 2153568:src/nio/implement.py` into a temp file.
- Action: old `implement.status(root, S)`.
- Assert: T-1 and T-2 read `done`; no exception.

## Quality tests

### TC-48 One test run per hand-back (NFR-1; integration) [agent]
- File: `tests/test_implement.py:test_one_run_per_hand_back` (new)
- Covers: CT-2
- Setup: E-1 of two tasks claimed; its test command appends a line to `runs.log` each time it runs.
- Action: `nio flow finish S E-1 --by BY`.
- Assert: `runs.log` has exactly 1 line.

### TC-49 At most one agent per epic attempt (NFR-2; integration) [agent]
- File: `tests/test_implement.py:test_one_claim_one_card_per_attempt` (new)
- Covers: CT-1, CT-8
- Setup: `impl()`.
- Action: claim E-1; read the output and `skills/implement/SKILL.md` step 2.
- Assert: the output has exactly one `card:` line; the skill says to start one agent per claimed epic.

## Misuse tests

### TC-50 "Tests pass" without the flow's run closes nothing (UJ-1 misuse; integration) [agent]
- File: `tests/test_implement.py:test_no_close_without_the_flows_run` (new)
- Covers: CT-2, CT-4
- Setup: E-1 claimed, tests passing, no `nio flow finish`.
- Action: `nio flow claim S --by BY`; `nio flow next S`.
- Assert: E-1 still reads `claimed`; no `task_done` for T-1 or T-2; `next` doesn't name the pr gate.

### TC-51 A trivially passing test is judged at the pr gate (UJ-1 misuse; integration) [agent]
- File: `tests/test_evidence.py:test_pr_test_proof_pack_lists_added_tests` (new)
- Covers: CT-31
- Setup: an effort at pr whose diff adds `def test_t(): assert True`.
- Action: `nio jury next S pr --run R`.
- Assert: the test-proof pack names `test_t` among the added tests to judge.

### TC-52 A second driver can't take the same epic (UJ-1 misuse; integration) [agent]
- File: `tests/test_waves.py:test_second_driver_gets_another_epic_or_none` (new)
- Covers: CT-1
- Setup: `impl()` where E-2 depends on E-1; E-1 claimed by A.
- Action: `nio flow claim S --by B`.
- Assert: exit non-zero with `no epic ready; E-2 waits on E-1`; E-1's claim is unchanged.

### TC-53 An agent can't grant itself auto (UJ-2 misuse; integration) [agent]
- File: `tests/test_flow.py:test_agent_cannot_grant_auto_on_done` (new)
- Covers: CT-33, CT-34
- Setup: `effort("drafting")` with a passing draft.
- Action: `nio flow done drafting S --auto --by BY`.
- Assert: exit non-zero with `only the human grants auto`; `auto: false`; no `pass` or `grant` line added.

### TC-54 A fix that changes the human's words pauses the run (UJ-2 misuse; integration) [agent]
- File: `tests/test_jury.py:test_auto_fix_touching_a_human_line_pauses` (new)
- Covers: CT-38, CT-37
- Setup: `auto_on` at spec_jury; round 1 judged; a fix edits FR-3, tagged `[human]`.
- Action: `nio jury check S spec`.
- Assert: outcome `human`; reasons hold `[human] line changed: FR-3`; no round 2 starts.

### TC-55 A gate looping without closing findings pauses (UJ-2 misuse; integration) [agent]
- File: `tests/test_flow.py:test_auto_no_progress_pauses` (new)
- Covers: CT-41
- Setup: `auto_on` at plan_jury; round 2 closed none of round 1's findings.
- Action: `nio flow next S`.
- Assert: `waiting.why` holds `closed none of round 1's findings`; the output holds `nio flow start S --by human`.

### TC-56 Without the mod the skills still forbid a poll loop (UJ-3 misuse; unit) [agent]
- File: `tests/test_talk.py:test_drivers_waiting_has_no_poll_loop` (new)
- Covers: CT-13, CT-11
- Setup: the repo files.
- Action: read the "Waiting for long work" text of `skills/implement/SKILL.md` and `skills/jury/SKILL.md`.
- Assert: each names `nio flow finish` and `nio jury evidence` as long commands, holds `no sleep, no loop`, and names no `nio flow green`.
