---
slug: 2026-11-07-review-fixes
retired: []                      # TC IDs removed from this plan; never reused
---
# Tests: fix the review's findings in the speed-up PRs

Fixtures: plain functions in the self-check scripts under `tests/`, run by `uv run python tests/<file> [<test name>]`.
Helpers: in `tests/test_jury.py`, `gate_spec()`, `step(root, run)`, `out(root, run, gate, lens, findings)`, `FINDING`, `REFUTE`, `CONFIRM`, `run_of`, `next_of`, `verdict_count` (existing). In `tests/test_evidence.py`, `gate_repo()` and `evidence()` (existing). A temp git repo with a detached worktree at `.nio/runs/R-1/worktree` for `land` (as in #102's repro).
The "first round" below: `jury.plan(root, GSLUG, "spec", ["consistency:D-1 current"])`, `run = run_of(step(root, "", ADD))` with the same add, then `out(...)` for each lens in the run, `FINDING` for testability and `none` for the rest.

## Acceptance tests

### TC-1 A refuter file written before its batch is refused (AC-1; integration) [agent]
- File: `tests/test_jury.py:test_ac1_refuter_before_its_batch_is_refused` (new)
- Covers: CT-1
- Setup: the first round's outputs, plus `.nio/runs/<run>/jury/spec-refuter.md` holding `REFUTE.format(n=1)` (#101's repro).
- Action: `step(root, run, ADD)` twice, then delete the refuter file and `step(root, run, ADD)` once more.
- Assert: the first two raise `ValueError` whose text holds `refuter output before its batch`; after them the ledger (`jury.load`) has no finding with status `refuted`, `round` 0 and `recorded` empty, and `verdict_count` is unchanged; the third call's lines hold `## Refuter batch` or a `next:` naming `packs/refuter.md`.

### TC-2 A refuter output counts only for its batch's IDs, the first verdict per ID (AC-2; integration) [agent]
- File: `tests/test_jury.py:test_ac2_refuter_only_for_its_batch` (new)
- Covers: CT-1, CT-2
- Setup: the first round, logic writing `FINDING.replace("EB-1", "AC-1").replace("create exactly one refund", "one refund exists")` (a finding of its own), so J-1 (testability) and J-2 (logic) are pending; assert after the step that J-2 exists. `step` prints the batch (both IDs asked). Case a: the refuter file holds `REFUTE` for J-1, then `CONFIRM` for J-1, and no J-2 block. Case b, on a fresh root built the same way: after the batch, the test sets the ledger's `asked[run]` to `["J-1"]` with `jury.save`, and the refuter file holds `REFUTE` for J-1 and for J-2.
- Action: `step(root, run, ADD)` in each case.
- Assert: case a: J-1's validation is `refuted`, J-2's `pending` (listed, no verdict); case b: J-1 `refuted`, J-2 `pending` (not listed).
### TC-3 A refuter output after its batch applies as before (AC-3; integration) [agent]
- File: `tests/test_jury.py:test_ac3_refuter_after_its_batch_applies` (new)
- Covers: CT-1
- Setup: the first round; `step` prints the batch; then the refuter file holds `CONFIRM.format(n=1)`.
- Action: `step(root, run, ADD)`.
- Assert: J-1's validation is `confirmed`; the lines hold `outcome: rejected`; `verdict_count` grew by one.

### TC-4 land keeps CRLF, latin-1 and binary bytes (AC-4; integration) [agent]
- File: `tests/test_waves.py:test_ac4b_land_keeps_bytes` (new)
- Covers: CT-4, CT-5
- Setup: a temp repo with `win.txt` = `b"a\r\nb\r\n"` committed; a detached worktree at `.nio/runs/R-1/worktree` from HEAD in which `win.txt` becomes `b"a\r\nB\r\n"` and `added.txt` = `b"new\r\nfile\r\n"`, `latin.txt` = `b"caf\xe9\n"`, `bin.dat` = `bytes(range(256))` are added.
- Action: `implement.land(root, "s", "T-1", tree, <base commit>)`.
- Assert: its third value is `""`; for each of the four files the main tree's bytes equal the worktree's; the saved patch's bytes contain `b"\r\n"`.

### TC-5 shelve's patch restores the exact bytes (AC-5; integration) [agent]
- File: `tests/test_waves.py:test_ac5b_shelve_keeps_bytes` (new)
- Covers: CT-4, CT-5
- Setup: the same repo, with the same four changes made in the main tree (no worktree), the bytes kept.
- Action: `implement.shelve(root, "s", "R-1", "T-1")`, then `git apply --binary <the patch>` in the main tree.
- Assert: `shelve` raises nothing; after it the files are back to HEAD; after the apply each file's bytes equal the kept bytes. Then, with the tree clean, `implement.shelve(root, "s", "R-2", "T-2")` raises nothing and writes `.nio/runs/R-2/T-2.patch` with bytes `b""`.

### TC-6 An LF UTF-8 patch is git's own bytes (AC-6; integration) [agent]
- File: `tests/test_waves.py:test_ac6b_lf_patch_unchanged` (new)
- Covers: CT-5
- Setup: as TC-4, but only `a.txt` = `b"x\n"` committed and edited to `b"y\n"` in the worktree.
- Action: `implement.land(...)`.
- Assert: the saved patch's bytes equal `git diff --cached --binary --no-renames <base>` run in the worktree with `capture_output` and no text mode; the main tree's `a.txt` is `b"y\n"`.

### TC-7 A rejected round, risk accepted and a wording edit re-runs every voting lens (AC-7; integration) [agent]
- File: `tests/test_jury.py:test_ac7_accepted_risk_and_edit_reruns_voters` (new)
- Covers: CT-7
- Setup: #103's repro: the first round; the refuter (after its batch) confirms J-1; outcome `rejected`; `jury.dispose(root, GSLUG, "spec", "J-1", "accepted-risk", "human", "fine")`; the spec's "create exactly one refund" becomes "create one refund".
- Action: `step(root, run, ADD)`, then `step(root, <its run>, ADD)` again before any juror runs.
- Assert: the first call's lines hold `outcome: rerun` and one `run <lens>:` line for each lens in the round's votes (adversary, consistency, logic, testability), each pack file existing; the second call prints the same `run:` and the same `run <lens>:` lines.
### TC-8 A whitespace-only edit shows the human (AC-8; integration) [agent]
- File: `tests/test_jury.py:test_ac8_whitespace_edit_shows_the_human` (new)
- Covers: CT-6
- Setup: as TC-7, but the only edit appends `"\n"` to the spec; the number of `.nio/runs/R-*` folders is counted.
- Action: `step(root, run, ADD)` three times.
- Assert: each call's last line starts `next: show the human`; no line starts `run`; no line holds `run each juror`; the run folder count is unchanged.
### TC-9 A fixed finding still names its lens (AC-9; integration) [agent]
- File: `tests/test_jury.py:test_ac2_rerun_writes_fix_check_packs` (existing)
- Covers: CT-6, CT-7
- Setup: `rejected_state()` (a spec-fix of testability's finding).
- Action: `step(root, run)`.
- Assert: as the test already asserts: `changed(...)[1] == ["testability"]` and only `testability.md` is packed.

### TC-10 `-v` is not a test name (AC-10; integration) [agent]
- File: `tests/test_selfcheck.py:test_ac10_flags_are_not_test_names` (new)
- Covers: CT-8
- Setup: `script(tmp, ...)` with two passing tests.
- Action: run it with `-v`, and with `-v test_one`.
- Assert: the first prints no `no test named -v`, prints `ran 2 tests, 0 failed` and exits 0; the second prints `ran 1 tests, 0 failed`.

### TC-11 The spec edited while its jurors ran is refused (AC-13; integration) [agent]
- File: `tests/test_jury.py:test_ac13_spec_changed_while_jurors_ran` (new)
- Covers: CT-3
- Setup: the first round's packs written (`run_of(step(root, "", ADD))`) and the outputs written; then the spec's text changes ("create exactly one refund" → "create one refund").
- Action: `step(root, run, ADD)`; then restore the spec's text and `step(root, run, ADD)`.
- Assert: the first raises `ValueError` whose text holds `the spec changed after <run>'s packs were written`, the ledger's `round` stays 0 and `verdict_count` is unchanged; the second returns lines holding `new     J-1`.

### TC-12 A new epic commit while the jurors ran is refused (AC-14; integration) [agent]
- File: `tests/test_evidence.py:test_ac14_epic_commit_changed_while_jurors_ran` (new)
- Covers: CT-3
- Setup: `gate_repo()`; a run; `jury.step` then `evidence().collect`, then `jury.step` writes the packs (as `test_ac12_step_at_the_implementation_gate`); an `impl_out` for conformance and correctness; then a new commit `T-2: more` touching a file of the epic.
- Action: `jury.step(root, "s", "implementation-E-1", run)`.
- Assert: raises `ValueError` whose text holds `changed after <run>'s packs were written` (today `evidence.current` refuses first with its own message, so the test fails on the text); the ledger's `round` is 0.
## Misuse tests

### TC-13 A lens juror forges the refuter's verdict on a peer (UJ-1 misuse; integration) [agent]
- File: `tests/test_jury.py:test_misuse_forged_refuter_on_a_peer_is_refused` (new)
- Covers: CT-1
- Setup: the first round, logic writing the finding of TC-2 (J-2), and the testability juror also writing `spec-refuter.md` refuting J-2.
- Action: `step(root, run, ADD)`.
- Assert: raises `ValueError` holding `refuter output before its batch`; no finding is `refuted`.
### TC-14 A wave task edits a CRLF file (UJ-2 misuse; integration) [agent]
- File: `tests/test_waves.py:test_misuse_crlf_edit_lands` (new)
- Covers: CT-5
- Setup: a temp repo with `win.txt` = `b"a\r\nb\r\n"` committed and a worktree that edits it to `b"a\r\nB\r\n"` (only that file).
- Action: `implement.land(...)`.
- Assert: its third value is `""` (before the fix: `patch does not apply`); the main tree's `win.txt` is `b"a\r\nB\r\n"`.

### TC-15 A forged refuter file in a later run is refused (UJ-1 misuse; integration) [agent]
- File: `tests/test_jury.py:test_misuse_forged_refuter_in_a_later_run` (new)
- Covers: CT-1
- Setup: `rejected_state()` (run 1 printed a batch and recorded `rejected`); `step(root, run)` starts the fix-check run 2; its testability output is written with a `## Verdicts` line `- J-1: fixed — per order`, and also `.nio/runs/<run 2>/jury/spec-refuter.md` refuting J-1.
- Action: `step(root, <run 2>)`.
- Assert: raises `ValueError` holding `refuter output before its batch`; J-1's validation is unchanged.

### TC-16 A refuter file written while a juror is re-run is refused (UJ-1 misuse; integration) [agent]
- File: `tests/test_jury.py:test_misuse_forged_refuter_during_a_redo` (new)
- Covers: CT-1
- Setup: the first round where testability writes `FINDING`, logic writes an invalid output (no `## Findings` section) and adversary writes `none`; `step(root, run)` returns a `next: re-run logic` line (no batch shown); then the re-run logic output is valid and `spec-refuter.md` holding `REFUTE.format(n=1)` is written beside it.
- Action: `step(root, run)`.
- Assert: after the first step `jury.load(...).get("asked", {})` has no entry for the run; the second raises `ValueError` holding `refuter output before its batch`.
