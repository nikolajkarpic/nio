---
slug: 2026-10-27-implementation-jury
retired: []                      # TC IDs removed from this plan; never reused
---
# Tests: implementation jury

Every test builds its fixture with one helper in `tests/test_evidence.py`: a temporary git repo with an effort at implementing, its `tasks.md`, the `T-n:` commits, and a small passing test suite in `tests.suite`. Lens outputs are fixed files, never model calls.

## Acceptance tests

### TC-1 it starts (AC-1; integration) [derived: AC-1]
- File: `tests/test_evidence.py:test_it_starts` (new)
- Covers: CT-1, CT-8, CT-10
- Setup: an epic from the tasks stage whose tasks the implement stage has all finished
- Action: the gate is asked to run on it
- Assert: exit status 0; the gate's plan for the epic lists conformance and correctness.

### TC-2 it refuses (AC-2; unit) [derived: FR-2]
- File: `tests/test_evidence.py:test_it_refuses` (new)
- Covers: CT-1
- Setup: an epic with one task not finished
- Action: the gate is asked to run on it
- Assert: non-zero exit; the message names the unfinished task's ID; no ledger is written.

### TC-3 it refuses (AC-3; unit) [derived: AC-3]
- File: `tests/test_evidence.py:test_it_refuses_again` (new)
- Covers: CT-1
- Setup: a spec and a git range but no epic
- Action: the gate is asked to run on them
- Assert: non-zero exit; the message says the subject must be an epic; no ledger is written.

### TC-4 the results list each AC with that test's file and line and the result passed (AC-4; integration) [derived: AC-4]
- File: `tests/test_evidence.py:test_the_results_list_each_ac_with_that_test_s` (new)
- Covers: CT-3, CT-7, CT-10, CT-21
- Setup: an epic covering AC-1 and AC-2, each exercised by a passing test whose name and description say what it checks and carry no spec IDs, and a fixed conformance lens output with only a `## Matches` line per AC
- Action: it is collected
- Assert: two entries, each with the AC ID, a `file:line` and `passed`, while the tests' source holds no AC IDs; the lens's own matching is judged by the lens card's evaluation, not this test.

### TC-5 a missing-evidence finding is recorded for it (AC-5; unit) [derived: AC-5]
- File: `tests/test_evidence.py:test_a_missing_evidence_finding_is_recorded_for_it` (new)
- Covers: CT-10, CT-21
- Setup: an AC the epic covers has no test, and a fixed conformance lens output with no match for it and no findings
- Action: it is collected
- Assert: one finding citing that AC with gap type missing and severity blocker.

### TC-6 a missing-evidence finding is recorded for it (AC-6; unit) [derived: AC-6]
- File: `tests/test_evidence.py:test_a_missing_evidence_finding_is_recorded_for_it_again` (new)
- Covers: CT-10, CT-21
- Setup: an AC's test fails, and a fixed conformance lens output with only a match to that test, no findings
- Action: it is collected
- Assert: one finding citing the AC, naming the failing test, with severity blocker.

### TC-7 the task is flagged as phantom completion despite its status (AC-7; unit) [derived: AC-7]
- File: `tests/test_evidence.py:test_the_task_is_flagged_as_phantom_completion_despite_its` (new)
- Covers: CT-3, CT-4, CT-20
- Setup: a task marked done names a file that doesn't exist
- Action: the gate starts
- Assert: a finding naming the task and the missing file.

### TC-8 it is flagged (AC-8; unit) [derived: AC-8]
- File: `tests/test_evidence.py:test_it_is_flagged` (new)
- Covers: CT-4
- Setup: a task names a file that exists but isn't in the epic's diff
- Action: the gate starts
- Assert: a finding naming the task and the file.

### TC-9 it is flagged as dead code (AC-9; unit) [derived: AC-9]
- File: `tests/test_evidence.py:test_it_is_flagged_as_dead_code` (new)
- Covers: CT-4
- Setup: a symbol defined in the diff is referenced nowhere but its own definition
- Action: the gate starts
- Assert: a finding naming the symbol and its file.

### TC-10 it is flagged as a possible stub, marked interpretive (AC-10; unit) [derived: AC-10]
- File: `tests/test_evidence.py:test_it_is_flagged_as_a_possible_stub_marked_interpretive` (new)
- Covers: CT-5
- Setup: a function in the diff whose body is empty or only a TODO
- Action: the gate starts
- Assert: a hint naming the function, marked interpretive, in every lens pack, and no ledger finding for it.

### TC-11 it is flagged as test tampering (AC-11; unit) [derived: AC-11]
- File: `tests/test_evidence.py:test_it_is_flagged_as_test_tampering` (new)
- Covers: CT-6, CT-20
- Setup: the diff deletes a test
- Action: the gate starts
- Assert: a test-tampering finding at severity major naming the deleted test.

### TC-12 it is flagged as test tampering (AC-12; unit) [derived: AC-12]
- File: `tests/test_evidence.py:test_it_is_flagged_as_test_tampering_again` (new)
- Covers: CT-6, CT-20
- Setup: the diff adds a skip to an existing test
- Action: the gate starts
- Assert: a test-tampering finding at severity major naming the skipped test.

### TC-13 it is recorded as test tampering (AC-13; unit) [derived: AC-13]
- File: `tests/test_evidence.py:test_it_is_recorded_as_test_tampering` (new)
- Covers: CT-6, CT-12, CT-5
- Setup: the diff removes an assertion from an existing test and a fixed correctness lens output with `- tampering: yes`
- Action: it is collected
- Assert: a test-tampering finding at severity major naming the test and the removed assertion.

### TC-14 the CLI flags the assertion, and the correctness lens's output says whether the test got weaker (AC-43; integration) [derived: AC-43]
- File: `tests/test_evidence.py:test_the_cli_flags_the_assertion_and_the_correctness_lens` (new)
- Covers: CT-5, CT-12
- Setup: the diff changes the expected value in an assertion of an existing test, and a fixed correctness lens output with a finding citing that line
- Action: the gate starts and the output is collected
- Assert: a flag naming the test and the changed assertion line in the results, and a ledger finding from correctness on that line.

### TC-15 the results record the failed check and its output (AC-14; integration) [derived: AC-14]
- File: `tests/test_evidence.py:test_the_results_record_the_failed_check_and_its_output` (new)
- Covers: CT-3, CT-7
- Setup: the type check reports an error in a file of the diff
- Action: the gate starts
- Assert: the type-check entry shows failed with the error's file and line.

### TC-16 both are run and their results are recorded (AC-15; integration) [derived: AC-15]
- File: `tests/test_evidence.py:test_both_are_run_and_their_results_are_recorded` (new)
- Covers: CT-3, CT-7
- Setup: the spec has a misuse line and quickstart.md a journey run
- Action: the gate starts
- Assert: one result for the misuse line and one for the journey run, each passed or failed with its output.

### TC-17 it is flagged, not passed (AC-16; unit) [derived: AC-16]
- File: `tests/test_evidence.py:test_it_is_flagged_not_passed` (new)
- Covers: CT-5
- Setup: a symbol whose only hit outside its definition is a string, as with a dynamic call
- Action: the gate starts
- Assert: a hint naming the symbol and saying the check was uncertain, in every lens pack, and no ledger finding for it.

### TC-18 every AC is recorded without passing evidence; the CLI only records the crash (AC-17; integration) [derived: FR-3]
- File: `tests/test_evidence.py:test_every_ac_is_recorded_without_passing_evidence_the_cli` (new)
- Covers: CT-3, CT-7, CT-21
- Setup: a test run that crashes before any test runs, and a fixed conformance lens output with no findings
- Action: the conformance lens has run
- Assert: one missing-evidence finding per AC of the epic; the crash output is in the results.

### TC-19 the plan holds conformance and correctness only (AC-18; unit) [derived: AC-18]
- File: `tests/test_evidence.py:test_the_plan_holds_conformance_and_correctness_only` (new)
- Covers: CT-8
- Setup: a spec with no risk flags and an epic that only adds new files
- Action: the gate is planned
- Assert: the planned lenses are exactly conformance and correctness.

### TC-20 security and risk and rollback are added (AC-19; unit) [derived: AC-19]
- File: `tests/test_evidence.py:test_security_and_risk_and_rollback_are_added` (new)
- Covers: CT-8
- Setup: a spec flagged auth and migration
- Action: the gate is planned
- Assert: the plan lists conformance, correctness, security and risk and rollback.

### TC-21 the adversary is added (AC-20; unit) [derived: AC-20]
- File: `tests/test_evidence.py:test_the_adversary_is_added` (new)
- Covers: CT-8
- Setup: a spec flagged external-input
- Action: the gate is planned
- Assert: the plan lists the adversary.

### TC-22 consistency is added (AC-21; unit) [derived: AC-21]
- File: `tests/test_evidence.py:test_consistency_is_added` (new)
- Covers: CT-8
- Setup: an epic whose diff changes a module that existed before the epic
- Action: the gate is planned
- Assert: the plan lists consistency.

### TC-23 no lens runs until the human picks, and the human sees each planned run and its model tier (AC-22; integration) [derived: AC-22]
- File: `tests/test_evidence.py:test_no_lens_runs_until_the_human_picks_and_the` (new)
- Covers: CT-8
- Setup: `jury.max_runs` set to 4 and a plan of 5 lens runs
- Action: the gate is planned, then a lens output is collected
- Assert: the plan output lists 5 runs, each with its tier, and the choices run all or pick (no hit rates recorded yet); collect refuses the output, naming the missing pick.

### TC-24 the dropped lens is named in the verdict (AC-23; integration) [derived: AC-23]
- File: `tests/test_evidence.py:test_the_dropped_lens_is_named_in_the_verdict` (new)
- Covers: CT-8, CT-16
- Setup: `jury.max_runs` set to 4, a plan of 5 runs, and `--pick` records a set without one triggered lens
- Action: the gate runs
- Assert: the verdict names each dropped lens, and conformance and correctness are not among them.

### TC-25 it holds the diff, the text of AC-3, FR-2 and CT-1 and the run results (AC-24; integration) [derived: AC-24]
- File: `tests/test_evidence.py:test_it_holds_the_diff_the_text_of_ac_3` (new)
- Covers: CT-9
- Setup: an epic whose diff touches the code for AC-3, FR-2 and CT-1
- Action: a lens's pack is built
- Assert: the pack holds the diff, those three items' text and the results, and no text of an AC, FR or CT the diff doesn't touch.

### TC-26 it can open any project file and can't write files or run commands (AC-25; unit) [derived: AC-25]
- File: `tests/test_evidence.py:test_it_can_open_any_project_file_and_can_t` (new)
- Covers: CT-9, CT-10
- Setup: any lens at the implementation gate
- Action: it runs
- Assert: each implementation lens card's tools are read-only (read, grep, glob).

### TC-27 they hold that run's result (AC-26; integration) [derived: AC-26]
- File: `tests/test_evidence.py:test_they_hold_that_run_s_result` (new)
- Covers: CT-11
- Setup: a round-1 finding asks for a specific run
- Action: the round-2 packs are built
- Assert: the round-2 pack holds the requested run and its output.

### TC-28 they say the run couldn't start and why (AC-27; unit) [derived: AC-27]
- File: `tests/test_evidence.py:test_they_say_the_run_couldn_t_start_and_why` (new)
- Covers: CT-11
- Setup: a finding asks for a run that can't start
- Action: the next packs are built
- Assert: the next pack holds the request with "couldn't run" and the error.

### TC-29 the command is not run and is listed for the human (AC-44; integration) [derived: AC-44]
- File: `tests/test_evidence.py:test_the_command_is_not_run_and_is_listed_for` (new)
- Covers: CT-11
- Setup: a finding asks the CLI to run a command that is not one of the project's tests or the spec's attacks
- Action: the next packs are built
- Assert: no process started for that command; the human's list names the request and the finding.

### TC-30 only 3 are run and the fourth is listed for the human (AC-45; unit) [derived: AC-45]
- File: `tests/test_evidence.py:test_only_3_are_run_and_the_fourth_is_listed` (new)
- Covers: CT-11
- Setup: four valid run requests in one round
- Action: the next packs are built
- Assert: exactly 3 run results in the packs; the fourth request on the human's list.

### TC-31 the output is invalid (AC-28; unit) [derived: AC-28]
- File: `tests/test_evidence.py:test_the_output_is_invalid` (new)
- Covers: CT-12
- Setup: a lens output with a finding that has no gap type
- Action: it is collected
- Assert: collect prints `INVALID` naming the finding's missing gap type.

### TC-32 it is dropped as ungrounded (AC-29; unit) [derived: AC-29]
- File: `tests/test_evidence.py:test_it_is_dropped_as_ungrounded` (new)
- Covers: CT-12
- Setup: a finding cites FR-99, which the spec doesn't define
- Action: it is collected
- Assert: the finding's status is dropped and the reason names FR-99.

### TC-33 it is kept (AC-30; unit) [derived: AC-30]
- File: `tests/test_evidence.py:test_it_is_kept` (new)
- Covers: CT-12
- Setup: a finding quotes code abbreviated with "…" and paraphrased
- Action: it is collected
- Assert: the finding's status is open, not dropped.

### TC-34 the finding goes to the refuter before the human sees it (AC-31; unit) [derived: AC-31]
- File: `tests/test_evidence.py:test_the_finding_goes_to_the_refuter_before_the_human` (new)
- Covers: CT-12
- Setup: a major finding from a lens
- Action: the gate composes its outcome
- Assert: the finding is in the refuter batch; the outcome waits on the refuter.

### TC-35 the output is invalid (AC-47; unit) [derived: FR-21]
- File: `tests/test_evidence.py:test_the_output_is_invalid_again` (new)
- Covers: CT-12
- Setup: a lens output with a finding that cites no AC, FR or CT, or names no file or area as evidence
- Action: it is collected
- Assert: collect prints `INVALID` naming the missing field.

### TC-36 it is not open and no fix task is written for it (AC-48; unit) [derived: FR-24]
- File: `tests/test_evidence.py:test_it_is_not_open_and_no_fix_task_is` (new)
- Covers: CT-12
- Setup: a major finding the refuter refutes
- Action: the outcome is composed
- Assert: the finding's status is refuted; the epic's task file has no task citing it.

### TC-37 it is rerun and never approved; after a second invalid output it is human (AC-49; unit) [derived: FR-32]
- File: `tests/test_evidence.py:test_it_is_rerun_and_never_approved_after_a_second` (new)
- Covers: CT-13
- Setup: a planned lens with no output, or an invalid one
- Action: the outcome is composed
- Assert: outcome `rerun` naming the lens; after the second failure, outcome `human`.

### TC-38 each finding has exactly one fix task (AC-50; unit) [derived: FR-26]
- File: `tests/test_evidence.py:test_each_finding_has_exactly_one_fix_task` (new)
- Covers: CT-14, CT-17
- Setup: a rejected outcome composed twice for the same round
- Action: fix tasks are appended
- Assert: one task per finding ID in the epic.

### TC-39 the packs hold a hint naming it, and a conformance lens output that matches it is not accepted as evidence (AC-51; integration) [derived: AC-51]
- File: `tests/test_evidence.py:test_the_packs_hold_a_hint_naming_it_and_a` (new)
- Covers: CT-10, CT-5, CT-21
- Setup: a new test named for an AC whose body has no assertion, and a fixed conformance lens output with only a match to it
- Action: the gate runs
- Assert: a no-assertion hint naming the test in every lens pack; the AC ends with a missing-evidence finding.

### TC-40 it is stopped at the time limit, recorded as failed, and the gate goes on (AC-52; integration) [derived: AC-52]
- File: `tests/test_evidence.py:test_it_is_stopped_at_the_time_limit_recorded_as` (new)
- Covers: CT-2
- Setup: a test that never ends
- Action: the gate runs it
- Assert: the test's result is `failed` with "timed out after" and the limit; the next command still runs.

### TC-41 only the throwaway copy is touched (AC-53; integration) [derived: AC-53]
- File: `tests/test_evidence.py:test_only_the_throwaway_copy_is_touched` (new)
- Covers: CT-2
- Setup: a test that deletes files and runs `git branch -D`, `git config`, `git update-ref` and `git push origin`
- Action: the gate runs it
- Assert: the human's working tree, refs, config and `git worktree list` are unchanged, after a normal run and after a timeout.

### TC-42 a major finding names the check and its first errors (AC-54; unit) [derived: AC-54]
- File: `tests/test_evidence.py:test_a_major_finding_names_the_check_and_its_first` (new)
- Covers: CT-3, CT-20
- Setup: the epic's type check fails
- Action: the gate starts
- Assert: one ledger finding with severity major naming the type check and holding its first error line.

### TC-43 the result holds its first and last 100 KB and says how much was cut (AC-55; unit) [derived: AC-55]
- File: `tests/test_evidence.py:test_the_result_holds_its_first_and_last_100_kb` (new)
- Covers: CT-2, CT-7
- Setup: a run that prints 1 MB
- Action: its result is recorded
- Assert: the result holds the run's first and last 100 KB, from markers at each end, and a "cut N bytes" line with the right N.

### TC-44 it is rejected, one fix task is appended for the major and none for the minor (AC-56; unit) [derived: AC-56]
- File: `tests/test_evidence.py:test_it_is_rejected_one_fix_task_is_appended_for` (new)
- Covers: CT-13
- Setup: one confirmed major and one minor in the first review
- Action: the outcome is composed
- Assert: outcome `rejected`; exactly one new task, citing the major.

### TC-45 no tampering finding is recorded (AC-57; unit) [derived: AC-57]
- File: `tests/test_evidence.py:test_no_tampering_finding_is_recorded` (new)
- Covers: CT-6, CT-12, CT-5
- Setup: the diff changes an assertion and a fixed correctness lens output saying the test did not get weaker
- Action: it is collected
- Assert: the hint is in the packs; no test-tampering finding for that assertion.

### TC-46 the epic waits on the change request and no fix task is appended (AC-58; unit) [derived: AC-58]
- File: `tests/test_evidence.py:test_the_epic_waits_on_the_change_request_and_no` (new)
- Covers: CT-15, CT-17
- Setup: the only open major is a contradicts finding with `right: code`
- Action: the outcome is composed
- Assert: the epic's state is waiting on change; no new task.

### TC-47 a fix task citing the finding is appended and the epic goes back to implementing (AC-59; unit) [derived: AC-59]
- File: `tests/test_evidence.py:test_a_fix_task_citing_the_finding_is_appended_and` (new)
- Covers: CT-14, CT-15, CT-17
- Setup: an epic waiting on change and the human rejects the change request
- Action: the ruling is recorded
- Assert: one new task citing the finding; the epic's state is implementing.

### TC-48 the plan holds the security lens (AC-60; unit) [derived: AC-60]
- File: `tests/test_evidence.py:test_the_plan_holds_the_security_lens` (new)
- Covers: CT-18
- Setup: a spec with `risk: [secrets]` and an epic of it
- Action: the implementation gate is planned
- Assert: the plan lists security with the reason "risk: secrets".

### TC-49 the security lens is listed (AC-61; unit) [derived: AC-61]
- File: `tests/test_evidence.py:test_the_security_lens_is_listed` (new)
- Covers: CT-18
- Setup: a spec with `risk: [secrets]`
- Action: `nio check spec` runs
- Assert: the lenses line includes security.

### TC-50 it is rejected and a fix task is appended to the epic (AC-32; integration) [derived: AC-32]
- File: `tests/test_evidence.py:test_it_is_rejected_and_a_fix_task_is_appended` (new)
- Covers: CT-13, CT-14, CT-17
- Setup: the first review raised one confirmed major with gap type missing
- Action: the outcome is composed
- Assert: outcome `rejected`; the epic gains one task citing the finding; the epic is back with the implement stage.

### TC-51 the four tasks are unchanged and the new one has the next free ID (AC-33; unit) [derived: AC-33]
- File: `tests/test_evidence.py:test_the_four_tasks_are_unchanged_and_the_new_one` (new)
- Covers: CT-14
- Setup: an epic with four tasks, one of them an earlier fix task
- Action: another round appends a fix task
- Assert: the four tasks' text and IDs are byte-for-byte unchanged; one new task with an ID not used before.

### TC-52 it is approved and no task is written (AC-34; unit) [derived: AC-34]
- File: `tests/test_evidence.py:test_it_is_approved_and_no_task_is_written` (new)
- Covers: CT-13
- Setup: a gate with no findings
- Action: the outcome is composed
- Assert: outcome `approved`; the epic's task file is unchanged.

### TC-53 a "justify or remove" task is appended and the code is not touched (AC-35; unit) [derived: AC-35]
- File: `tests/test_evidence.py:test_a_justify_or_remove_task_is_appended_and_the` (new)
- Covers: CT-14
- Setup: a confirmed finding with gap type unrequested
- Action: the outcome is composed
- Assert: one appended task whose text says justify or remove; the diff of the code it names is unchanged.

### TC-54 a change request is raised and spec.md is unchanged (AC-36; integration) [derived: AC-36]
- File: `tests/test_evidence.py:test_a_change_request_is_raised_and_spec_md_is` (new)
- Covers: CT-15
- Setup: a contradicts finding with `right: code`
- Action: it is disposed of
- Assert: one change request citing the finding and the spec item; spec.md's text is unchanged.

### TC-55 it is approved and the verdict lists both (AC-37; unit) [derived: AC-37]
- File: `tests/test_evidence.py:test_it_is_approved_and_the_verdict_lists_both` (new)
- Covers: CT-13, CT-16
- Setup: two minor findings and nothing else open
- Action: the outcome is composed
- Assert: outcome `approved`; the verdict names both findings.

### TC-56 it is human, not rejected, as at the spec gate (AC-38; unit) [derived: AC-38]
- File: `tests/test_evidence.py:test_it_is_human_not_rejected_as_at_the_spec` (new)
- Covers: CT-13
- Setup: a re-review that raises a new major and no blocker, with nothing else open
- Action: the outcome is composed
- Assert: outcome `human`, naming the new major; the epic isn't approved.

### TC-57 the record names the epic, the outcome and the round (AC-39; unit) [derived: FR-25]
- File: `tests/test_evidence.py:test_the_record_names_the_epic_the_outcome_and_the` (new)
- Covers: CT-16
- Setup: a gate that ends approved
- Action: the verdict is recorded
- Assert: one verdict record with the epic's ID, `approved` and the round number.

### TC-58 that round is a re-review of the open findings (AC-40; integration) [derived: AC-40]
- File: `tests/test_evidence.py:test_that_round_is_a_re_review_of_the_open` (new)
- Covers: CT-1, CT-17, CT-19, CT-14, CT-13, CT-9
- Setup: a rejected epic whose fix tasks the implement stage has finished
- Action: the gate runs again
- Assert: the round number rose by 1, each lens pack is a fix check of its findings, and its diff starts at the commit the last round judged.

### TC-59 a fix task for it is appended to the epic and the final fix check waits until that task is finished (AC-46; integration) [derived: AC-46]
- File: `tests/test_evidence.py:test_a_fix_task_for_it_is_appended_to_the` (new)
- Covers: CT-14
- Setup: the human chooses fix for a major on the end-of-review list
- Action: the choice is recorded
- Assert: a new task citing the finding in the epic; the gate's state shows the final fix check pending until the task is done.

### TC-60 conformance, correctness and risk and rollback cards exist, each saying what it judges at the implementation gate (AC-41; unit) [derived: AC-41]
- File: `tests/test_evidence.py:test_conformance_correctness_and_risk_and_rollback_cards_exist_each` (new)
- Covers: CT-10
- Setup: the shipped lens cards
- Action: they are listed
- Assert: the three card files exist in `src/nio/agents/`, each with an `## At implementation` section.

### TC-61 each has an `## At implementation` section (AC-42; unit) [derived: AC-42]
- File: `tests/test_evidence.py:test_each_has_an_at_implementation_section` (new)
- Covers: CT-10
- Setup: the existing lens cards the implementation gate uses
- Action: they are read
- Assert: `security.md`, `adversary.md` and `consistency.md` each have an `## At implementation` heading.

### TC-67 a money flag adds no lens (AC-20; unit) [derived: FR-15]
- File: `tests/test_evidence.py:test_every_row_of_the_trigger_table` (new)
- Covers: CT-8
- Setup: one spec per row of the trigger table, including money, pii, public-api, multi-party and data-deletion
- Action: the gate is planned for each
- Assert: the planned lenses are exactly conformance and correctness plus that row's lens; for money, none added.

### TC-68 the CLI's findings skip the refuter and only the human accepts tampering (AC-31; unit) [derived: FR-24]
- File: `tests/test_evidence.py:test_cli_findings_skip_the_refuter` (new)
- Covers: CT-20
- Setup: a diff that deletes a test
- Action: the gate starts twice, then collect, then `dispose` as accepted-risk `--by agent`
- Assert: one finding, lens `cli`, validation `confirmed`, absent from the refuter batch; the dispose is refused and the finding stays open.

### TC-69 the last epic's gate ends the effort (AC-40; integration) [derived: FR-1]
- File: `tests/test_evidence.py:test_the_last_epics_gate_ends_the_effort` (new)
- Covers: CT-17
- Setup: an effort whose last epic's final task commits
- Action: the task commits, the gate rejects once, the fix commits, the gate approves, `nio flow done implementation-E-n` runs
- Assert: history has no `epic` or `pass` line and the report no `merge:` until that call; then one of each, with `reason` approved, and the state is done.

### TC-70 an old skipped epic stays closed and is reported (AC-1; integration) [derived: FR-1]
- File: `tests/test_evidence.py:test_an_old_skipped_epic_stays_closed` (new)
- Covers: CT-17
- Setup: a history holding a `skipped: not built` line for E-1, E-2 unfinished
- Action: `nio flow next`, `nio flow claim` and the stage's `left` check
- Assert: `next` names E-1 as never reviewed; claim of an E-2 task succeeds; `left` doesn't list E-1.

### TC-71 a repeat raises no second change request (AC-36; integration) [derived: FR-30]
- File: `tests/test_evidence.py:test_a_repeat_raises_no_second_change_request` (new)
- Covers: CT-15
- Setup: a contradicts finding with `right: code`
- Action: `nio jury check --record` twice, and once more with the ledger save made to fail after the raise
- Assert: one change record names the finding.

### TC-72 each recorded outcome is committed (AC-32; integration) [derived: FR-26]
- File: `tests/test_evidence.py:test_each_recorded_outcome_is_committed` (new)
- Covers: CT-14, CT-17
- Setup: a rejected outcome with one fix task
- Action: `nio jury check --record`
- Assert: `git log` holds `nio: jury implementation-E-n round 1`; `git status` is clean for the ledger, `tasks.md` and the verdict; `nio check tasks` passes with the new task.

### TC-73 a lens can't claim a pass (AC-6; unit) [derived: FR-5]
- File: `tests/test_evidence.py:test_a_lens_cant_claim_a_pass` (new)
- Covers: CT-21
- Setup: an AC's test fails, and a fixed conformance lens output matching it and saying it passed; a second AC matched to a test absent from the results
- Action: it is collected
- Assert: the first evidence entry says `failed`, the second has no passing result; one blocker missing-evidence finding for each.

### TC-74 an unset right side goes to a fix task (AC-32; integration) [derived: FR-26]
- File: `tests/test_evidence.py:test_an_unset_right_side_goes_to_a_fix_task` (new)
- Covers: CT-12, CT-14
- Setup: a contradicts finding with no `right`
- Action: the outcome is composed
- Assert: one fix task citing it; no change record.

### TC-75 a fix task that didn't fix the check doesn't pass the gate (AC-40; integration) [derived: FR-5]
- File: `tests/test_evidence.py:test_a_fix_task_that_did_not_fix_the_check` (new)
- Covers: CT-13, CT-14, CT-20
- Setup: a CLI finding for a failing test, its fix task finished, and the test still failing; a second CLI finding whose check now passes
- Action: `nio jury evidence` runs again and the outcome is composed
- Assert: the first has the same J-n, `not fixed`, and no second task; the outcome isn't approved; the second is `fixed` with no juror's verdict.

## Quality tests

### TC-62 The CLI-first checks call no model (NFR-1; unit) [derived: NFR-1]
- File: `tests/test_evidence.py:test_cli_checks_make_no_model_calls` (new)
- Covers: CT-3, CT-7, CT-4, CT-6, CT-20
- Setup: the fixture repo, with every model client module blocked from import
- Action: run `evidence.collect` on the fixture epic
- Assert: it completes, and `src/nio/evidence.py` imports no model client

## Misuse tests

### TC-63 The gate refuses an unfinished epic whose lens would take done as proof (UJ-1 misuse; integration) [derived: FR-2]
- File: `tests/test_evidence.py:test_the_gate_refuses_an_unfinished_epic_whose_lens_would_take_done_as_proof` (new)
- Covers: CT-1, CT-3, CT-4, CT-20
- Setup: an epic with one task not done, and a done task whose file is missing
- Action: run `nio jury evidence` on each
- Assert: the first exits non-zero naming the task; the second records a phantom-completion finding despite the status

### TC-64 An old task is never rewritten and code never deleted (UJ-2 misuse; integration) [derived: FR-27]
- File: `tests/test_evidence.py:test_an_old_task_is_never_rewritten_and_code_never_deleted` (new)
- Covers: CT-14
- Setup: an epic with four tasks and a confirmed unrequested finding
- Action: run `nio jury check --record` twice
- Assert: the four tasks are byte-for-byte unchanged, one task says justify or remove, and the named code is unchanged

### TC-65 The spec is never edited to match the code (UJ-3 misuse; integration) [derived: FR-30]
- File: `tests/test_evidence.py:test_the_spec_is_never_edited_to_match_the_code` (new)
- Covers: CT-15
- Setup: a contradicts finding where the code is the right side
- Action: run `nio jury check --record`
- Assert: spec.md is byte-for-byte unchanged and one pending change request cites the finding

### TC-66 A lens isn't dropped without the human (UJ-4 misuse; integration) [derived: FR-16]
- File: `tests/test_evidence.py:test_a_lens_isn_t_dropped_without_the_human` (new)
- Covers: CT-8
- Setup: `jury.max_runs` 4 and a plan of 5 runs
- Action: collect outputs for 4 lenses with no recorded pick
- Assert: collect refuses, naming the missing pick, whatever `--expect` values the agent passed; the outcome is not approved
