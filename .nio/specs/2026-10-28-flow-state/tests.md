---
slug: 2026-10-28-flow-state
retired: []                      # TC IDs removed from this plan; never reused
---
# Tests: flow state

## Acceptance tests
<!-- Every test is a `test_*` function in tests/test_flow.py, run as a plain script (RF-16). Shared helpers there:
- `effort(stage, slug="2026-10-20-refunds", risk="[]", route="full")`: a temporary git repo (as tests/test_records.py:repo)
  holding the refunds spec and plan fixtures (tests/fixtures/spec, tests/fixtures/plan) copied to the dated folder with
  `slug:` set, brought to `stage` with real files: intake.md; a spec passing `nio check spec --gate`; real jury rounds
  (as tests/test_jury.py:approve_spec, approve_plan) and their `nio: approve <gate>` commits; tasks.md from
  tests/fixtures/tasks. No history.jsonl unless the test says so.
- `history(root, slug, *lines)`: writes history.jsonl and state.json through `flow.record`, passing each line's `at=` so ordering tests control the times; hashes match because `record` computes them over the state it writes.
- `cli(root, *args)`: runs `uv run nio flow ...` in `root` as a subprocess, adding `--by "orchestrator / test / test"` to the writing subcommands (`start`, `done`, `park`, `abandon`, `seen`) unless the test says "without --by"; returns (exit code, stdout + stderr).
- In-process calls pass `by="orchestrator / test / test"` wherever a line is expected, `next_step` included; a `next_step` without `by=` records nothing.
- `snap(root, slug)`: the bytes of every file in the effort folder, to compare before and after.
"S" below is `2026-10-20-refunds`. The 4 tests of #42 that wait on #43 stay as they are. -->

### TC-1 next names planning, the plan skill, spec.md and the done command (AC-1; unit) [default]
- File: `tests/test_flow.py:test_ac1_next_names_planning` (new)
- Covers: CT-6, CT-9
- Setup: `effort("planning")`: spec gate approved and committed `nio: approve spec`; no plan files.
- Action: `flow.next_step(root, "S")`.
- Assert: the output contains `state: planning`, `skill: @nio:plan`, `spec.md` on the `inputs:` line, and a line starting `done: nio flow done planning 2026-10-20-refunds --by`.

### TC-2 an unanswered grill question waits for the human (AC-2; unit) [default]
- File: `tests/test_flow.py:test_ac2_open_question_waits` (new)
- Covers: CT-6, CT-9
- Setup: `effort("grilling")` whose `grill.md` ends with `## Asked · Q4 · OP-3 · 2026-10-20` and a `Question:` line, with no `## Q4` entry after it.
- Action: `flow.next_step(root, "S")`.
- Assert: the output contains `waiting_for_human` and `Q4`; it contains no `@nio:` at all, so no skill other than the grill is named.

### TC-3 the effort just started is the current one, with no pointer file (AC-3; integration) [default]
- File: `tests/test_flow.py:test_ac3_start_makes_current` (new)
- Covers: CT-4, CT-10, CT-16
- Setup: two efforts, `2026-10-20-refunds` with a history line at `2026-10-20T10:00:00Z` and `2026-10-21-refunds` with one at `2026-10-21T10:00:00Z`; list every file under the repo except `.git/`.
- Action: `cli(root, "start", "2026-10-20-refunds")`, then `cli(root, "next")`.
- Assert: the `next` output contains `effort: 2026-10-20-refunds`; every file created or changed is under `.nio/specs/2026-10-20-refunds/` or `.nio/specs/2026-10-21-refunds/`.

### TC-4 no current effort fails and lists what it could start (AC-4; unit) [default]
- File: `tests/test_flow.py:test_ac4_no_current_effort` (new)
- Covers: CT-4
- Setup: efforts `2026-10-20-refunds` and `2026-10-21-refunds` with no history, and the legacy folder `.nio/specs/grilling/`.
- Action: `flow.pick(root)`.
- Assert: it raises `ValueError`; the message names `2026-10-20-refunds`, `2026-10-21-refunds` and `nio flow start`, and not `grilling`; no `state.json` or `history.jsonl` exists anywhere.

### TC-5 start on an unknown slug fails and writes nothing (AC-5; unit) [default]
- File: `tests/test_flow.py:test_ac5_unknown_slug` (new)
- Covers: CT-4, CT-10
- Setup: `effort("planning")`.
- Action: `flow.start(root, "2026-10-29-nothing")`.
- Assert: it raises `ValueError` naming `2026-10-29-nothing`; `.nio/specs/2026-10-29-nothing` does not exist; no `state.json` or `history.jsonl` was created anywhere.

### TC-6 start creates both files and one start line (AC-6; unit) [default]
- File: `tests/test_flow.py:test_ac6_start_creates_files` (new)
- Covers: CT-1, CT-2, CT-10
- Setup: `effort("planning")` with no `state.json`.
- Action: `flow.start(root, "S", by="orchestrator / claude-code / opus")`.
- Assert: `state.json` and `history.jsonl` exist; `history.jsonl` has exactly 1 line, `kind` `start`, with `who.role` `orchestrator`, `who.host` `claude-code`, `who.model` `opus`, an `at` parsing as an ISO time, and a `run` key; its `state` equals the sha256 of `state.json`.

### TC-7 state.json holds none of the ledger's facts (AC-7; unit) [default]
- File: `tests/test_flow.py:test_ac7_state_keys` (new)
- Covers: CT-1, CT-2
- Setup: `effort("planning")`, then `flow.start`.
- Action: read `state.json`.
- Assert: its keys are a subset of `{"auto", "pause", "abandon", "waiting", "claims", "attempts", "run"}`; no key or value names `outcome`, `round`, `version`, `Q` IDs or `C-` IDs.

### TC-8 a ledger edited to rejected shows without any flow write (AC-8; unit) [default]
- File: `tests/test_flow.py:test_ac8_ledger_read_live` (new)
- Covers: CT-6
- Setup: `effort("planning")`, then `flow.start`; `spec.md` unchanged since the approved round; take the bytes of `state.json`.
- Action: set `outcome` to `rejected` in `jury/spec.json`, then `flow.next_step(root, "S")`.
- Assert: the output contains `state: grilling`; `state.json` is byte-identical to before.

### TC-9 an unknown key in state.json stops every command (AC-9; unit) [default]
- File: `tests/test_flow.py:test_ac9_unknown_state_key` (new)
- Covers: CT-1
- Setup: `effort("planning")`, then `flow.start`; add `"stage": "done"` to `state.json` and append a matching history line through a test-only write that fixes the hash, so only the key is wrong.
- Action: each of `next`, `start S` and `park S x` through `cli`.
- Assert: each exits non-zero and its output contains `state.json` and `stage`. (`done`, `abandon` and `seen` are TC-78, TC-79 and TC-80.)

### TC-10 a bad middle history line stops next and shows broken in status (AC-10; unit) [default]
- File: `tests/test_flow.py:test_ac10_bad_history_line` (new)
- Covers: CT-1, CT-12
- Setup: `effort("planning")` with a 5-line `history.jsonl` whose line 3 is `{not json`; a second effort `2026-10-21-refunds`, started.
- Action: `cli(root, "next", "S")` and `cli(root, "status")`.
- Assert: `next` exits non-zero with `history.jsonl` and `line 3` in its output; `status` exits 0, one line contains `2026-10-20-refunds · broken: history.jsonl, line 3`, and another line starts with `2026-10-21-refunds`.

### TC-11 no skill or card tells an agent to edit the flow files (AC-11; unit) [default]
- File: `tests/test_flow.py:test_ac11_no_hand_edit_instruction` (new)
- Covers: CT-18
- Setup: the repository itself.
- Action: read every `skills/*/SKILL.md` and `src/nio/agents/*.md`.
- Assert: every line that mentions `state.json` or `history.jsonl` also contains `nio flow`, apart from the flow-rule line itself, whose text is "never edit them"; no line matches `(edit|write|append to|change) .*(state\.json|history\.jsonl)` outside that rule line.

### TC-12 a second writer is refused while the first writes (AC-12; integration) [default]
- File: `tests/test_flow.py:test_ac12_second_writer_refused` (new)
- Covers: CT-3, CT-16
- Setup: `effort("drafting")`, then `flow.start`; count the history lines.
- Action: inside `with flow.lock(root, "S"):` run `git check-ignore .nio/specs/S/flow.lock` and `cli(root, "park", "S", "x")`, then, still inside, finish the first call's write with `flow.record` of one `pass` line.
- Assert: `git check-ignore` exits 0 while the lock is held; the `park` call exits non-zero and its output contains `being written`; after the block, `history.jsonl` has exactly one more line than before, of kind `pass`; `flow.lock` no longer exists.

### TC-13 a passing grill gate moves to spec_jury with one line (AC-13; unit) [default]
- File: `tests/test_flow.py:test_ac13_done_grilling_passes` (new)
- Covers: CT-2, CT-5, CT-11
- Setup: `effort("grilling")` whose spec passes `nio check spec --gate`, started.
- Action: `flow.done(root, "grilling", "S")`.
- Assert: exit 0; `next` contains `state: spec_jury`; exactly 1 new line: `kind` `pass`, `from` `grilling`, `to` `spec_jury`, `evidence.paths` containing `spec.md` and `evidence.output` a 64-hex hash.

### TC-14 a failing grill gate names the open point and the default (AC-14; unit) [default]
- File: `tests/test_flow.py:test_ac14_done_grilling_fails` (new)
- Covers: CT-5, CT-11
- Setup: `effort("grilling")`, started; the spec has `- **OP-3** (decision; FR-1) Which currency?` under `## Open points` and FR-2 tagged `[default]`.
- Action: `flow.done(root, "grilling", "S")`.
- Assert: non-zero exit; the output contains `OP-3` and `FR-2`; `next` still contains `state: grilling`; `history.jsonl` line count unchanged.

### TC-15 a worker's handoff never passes the spec gate (AC-15; unit) [default]
- File: `tests/test_flow.py:test_ac15_handoff_is_not_evidence` (new)
- Covers: CT-5, CT-11
- Setup: `effort("spec_jury")` whose spec ledger was rejected in round 1 and the spec edited since (stage spec_jury, standing `rerun`), started; `.nio/specs/S/handoff.md` says `all tests pass`.
- Action: `flow.done(root, "spec_jury", "S")`.
- Assert: non-zero exit; the output contains `the spec jury's outcome is rerun`; it does not contain `all tests pass` or `handoff.md`.

### TC-16 an AC with no task fails tasking (AC-16; unit) [default]
- File: `tests/test_flow.py:test_ac16_done_tasking_fails` (new)
- Covers: CT-5, CT-11
- Setup: `effort("tasking")`, started, whose `tasks.md` has no task serving AC-4.
- Action: `flow.done(root, "tasking", "S")`.
- Assert: non-zero exit; the output contains the line `tasks.check(root, "S")[0]` gives for AC-4 (it names `AC-4`).

### TC-17 done on a stage not reached names the current one (AC-17; unit) [default]
- File: `tests/test_flow.py:test_ac17_stage_not_reached` (new)
- Covers: CT-11
- Setup: `effort("drafting")` (only `intake.md` and a spec missing a mandatory section), started.
- Action: `flow.done(root, "planning", "S")`.
- Assert: non-zero exit; the message contains `drafting`; `history.jsonl` line count unchanged.

### TC-18 done on a passed stage changes nothing (AC-18; unit) [default]
- File: `tests/test_flow.py:test_ac18_stage_already_passed` (new)
- Covers: CT-11
- Setup: `effort("grilling")`, started; snapshot `history.jsonl` and `state.json` bytes.
- Action: `flow.done(root, "drafting", "S")`.
- Assert: exit 0; both files byte-identical to the snapshot.

### TC-19 --commit makes one approval commit of the effort folder (AC-19; integration) [default]
- File: `tests/test_flow.py:test_ac19_commit_on_gate` (new)
- Covers: CT-11, CT-16
- Setup: `effort("spec_jury")` with the spec ledger approved (`unresolved: 0`) and not committed, started; an unrelated untracked file `notes.txt` at the repo root.
- Action: `cli(root, "done", "spec_jury", "S", "--commit")`.
- Assert: exit 0; `git log -1 --format=%s` is `nio: approve spec`; `git show --name-only HEAD` lists `.nio/specs/S/history.jsonl` and `.nio/specs/S/jury/spec.json`, and every listed path starts with `.nio/specs/S/`; `notes.txt` is still untracked.

### TC-20 a non-gate pass makes no commit (AC-20; integration) [default]
- File: `tests/test_flow.py:test_ac20_no_commit_off_gate` (new)
- Covers: CT-11
- Setup: `effort("drafting")` whose spec passes `nio check spec`, started; record `HEAD`.
- Action: `cli(root, "done", "drafting", "S")`.
- Assert: exit 0; `HEAD` unchanged; `git status --porcelain` lists `.nio/specs/S/history.jsonl`.

### TC-21 a rejected commit records nothing (AC-21; integration) [default]
- File: `tests/test_flow.py:test_ac21_commit_fails` (new)
- Covers: CT-11
- Setup: `effort("spec_jury")` with the ledger approved and uncommitted, started; a `.git/hooks/pre-commit` that prints `hook says no` and exits 1; `.nio/specs/S/notes.md` committed, then edited twice with only the first edit staged (`git add`), so it is partly staged; snapshot `history.jsonl`, `state.json`, `notes.md`, `git ls-files -s` and `git diff --cached`.
- Action: `cli(root, "done", "spec_jury", "S", "--commit")`.
- Assert: non-zero exit; the output contains `hook says no`; `history.jsonl`, `state.json`, `notes.md`, `git ls-files -s` and `git diff --cached` equal the snapshot; no `state.json.new` exists; `next` contains `state: spec_jury`.

### TC-22 not-built stages are skipped on the record (AC-22; unit) [default]
- File: `tests/test_flow.py:test_ac22_skips_not_built` (new)
- Covers: CT-2, CT-6, CT-11
- Setup: `effort("drafting")` whose spec passes `nio check spec`, started; count the lines.
- Action: `flow.done(root, "drafting", "S")`, then `flow.next_step(root, "S")`.
- Assert: exactly 3 new lines, in order: `pass` from `drafting`; `skip` from `researching` with `reason` `skipped: not built`; `skip` from `advocate_walking` with `reason` `skipped: not built`, `to` `grilling`; `next` contains `state: grilling` and `skipped: researching, advocate_walking (not built)`.

### TC-23 implementing waits for the human (AC-23; unit) [default]
- File: `tests/test_flow.py:test_ac23_implement_not_built` (new)
- Covers: CT-6, CT-9
- Setup: `effort("implementing")`: tasks gate approved and committed `nio: approve tasks`.
- Action: `flow.next_step(root, "S")`.
- Assert: the output contains `waiting_for_human: implement not built` and no `@nio:`.

### TC-24 a rejected spec round sends the effort back to grilling (AC-24; unit) [default]
- File: `tests/test_flow.py:test_ac24_spec_rejected` (new)
- Covers: CT-6
- Setup: `effort("spec_jury")` whose spec jury round 1 is recorded `rejected` (as tests/test_jury.py:first_review, before the fixes), spec unchanged since.
- Action: `flow.next_step(root, "S")`.
- Assert: the output contains `state: grilling` and `round 1`.

### TC-25 a rejected tasks round sends the effort back to tasking (AC-25; unit) [default]
- File: `tests/test_flow.py:test_ac25_tasks_rejected` (new)
- Covers: CT-6
- Setup: `effort("tasks_jury")` whose tasks ledger round 1 has `outcome: rejected`, `tasks.md` unchanged since.
- Action: `flow.next_step(root, "S")`.
- Assert: the output contains `state: tasking`.

### TC-26 an override passes a failing check and keeps its own line (AC-26; unit) [default]
- File: `tests/test_flow.py:test_ac26_override` (new)
- Covers: CT-2, CT-11
- Setup: `effort("grilling")`, started, whose spec still has OP-3 under `## Open points`.
- Action: `flow.done(root, "grilling", "S", human="OP-3 is settled in Q5")`.
- Assert: exit 0; `next` contains `state: spec_jury`; exactly 1 new line: `kind` `override`, `from` `grilling`, `reason` `OP-3 is settled in Q5`, `evidence.output_text` containing `OP-3`.

### TC-27 identical overrides on two efforts are two lines (AC-27; unit) [default]
- File: `tests/test_flow.py:test_ac27_overrides_not_merged` (new)
- Covers: CT-2, CT-11
- Setup: efforts `2026-10-20-refunds` and `2026-10-21-refunds`, both at grilling with the same OP-3, both started.
- Action: `flow.done(root, "grilling", slug, human="same reason")` on each.
- Assert: each `history.jsonl` has exactly 1 line of kind `override`, each with `reason` `same reason`.

### TC-28 an empty override reason is refused (AC-28; unit) [default]
- File: `tests/test_flow.py:test_ac28_empty_reason` (new)
- Covers: CT-11
- Setup: `effort("grilling")`, started, with OP-3 open.
- Action: `flow.done(root, "grilling", "S", human="")`, then again with `human="   "`.
- Assert: each raises `ValueError` whose message contains `reason`; `history.jsonl` line count unchanged.

### TC-29 a gate the human closed passes as an override (AC-29; unit) [default]
- File: `tests/test_flow.py:test_ac29_jury_closed_by_human` (new)
- Covers: CT-5, CT-11
- Setup: `effort("spec_jury")` whose spec jury is not approved, then `jury.check(root, "S", "spec", record=True, human="pack bug")`; started.
- Action: `flow.done(root, "spec_jury", "S")`.
- Assert: exit 0; the new line has `kind` `override`, `from` `spec_jury`, `reason` `pack bug`; `HEAD` unchanged.

### TC-30 --human on a passing guard is a normal pass (AC-30; unit) [default]
- File: `tests/test_flow.py:test_ac30_human_on_passing_guard` (new)
- Covers: CT-11
- Setup: `effort("grilling")` passing `nio check spec --gate`, started.
- Action: `flow.done(root, "grilling", "S", human="just in case")`.
- Assert: exactly 1 new line, `kind` `pass`, `reason` `just in case`; no line of kind `override`.

### TC-31 status lists five efforts, newest first, with their words (AC-31; integration) [default]
- File: `tests/test_flow.py:test_ac31_status_five_efforts` (new)
- Covers: CT-12, CT-16
- Setup: five dated efforts: A working at planning (last line `2026-10-25T10:00:00Z`), B at grilling with an unanswered `## Asked · Q4` (last line `2026-10-24T10:00:00Z`), C parked "waiting on #43" (last line `2026-10-23T10:00:00Z`), D at implementing (last line `2026-10-22T10:00:00Z`), E with no history whose newest commit is dated `2026-10-21T10:00:00Z` (`GIT_COMMITTER_DATE`).
- Action: `cli(root, "status")`.
- Assert: exactly 5 lines, starting with A, B, C, D, E in that order; they contain `working`, `waiting_for_human: Q4`, `parked: waiting on #43`, `waiting_for_human: implement not built`, and E's contains `2026-10-21 10:00`.

### TC-32 an undated folder is legacy and never written (AC-32; unit) [default]
- File: `tests/test_flow.py:test_ac32_legacy_folder` (new)
- Covers: CT-4, CT-12
- Setup: `.nio/specs/grilling/` holding a `spec.md`; `snap` it.
- Action: `flow.status(root)`, then `flow.start(root, "grilling")`.
- Assert: the status line for it contains `grilling · legacy`; `start` raises `ValueError`; `snap` is unchanged.

### TC-33 park records the reason (AC-33; unit) [default]
- File: `tests/test_flow.py:test_ac33_park` (new)
- Covers: CT-13
- Setup: `effort("planning")`, started.
- Action: `flow.park(root, "S", "waiting on #43")`.
- Assert: the status line contains `parked: waiting on #43`; exactly 1 new line, `kind` `park`, `reason` `waiting on #43`.

### TC-34 next resumes a parked effort (AC-34; unit) [default]
- File: `tests/test_flow.py:test_ac34_next_resumes` (new)
- Covers: CT-9
- Setup: `effort("planning")`, started, then parked.
- Action: `flow.next_step(root, "S", by="orchestrator / test / test")`.
- Assert: the status line contains `working`; exactly 1 new line, `kind` `resume`; `state.json`'s `pause` is null.

### TC-35 park refuses an empty reason and a done effort (AC-35; unit) [default]
- File: `tests/test_flow.py:test_ac35_park_refusals` (new)
- Covers: CT-13
- Setup: `effort("planning")`, started; a second effort `2026-10-21-refunds` at implementing, started, then passed with `flow.done(root, "implementing", "2026-10-21-refunds", human="shipped by hand")`, so its stage is `done`.
- Action: `flow.park(root, "S", "")` and `flow.park(root, "2026-10-21-refunds", "x")`.
- Assert: each raises `ValueError`; neither `history.jsonl` gained a line.

### TC-36 a run names its effort and the line carries it (AC-36; integration) [default]
- File: `tests/test_flow.py:test_ac36_run_names_effort` (new)
- Covers: CT-17, CT-11
- Setup: `effort("planning")` with plan files passing `nio check plan --gate`, started.
- Action: `uv run nio run S planning` (prints the run ID R), then `cli(root, "done", "planning", "S")`.
- Assert: `.nio/runs/R/flow.json` has `effort` S and `stage` `planning`; the new history line's `run` is R.

### TC-37 nio run with no arguments works as today (AC-37; integration) [default]
- File: `tests/test_flow.py:test_ac37_plain_run` (new)
- Covers: CT-17
- Setup: `tests/test_records.py:repo()`.
- Action: `uv run nio run`.
- Assert: exit 0; stdout is one line matching `R-\d{6}-[a-z2-7]{4}`; `.nio/runs/<that ID>/promote.md` exists; no `flow.json` in it.

### TC-38 a pending change waits and moves back once (AC-38; unit) [default]
- File: `tests/test_flow.py:test_ac38_pending_change` (new)
- Covers: CT-7, CT-9
- Setup: `effort("tasking")`, started (last line `to` `tasking`); a change record with `outcome: pending` and `against: ".nio/specs/S/plan.md"`, ID C.
- Action: `flow.next_step(root, "S", by="orchestrator / test / test")` twice.
- Assert: the first output contains `waiting_for_human`, C and `planning`; after it, exactly 1 new line: `kind` `back`, `from` `tasking`, `to` `planning`, `change` C; the second call adds no line.

### TC-39 an approved tasks.md edited later goes back to the tasks jury (AC-39; unit) [default]
- File: `tests/test_flow.py:test_ac39_edited_tasks` (new)
- Covers: CT-7, CT-6
- Setup: `effort("implementing")`, started; append a line to a planned task in `tasks.md` (above any `#### Fixes`); J = its blob at the `nio: approve tasks` commit, K = `git hash-object` of the planned part now.
- Action: `flow.next_step(root, "S")`.
- Assert: the output contains `state: tasks_jury`; the new `back` line has `change.file` `tasks.md`, `change.judged` J and `change.current` K.

### TC-40 a rejected change record moves nothing (AC-40; unit) [default]
- File: `tests/test_flow.py:test_ac40_rejected_change` (new)
- Covers: CT-7
- Setup: `effort("tasking")`, started; a change record with `outcome: rejected` against `.nio/specs/S/plan.md`.
- Action: `flow.next_step(root, "S")`.
- Assert: the output contains `state: tasking`; `history.jsonl` line count unchanged.

### TC-41 done planning is refused while a change is pending (AC-41; unit) [default]
- File: `tests/test_flow.py:test_ac41_done_refused_while_pending` (new)
- Covers: CT-7, CT-11
- Setup: TC-38's effort after its `next` (back in planning), plan files passing `nio check plan --gate`.
- Action: `flow.done(root, "planning", "S")`.
- Assert: it raises `ValueError` whose message contains C and `outcome: pending`; no new line.

### TC-42 a parked effort moves back and stays parked (AC-42; unit) [default]
- File: `tests/test_flow.py:test_ac42_parked_moves_back` (new)
- Covers: CT-7, CT-12
- Setup: `effort("tasking")`, started, parked "on hold"; a pending change record against `.nio/specs/S/research.md`.
- Action: `flow.status(root)`.
- Assert: S's line contains `· grilling ·` and `parked: on hold`.

### TC-43 three plan rounds pause an auto effort (AC-43; unit) [default]
- File: `tests/test_flow.py:test_ac43_round_cap` (new)
- Covers: CT-8, CT-9
- Setup: `effort("plan_jury")`, started, `"auto": true` set through `flow.record`; the plan ledger at `round` 3, outcome `rejected`, plan changed since (stage plan_jury), open findings J-2 and J-5.
- Action: `flow.next_step(root, "S", by="orchestrator / test / test")`.
- Assert: the output contains no `@nio:`; it contains `3 rounds`, `J-2` and `J-5`; a `pause` line was appended.

### TC-44 round 2 that closed nothing pauses (AC-44; unit) [default]
- File: `tests/test_flow.py:test_ac44_no_progress` (new)
- Covers: CT-8, CT-9
- Setup: as TC-43 but the spec gate (stage spec_jury), ledger `round` 2 recorded `rejected`, J-1 raised in round 1 still `open`, no finding with `fixed_in` 2, `spec.md` edited since round 2 (stage spec_jury).
- Action: `flow.next_step(root, "S")`.
- Assert: no `@nio:`; the output contains `round 2` and `J-1`.

### TC-45 the fifth jury suspends on the cap (AC-45; unit) [default]
- File: `tests/test_flow.py:test_ac45_jury_cap` (new)
- Covers: CT-8, CT-9
- Setup: auto effort at plan_jury whose ledgers' rounds sum to 4 (spec 2, plan 2) and whose `collected` maps hold 7 keys in all; plan round 2 has a finding with `fixed_in` 2 and no finding from round 1 is still `open`, so only the cap applies (not FR-39); `.nio/config.json` has `"budgets": {"juries": 4}`.
- Action: `flow.next_step(root, "S", by="orchestrator / test / test")`, then `flow.status(root)`.
- Assert: the status line contains `suspended: cap`; `next` contains `juries used: 4` and `subagent runs used: 7`.

### TC-46 three identical failures suspend as stuck (AC-46; unit) [default]
- File: `tests/test_flow.py:test_ac46_stuck` (new)
- Covers: CT-8, CT-11
- Setup: auto effort at tasking whose `tasks.md` leaves AC-4 with no task.
- Action: `flow.done(root, "tasking", "S")` 3 times, then a 4th time.
- Assert: 3 `fail` lines with the same guard and `evidence.output`; the status line contains `suspended: stuck`; the 4th call is refused and its output names no `@nio:`.

### TC-47 three different failures don't suspend (AC-47; unit) [default]
- File: `tests/test_flow.py:test_ac47_not_stuck` (new)
- Covers: CT-8, CT-11
- Setup: as TC-46.
- Action: `done tasking` 3 times, removing a different task's `Serves:` line before each call so each output differs.
- Assert: 3 `fail` lines with 3 different `evidence.output` hashes; the status line contains `working`.

### TC-48 an auto effort waits before a change moves it back (AC-48; unit) [default]
- File: `tests/test_flow.py:test_ac48_auto_change_pause` (new)
- Covers: CT-8, CT-10
- Setup: auto effort at tasking, started; a pending change record C against `.nio/specs/S/plan.md`.
- Action: `flow.next_step`, then `flow.start(root, "S")`, then `flow.next_step`.
- Assert: the first `next` contains `waiting_for_human`, C and `state: tasking`, and no `back` line exists; after `start`, a `resume` line naming C and a `back` line to `planning` exist, and the second `next` contains `state: planning`.

### TC-49 a suspended effort speaks in the human's shape (AC-49; unit) [default]
- File: `tests/test_flow.py:test_ac49_suspended_shape` (new)
- Covers: CT-9, CT-10
- Setup: TC-46's suspended effort.
- Action: `flow.next_step`, then `flow.start(root, "S")`, then `flow.next_step`.
- Assert: the first output's first line is `Run this command to resume`, a line is `nio flow start 2026-10-20-refunds --by human`, the last line starts with `Refs:`, and it contains no `@nio:`; after `start` the output contains `skill: @nio:tasks`.

### TC-50 the stop list ignores a manual effort (AC-50; unit) [default]
- File: `tests/test_flow.py:test_ac50_manual_no_pause` (new)
- Covers: CT-8
- Setup: TC-43's effort with `"auto": false`.
- Action: `flow.next_step(root, "S")`.
- Assert: the output contains `skill: @nio:jury`; no `pause` line.

### TC-51 a past effort with no history reads as planning and is not written (AC-51; unit) [default]
- File: `tests/test_flow.py:test_ac51_no_history_no_write` (new)
- Covers: CT-6, CT-9
- Setup: `effort("planning")` with no `history.jsonl`.
- Action: `flow.next_step(root, "S")`.
- Assert: the output contains `state: planning`; neither `state.json` nor `history.jsonl` exists.

### TC-52 without --commit nothing is committed or recorded (AC-52; integration) [default]
- File: `tests/test_flow.py:test_ac52_needs_commit_flag` (new)
- Covers: CT-6, CT-11
- Setup: `effort("spec_jury")` with the ledger approved, uncommitted, auto off, started; record `HEAD` and the line count.
- Action: `cli(root, "done", "spec_jury", "S")`, then `cli(root, "next", "S")`.
- Assert: `HEAD` unchanged; no new line; both outputs contain `nio flow done spec_jury --commit` and `--by human`.

### TC-53 a lite spec is unsupported and not written (AC-53; unit) [default]
- File: `tests/test_flow.py:test_ac53_lite_unsupported` (new)
- Covers: CT-4, CT-9, CT-12
- Setup: `effort("drafting", route="lite")` using tests/fixtures/spec/spec-bugfix.md.
- Action: `flow.status(root)` and `flow.next_step(root, "S")`.
- Assert: the status line contains `unsupported: lite`; `next` contains `unsupported: lite` and no `@nio:`; no `state.json` or `history.jsonl` exists.

### TC-54 an auto effort with a money risk waits for --commit (AC-54; unit) [default]
- File: `tests/test_flow.py:test_ac54_risk_waits` (new)
- Covers: CT-8, CT-11
- Setup: `effort("spec_jury", risk="[money]")` with the ledger approved and uncommitted, started, `"auto": true`; record `HEAD`.
- Action: `flow.done(root, "spec_jury", "S")`, then `flow.status(root)`.
- Assert: `HEAD` unchanged; the output contains `nio flow done spec_jury --commit`; the status line contains `waiting_for_human: approve spec`.

### TC-55 abandon freezes the effort until start (AC-55; unit) [default]
- File: `tests/test_flow.py:test_ac55_abandon` (new)
- Covers: CT-14, CT-7, CT-10
- Setup: `effort("tasking")`, started, parked; a second working effort `2026-10-21-refunds`.
- Action: `flow.abandon(root, "S", "superseded by #60")`; file a pending change record against `.nio/specs/S/plan.md`; `flow.status(root)`; then `flow.start(root, "S")` and `flow.status(root)`.
- Assert: the first status's last line is S's and contains `· tasking ·` and `abandoned: superseded by #60`; after `start`, S's line contains `working`; history holds an `abandon` line followed by a `resume` line.

### TC-56 a stale lock with no call running is taken over (AC-56; integration) [default]
- File: `tests/test_flow.py:test_ac56_stale_lock` (new)
- Covers: CT-3, CT-13
- Setup: `effort("planning")`, started, committed; `.nio/specs/S/flow.lock` holding `{"pid": <a pid that has exited>, "host": <this host>}` with its mtime set 120 seconds back.
- Action: `cli(root, "park", "S", "x")`.
- Assert: exit 0; exactly 1 new line, `kind` `park`; `git status --porcelain -- .nio/specs/S` lists exactly `.nio/specs/S/history.jsonl` and `.nio/specs/S/state.json`, so neither the new lock nor the renamed stale one shows.

### TC-57 an override shows until the human has seen it (AC-57; unit) [default]
- File: `tests/test_flow.py:test_ac57_seen` (new)
- Covers: CT-15, CT-12
- Setup: TC-26's effort after its override.
- Action: `flow.status(root)`, `flow.seen(root, "S")`, `flow.status(root)`.
- Assert: the first status line contains `override not seen: grilling: OP-3 is settled in Q5`; the second doesn't contain `override not seen`; exactly 1 new line of kind `seen`.

### TC-58 a hand-edited state.json stops next (AC-58; unit) [default]
- File: `tests/test_flow.py:test_ac58_hash_mismatch` (new)
- Covers: CT-1
- Setup: `effort("planning")`, started; edit `state.json` to `"auto": true` by hand; snapshot the folder.
- Action: `flow.next_step(root, "S")`.
- Assert: it raises `flow.Broken` whose message contains `state.json` and `hash mismatch`; the folder equals the snapshot.

### TC-59 a torn last line is cut and noted (AC-59; unit) [default]
- File: `tests/test_flow.py:test_ac59_torn_line` (new)
- Covers: CT-1, CT-2, CT-13
- Setup: `effort("planning")`, started; append `{"kind": "pass", "fr` with no line ending.
- Action: `flow.park(root, "S", "x")`.
- Assert: exit 0; the file ends with `\n`; it holds a `repair` line followed by a `park` line; the `repair` line's `reason` contains `'{"kind": "pass", "fr'.encode().hex()`; the text `{"kind": "pass", "fr` no longer appears in the file.

### TC-60 round 1 with open findings doesn't pause (AC-60; unit) [default]
- File: `tests/test_flow.py:test_ac60_round_one` (new)
- Covers: CT-8
- Setup: auto effort at spec_jury whose spec ledger `round` is 1 with J-1 `open`.
- Action: `flow.next_step(root, "S")`.
- Assert: the output contains `skill: @nio:jury`; no `pause` line.

### TC-61 a live lock on this host is not taken over (AC-61; integration) [default]
- File: `tests/test_flow.py:test_ac61_live_lock` (new)
- Covers: CT-3, CT-13
- Setup: `effort("planning")`, started; `flow.lock` holding `{"pid": <this test process's pid>, "host": <this host>}` with mtime 120 seconds back.
- Action: `cli(root, "park", "S", "x")`.
- Assert: non-zero exit; the output contains `being written`; no new line; the lock file is unchanged.

### TC-62 abandon refuses the four cases (AC-62; unit) [default]
- File: `tests/test_flow.py:test_ac62_abandon_refusals` (new)
- Covers: CT-14
- Setup: a working effort S, the legacy `.nio/specs/grilling/`, a lite effort `2026-10-21-fix`, and a done effort `2026-10-22-refunds` (implementing passed with `--human "shipped by hand"`, as in TC-35); snapshot each folder.
- Action: `flow.abandon` on S with `""`, and on each of the other three with `"x"`.
- Assert: each raises `ValueError`; no new line anywhere; every folder equals its snapshot.

### TC-63 a spec edited after its rejection goes to re-review (AC-63; unit) [default]
- File: `tests/test_flow.py:test_ac63_rereview` (new)
- Covers: CT-6
- Setup: TC-24's effort.
- Action: append a sentence to the Summary of `spec.md`, then `flow.next_step(root, "S")`.
- Assert: the output contains `state: spec_jury`.

### TC-64 a past approval counts only with its commit (AC-64; integration) [default]
- File: `tests/test_flow.py:test_ac64_approval_commit` (new)
- Covers: CT-6
- Setup: two repos from `effort("spec_jury")` with the ledger approved and no `history.jsonl`: in one the effort folder is committed `nio: approve spec`, in the other `init` only.
- Action: `cli(root, "next", "S")` in each.
- Assert: the first contains `state: planning`; the second contains `waiting_for_human` and `nio flow done spec_jury --commit`.

### TC-72 --human at a jury gate is refused and points to the jury (AC-65; unit) [default]
- File: `tests/test_flow.py:test_ac65_human_at_gate_refused` (new)
- Covers: CT-11
- Setup: `effort("spec_jury")` whose spec ledger round 1 is recorded `rejected`, spec edited since (stage spec_jury), started.
- Action: `cli(root, "done", "spec_jury", "S", "--human", "pack bug")`.
- Assert: non-zero exit; no new line; the output contains `nio jury check 2026-10-20-refunds spec --human "pack bug" --record`.

### TC-73 a leftover temp state matching the last line is rolled forward (AC-58; unit) [default]
- File: `tests/test_flow.py:test_ac58_temp_state_rolled_forward` (new)
- Covers: CT-1, CT-2, CT-10
- Setup: `effort("planning")`, started; simulate a crash after step (2) of CT-2: append a `park` line (`end: true`) whose `state` is the hash of a new state with `pause` set, write that state to `state.json.new`, leave `state.json` as it was.
- Action: `flow.load(root, "S")`, then `flow.start(root, "S", by="orchestrator / test / test")` (a writing call).
- Assert: `load` returns the state with `pause` set and raises nothing; after the write, `state.json.new` is gone, `state.json` holds `pause` set, and its hash equals the last line's `state`.

### TC-74 a leftover temp state matching no line is dropped (AC-58; unit) [default]
- File: `tests/test_flow.py:test_ac58_temp_state_dropped` (new)
- Covers: CT-1, CT-2
- Setup: `effort("planning")`, started; simulate a crash during step (2): write a new state to `state.json.new` and append a `park` line prefix with no line ending (no `end` line).
- Action: `flow.load(root, "S")`, then `flow.park(root, "S", "x", by="orchestrator / test / test")`.
- Assert: `load` returns the state as `state.json` holds it; after `park`, `state.json.new` is gone, the file holds a `repair` line then a `park` line, and `state.json`'s hash equals the last line's `state`.

### TC-75 a whole last line missing its newline is kept (AC-59; unit) [default]
- File: `tests/test_flow.py:test_ac59_whole_line_no_newline` (new)
- Covers: CT-1, CT-2
- Setup: `effort("planning")`, started; remove the final `\n` of `history.jsonl` (the start line still parses and its `state` matches `state.json`).
- Action: `flow.park(root, "S", "x", by="orchestrator / test / test")`.
- Assert: exit 0; the start line is still there, byte for byte, now followed by `\n`; the next line is the `park` line; no `repair` line.

### TC-76 a dated folder with only intake.md is an effort, not unsupported (AC-6; unit) [default]
- File: `tests/test_flow.py:test_ac6_intake_only_folder` (new)
- Covers: CT-4, CT-10
- Setup: `.nio/specs/2026-10-22-new/` holding only `intake.md`.
- Action: `flow.start(root, "2026-10-22-new", by="orchestrator / test / test")`, then `flow.status(root)`.
- Assert: `state.json` and `history.jsonl` are created with one `start` line whose `to` is `drafting` (intake's guard passes, there is no `spec.md`); the status line contains `2026-10-22-new · drafting` and not `unsupported`.

### TC-77 a CLI writer without --by refuses (AC-6; unit) [default]
- File: `tests/test_flow.py:test_ac6_by_required` (new)
- Covers: CT-16
- Setup: `effort("planning")` with no history; `snap` the folder.
- Action: `cli(root, "start", "S")` without --by.
- Assert: non-zero exit; the output contains `--by`; the folder equals the snapshot.

### TC-78 a bad state.json stops done (AC-9; unit) [default]
- File: `tests/test_flow.py:test_ac9_done_refuses` (new)
- Covers: CT-1, CT-11
- Setup: TC-9's effort, with `"stage"` in `state.json`.
- Action: `cli(root, "done", "planning", "S")`.
- Assert: non-zero exit; the output contains `state.json` and `stage`.

### TC-79 a bad state.json stops abandon (AC-9; unit) [default]
- File: `tests/test_flow.py:test_ac9_abandon_refuses` (new)
- Covers: CT-1, CT-14
- Setup: as TC-78.
- Action: `cli(root, "abandon", "S", "x")`.
- Assert: non-zero exit; the output contains `state.json` and `stage`.

### TC-80 a bad state.json stops seen (AC-9; unit) [default]
- File: `tests/test_flow.py:test_ac9_seen_refuses` (new)
- Covers: CT-1, CT-15
- Setup: as TC-78.
- Action: `cli(root, "seen", "S")`.
- Assert: non-zero exit; the output contains `state.json` and `stage`.

## Quality tests

### TC-65 next fits in 12 lines (NFR-1; unit) [default]
- File: `tests/test_flow.py:test_nfr1_next_twelve_lines` (new)
- Covers: CT-9
- Setup: working efforts at drafting, grilling (just after skips), planning, plan_jury and tasking, the planning one with 5 unseen overrides.
- Action: `flow.next_step(root, slug)` on each.
- Assert: each output has at most 12 lines.

### TC-66 next, status and park need no network or model (NFR-2; integration) [default]
- File: `tests/test_flow.py:test_nfr2_offline` (new)
- Covers: CT-9, CT-12, CT-13
- Setup: `effort("planning")`, started; a `sitecustomize.py` in a temp dir on `PYTHONPATH` that makes `socket.socket.connect` and `socket.create_connection` raise `OSError("network blocked")`.
- Action: run `next`, `status` and `park S x` through `cli` with that `PYTHONPATH`, and in-process check `"fastembed" not in sys.modules` after calling `flow.next_step`, `flow.status`, `flow.park`.
- Assert: each exits 0 and no output contains `network blocked`; `fastembed` was never imported.

### TC-67 status of 20 efforts of 50 lines takes under 2 seconds (NFR-3; integration) [default]
- File: `tests/test_flow.py:test_nfr3_status_speed` (new)
- Covers: CT-12
- Setup: 20 dated efforts at tasks_jury (spec, plan and tasks approved and committed), each with 50 history lines.
- Action: time `cli(root, "status")` from before the subprocess starts to its exit, with `time.perf_counter()`.
- Assert: exit 0, 20 lines, elapsed under 2.0 seconds.

## Misuse tests

### TC-68 hand edits and say-so don't move the effort (UJ-1 misuse; unit) [default]
- File: `tests/test_flow.py:test_uj1_no_say_so` (new)
- Covers: CT-1, CT-5, CT-11
- Setup: `effort("grilling")`, started, with OP-3 open; a `handoff.md` saying `grilling done`.
- Action: `flow.done(root, "grilling", "S", by="orchestrator / claude-code / opus")`; then set `"waiting"` to `{"why": "x"}` in `state.json` by hand and call `flow.next_step`.
- Assert: `done` exits non-zero naming OP-3 and adds no line; `next` raises `flow.Broken` naming `state.json` and `hash mismatch`.

### TC-69 an idle effort shows how long it has been idle (UJ-2 misuse; unit) [default]
- File: `tests/test_flow.py:test_uj2_idle_visible` (new)
- Covers: CT-12
- Setup: effort A with its last line at `2026-10-28T09:00:00Z`; effort B working, last line `2026-10-21T09:00:00Z`, never parked.
- Action: `flow.status(root)`.
- Assert: A's line comes first; B's line contains `2026-10-21 09:00`.

### TC-70 an agent's override can't hide (UJ-3 misuse; unit) [default]
- File: `tests/test_flow.py:test_uj3_override_shown` (new)
- Covers: CT-11, CT-12, CT-15, CT-18
- Setup: `effort("grilling")`, started, with OP-3 open.
- Action: `flow.done(root, "grilling", "S", human="settled", by="orchestrator / claude-code / opus")`, then `flow.status(root)` and `flow.next_step(root, "S")`; read every skill and card.
- Assert: the override line's `who.role` is `orchestrator`; both outputs contain `override not seen: grilling: settled`; every `skills/*/SKILL.md` and `src/nio/agents/*.md` contains the flow-rule line of CT-18 word for word.

### TC-71 work doesn't carry on against a changed spec (UJ-4 misuse; unit) [default]
- File: `tests/test_flow.py:test_uj4_changed_spec_blocks` (new)
- Covers: CT-6, CT-7, CT-11
- Setup: `effort("planning")`, started (last line `to` `planning`), plan files passing `nio check plan --gate`; then append a sentence to `spec.md`.
- Action: `flow.next_step(root, "S")`, then `flow.done(root, "planning", "S")`.
- Assert: `next` contains `state: spec_jury`; a `back` line names `spec.md`; `done planning` raises naming `spec_jury` as the current stage and adds no line.
