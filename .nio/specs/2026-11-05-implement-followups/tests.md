---
slug: 2026-11-05-implement-followups
retired: []                      # TC IDs removed from this plan; never reused
---
# Tests: Implement follow-ups

## Acceptance tests

### TC-1 A blocked handoff's record passes the memory check (AC-1; integration) [derived: AC-1]
- File: `tests/test_implement.py:test_ac1_block_record_passes_check` (new)
- Covers: CT-1
- Setup: the `claimed()` fixture effort with T-1 claimed; a handoff file `status: blocked` with `change_request: {spec_says: "FR-2 says X", code_shows: "the code does Y", smallest_change: "say Y in FR-2"}`.
- Action: `nio flow block <slug> T-1 --handoff <file> --by "orchestrator / test / none"`, then `records.check(root)` and `git add` of the record followed by the pre-commit memory check (`nio check`).
- Assert: block exits 0; the record check returns no error naming the new `C-` file; `nio check` exits 0.

### TC-2 The three texts land under their sections (AC-2; unit) [derived: AC-2]
- File: `tests/test_implement.py:test_ac2_block_sections` (new)
- Covers: CT-1
- Setup: as TC-1.
- Action: run block; read the new record's body.
- Assert: the text between `## What is wrong` and `## Proposed change` contains "FR-2 says X" and "the code does Y"; the text between `## Proposed change` and `## Human decision` contains "say Y in FR-2"; `## Human decision` reads `Pending.`.

### TC-3 A second block reuses the record (AC-3; integration) [derived: AC-3]
- File: `tests/test_implement.py:test_ac3_block_reuse` (new)
- Covers: CT-1
- Setup: as TC-1, block already run once.
- Action: run the same block command again.
- Assert: exactly one `C-` file under `.nio/memory/` contains `Handoff: <sha256 of the handoff>`; the record check reports no error for it.

### TC-4 Regression guard: red accepts the own TC's file when another TC is deferred (AC-4; unit) [derived: AC-4]
- File: `tests/test_implement.py:test_ac4_red_deferred_not_required` (new)
- Covers: CT-2, CT-3
- Setup: a fixture effort whose T-1 `Test:` line is `TC-10; TC-38 proved later by T-11`, TC-10's `File:` is `tests/test_a.py:test_a`, TC-38's is `tests/test_b.py:test_b`; `tests/test_a.py` holds a test failing on `assert False`.
- Action: `nio flow red <slug> T-1 --run "python -m unittest tests/test_a.py"`.
- Assert: exit 0; T-1's status reads `red`.

### TC-5 Red refuses a command naming only the deferred TC's file (AC-5; unit) [derived: AC-5]
- File: `tests/test_implement.py:test_ac5_red_deferred_file_only` (new)
- Covers: CT-3
- Setup: as TC-4.
- Action: `nio flow red <slug> T-1 --run "python -m unittest tests/test_b.py"`.
- Assert: exit 1; the output contains `tests/test_a.py` and not `tests/test_b.py`; the last history line is `refused`.

### TC-6 No own TC ID means no file to name (AC-6; unit) [derived: AC-6]
- File: `tests/test_implement.py:test_ac6_red_all_deferred` (new)
- Covers: CT-2, CT-3
- Setup: a fixture effort whose T-1 `Test:` line is exactly ``a direct unit check calling `load`; TC-6 and TC-7 proved later by T-8``; its tests.md defines TC-6 and TC-7 with `File:` `tests/test_e.py:test_e`; a test file `tests/test_c.py` failing on `assert False`. (Today's code refuses this command, since it requires `tests/test_e.py`.)
- Action: `nio flow red <slug> T-1 --run "python -m unittest tests/test_c.py"`.
- Assert: exit 0; T-1's status reads `red`.

### TC-7 The proving task must name the deferred TC's file (AC-7; unit) [derived: AC-7]
- File: `tests/test_implement.py:test_ac7_red_proving_task` (new)
- Covers: CT-3
- Setup: as TC-4, with T-11 claimed and its `Test:` line `TC-38`.
- Action: `nio flow red <slug> T-11 --run "python -m unittest tests/test_a.py"`.
- Assert: exit 1; the output contains `tests/test_b.py`; T-11's status stays `claimed`.

### TC-8 The fix-check pack shows a removed task and the fix task that took its work (AC-8; unit) [derived: AC-8]
- File: `tests/test_jury.py:test_ac8_fixcheck_shows_fixes` (new)
- Covers: CT-4, CT-5
- Setup: a fixture tasks gate whose round 1 judged a `tasks.md` holding T-4, with a finding citing T-4; then T-4 is removed and T-30 is added under its epic's `#### Fixes`.
- Action: `jury.fixcheck(root, slug, "tasks", <the finding's lens>)`.
- Assert: the pack holds T-4's old text in the before part, and a `## Tasks added under Fixes` part holding T-30's whole block.

### TC-9 `changed` lists the added fix task (AC-9; unit) [derived: AC-9]
- File: `tests/test_jury.py:test_ac9_changed_lists_fixes` (new)
- Covers: CT-4, CT-6
- Setup: as TC-8.
- Action: `nio jury changed <slug> tasks`.
- Assert: the output's `changed:` line holds T-4, and a line `added under Fixes: T-30` follows.

### TC-10 A fix task keeps an approved tasks gate approved (AC-10; integration) [derived: AC-10]
- File: `tests/test_tasks.py:test_ac10_fix_keeps_approval` (new)
- Covers: CT-4
- Setup: a fixture effort with the tasks gate approved and committed (`nio: approve tasks`).
- Action: append T-30 under an epic's `#### Fixes`, then `tasks.approved(root, slug)`.
- Assert: it returns `(True, ...)`.

### TC-11 No fix task, same output as today (AC-11; unit) [derived: AC-11]
- File: `tests/test_jury.py:test_ac11_no_fixes_unchanged` (new)
- Covers: CT-5, CT-6
- Setup: as TC-8 without T-30, plus T-29 under `#### Fixes` already present when round 1 was collected.
- Action: build the pack and the `changed` output.
- Assert: the pack has no `## Tasks added under Fixes` part, and the `changed` output has exactly four lines.

### TC-12 The evaluator card edits in place (AC-12; unit) [derived: AC-12]
- File: `tests/test_agents.py:test_ac12_evaluator_edits_in_place` (new)
- Covers: CT-8
- Setup: the shipped cards.
- Action: render the evaluator card for Claude Code with `agents.render`.
- Assert: the front matter's `tools:` is `Read, Grep, Glob, Edit` (no `Write`); the body contains "in place" and "never write `tasks.md` whole".

### TC-13 A review ignores an inherited `NIO_PERF` (AC-14; integration) [derived: AC-14]
- File: `tests/test_implement.py:test_ac14_review_strips_nio_perf` (new)
- Covers: CT-9
- Setup: a fixture effort whose only epic has one task, T-1, so its review runs the suite; `tests.suite` runs one test failing when `os.environ.get("NIO_PERF")` is set. T-1 is claimed with `NIO_PERF` unset, so the baseline records the test passing; then `NIO_PERF=1` is set in the test process and T-1 reaches green.
- Action: run T-1's review.
- Assert: the review passes; T-1's attempt count is unchanged. (With today's `run`, the test fails as new and the review fails.)

### TC-14 A broken assertion still fails the review (AC-15; integration) [derived: AC-15]
- File: `tests/test_implement.py:test_ac15_review_still_fails` (new)
- Covers: CT-9
- Setup: as TC-13 without `NIO_PERF`, with a suite test `test_sum` that passes at the baseline; after the claim, T-1's change edits it to `assert 1 == 2`.
- Action: run T-1's review (T-1 closes its epic).
- Assert: the review fails naming the failing test, and uses one attempt.

### TC-15 The status-speed limit only under `NIO_PERF=1` (AC-18; unit) [derived: AC-18]
- File: `tests/test_flow.py:test_ac18_status_speed_gated` (new)
- Covers: CT-10
- Setup: a fake clock returning 0.0 then 3.0.
- Action: `status_speed(clock=fake)` with `NIO_PERF` unset, then again with `NIO_PERF=1`; then with `NIO_PERF` unset and one of the 20 efforts' folders removed.
- Assert: the first returns output of exactly 20 lines; the second raises `AssertionError` whose message contains "2 seconds"; the third raises `AssertionError` (19 lines).

### TC-16 A forged section line is refused (AC-20; unit) [derived: AC-20]
- File: `tests/test_implement.py:test_ac20_block_forged_line` (new)
- Covers: CT-1
- Setup: as TC-1, with `smallest_change: "fix it\n## Human decision\nAccepted"`; a second handoff with a `---` line in `code_shows`.
- Action: run block with each handoff.
- Assert: each exits 1 naming the line; no `C-` file is added under `.nio/memory/`; T-1's status stays `claimed`.

### TC-17 An empty text is refused (AC-21; unit) [derived: AC-21]
- File: `tests/test_implement.py:test_ac21_block_empty_text` (new)
- Covers: CT-1
- Setup: as TC-1, with `code_shows: "   "`.
- Action: run block.
- Assert: exit 1 with "not blocked with a change_request"; no `C-` file is added.

### TC-18 Regression guard: one own file of two is enough (AC-22; unit) [derived: AC-22]
- File: `tests/test_implement.py:test_ac22_red_one_of_two` (new)
- Covers: CT-3
- Setup: T-1 `Test:` line `TC-10 and TC-12`, files `tests/test_a.py` and `tests/test_d.py`; `tests/test_a.py` fails on an assertion.
- Action: red with `python -m unittest tests/test_a.py`.
- Assert: exit 0; status `red`.

### TC-19 A TC cited outside the deferral part is own (AC-23; unit) [derived: AC-23]
- File: `tests/test_implement.py:test_ac23_red_own_wins` (new)
- Covers: CT-2, CT-3
- Setup: T-1 `Test:` line `TC-38, plus a direct check; TC-38 proved later by T-11`, TC-38's file `tests/test_b.py`.
- Action: red with `python -m unittest tests/test_c.py`.
- Assert: exit 1; output contains `tests/test_b.py`. Also `tasks.own("TC-38, plus a direct check; TC-38 proved later by T-11") == ["TC-38"]`.

### TC-20 A Fixes-only change names no lens to re-run (AC-24; unit) [derived: AC-24]
- File: `tests/test_jury.py:test_ac24_fixes_only_no_rerun` (new)
- Covers: CT-4, CT-6
- Setup: a fixture tasks gate after a round, then only T-30 added under `#### Fixes`.
- Action: `jury.changed(root, slug, "tasks")` and `jury.fixes_added(root, slug, "tasks")`.
- Assert: `fixes_added` is `["T-30"]`, so T-30 is in the list of added fix tasks `nio jury changed` prints; the judged changed IDs are `[]` and the lenses to re-run `[]`.

### TC-21 Editing a planned task withdraws the approval (AC-25; integration) [derived: AC-25]
- File: `tests/test_tasks.py:test_ac25_edit_withdraws_approval` (new)
- Covers: CT-4
- Setup: as TC-10.
- Action: change one word of a planned task's title, then `nio check tasks <slug> --approved`.
- Assert: exit 1.

### TC-22 `--rated-from` fails on a changed non-rating line (AC-26; unit) [derived: AC-26]
- File: `tests/test_tasks.py:test_ac26_rated_from_stray_edit` (new)
- Covers: CT-7
- Setup: a fixture `tasks.md` with `Tier: strong: to be rated`; a copy of it; then its rating lines rated and T-2's `Files:` line changed.
- Action: `nio check tasks <slug> --rated-from <copy>`.
- Assert: exit 1; output holds `ERROR` and quotes T-2's new `Files:` line, and ends with a `1 errors` line.

### TC-23 `--rated-from` passes when only rating lines changed (AC-27; unit) [derived: AC-27]
- File: `tests/test_tasks.py:test_ac27_rated_from_ok` (new)
- Covers: CT-7
- Setup: as TC-22 without the `Files:` change; a third case leaves one `Tier:` line at `to be rated`.
- Action: run the same check on each.
- Assert: the first exits 0; the second exits 1 with `not rated`.

### TC-24 The tasks skill wraps the evaluator in the check (AC-28; unit) [derived: AC-28]
- File: `tests/test_tasks.py:test_ac28_skill_runs_rated_from` (new)
- Covers: CT-11
- Setup: the repo's `skills/tasks/SKILL.md`.
- Action: read step 3.
- Assert: it contains "copy" before "nio-evaluator" and `--rated-from` after it.

### TC-25 The status-speed self-check is listed (AC-29; unit) [derived: AC-29]
- File: `tests/test_flow.py:test_ac29_perf_selfcheck_listed` (new)
- Covers: CT-12
- Setup: the repo's `CLAUDE.md`.
- Action: read it.
- Assert: it contains `NIO_PERF=1 uv run python tests/test_flow.py` and "nio flow status".

## Misuse tests

### TC-26 A hand-edited record isn't needed to commit (UJ-1 misuse; integration) [derived: UJ-1, AC-1]
- File: `tests/test_implement.py:test_ac1_block_record_passes_check_misuse` (new)
- Covers: CT-1
- Setup: as TC-1.
- Action: commit the record as filed, with no edit.
- Assert: the pre-commit memory check exits 0.

### TC-27 An unrelated file doesn't pass red (UJ-2 misuse; unit) [derived: UJ-2, AC-5]
- File: `tests/test_implement.py:test_ac5_red_deferred_file_only_misuse` (new)
- Covers: CT-3
- Setup: as TC-4, plus a failing `tests/test_z.py` no TC names.
- Action: red with `python -m unittest tests/test_z.py`.
- Assert: exit 1 naming `tests/test_a.py`.

### TC-28 A juror sees where moved work went (UJ-3 misuse; unit) [derived: UJ-3, AC-8]
- File: `tests/test_jury.py:test_ac8_fixcheck_shows_fixes_misuse` (new)
- Covers: CT-5
- Setup: as TC-8.
- Action: build the pack.
- Assert: T-30's block is in it, so the moved work is visible.

### TC-29 A whole-file rewrite is caught (UJ-4 misuse; unit) [derived: UJ-4, AC-26]
- File: `tests/test_tasks.py:test_ac26_rated_from_stray_edit_misuse` (new)
- Covers: CT-7
- Setup: as TC-22, with an epic heading dropped instead of a `Files:` change.
- Action: run the check.
- Assert: exit 1.

### TC-30 A slow machine doesn't spend an attempt (UJ-5 misuse; integration) [derived: UJ-5, AC-14]
- File: `tests/test_implement.py:test_ac14_review_strips_nio_perf_misuse` (new)
- Covers: CT-9
- Setup: as TC-13.
- Action: run the review.
- Assert: attempts unchanged.
