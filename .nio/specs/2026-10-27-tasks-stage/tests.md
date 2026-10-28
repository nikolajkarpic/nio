---
slug: 2026-10-27-tasks-stage
retired: []                      # TC IDs removed from this plan; never reused
---
# Tests: the tasks stage

## Acceptance tests
<!-- e2e tests run the tasks drafter or evaluator on a real model, only when NIO_E2E=1 (as tests/test_lenses.py). Tests of the state (#45) and implement (#43) stages call tasks.finished and tasks.approved, which those stages will call. -->

### TC-1 It writes one `tasks.md` with one epic per user story (AC-1; e2e) [default]
- File: `tests/test_tasks_e2e.py:test_ac1_it_writes_one_tasks_md_with_one_epic_per` (new)
- Covers: CT-1, CT-2, CT-8
- Setup: An approved full spec with US-1 and US-2, whose approved plan has a build-order entry for each and no Foundation entry.
- Action: The tasks stage runs.
- Assert: `.nio/specs/<slug>/tasks.md` exists with exactly two epic sections, `E-1` naming US-1 and `E-2` naming US-2, each with its tasks under it.

### TC-2 A foundational epic comes first and both story epics depend on it (AC-2; e2e) [default]
- File: `tests/test_tasks_e2e.py:test_ac2_a_foundational_epic_comes_first_and_both` (new)
- Covers: CT-1, CT-8
- Setup: An approved full spec whose approved plan has a Foundation entry that both user stories' entries depend on.
- Action: The tasks stage runs.
- Assert: the first epic section is the foundational one; in every story epic, some task depends, directly or through other tasks, on a task of the foundational epic

### TC-3 It refuses (AC-3; integration) [default]
- File: `tests/test_tasks.py:test_ac3_it_refuses` (new)
- Covers: CT-1, CT-3
- Setup: A spec that is not approved.
- Action: The tasks stage is asked to run on it.
- Assert: no `tasks.md` is written; the message says the spec must be approved first.

### TC-4 It refuses and points to its slices (AC-4; integration) [default]
- File: `tests/test_tasks.py:test_ac4_it_refuses_and_points_to_its_slices` (new)
- Covers: CT-1, CT-3
- Setup: An epic-route spec (a roadmap of slices with no ACs).
- Action: The tasks stage is asked to run on it.
- Assert: no `tasks.md` is written; the message says to run the tasks stage on each slice's spec.

### TC-5 It fails (AC-5; unit) [default]
- File: `tests/test_tasks.py:test_ac5_it_fails` (new)
- Covers: CT-1, CT-4, CT-8
- Setup: A full spec whose plan's US-1 entry delivers CT-2 (bound to `src/cart.py`) and lists TC-3, and E-1 for US-1 whose tasks name neither.
- Action: `nio check tasks` runs.
- Assert: non-zero exit; one error names E-1 and `src/cart.py`, another names E-1 and TC-3.

### TC-6 Every task names its files from the spec and the code (AC-6; e2e) [default]
- File: `tests/test_tasks_e2e.py:test_ac6_every_task_names_its_files_from_the_spec` (new)
- Covers: CT-1, CT-8
- Setup: An approved bug-fix spec, which has no `plan.md`.
- Action: The tasks stage runs.
- Assert: every task has a non-empty `Files:` line.

### TC-7 It fails (AC-8; unit) [default]
- File: `tests/test_tasks.py:test_ac8_it_fails` (new)
- Covers: CT-2, CT-4
- Setup: T-3 has no `Effort:` line.
- Action: `nio check tasks` runs.
- Assert: non-zero exit; the error names T-3 and `Effort`.

### TC-8 It fails (AC-9; unit) [default]
- File: `tests/test_tasks.py:test_ac9_it_fails` (new)
- Covers: CT-4
- Setup: T-3's `Serves:` cites AC-99, which the spec doesn't define.
- Action: The check runs.
- Assert: non-zero exit; the error names T-3 and AC-99.

### TC-9 It fails (AC-10; unit) [default]
- File: `tests/test_tasks.py:test_ac10_it_fails` (new)
- Covers: CT-4
- Setup: T-5's `Depends on:` cites T-40, which `tasks.md` doesn't define.
- Action: The check runs.
- Assert: non-zero exit; the error names T-5 and T-40.

### TC-10 It fails (AC-11; unit) [default]
- File: `tests/test_tasks.py:test_ac11_it_fails` (new)
- Covers: CT-4
- Setup: T-2 is listed in `retired:` and T-5 depends on T-2.
- Action: The check runs.
- Assert: non-zero exit; the error names T-2 as retired.

### TC-11 It fails (AC-12; unit) [default]
- File: `tests/test_tasks.py:test_ac12_it_fails` (new)
- Covers: CT-2, CT-4
- Setup: Two task headings both `T-7` (for example two epics each numbering from T-1).
- Action: The check runs.
- Assert: non-zero exit; the error names T-7 as defined twice.

### TC-12 Only the second is an error (AC-13; unit) [default]
- File: `tests/test_tasks.py:test_ac13_only_the_second_is_an_error` (new)
- Covers: CT-4
- Setup: A task with `Depends on: none` and `Parallel: yes`, and another with `Parallel: maybe`.
- Action: The check runs.
- Assert: one error, naming the second task and its `Parallel:` value.

### TC-13 Both are errors (AC-14; unit) [default]
- File: `tests/test_tasks.py:test_ac14_both_are_errors` (new)
- Covers: CT-2, CT-4
- Setup: One task with `Tier: strong` and no reason and another with `Tier: huge: big change`.
- Action: The check runs.
- Assert: two errors, one naming the missing reason, one naming `huge` as not cheap, strong, max or frontier.

### TC-14 It fails (AC-15; unit) [default]
- File: `tests/test_tasks.py:test_ac15_it_fails` (new)
- Covers: CT-2, CT-4
- Setup: A task with a `- [ ]` checkbox or a `Status:` line.
- Action: The check runs.
- Assert: non-zero exit; the error names the task and says status lives in the CLI's state.

### TC-15 It fails (AC-16; unit) [default]
- File: `tests/test_tasks.py:test_ac16_it_fails` (new)
- Covers: CT-4
- Setup: The spec defines AC-4 and no task serves it.
- Action: The check runs.
- Assert: non-zero exit; the error names AC-4 as served by no task.

### TC-16 It fails (AC-17; unit) [default]
- File: `tests/test_tasks.py:test_ac17_it_fails` (new)
- Covers: CT-4
- Setup: T-6 has a `Serves:` line that cites no AC.
- Action: The check runs.
- Assert: non-zero exit; the error names T-6 as serving no AC.

### TC-17 It fails (AC-18; unit) [default]
- File: `tests/test_tasks.py:test_ac18_it_fails` (new)
- Covers: CT-4
- Setup: T-2 depends on T-3 and T-3 depends on T-2.
- Action: The check runs.
- Assert: non-zero exit; the error names T-2 and T-3 as a cycle.

### TC-18 It fails (AC-19; unit) [default]
- File: `tests/test_tasks.py:test_ac19_it_fails` (new)
- Covers: CT-4
- Setup: T-1 depends on T-3, T-3 on T-2 and T-2 on T-1.
- Action: The check runs.
- Assert: non-zero exit; the error names all three tasks in the cycle.

### TC-19 It fails (AC-20; unit) [default]
- File: `tests/test_tasks.py:test_ac20_it_fails` (new)
- Covers: CT-4
- Setup: T-4 and T-5 are both `Parallel: yes` and both name `src/a.py`.
- Action: The check runs.
- Assert: non-zero exit; the error names T-4, T-5 and `src/a.py`.

### TC-20 There is no clash (AC-21; unit) [default]
- File: `tests/test_tasks.py:test_ac21_there_is_no_clash` (new)
- Covers: CT-4
- Setup: T-4 is `Parallel: yes`, T-5 is `Parallel: no` and both name `src/a.py`.
- Action: The check runs.
- Assert: no error for T-4 or T-5.

### TC-21 It passes (AC-22; integration) [default]
- File: `tests/test_tasks.py:test_ac22_it_passes` (new)
- Covers: CT-4
- Setup: A valid `tasks.md`.
- Action: The check runs with no network and no model configured.
- Assert: exit 0; no model or network call is made (NFR-1).

### TC-22 It does not start (AC-23; integration) [default]
- File: `tests/test_tasks.py:test_ac23_it_does_not_start` (new)
- Covers: CT-1, CT-11
- Setup: `nio check tasks` fails for a spec.
- Action: The tasks jury is asked to run.
- Assert: no lens runs; the message says the check must pass first.

### TC-23 `executability` exists with tier cheap and an `## At tasks` section (AC-40; unit) [default]
- File: `tests/test_agents.py:test_ac40_executability_exists_with_tier_cheap_an` (new)
- Covers: CT-10
- Setup: The shipped agent cards.
- Action: They are listed.
- Assert: `src/nio/agents/executability.md` with `tier: cheap` and the heading.

### TC-24 It plans executability as the core lens (AC-41; unit) [default]
- File: `tests/test_jury.py:test_ac41_it_plans_executability_as_the_core_lens` (new)
- Covers: CT-11
- Setup: A spec with `risk: [auth, money]` whose `nio check tasks` passes
- Action: `nio jury plan <slug> tasks` runs.
- Assert: the lens line is exactly `lenses: executability (core)`, with no risk or scope lens and no error about the gate not being built

### TC-25 It refuses; given a bug-fix spec whose spec gate is approved, it proceeds (AC-59; integration) [default]
- File: `tests/test_tasks.py:test_ac59_it_refuses_given_a_bug_fix_spec_whose_sp` (new)
- Covers: CT-1, CT-3
- Setup: A full spec whose spec gate is approved but whose `nio check plan <slug> --approved` exits 1, and a bug-fix spec whose spec gate is approved
- Action: `nio new tasks <slug>` runs on each
- Assert: the first exits 1 saying the plan must be approved first and writes no `tasks.md`; the second exits 0 and writes `tasks.md`

### TC-26 It stops and says the spec must become a full spec with a plan (AC-60; e2e) [default]
- File: `tests/test_tasks_e2e.py:test_ac60_it_stops_and_says_the_spec_must_become_a` (new)
- Covers: CT-1, CT-8
- Setup: A bug-fix spec whose fix needs a choice between two storage options the spec doesn't make.
- Action: The drafter meets it.
- Assert: no `tasks.md` is written; the message names the choice and says to re-route the spec to full.

### TC-27 The epics follow that order and E-3 (US-2) depends on E-2 (US-1) (AC-61; e2e) [default]
- File: `tests/test_tasks_e2e.py:test_ac61_the_epics_follow_that_order_and_e_3_us_2` (new)
- Covers: CT-1, CT-8
- Setup: A full spec whose plan's build order has Foundation, US-1, and US-2 with `Depends on: US-1`.
- Action: The tasks stage runs.
- Assert: epic sections in the order foundational, US-1, US-2; some task in E-3 depends on a task in E-2

### TC-28 It fails; given a task with `Test: second refund gets 409` on a full spec, it fails too (AC-62; unit) [default]
- File: `tests/test_tasks.py:test_ac62_it_fails_given_a_task_with_test_second_r` (new)
- Covers: CT-4, CT-8
- Setup: A full spec whose task T-4 has `Test: TC-99` and the plan defines no TC-99.
- Action: The check runs.
- Assert: non-zero exit; one error names T-4 and TC-99, the other names the task and says a full spec's `Test:` cites a `TC-n`.

### TC-29 The tasks approval no longer stands (AC-63; integration) [default]
- File: `tests/test_tasks.py:test_ac63_the_tasks_approval_no_longer_stands` (new)
- Covers: CT-12, CT-14
- Setup: An approved estimate.
- Action: The plan's `contracts.md` or the spec changes afterwards.
- Assert: the implement stage refuses, saying the tasks must be approved again; `nio jury check <slug> tasks` says `rerun`.

### TC-30 It proceeds (AC-42; integration) [default]
- File: `tests/test_tasks.py:test_ac42_it_proceeds` (new)
- Covers: CT-1, CT-3
- Setup: A full spec whose spec jury the human closed with a reason and whose plan is approved.
- Action: The tasks stage starts.
- Assert: no refusal; the drafter is started.

### TC-31 It refuses (AC-43; unit) [default]
- File: `tests/test_tasks.py:test_ac43_it_refuses` (new)
- Covers: CT-1, CT-3
- Setup: A spec whose jury ended `human` because a juror failed twice, and the human never closed it.
- Action: The tasks stage starts.
- Assert: non-zero exit; the message says the spec must be approved first.

### TC-32 The evaluator card exists with `tier: strong` and `effort: med` (AC-44; unit) [default]
- File: `tests/test_agents.py:test_ac44_the_evaluator_card_exists_with_tier_stro` (new)
- Covers: CT-9
- Setup: The shipped agent cards.
- Action: They are listed.
- Assert: the card's frontmatter holds both values.

### TC-33 One `nio: approve tasks` commit holds `tasks.md` and the tasks verdict (AC-45; integration) [default]
- File: `tests/test_tasks.py:test_ac45_one_nio_approve_tasks_commit_holds_tasks` (new)
- Covers: CT-1, CT-14
- Setup: A spec whose tasks gate the jury approved and recorded (`nio jury check <slug> tasks --record`), and one whose gate isn't recorded
- Action: `nio check tasks <slug> --approved` runs on each
- Assert: the first exits 0 and names the tasks verdict record; the second exits 1 saying the tasks must be approved first. The `nio: approve tasks` commit itself is the skill's step, walked in QS-2

### TC-34 It fails naming T-1 and AC-4 (AC-46; unit) [default]
- File: `tests/test_tasks.py:test_ac46_it_fails_naming_t_1_and_ac_4` (new)
- Covers: CT-4
- Setup: Foundational task T-1 with `Serves: AC-1, AC-4` and only T-5 (serving AC-1) depending on it.
- Action: The check runs.
- Assert: non-zero exit; the error names T-1 and AC-4.

### TC-35 Both are listed as parallel (AC-48; unit) [default]
- File: `tests/test_tasks.py:test_ac48_both_are_listed_as_parallel` (new)
- Covers: CT-5
- Setup: Two tasks marked `Parallel: yes`, one `cheap` and one `max`, with no dependencies and no shared file.
- Action: The estimate is printed.
- Assert: both IDs appear in the epic's parallel list.

### TC-36 It fails naming both (AC-49; unit) [default]
- File: `tests/test_tasks.py:test_ac49_it_fails_naming_both` (new)
- Covers: CT-4
- Setup: T-2 in E-1 and T-7 in E-2, both `Parallel: yes` and both listing `src/cart.py`.
- Action: The check runs.
- Assert: non-zero exit; the error names T-2, T-7 and the file.

### TC-37 It passes, and T-4 is listed as parallel (AC-50; unit) [default]
- File: `tests/test_tasks.py:test_ac50_it_passes_and_t_4_is_listed_as_parallel` (new)
- Covers: CT-4
- Setup: T-4 `Parallel: yes` with `Depends on: T-1`.
- Action: The check runs.
- Assert: exit 0; T-4 in the parallel list.

### TC-38 It passes; the same `Serves: J-4` on a planned task fails (AC-51; unit) [default]
- File: `tests/test_tasks.py:test_ac51_it_passes_the_same_serves_j_4_on_a_plann` (new)
- Covers: CT-16
- Setup: A "justify or remove" task under `#### Fixes` with `From: J-4 (implementation-E-2, round 1)` and `Serves: J-4`.
- Action: The check runs.
- Assert: exit 0 for the first; for the second, an error naming the task and J-4.

### TC-39 It fails naming the task (AC-52; unit) [default]
- File: `tests/test_tasks.py:test_ac52_it_fails_naming_the_task` (new)
- Covers: CT-16
- Setup: An approved estimate and a planned task whose `Files:` line was edited afterwards.
- Action: The check runs.
- Assert: non-zero exit; the error names the task and says planned tasks are frozen after approval.

### TC-40 It sits under `#### Fixes` with `From: C-1` and the check passes (AC-53; unit) [default]
- File: `tests/test_tasks.py:test_ac53_it_sits_under_fixes_with_from_c_1_and_th` (new)
- Covers: CT-16
- Setup: An accepted change request C-1 after approval.
- Action: Its task is added.
- Assert: exit 0; the new task is under the Fixes heading with that From line.

### TC-41 `tasks.md` has exactly one epic, E-1, whose tasks serve both ACs (AC-54; integration) [default]
- File: `tests/test_tasks.py:test_ac54_tasks_md_has_exactly_one_epic_e_1_whose` (new)
- Covers: CT-1, CT-8
- Setup: A bug-fix spec with AC-1 and AC-2.
- Action: The tasks are drafted and checked.
- Assert: one `## E-1` section; no other epic heading; the check passes.

### TC-42 It proceeds (AC-55; integration) [default]
- File: `tests/test_tasks.py:test_ac55_it_proceeds` (new)
- Covers: CT-1, CT-14
- Setup: A `nio: approve tasks` commit holding `tasks.md` and the tasks verdict.
- Action: The implement stage is asked to start.
- Assert: the first ready task can be claimed.

### TC-43 The change is refused (AC-56; integration) [default]
- File: `tests/test_flow.py:test_ac56_the_change_is_refused` (new)
- Runs: once #45 builds `nio flow`, as the spec's non-goal says
- Covers: CT-15
- Setup: T-3 is claimed in the CLI's state.
- Action: It is set to done.
- Assert: T-3 stays claimed; the message names the missing red, green and review steps.

### TC-44 The claim is refused; and given T-5 is already claimed, a second claim is refused (AC-57; integration) [default]
- File: `tests/test_flow.py:test_ac57_the_claim_is_refused_and_given_t_5_is_al` (new)
- Runs: once #45 builds `nio flow`, as the spec's non-goal says
- Covers: CT-15
- Setup: T-4 is pending because T-1 is not done.
- Action: T-4 is claimed.
- Assert: both claims refused with "dependencies not done" and "already claimed".

### TC-45 The card runs on the strong model and a warning names max and that model (AC-58; unit) [default]
- File: `tests/test_agents.py:test_ac58_the_card_runs_on_the_strong_model_and_a` (new)
- Covers: CT-7
- Setup: A host config mapping cheap and strong but not max, and an agent card with `tier: max`.
- Action: `nio agents sync` renders it.
- Assert: the rendered card's model is the strong model; the output holds the warning.

### TC-46 Size raises no error (AC-24; unit) [default]
- File: `tests/test_tasks.py:test_ac24_size_raises_no_error` (new)
- Covers: CT-4
- Setup: A task naming 12 files and serving 6 ACs.
- Action: The check runs.
- Assert: no error or warning about the task's size.

### TC-47 Every task has a tier with a reason and an effort (AC-25; e2e) [default]
- File: `tests/test_tasks_e2e.py:test_ac25_every_task_has_a_tier_with_a_reason_and` (new)
- Covers: CT-1, CT-9
- Setup: The drafter has written `tasks.md`.
- Action: The evaluator runs.
- Assert: every task's `Tier:` line is cheap, strong, max or frontier followed by a one-line reason, and its `Effort:` line is low, med or high.

### TC-48 It runs on Fable; on a host that maps no frontier model, it runs on that host's max model (AC-26; integration) [default]
- File: `tests/test_agents.py:test_ac26_it_runs_on_fable_on_a_host_that_maps_no` (new)
- Covers: CT-7
- Setup: A task with `Tier: frontier` and `Effort: med`, resolved for the Claude host, and for a host whose config maps cheap, strong and max but not frontier
- Action: `agents.resolve(cfg, None, {"tier": "frontier", "effort": "med"}, host)` runs for each
- Assert: Claude gives `fable` with no warning; the other host gives its max model and a warning naming `frontier` and that model

### TC-49 It prints E-1's estimate row (AC-27; unit) [default]
- File: `tests/test_tasks.py:test_ac27_it_prints_e_1_s_estimate_row` (new)
- Covers: CT-5
- Setup: E-1 with T-1 (cheap, low, parallel), T-2 (cheap, med, parallel) and T-3 (max, high).
- Action: `nio check tasks` runs.
- Assert: a row for E-1 showing 3 tasks, 2 cheap, 0 strong, 1 max, 0 frontier, 1 low, 1 med, 1 high effort, and T-1, T-2 as parallel.

### TC-50 It holds no token or money figure (AC-28; unit) [default]
- File: `tests/test_tasks.py:test_ac28_it_holds_no_token_or_money_figure` (new)
- Covers: CT-5
- Setup: Any `tasks.md`.
- Action: The estimate is printed.
- Assert: the estimate's columns are task counts, tier and effort counts and parallel tasks only.

### TC-51 It refuses (AC-29; integration) [default]
- File: `tests/test_tasks.py:test_ac29_it_refuses` (new)
- Covers: CT-14
- Setup: A spec whose estimate the human has not approved.
- Action: The implement stage is asked to start.
- Assert: no task is claimed; the message says the human must approve the estimate first.

### TC-52 It still refuses (AC-30; integration) [default]
- File: `tests/test_tasks.py:test_ac30_it_still_refuses` (new)
- Covers: CT-14
- Setup: The human pushes back on the estimate.
- Action: The implement stage is asked to start.
- Assert: the tasks stage is not approved; no task is claimed.

### TC-53 T-12 is added under E-2's `#### Fixes` heading (AC-31; unit) [default]
- File: `tests/test_tasks.py:test_ac31_t_12_is_added_under_e_2_s_fixes_heading` (new)
- Covers: CT-1, CT-16
- Setup: `tasks.md` where E-2 holds T-5 to T-7, the highest task ID ever used is T-11, and T-12 sits under E-2's `#### Fixes` with `From: J-4 (implementation-E-2, round 1)` and the seven lines; a second copy numbers it T-8 instead
- Action: `nio check tasks <slug>` runs on each
- Assert: the first passes; the second fails, naming T-8 and saying a fix task takes the next free ID, T-12

### TC-54 The planned tasks above the heading are unchanged (AC-32; unit) [default]
- File: `tests/test_tasks.py:test_ac32_the_planned_tasks_above_the_heading_are` (new)
- Covers: CT-1, CT-16
- Setup: An approved `tasks.md`, then T-12 appended under E-2's `#### Fixes` and, in a second copy, T-6's `Files:` line also edited
- Action: `nio check tasks <slug>` runs on each
- Assert: the first passes; the second fails, naming T-6 and saying planned tasks are frozen after approval

### TC-55 It goes under the epic's `Fixes` heading citing the change request (AC-33; unit) [default]
- File: `tests/test_tasks.py:test_ac33_it_goes_under_the_epic_s_fixes_heading_c` (new)
- Covers: CT-1, CT-16
- Setup: A task under `#### Fixes` with `From: C-261028-abcd`, the ID of a rejected change record, and another with `From:` naming no record
- Action: `nio check tasks <slug>` runs
- Assert: no error for the first; the second fails, naming the task and its `From:` line

### TC-56 It fails (AC-34; unit) [default]
- File: `tests/test_tasks.py:test_ac34_it_fails` (new)
- Covers: CT-16
- Setup: A task under `#### Fixes` with no `From:` line.
- Action: The check runs.
- Assert: non-zero exit; the error names the task and `From`.

### TC-57 It fails as a parallel clash (AC-35; unit) [default]
- File: `tests/test_tasks.py:test_ac35_it_fails_as_a_parallel_clash` (new)
- Covers: CT-16
- Setup: A fix task marked `Parallel: yes` naming the same file as a planned `Parallel: yes` task.
- Action: The check runs.
- Assert: non-zero exit; the error names both tasks and the file.

### TC-58 The change is refused (AC-36; integration) [default]
- File: `tests/test_flow.py:test_ac36_the_change_is_refused` (new)
- Runs: once #45 builds `nio flow`, as the spec's non-goal says
- Covers: CT-15
- Setup: T-3 is green in the CLI's state.
- Action: It is set to done without a review.
- Assert: T-3's state stays green; the message names the missing review.

### TC-59 It is not finished (AC-37; integration) [default]
- File: `tests/test_tasks.py:test_ac37_it_is_not_finished` (new)
- Covers: CT-15
- Setup: Every planned task of E-2 is done and its fix task T-12 is in review.
- Action: E-2's readiness for the implementation jury is asked.
- Assert: E-2 is reported not finished, naming T-12.

### TC-60 It sits next to the spec gate's ledger, named for the epic (AC-38; integration) [default]
- File: `tests/test_jury.py:test_ac38_it_sits_next_to_the_spec_gate_s_ledger_n` (new)
- Covers: CT-13
- Setup: A ledger for gate `implementation-E-2` written through `jury.save` and its verdict through `jury.verdict`
- Action: The round is recorded
- Assert: `.nio/specs/<slug>/jury/implementation-E-2.json` and `.md` exist; the verdict subject is `implementation-E-2:<slug>`. This pins behaviour that already holds; collecting such a round is #29's

### TC-61 It prints T-3 alone (AC-39; unit) [default]
- File: `tests/test_tasks.py:test_ac39_it_prints_t_3_alone` (new)
- Covers: CT-6
- Setup: A `tasks.md` with several tasks.
- Action: `nio task show <slug> T-3` runs.
- Assert: the output holds T-3's heading and seven lines and its epic's title, and no other task.

## Quality tests

### TC-62 `nio check tasks` and its estimate call no model (NFR-1; unit) [default]
- File: `tests/test_tasks.py:test_nfr1_check_tasks_makes_no_model_call` (new)
- Covers: CT-4, CT-5
- Setup: A fixture spec, plan and valid `tasks.md`, with `subprocess.run` patched to record every call.
- Action: Call `tasks.check(root, slug)`.
- Assert: it returns no errors and the estimate rows, and every recorded call is `git`.

## Misuse tests

### TC-63 The drafter groups tasks by layer, leaves an AC with no task, or adds a task that serves no AC (UJ-1 misuse; integration) [default]
- File: `tests/test_tasks.py:test_uj1_layered_tasks_fail_coverage` (new)
- Covers: CT-4
- Setup: A `tasks.md` whose epics are named by layer, with AC-2 served by no task and T-9 serving no AC.
- Action: `nio check tasks <slug>` runs.
- Assert: non-zero exit; errors name AC-2 as served by no task and T-9 as serving no AC.

### TC-64 The implement stage starts before the human has seen the estimate (UJ-2 misuse; integration) [default]
- File: `tests/test_tasks.py:test_uj2_unapproved_tasks_block_implement` (new)
- Covers: CT-14
- Setup: A spec whose `tasks.md` passes its check but whose tasks gate isn't approved.
- Action: `nio check tasks <slug> --approved` runs.
- Assert: exit 1; the message says the tasks must be approved first.

### TC-65 A planned task is edited or renumbered to absorb a fix (UJ-3 misuse; integration) [default]
- File: `tests/test_tasks.py:test_uj3_edited_planned_task_fails` (new)
- Covers: CT-4
- Setup: An approved `tasks.md`; T-3 above `#### Fixes` is edited to absorb a fix.
- Action: `nio check tasks <slug>` runs.
- Assert: non-zero exit; the error names T-3 and says planned tasks are frozen after approval.
