---
slug: 2026-11-07-fewer-gate-turns
retired: []                      # TC IDs removed from this plan; never reused
---
# Tests: drive a jury gate in fewer orchestrator calls

Fixtures: plain functions in `tests/test_jury.py`, run by `uv run python tests/test_jury.py [names]` through `selfcheck.main`.
Helpers used below:
- `gate_spec()`: new in `tests/test_jury.py`; `setup()` plus `.nio/specs/refund-double-charge/spec.md` copied from `tests/fixtures/spec/spec-bugfix.md` (it passes `nio check spec --gate`; its plan is testability, logic and adversary, tier high). Returns the root; the slug is `refund-double-charge`.
- `out(root, run, gate, lens, findings="none", verdicts="", lens_name=None, context="sufficient")`: new; writes `.nio/runs/<run>/jury/<gate>-<lens>.md` in the lens output format, subject `refund-double-charge`, front matter `lens: <lens_name or lens>`.
- `FINDING`: a major `gap` finding citing `EB-1` and quoting `create exactly one refund` (it grounds in the fixture).
- `step(root, *args)`: calls `jury.step(root, "refund-double-charge", "spec", *args)` and returns its lines; `next_of(lines)` is the text after `next: ` on the last line; `run_of(lines)` the run after `run: `.
- `cli(root, *argv)`: runs `nio.cli.main` in-process in `root` with `sys.argv = ["nio", *argv]` and returns (exit code, stdout, stderr), like `test_cli_dispose_order`.

## Acceptance tests

### TC-1 A step writes the refuter batch to a file (AC-1; integration) [agent]
- File: `tests/test_jury.py:test_ac1_step_writes_the_refuter_batch` (new)
- Covers: CT-1, CT-2
- Setup: `gate_spec()`; `run = run_of(step(root))`; `out` for testability with `FINDING`, logic and adversary with `none`, in `run`.
- Action: `lines = step(root, "--run"...)`, i.e. `jury.step(root, slug, "spec", run)`.
- Assert: the ledger has `J-1` with validation `pending`; `.nio/runs/<run>/jury/packs/refuter.md` exists and holds `### J-1`; `next_of(lines)` contains `packs/refuter.md` and `spec-refuter.md`; no outcome line (`outcome:`) is printed.

### TC-2 A rerun writes each fix-check pack in a new run (AC-2; integration) [agent]
- File: `tests/test_jury.py:test_ac2_rerun_writes_fix_check_packs` (new)
- Covers: CT-1, CT-2
- Setup: TC-1's state; the refuter output `### J-1\n- result: confirmed\n- reason: yes\n` in the run; `step` → `outcome: rejected`; `jury.dispose(root, slug, "spec", "J-1", "spec-fix", "agent", "EB-1 says per order")`; EB-1's text changed to `create exactly one refund per order`.
- Action: `lines = step(root, run)`.
- Assert: `outcome: rerun` in lines; `run_of(lines)` is a new run ≠ `run`; the files under its `jury/packs/` (`step.json` aside) are exactly `<lens>.md` for each lens `changed(root, slug, "spec")[1]` names, here `testability.md`; `testability.md` starts with the lines `jury.fixcheck(root, slug, "spec", "testability")` returns, in order, and ends with the `## Your output` line naming `<new run>/jury/spec-testability.md`; the verdict record count under `.nio/memory/project/` is the count after the rejected step (no new record for `rerun`).

### TC-3 A step prints no finding body (AC-3; integration) [agent]
- File: `tests/test_jury.py:test_ac3_step_prints_no_finding_body` (new)
- Covers: CT-1
- Setup: TC-1's setup, with logic's output holding a finding the fixture can't ground (quote `no such words`) in place of `none`.
- Action: `lines = step(root, run)`.
- Assert: no line starts with `- quote:`, `- situation` or `- fix:`, and none is `## Refuter batch...`; a line starts `dropped J-` for the ungrounded finding; the last line starts `next: `.

### TC-4 A missing and an invalid lens are named to re-run (AC-4; integration) [agent]
- File: `tests/test_jury.py:test_ac4_missing_and_invalid_lenses_rerun` (new)
- Covers: CT-1
- Setup: `gate_spec()`; `run = run_of(step(root))`; `out` for testability (`none`) and for logic with its `## Reasoning` section removed; no adversary output.
- Action: `lines = step(root, run)`.
- Assert: a line `INVALID spec-logic.md: ...`; `next` lines name `re-run logic` and `re-run adversary`, each with `packs/<lens>.md`; no `outcome:` and no `recorded` line; the ledger's `recorded` list is empty.

### TC-5 A repeated step changes nothing (AC-5; integration) [agent]
- File: `tests/test_jury.py:test_ac5_repeated_step_changes_nothing` (new)
- Covers: CT-1, CT-2
- Setup: (a) `gate_spec()`, `first = step(root)`; (b) TC-2's state after its action, `second = step(root, run)`.
- Action: (a) `step(root, run_of(first))` and `step(root)`; (b) `step(root, run)` again.
- Assert: (a) both print `run: <run_of(first)>` and the same `next:` line; the bytes of every file under `<run>/jury/packs/` are unchanged; the number of folders under `.nio/runs/` is unchanged. (b) the same `run:` line as `second`; the ledger's `recorded` and `round` unchanged; the run folder count unchanged; the verdict record count unchanged.

### TC-6 One dispose call sets three findings (AC-6; integration) [agent]
- File: `tests/test_jury.py:test_ac6_dispose_three_in_one_call` (new)
- Covers: CT-3
- Setup: the `refunds` ledger of `setup()` with three open findings J-1, J-2, J-3 (one lens output with three findings, collected, refuter confirming all).
- Action: `cli(root, "jury", "dispose", "refunds", "spec", "J-1,J-2,J-3", "spec-fix", "--by", "agent", "--note", "fixed")`.
- Assert: exit 0; stdout lines are `J-1: spec-fix by agent`, `J-2: spec-fix by agent`, `J-3: spec-fix by agent`; each finding has status `disposed`, disposition `spec-fix`, by `agent`, note `fixed`.

### TC-7 A refused ID, a repeat or a wrong note count changes nothing (AC-7; integration) [agent]
- File: `tests/test_jury.py:test_ac7_refused_dispose_changes_nothing` (new)
- Covers: CT-3
- Setup: TC-6's ledger; its file bytes kept.
- Action: four calls: `J-1,J-9` (`J-9` unknown) as `spec-fix`; `J-1,J-2` as `accepted-risk --by agent`; `J-1,J-1`; `J-1,J-2,J-3` with two `--note` values.
- Assert: each exits 1; the stderr names `J-9`, then `J-1` and `J-2` with `the human's call`, then `distinct`, then `2 notes for 3 findings`; the ledger file bytes are unchanged after each.

### TC-8 Every rendered juror agent may write its output file (AC-8; e2e) [agent]
- File: `tests/test_agents.py:test_ac8_juror_cards_write_their_output` (new)
- Covers: CT-5
- Setup: a temp repo (`test_records.repo()`) with `agents.hosts` set to `["claude", "codex"]`.
- Action: `nio agents sync` there (in-process CLI), then read each rendered juror agent and its card: adversary, architecture-fit, conformance, consistency, correctness, executability, logic, refuter, risk-rollback, scope, security, test-proof, testability.
- Assert: each card's `tools` is `["read", "write"]`; its `## Output format` section holds `the file your pack names, and to no other file`; `render_claude` of logic has `tools: "Read, Grep, Glob, Write"` and no `Edit`; no other card's `tools` changed (the worker, drafters and evaluator keep theirs).

### TC-9 A copied lens name is filed under the file's lens (AC-9; integration) [agent]
- File: `tests/test_jury.py:test_ac9_file_name_gives_the_lens` (new)
- Covers: CT-4
- Setup: `setup()`; `lens(root, "R-1", "testability", MINOR, lens_name="logic")` (the existing helper: file `spec-testability.md`, front matter `lens: logic`).
- Action: `lines = jury.collect(root, "refunds", "spec", "R-1", ["testability"])`.
- Assert: every finding's sources have lens `testability`; `led["jurors"]["spec-testability"]["lens"] == "testability"`; exactly one line contains `spec-testability.md` and `logic`; `jury.check` lines hold no `testability: no output`.

### TC-10 An escalation juror counts as its lens (AC-10; integration) [agent]
- File: `tests/test_jury.py:test_ac10_escalation_file_counts_as_its_lens` (new)
- Covers: CT-4
- Setup: `setup()`; `lens(root, "R-1", "logic-2", "none", lens_name="logic-2")` (file `spec-logic-2.md`, front matter `lens: logic-2`, as a juror copying its file name would write).
- Action: `jury.collect(root, "refunds", "spec", "R-1")`.
- Assert: `led["jurors"]["spec-logic-2"]["lens"] == "logic"` (today it is `logic-2`); exactly one line names `spec-logic-2.md` and `logic-2`.

### TC-11 Scenario A takes at most 15 orchestrator calls (AC-11; e2e) [agent]
- File: `tests/test_jury.py:test_ac11_scenario_a_in_at_most_15_calls` (new)
- Covers: CT-1, CT-2, CT-3, CT-6
- Setup: `gate_spec()`; a counter `calls` that each orchestrator action below adds one to; an action is a step call, a juror output written by the test as a juror would (a juror launch), a dispose call, or the `nio pack` call the consistency trigger needs; edits to `spec.md` are not counted.
- Action: drive scenario A of research RF-2 the way the skill's `## Steps` say, in their order: `nio jury plan` (1); `nio pack` (1); `step(root, "", ["consistency:D-1 current"])` (1); three juror outputs, testability and logic each with one major finding grounded in EB-1 or AC-1, consistency `none` (3); `step` (1); the refuter output confirming both (1); `step` → `rejected` (1); one dispose call for both IDs (1); edit EB-1 and AC-1 (0); `step` → new run with two fix-check packs (1); two juror outputs with `fixed` verdicts (2); `step` (1).
- Assert: the last step prints `outcome: approved` and `next: tell the human`, and no step after the fix-check run's packs names `re-run consistency`; `calls <= 15` (it is 14); the test's docstring lists the 31 calls of RF-2 for the same scenario and the 14 here, call by call.

### TC-12 First-review packs hold today's content plus the output path (AC-12; integration) [agent]
- File: `tests/test_jury.py:test_ac12_first_review_packs` (new)
- Covers: CT-1, CT-2
- Setup: `gate_spec()` (its risk flags are `[money]`) with `agents.hosts` set to `["claude"]` in `.nio/config.json`.
- Action: `lines = step(root, "", ["scope:asked", "consistency:D-1"])`.
- Assert: one `run <lens>:` line per planned lens (testability, logic, adversary, scope, consistency), each naming `packs/<lens>.md` and `spec-<lens>.md`; every pack holds `.nio/specs/refund-double-charge/spec.md`, the `nio check spec` output's last line (`0 errors`), the template's `## Findings` heading, and the `## Your output` line with its own output path; only `scope.md` holds `intake.md`; only `consistency.md` holds `# Memory for`; a file under `<run>/packs/` holds that memory pack; the next line names `nio jury next refund-double-charge spec --run <run>`. `.claude/agents/nio-logic.md` exists (the step rendered the agents; that it grants `Write` is TC-8's, after T-4 changes the cards).

### TC-13 A needs-more lens is re-run (AC-13; integration) [agent]
- File: `tests/test_jury.py:test_ac13_needs_more_is_rerun` (new)
- Covers: CT-1
- Setup: `gate_spec()`, `run`; outputs testability and adversary `none`, logic `none` with `context: needs-more`.
- Action: `lines = step(root, run)`.
- Assert: a `next:` line names `re-run logic`; no `outcome:` line; the ledger's `recorded` is empty.

### TC-14 Rejected, human and approved each give their next line (AC-14; integration) [agent]
- File: `tests/test_jury.py:test_ac14_outcome_next_lines` (new)
- Covers: CT-1
- Setup: three fixtures from `gate_spec()`: (a) TC-2's rejected state; (b) a first review whose only finding is a major the refuter confirms, disposed, fixed, then a fix check whose verdict is `not fixed` after the first review (the human's list); (c) three lenses with `none`.
- Action: `step` on each.
- Assert: (a) `outcome: rejected` and the next line contains `nio jury dispose`; (b) `outcome: human` and the next line contains `show the human`, and no line names `re-run` for a lens the fix-check run has no pack for; (c) `outcome: approved` and the next line contains `nio flow next refund-double-charge`.

### TC-15 Per-ID notes land in order (AC-15; integration) [agent]
- File: `tests/test_jury.py:test_ac15_notes_per_finding_in_order` (new)
- Covers: CT-3
- Setup: TC-6's ledger.
- Action: `cli(root, "jury", "dispose", "refunds", "spec", "J-1,J-2,J-3", "spec-fix", "--by", "agent", "--note", "one", "--note", "two", "--note", "three")`.
- Assert: J-1's note is `one`, J-2's `two`, J-3's `three`.

### TC-16 An unplanned lens file stops the step (AC-16; integration) [agent]
- File: `tests/test_jury.py:test_ac16_unplanned_lens_file_stops_the_step` (new)
- Covers: CT-1
- Setup: `gate_spec()`, `run`; outputs for the three planned lenses and `out(root, run, "spec", "security")`.
- Action: `cli(root, "jury", "next", "refund-double-charge", "spec", "--run", run)`.
- Assert: exit 1; stderr names `spec-security.md` and `testability, logic, adversary`; no ledger file `.nio/specs/refund-double-charge/jury/spec.json` was written.

### TC-17 The implementation gate's step asks for evidence, then writes packs (AC-12; integration) [agent]
- File: `tests/test_evidence.py:test_ac12_step_at_the_implementation_gate` (new)
- Covers: CT-1, CT-2
- Setup: `gate_repo()`; `run = records.new_run(root)`.
- Action: `jury.step(root, "s", "implementation-E-1", run)`; then `evidence.collect(root, "s", "E-1", run)`; then `jury.step(root, "s", "implementation-E-1", run)`.
- Assert: the first prints `next: nio jury evidence s E-1 --run <run>` and writes no pack; the second writes `packs/conformance.md` and `packs/correctness.md`, each starting with the text of `evidence.pack` for its lens with "You may write only your output file" in place of "You have no way to write files", and ending with the `## Your output` line naming `implementation-E-1-<lens>.md`.

## Quality tests
### TC-18 The skill's steps for scenario A count at most 15 calls (NFR-1; unit) [agent]
- File: `tests/test_jury.py:test_nfr1_skill_names_the_step` (new)
- Covers: CT-6
- Setup: `skills/jury/SKILL.md` as shipped.
- Action: read its `## Steps` section.
- Assert: it names `nio jury next` and `J-a,J-b` (several IDs in one dispose); `save each one's answer verbatim` is gone; outside the escalation step (the one naming `--blocker`) and the gate-closing text (`--human`), it names none of `nio run`, `nio agents sync`, `nio jury template`, `nio jury collect`, `nio jury check`, `nio jury changed`, `nio jury fixcheck`, `nio check spec <slug> --gate`. Every orchestrator call the steps name for scenario A is one TC-11 counts.

## Misuse tests
### TC-19 Separate collect and check calls still work beside the step (UJ-1 misuse; integration) [agent]
- File: `tests/test_jury.py:test_misuse_separate_calls_beside_the_step` (new)
- Covers: CT-1
- Setup: TC-1's state.
- Action: `jury.collect(root, slug, "spec", run)` and `jury.check(root, slug, "spec", record=True)` by hand, then `step(root, run)`.
- Assert: the step prints no `outcome:` line and its `next:` line is the refuter action (the batch still pending). Then, in TC-2's `rejected` state, a hand-run `jury.check(..., record=True)` followed by `step(root, run)` leaves the verdict record count where the hand-run check left it.
