---
slug: 2026-10-28-plan-jury
retired: []                      # TC IDs removed from this plan; never reused
---
# Tests: the plan gate's jury

## Acceptance tests
<!-- The e2e tests in tests/test_lenses.py run a lens on a real model, and only when NIO_E2E=1 is set (grill Q13). -->

### TC-1 It plans the two core lenses (AC-1; unit) [default]
- File: `tests/test_jury.py:test_ac1_it_plans_the_two_core_lenses` (new)
- Covers: CT-1, CT-2
- Setup: A spec with no risk flags whose plan passes `nio check plan --gate` and has no contract with a `State:` line and no `## Data model` section.
- Action: `nio jury plan <slug> plan` runs.
- Assert: exit 0; the lens line lists `test-proof (core)` and `architecture-fit (core)` and nothing else; no "only the spec gate" error.

### TC-2 No lens is planned (AC-2; unit) [default]
- File: `tests/test_jury.py:test_ac2_no_lens_is_planned` (new)
- Covers: CT-2
- Setup: A plan that fails `nio check plan <slug> --gate`.
- Action: `nio jury plan <slug> plan` runs.
- Assert: non-zero exit; the output names `nio check plan <slug> --gate` and its error count, and lists no lens.

### TC-3 The spec check is not what decides it (AC-3; unit) [default]
- File: `tests/test_jury.py:test_ac3_the_spec_check_is_not_what_decides_it` (new)
- Covers: CT-2
- Setup: A spec that fails `nio check spec --gate` but a plan that passes `nio check plan --gate`.
- Action: The plan gate is planned.
- Assert: the output holds no line about `nio check spec`; the lenses are planned.

### TC-4 Logic runs with its reason (AC-4; unit) [default]
- File: `tests/test_jury.py:test_ac4_logic_runs_with_its_reason` (new)
- Covers: CT-2
- Setup: A plan where CT-2 has a `State:` line.
- Action: The plan gate is planned.
- Assert: the lens line holds `logic` with a reason naming state.

### TC-5 Logic does not run (AC-5; unit) [default]
- File: `tests/test_jury.py:test_ac5_logic_does_not_run` (new)
- Covers: CT-2
- Setup: A plan where no contract has a `State:` line.
- Action: The plan gate is planned.
- Assert: `logic` is not in the lens line.

### TC-6 Security runs with its reason (AC-6; unit) [default]
- File: `tests/test_jury.py:test_ac6_security_runs_with_its_reason` (new)
- Covers: CT-2
- Setup: A spec with `risk: [pii]`.
- Action: The plan gate is planned.
- Assert: the lens line holds `security (risk: pii)`.

### TC-7 `risk-rollback` exists with an `## At plan` section (AC-46; unit) [default]
- File: `tests/test_agents.py:test_ac46_risk_rollback_exists_with_an_at_plan_se` (new)
- Covers: CT-11, CT-12, CT-13
- Setup: The shipped agent cards.
- Action: They are listed.
- Assert: `src/nio/agents/risk-rollback.md` passes the card check, has `tier: max` and `effort: med`, and has the heading `## At plan`.

### TC-8 It has an `## At plan` section next to `## At spec` (AC-47; unit) [default]
- File: `tests/test_agents.py:test_ac47_it_has_an_at_plan_section_next_to_at_spe` (new)
- Covers: CT-14
- Setup: The shipped security card.
- Action: It is read.
- Assert: both headings are in `src/nio/agents/security.md`; the card passes the card check.

### TC-9 Risk-rollback runs with its reason (AC-48; unit) [default]
- File: `tests/test_jury.py:test_ac48_risk_rollback_runs_with_its_reason` (new)
- Covers: CT-2
- Setup: A spec with no risk flags whose `contracts.md` has a `## Data model` section.
- Action: The plan gate is planned.
- Assert: the lens line holds `risk-rollback` with a reason naming the data model.

### TC-10 Security runs with its reason (AC-53; unit) [default]
- File: `tests/test_jury.py:test_ac53_security_runs_with_its_reason` (new)
- Covers: CT-2
- Setup: A spec with `risk: [auth]`.
- Action: The plan gate is planned.
- Assert: the lens line holds `security (risk: auth)`.

### TC-11 Risk-rollback runs with its reason (AC-54; unit) [default]
- File: `tests/test_jury.py:test_ac54_risk_rollback_runs_with_its_reason` (new)
- Covers: CT-2
- Setup: A spec with `risk: [data-deletion]`.
- Action: The plan gate is planned.
- Assert: the lens line holds `risk-rollback (risk: data-deletion)`.

### TC-12 The gate is blocked naming the missing card (AC-7; unit) [default]
- File: `tests/test_jury.py:test_ac7_the_gate_is_blocked_naming_the_missing_c` (new)
- Covers: CT-2
- Setup: A spec with `risk: [migration]` and no risk-rollback card.
- Action: The plan gate is planned.
- Assert: non-zero exit; the output lists the risk-rollback lens with `risk: migration` and says the gate is blocked until its card exists.

### TC-13 It is the plan gate's own ledger (AC-8; integration) [default]
- File: `tests/test_jury.py:test_ac8_it_is_the_plan_gate_s_own_ledger` (new)
- Covers: CT-3
- Setup: A plan gate that has run.
- Action: Its ledger is read.
- Assert: `.nio/specs/<slug>/jury/plan.json` and `plan.md` exist; `.nio/specs/<slug>/jury/spec.json` is unchanged.

### TC-14 It holds all four plan files (AC-9; unit) [default]
- File: `tests/test_jury.py:test_ac9_it_holds_all_four_plan_files` (new)
- Covers: CT-4
- Setup: A plan-gate juror's pack.
- Action: It is built.
- Assert: the pack holds `plan.md`, `contracts.md`, `tests.md` and `quickstart.md`.

### TC-15 The first is kept and the second dropped (AC-44; unit) [default]
- File: `tests/test_jury.py:test_ac44_the_first_is_kept_and_the_second_dropped` (new)
- Covers: CT-4, CT-5
- Setup: A plan-gate finding quoting a line of the file CT-2 binds, and another quoting a file no contract binds.
- Action: They are collected.
- Assert: the ledger holds the first finding; the collect output names the second as not grounded.

### TC-16 They hold the plan files, the spec, CLAUDE.md, `src/a.py` and `src/b.py` (AC-45; unit) [default]
- File: `tests/test_jury.py:test_ac45_they_hold_the_plan_files_the_spec_claude` (new)
- Covers: CT-4
- Setup: A plan whose contracts bind `src/a.py` and name `src/b.py` on a `Like:` line.
- Action: The plan gate's juror files are listed.
- Assert: the listed files are exactly those, plus `architecture.md` when it exists.

### TC-17 It is invalid, as at the spec gate (AC-10; unit) [default]
- File: `tests/test_jury.py:test_ac10_it_is_invalid_as_at_the_spec_gate` (new)
- Covers: CT-5, CT-8
- Setup: A plan-gate lens output with 6 findings.
- Action: It is collected.
- Assert: the collect error says a lens returns at most 5 findings.

### TC-18 It runs the plan gate (AC-11; e2e) [default]
- File: `tests/test_lenses.py:test_ac11_it_runs_the_plan_gate` (new)
- Covers: CT-15
- Setup: `@nio:plan` has finished and the human asks for the plan jury.
- Action: The jury skill starts.
- Assert: the skill runs `nio jury plan <slug> plan`, not the spec gate.

### TC-19 `test-proof` exists with an `## At plan` section (AC-12; unit) [default]
- File: `tests/test_agents.py:test_ac12_test_proof_exists_with_an_at_plan_secti` (new)
- Covers: CT-11, CT-12, CT-13
- Setup: The shipped agent cards.
- Action: They are listed.
- Assert: `src/nio/agents/test-proof.md` passes the card check, has `tier: max` and `effort: med`, and has the heading `## At plan`.

### TC-20 Its reasoning names a concrete bug for AC-1 and the `Assert:` line that fails on it (AC-13; e2e) [default]
- File: `tests/test_lenses.py:test_ac13_its_reasoning_names_a_concrete_bug_for_a` (new)
- Covers: CT-11
- Setup: A plan with TC-1 whose `Assert:` checks an exact returned value.
- Action: Test-proof reviews it.
- Assert: the lens output's reasoning for TC-1 names one changed line of the code TC-1's contract binds (e.g. a flipped condition) and quotes TC-1's `Assert:` line.

### TC-21 It raises a finding on TC-2 (AC-14; e2e) [default]
- File: `tests/test_lenses.py:test_ac14_it_raises_a_finding_on_tc_2` (new)
- Covers: CT-11
- Setup: TC-2 whose `Assert:` only checks that the command didn't throw.
- Action: Test-proof reviews it.
- Assert: one finding citing TC-2 and its AC, kind `untestable`, quoting the `Assert:` line.

### TC-22 It raises a finding on TC-3 (AC-15; e2e) [default]
- File: `tests/test_lenses.py:test_ac15_it_raises_a_finding_on_tc_3` (new)
- Covers: CT-11
- Setup: TC-3 that mocks away the integration its AC is about.
- Action: Test-proof reviews it.
- Assert: one finding citing TC-3, quoting its `Setup:` or `Action:` line naming the mock.

### TC-23 It raises a finding on TC-4 (AC-16; e2e) [default]
- File: `tests/test_lenses.py:test_ac16_it_raises_a_finding_on_tc_4` (new)
- Covers: CT-11
- Setup: TC-4 whose expected value is computed the same way as the code under test.
- Action: Test-proof reviews it.
- Assert: one finding citing TC-4 that says the expected value has no independent source.

### TC-24 It raises a finding that TC-5 would pass before any work, without running any test (AC-17; e2e) [default]
- File: `tests/test_lenses.py:test_ac17_it_raises_a_finding_that_tc_5_would_pass` (new)
- Covers: CT-11
- Setup: TC-5 whose AC already holds on today's code (the bound function already returns the expected value).
- Action: Test-proof reviews it.
- Assert: one finding citing TC-5 and quoting the bound code; the test-proof card's tools are read-only (`tools: [read]`), so it can't run a test.

### TC-25 It raises a finding on TC-6 (AC-18; e2e) [default]
- File: `tests/test_lenses.py:test_ac18_it_raises_a_finding_on_tc_6` (new)
- Covers: CT-11
- Setup: TC-6, filed under US-1's build-order entry, whose AC only US-2's contracts can satisfy.
- Action: Test-proof reviews it.
- Assert: one finding citing TC-6 and naming US-2.

### TC-26 It raises no "test missing" finding without having searched the repo (AC-19; e2e) [default]
- File: `tests/test_lenses.py:test_ac19_it_raises_no_test_missing_finding_withou` (new)
- Covers: CT-11
- Setup: An AC whose test exists in the repo but isn't listed in `tests.md`.
- Action: Test-proof reviews the plan.
- Assert: any finding saying a test is missing names where it searched; none is raised for the AC whose test exists.

### TC-27 `architecture-fit` exists with an `## At plan` section (AC-20; unit) [default]
- File: `tests/test_agents.py:test_ac20_architecture_fit_exists_with_an_at_plan` (new)
- Covers: CT-11, CT-12, CT-13
- Setup: The shipped agent cards.
- Action: They are listed.
- Assert: `src/nio/agents/architecture-fit.md` passes the card check, has `tier: max` and `effort: med`, and has the heading `## At plan`.

### TC-28 It raises a finding on CT-3 (AC-21; e2e) [default]
- File: `tests/test_lenses.py:test_ac21_it_raises_a_finding_on_ct_3` (new)
- Covers: CT-12
- Setup: New contract CT-3 whose `Like:` names `src/nio/jury.py:plan` but whose shape follows a different pattern.
- Action: Architecture-fit reviews it.
- Assert: one finding citing CT-3 and quoting its `Like:` line.

### TC-29 It raises a finding quoting that rule (AC-22; e2e) [default]
- File: `tests/test_lenses.py:test_ac22_it_raises_a_finding_quoting_that_rule` (new)
- Covers: CT-12
- Setup: A project rule "Never commit without the human asking" and a contract that commits on its own.
- Action: Architecture-fit reviews the plan.
- Assert: one finding citing the contract, kind `contradiction`, quoting the rule word for word.

### TC-30 It raises a finding that the component is an orphan (AC-23; e2e) [default]
- File: `tests/test_lenses.py:test_ac23_it_raises_a_finding_that_the_component_i` (new)
- Covers: CT-12
- Setup: A new contract that a build-order entry delivers and that cites an FR, but that no other contract and no existing code calls.
- Action: Architecture-fit reviews it.
- Assert: one finding citing the contract.

### TC-31 It raises a finding on it (AC-24; e2e) [default]
- File: `tests/test_lenses.py:test_ac24_it_raises_a_finding_on_it` (new)
- Covers: CT-12
- Setup: A new module whose contract cites FR-2, which doesn't need it, and no row in `## Complexity tracking`.
- Action: Architecture-fit reviews the plan.
- Assert: one finding citing the contract and FR-2, kind `scope`.

### TC-32 It raises a finding on US-2 (AC-25; e2e) [default]
- File: `tests/test_lenses.py:test_ac25_it_raises_a_finding_on_us_2` (new)
- Covers: CT-12
- Setup: A build-order entry for US-2 with nothing that can be shown when it is done.
- Action: Architecture-fit reviews the plan.
- Assert: one finding citing US-2 that asks what can be shown when it is done.

### TC-33 It raises a finding citing both (AC-26; e2e) [default]
- File: `tests/test_lenses.py:test_ac26_it_raises_a_finding_citing_both` (new)
- Covers: CT-12
- Setup: Two contracts that give the same input different limits.
- Action: Architecture-fit reviews the plan.
- Assert: one finding, kind `inconsistency`, citing both CT IDs.

### TC-34 It fails naming CT-2 (AC-27; unit) [default]
- File: `tests/test_plan.py:test_ac27_it_fails_naming_ct_2` (new)
- Covers: CT-9, CT-10
- Setup: CT-2 bound `(new)` with no `Like:` line.
- Action: `nio check plan` runs.
- Assert: non-zero exit; the error names CT-2 and `Like`.

### TC-35 Only CT-6 is an error (AC-49; unit) [default]
- File: `tests/test_plan.py:test_ac49_only_ct_6_is_an_error` (new)
- Covers: CT-9, CT-10
- Setup: CT-5 bound `(new)` with `Like: none: first HTTP endpoint in the project`, and CT-6 with `Like: none` and no reason.
- Action: `nio check plan` runs.
- Assert: one error, naming CT-6 and the missing reason.

### TC-36 It raises a finding naming the existing parser (AC-50; e2e) [default]
- File: `tests/test_lenses.py:test_ac50_it_raises_a_finding_naming_the_existing` (new)
- Covers: CT-12
- Setup: CT-5 with `Like: none: first parser` while the repo already has a parser.
- Action: Architecture-fit reviews it.
- Assert: one finding citing CT-5, quoting its `Like:` line and naming the existing file.

### TC-37 It fails (AC-28; unit) [default]
- File: `tests/test_plan.py:test_ac28_it_fails` (new)
- Covers: CT-9
- Setup: CT-2 with `Like: src/nio/nope.py:thing` and no such file.
- Action: `nio check plan` runs.
- Assert: non-zero exit; the error names CT-2 and `src/nio/nope.py`.

### TC-38 It fails (AC-29; unit) [default]
- File: `tests/test_plan.py:test_ac29_it_fails` (new)
- Covers: CT-9
- Setup: CT-2 with `Like: src/nio/jury.py:no_such_symbol`.
- Action: `nio check plan` runs.
- Assert: non-zero exit; the error names CT-2 and `no_such_symbol`.

### TC-39 CT-2 raises no error (AC-30; unit) [default]
- File: `tests/test_plan.py:test_ac30_ct_2_raises_no_error` (new)
- Covers: CT-9, CT-10
- Setup: CT-2 with `Like: src/nio/jury.py:plan`.
- Action: `nio check plan` runs with no network and no model.
- Assert: no error naming CT-2; no model or network call is made (NFR-1).

### TC-40 CT-4 raises no error (AC-31; unit) [default]
- File: `tests/test_plan.py:test_ac31_ct_4_raises_no_error` (new)
- Covers: CT-9, CT-10
- Setup: CT-4 bound `(existing)` with no `Like:` line.
- Action: `nio check plan` runs.
- Assert: no error naming CT-4.

### TC-41 It raises no error for it (AC-32; unit) [default]
- File: `tests/test_plan.py:test_ac32_it_raises_no_error_for_it` (new)
- Covers: CT-9
- Setup: A build-order entry `### US-2` with no `Scenario:` line.
- Action: `nio check plan` runs.
- Assert: no error naming US-2 or `Scenario`.

### TC-42 The ledger records it (AC-33; unit) [default]
- File: `tests/test_jury.py:test_ac33_the_ledger_records_it` (new)
- Covers: CT-6, CT-8
- Setup: Confirmed plan-gate finding J-2.
- Action: It is disposed `plan-fix` and the plan files are changed.
- Assert: `nio jury dispose <slug> plan J-2 plan-fix` exits 0; `jury/plan.json` shows J-2 as `plan-fix`.

### TC-43 The disposition is refused (AC-34; unit) [default]
- File: `tests/test_jury.py:test_ac34_the_disposition_is_refused` (new)
- Covers: CT-6
- Setup: Spec-gate finding J-1.
- Action: It is disposed `plan-fix`.
- Assert: non-zero exit; the error says `plan-fix` belongs to the plan gate.

### TC-44 A change request on the spec is written and the plan gate waits (AC-35; integration) [default]
- File: `tests/test_jury.py:test_ac35_a_change_request_on_the_spec_is_written` (new)
- Covers: CT-6, CT-7, CT-15
- Setup: Confirmed plan-gate finding J-3 rooted in the approved spec.
- Action: It is handled.
- Assert: a change record naming J-3 and the spec items it changes; no further plan-gate round is collected until the spec gate re-approves.

### TC-45 Only FR-4 and the items around it are in its pack, and the plan jury resumes once the spec is re-approved (AC-36; integration) [default]
- File: `tests/test_jury.py:test_ac36_only_fr_4_and_the_items_around_it_are_in` (new)
- Covers: CT-7
- Setup: The change request for J-3 edits FR-4 only.
- Action: The spec jury re-checks.
- Assert: the fix-check pack names FR-4 and no unchanged FR; after re-approval the next plan-gate round can be collected.

### TC-46 The plan does not state its own limit for it (AC-37; integration) [default]
- File: `tests/test_jury.py:test_ac37_the_plan_does_not_state_its_own_limit_fo` (new)
- Covers: CT-15
- Setup: A finding that the spec leaves a limit unstated.
- Action: It is fixed.
- Assert: the ledger shows the finding as `spec-change`; no `plan-fix` is recorded for it; the plan files are unchanged until the spec is re-approved.

### TC-47 The ledger records it with its change request (AC-43; unit) [default]
- File: `tests/test_jury.py:test_ac43_the_ledger_records_it_with_its_change_re` (new)
- Covers: CT-6
- Setup: Confirmed plan-gate finding J-3 that the human confirmed as spec-rooted.
- Action: It is disposed.
- Assert: `jury/plan.json` shows J-3 as `spec-change` with the change record's ID.

### TC-48 It tells the juror not to raise J-2 again (AC-38; unit) [default]
- File: `tests/test_jury.py:test_ac38_it_tells_the_juror_not_to_raise_j_2_agai` (new)
- Covers: CT-5, CT-8
- Setup: Plan-gate finding J-2 the human accepted as risk in an earlier round.
- Action: A lens's fix-check pack is built for the next round.
- Assert: `nio jury fixcheck <slug> plan --lens test-proof` lists J-2 under "Settled by the human: don't raise these again".

### TC-49 J-1 goes to the refuter before any outcome (AC-51; unit) [default]
- File: `tests/test_jury.py:test_ac51_j_1_goes_to_the_refuter_before_any_outco` (new)
- Covers: CT-5, CT-8
- Setup: A plan-gate round whose lenses raise major finding J-1.
- Action: It is collected.
- Assert: collect prints a refuter batch holding J-1; `nio jury check <slug> plan` says `pending` until the refuter answers.

### TC-50 No new round is asked for and the majors go to the human as one list (AC-52; unit) [default]
- File: `tests/test_jury.py:test_ac52_no_new_round_is_asked_for_and_the_majors` (new)
- Covers: CT-5, CT-8
- Setup: The plan gate's first review is done and only confirmed majors remain.
- Action: `nio jury check <slug> plan --record` runs.
- Assert: outcome `human`, listing every remaining major in one list; no `rerun`.

### TC-51 One `nio: approve plan` commit holds the plan files and the plan verdict (AC-39; integration) [default]
- File: `tests/test_jury.py:test_ac39_one_nio_approve_plan_commit_holds_the_pl` (new)
- Covers: CT-15
- Setup: The plan gate's outcome is approved.
- Action: The approval is recorded.
- Assert: the latest commit's message is `nio: approve plan` and it touches the four plan files and the plan gate's verdict record.

### TC-52 It refuses (AC-40; integration) [default]
- File: `tests/test_plan.py:test_ac40_it_refuses` (new)
- Covers: CT-16
- Setup: A spec with a `plan.md` whose plan gate is not approved.
- Action: The tasks stage is asked to start.
- Assert: `nio check plan <slug> --approved` exits 1 saying "the plan must be approved first"; no `tasks.md` exists. The tasks stage's own refusal is proven when #42 wires in this check.

### TC-53 It refuses; given a bug-fix spec with no `plan.md`, it proceeds (AC-55; integration) [default]
- File: `tests/test_plan.py:test_ac55_it_refuses_given_a_bug_fix_spec_with_no` (new)
- Covers: CT-16
- Setup: A full spec with no `plan.md`.
- Action: The tasks stage is asked to start.
- Assert: for the full spec, `nio check plan <slug> --approved` exits 1 saying "the plan must be approved first"; for the bug-fix spec it exits 0 saying "a bug-fix spec has no plan stage". Starting the drafter is proven when #42 wires in this check.

### TC-54 The plan gate is no longer approved and its next pack covers CT-2 (AC-56; integration) [default]
- File: `tests/test_jury.py:test_ac56_the_plan_gate_is_no_longer_approved_and` (new)
- Covers: CT-3, CT-7, CT-16
- Setup: An approved plan whose CT-2 cites FR-4.
- Action: A change request edits FR-4 and the spec is re-approved.
- Assert: `nio check plan <slug> --approved` exits 1 saying "the plan must be approved first"; `nio jury fixcheck <slug> plan --lens architecture-fit` names CT-2 and the changed FR-4.

### TC-55 J-6 joins C-1 (AC-57; integration) [default]
- File: `tests/test_jury.py:test_ac57_j_6_joins_c_1` (new)
- Covers: CT-6
- Setup: The plan gate waits on change request C-1 for J-3.
- Action: J-6 is confirmed spec-rooted.
- Assert: the ledger shows J-6 as `spec-change` naming C-1; no second change record is written; the gate still waits.

### TC-56 The plan jury resumes and J-3 is open again for the human (AC-58; integration) [default]
- File: `tests/test_jury.py:test_ac58_the_plan_jury_resumes_and_j_3_is_open_ag` (new)
- Covers: CT-6, CT-7
- Setup: The plan gate waits on change request C-1 for J-3.
- Action: The human drops C-1.
- Assert: `nio jury check <slug> plan` no longer says the gate is paused; J-3 is listed for the human with fix in the plan or accept as risk.

### TC-57 It is refused, and the tasks stage refuses too (AC-59; integration) [default]
- File: `tests/test_jury.py:test_ac59_it_is_refused_and_the_tasks_stage_refuse` (new)
- Covers: CT-5, CT-7, CT-16
- Setup: The plan gate was handed to the human with majors J-2 and J-4 open.
- Action: A new round is collected before the human rules.
- Assert: collect exits non-zero saying the gate waits on the human's ruling; `nio check plan <slug> --approved` exits 1 saying "the plan must be approved first (`with-human`)".

### TC-58 It proceeds (AC-41; integration) [default]
- File: `tests/test_plan.py:test_ac41_it_proceeds` (new)
- Covers: CT-16
- Setup: A spec with a `nio: approve plan` commit.
- Action: The tasks stage is asked to start.
- Assert: `nio check plan <slug> --approved` exits 0. Starting the drafter is proven when #42 wires in this check.

### TC-59 It proceeds; given a plan gate handed to the human but not closed, it refuses (AC-42; integration) [default]
- File: `tests/test_jury.py:test_ac42_it_proceeds_given_a_plan_gate_handed_to` (new)
- Covers: CT-7, CT-16
- Setup: A plan gate the human closed with a reason.
- Action: The tasks stage is asked to start.
- Assert: `nio check plan <slug> --approved` exits 0 for the closed gate and exits 1 saying "the plan must be approved first (`with-human`)" for the one handed over.
## Quality tests

### TC-60 Planning the gate and checking `Like:` call no model (NFR-1; unit) [default]
- File: `tests/test_jury.py:test_nfr1_plan_gate_makes_no_model_call` (new)
- Covers: CT-2, CT-9
- Setup: A fixture repo with a passing plan, and `PATH` stripped of every host CLI (`claude`, `codex`) and network disabled by unsetting proxy variables.
- Action: Call `jury.plan(root, slug, "plan")` and `plan.check(root, slug, gate=True)`.
- Assert: both return without error, and a patched `subprocess.run` records no call other than `git`.

## Misuse tests

### TC-61 The plan's author can't call its own review the gate (UJ-1 misuse; integration) [default]
- File: `tests/test_jury.py:test_uj1_plan_gate_needs_lens_outputs` (new)
- Covers: CT-5, CT-8
- Setup: A fixture plan that passes its check, with no lens output in the run folder.
- Action: `nio jury check <slug> plan --record` runs.
- Assert: outcome `rerun` with "no lens output has been collected yet"; no verdict record is written.

### TC-62 A juror given only `plan.md` would miss the other files (UJ-1 misuse; unit) [default]
- File: `tests/test_jury.py:test_uj1_juror_files_hold_all_plan_files` (new)
- Covers: CT-4
- Setup: A fixture plan with all four plan files.
- Action: `nio jury files <slug> plan` runs.
- Assert: the output holds `plan.md`, `contracts.md`, `tests.md` and `quickstart.md`, each once.

### TC-63 The plan can't settle a spec-rooted finding with a plan fix (UJ-2 misuse; integration) [default]
- File: `tests/test_jury.py:test_uj2_spec_change_blocks_plan_fix` (new)
- Covers: CT-6, CT-7
- Setup: Plan-gate finding J-3 disposed `spec-change` with change record C-1 still `pending`.
- Action: `nio jury dispose <slug> plan J-3 plan-fix --by agent --note "filled the limit in the plan"` runs.
- Assert: non-zero exit; the error says J-3 is disposed and waits on C-1; the ledger still shows `spec-change`.
