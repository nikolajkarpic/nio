---
slug: 2026-11-15-extensions
retired: [T-48, T-49, T-50, T-51, T-52, T-53, T-54]                      # task IDs removed from this file; never reused
---
<!-- Tasks template: the spec's work, one epic per user story (a full spec: one per entry of the plan's build order, in
its order; a bug-fix spec: one epic, E-1). A foundational epic, when there is shared setup, comes first. Task IDs run
across the whole spec and are never renumbered or reused. No status or checkbox here: a task's status lives in the CLI's
state. Work added after approval goes under the epic's `#### Fixes` heading, with the next free ID and a `From:` line.
`nio check tasks 2026-11-15-extensions` checks all of this and prints the estimate. Remove what doesn't apply; never write N/A. -->
# Tasks: Extensions

## E-1 Add, list and remove extensions (US-1)
- Tier: strong: ordinary logic with clear refusal order and tests, atomic replace is a known pattern
- Effort: low

### T-1 Manifest check: format, add-only rule, unknown after, cards, hooks, trigger, timeouts, names in use (CT-2)
- Files: `src/nio/extensions.py`, `tests/test_extensions.py`
- Serves: AC-5, AC-11, AC-20, AC-22, AC-28, AC-43
- Test: TC-5, TC-11, TC-20, TC-22, TC-28, TC-43
- Depends on: none
- Parallel: no
- Note: `check(folder, manifest, others, stages)` with every refusal in CT-2's order, including FR-39 names in use and the timeout rule (NFR-2); the shipped card names are read from `resources.files("nio")` directly.

### T-2 Add an extension from a folder, git URL, or name; record and hash it; print its commands, run none (CT-1)
- Files: `src/nio/extensions.py`, `src/nio/cli.py`, `tests/test_extensions.py`
- Serves: AC-1, AC-2, AC-4, AC-39
- Test: TC-1, TC-2, TC-4, TC-39
- Depends on: T-1
- Parallel: no
- Note: `add(root, source)`, `record.json` through temp file and `os.replace`, the hash, replace through `.<name>.new/` and `.old/`, `nio extensions add` in cli.py. Adding from `.nio/extensions/<name>` re-records only its hash. The replace-vs-effort-stage refusal comes in T-8.

### T-3 List extensions and read the active ones (CT-3, CT-5)
- Files: `src/nio/extensions.py`, `src/nio/cli.py`, `tests/test_extensions.py`
- Serves: AC-6
- Test: TC-6
- Depends on: T-2
- Parallel: no
- Note: `listing` and `active(root, guard=True)` (the guard itself is wired in T-9); `.`-folders left out; no `.nio/extensions` gives `[]` without reading anything else.

### T-4 Remove an extension; protect steps others follow (CT-4, part)
- Files: `src/nio/extensions.py`, `src/nio/cli.py`, `tests/test_extensions.py`
- Serves: AC-42
- Test: TC-42
- Depends on: T-3
- Parallel: no
- Note: `remove(root, name)`: record first then folder, half-done adds and removes count as added, `another added extension's step follows` refusal, and the same FR-39 check on a CT-1 replace. Refusing for an effort sitting at its step comes in T-8.

## E-2 The flow runs an extension step at its spot (US-2)
- Tier: max: rewires every reader of the core flow stage table, with state, skip records and guard=False edge cases
- Effort: med

### T-5 The per-project stage table and every reader through it (CT-6)
- Files: `src/nio/flow.py`, `src/nio/cli.py`, `src/nio/extensions.py`, `tests/test_flow.py`, `tests/test_extensions.py`
- Serves: AC-8, AC-9, AC-10, AC-18, AC-46, AC-48
- Test: TC-8, TC-9, TC-10, TC-18, TC-46, TC-48
- Depends on: T-3
- Parallel: no
- Note: `table(root, guard=True)`: with no active extension it returns `STAGES`, `GATES`, `SKILL`, `INPUTS`, `EXIT` themselves; else splices steps and `.jury` stages in; `where` passes an extension stage over until reached; `where`, `done`, `moves`, `guard`, `stops`, `approvals`, `jury_files`, `next_step`, `stage_arg` and cli.py:282 read it. Plan-jury note J-19: `table` and `where` take `guard` and pass it to `extensions.active`; under `guard=False` a step left unplaced is skipped instead of raising `ValueError` (with guard it still raises), so `remove` can read efforts' stages through a hand-broken extension.

### T-6 Trigger rules and the recorded skip; an AC's own level (CT-7, CT-17)
- Files: `src/nio/spec.py`, `src/nio/plan.py`, `src/nio/extensions.py`, `src/nio/flow.py`, `tests/test_spec.py`, `tests/test_extensions.py`
- Serves: AC-12, AC-13, AC-14
- Test: TC-12, TC-13, TC-14
- Depends on: T-5
- Parallel: no
- Note: `spec.level(block)` is the last `Level:` after `Observable:`; `plan.check`'s TC level check and `applies` read through it; `flow.moves` writes the `skip` lines for an extension step and its `.jury` stage.

### T-7 An extension step's check at `nio flow done` (CT-8)
- Files: `src/nio/flow.py`, `src/nio/implement.py`, `tests/test_implement.py`, `tests/test_extensions.py`
- Serves: AC-15, AC-16, AC-17
- Test: TC-15, TC-16, TC-17
- Depends on: T-5
- Parallel: no
- Note: `implement.run` gains `env` (`NIO_SLUG`, `NIO_STAGE`, `NIO_EXTENSION_DIR`); the guard runs the check with the step's timeout, else 300; a failure writes one `fail` line with `code`, `timed_out`, `tail` (last 50 lines) even without auto.

### T-8 Remove and replace refuse while an effort sits at the step (CT-4, CT-1)
- Files: `src/nio/extensions.py`, `src/nio/flow.py`, `tests/test_extensions.py`
- Serves: AC-7, AC-44
- Test: TC-7, TC-44
- Depends on: T-4, T-5
- Parallel: no
- Note: `remove` and a CT-1 replace read each effort's stage through `flow.where(..., guard=False)` (J-19), refuse for an effort not abandoned, write no effort file. Add a test, `test_remove_hand_broken_extension` (no plan TC of its own; cite TC-44's setup), that removes a hand-broken extension twice and succeeds: once with a hand-changed hash, once with a manifest whose step is unplaced; effort files stay byte-equal.

## E-3 Built-in steps and gates can't be removed or skipped (US-3)
- Tier: strong: hash-and-verify guard plus tolerant clearing, cases spelled out in the notes
- Effort: low

### T-9 The hand-edit guard (CT-18, CT-1)
- Files: `src/nio/extensions.py`, `src/nio/flow.py`, `src/nio/cli.py`, `tests/test_extensions.py`
- Serves: AC-21, AC-41
- Test: TC-21, TC-41
- Depends on: T-8
- Parallel: no
- Note: `verify(root, manifests)` run by `active` with guard: hash change, half added or removed, and CT-2 failure against the others raise `ValueError`; every `nio flow` command and `nio extensions list` print `error: <message>` exit 1 and move no effort; `nio extensions add .nio/extensions/<name>` re-records the hash.

### T-10 Half-done adds and removes and broken extensions can be cleared (CT-4, CT-18)
- Files: `src/nio/extensions.py`, `tests/test_extensions.py`
- Serves: AC-41
- Test: TC-49
- Depends on: T-9
- Parallel: no
- Note: `active(guard=False)` and `remove` tolerate a folder without entry, an entry without folder, a hand-changed hash and an unreadable `manifest.json` (J-19: the broken extension counts as having no stages), so `nio extensions remove <name>` clears each; a leftover `.<name>.new/` is ignored. The J-19 hand-broken-remove test from T-8 also runs here against the guard.

## E-4 An extension step can have its own jury gate (US-4)
- Tier: strong: extends existing gate lists following the built-in gate pattern
- Effort: low

### T-11 Jury gates for extension steps (CT-9)
- Files: `src/nio/jury.py`, `tests/test_jury.py`, `tests/test_extensions.py`
- Serves: AC-23
- Test: TC-23
- Depends on: T-10
- Parallel: no
- Note: `jury.gates(root)` returns `GATES`, `CORE` plus each extension gate; `gate_arg`, `plan`, `next`, `load` and the packs read it; `plan` at an extension gate checks only the output file and adds no risk-flag lens. Write TC-23 without its `passed.log` assertion: hook firing comes in T-14, which adds that assertion to TC-23.

### T-12 Extension gate stage in the flow: approval, rejection, auto (CT-6, CT-9)
- Files: `src/nio/flow.py`, `tests/test_extensions.py`
- Serves: AC-19, AC-24
- Test: TC-19, TC-24
- Depends on: T-11
- Parallel: no
- Note: `approvals` maps `nio: approve <ext>.<step>` to the gate stage; a rejection goes back to the step; under auto the driver's `done` approves it and the stop list reads its ledger as for built-in gates.

## E-5 Extension agent cards and hooks on NIO events (US-5)
- Tier: strong: hooks outside the lock and process timeouts are ordinary logic with clear tests
- Effort: med

### T-13 Extension agent cards in the card layers (CT-10)
- Files: `src/nio/agents.py`, `tests/test_agents.py`, `tests/test_extensions.py`
- Serves: AC-25
- Test: TC-25
- Depends on: T-10
- Parallel: no
- Note: `layers(root)` returns shipped, active extension `agents/` folders in name order, personal, team; `nio agents sync` renders them as `nio-<card>`.

### T-14 Hooks on NIO events (CT-11)
- Files: `src/nio/extensions.py`, `src/nio/flow.py`, `src/nio/implement.py`, `src/nio/jury.py`, `tests/test_extensions.py`
- Serves: AC-26, AC-27, AC-40
- Test: TC-26, TC-27, TC-40
- Depends on: T-13
- Parallel: no
- Note: `fire` and `extensions.after(root, slug, n, old_state)` called at the end of `flow.done`, `next_step`, `epic_done` and `implement.finish`, outside the lock; `hook` history lines through `flow.record`; `jury` fires `gate-rejected`; a failing hook never blocks; no extension runs and writes nothing. Add TC-23's `passed.log` assertion (left out in T-11) here.

### T-15 Timeouts stop checks and hooks and are recorded (NFR-2)
- Files: `src/nio/extensions.py`, `src/nio/flow.py`, `src/nio/implement.py`, `tests/test_extensions.py`
- Serves: AC-47
- Test: TC-47
- Depends on: T-14
- Parallel: no
- Note: Verifies the check timeout (T-7), the hook timeout (T-14) and the manifest timeout rule (T-1) together, with no leftover process; fix any gap found.

## E-6 The shipped e2e tester (US-6)
- Tier: strong: a manifest, a stdlib check script and a skill with clear contracts and tests
- Effort: med

### T-16 A task covering an e2e AC names its test (CT-12)
- Files: `src/nio/tasks.py`, `tests/test_tasks.py`, `tests/test_extensions.py`
- Serves: AC-32
- Test: TC-32
- Depends on: T-6
- Parallel: no
- Note: On a full spec a task whose `Serves:` holds an AC at `Level: e2e` (via `spec.level`) must cite a TC aimed at it in `Test:`.

### T-17 Playwright as a known runner (CT-13)
- Files: `src/nio/evidence.py`, `src/nio/implement.py`, `tests/test_evidence.py`, `tests/test_implement.py`, `tests/test_extensions.py`, `tests/test_extensions_e2e.py`
- Serves: AC-32, AC-33, AC-34, AC-36
- Test: TC-32, TC-33, TC-34, TC-36
- Depends on: T-16
- Parallel: no
- Note: `one_test(suite, file, name, root=None)`, `implement.RUNNERS` playwright entry, `epic_tests` passes `root` and builds one Playwright command joined with ` && `, `evidence.collect` runs each Playwright test alone at the pr gate. TC-34 lives in `tests/test_extensions_e2e.py` and runs only with `NIO_E2E=1` (Node, Chromium and T-20's `tests/fixtures/e2e-app`); the epic's closing run proves it with `NIO_E2E=1`, after T-20.

### T-18 The shipped e2e extension manifest and package data (CT-14)
- Files: `src/nio/shipped/e2e/manifest.json`, `pyproject.toml`, `tests/test_extensions.py`
- Serves: AC-3, AC-37
- Test: TC-3, TC-37
- Depends on: T-17
- Parallel: no
- Note: The manifest as CT-14 gives it; `pyproject.toml` ships `src/nio/shipped`; no file under `src/nio/` outside `src/nio/shipped/e2e/` names the extension.

### T-19 The e2e check script (CT-15)
- Files: `src/nio/shipped/e2e/check.py`, `tests/test_extensions.py`
- Serves: AC-30, AC-31, AC-45
- Test: TC-30, TC-31, TC-45
- Depends on: T-18
- Parallel: no
- Note: Standard library only; reads `Level:` as CT-17 does; failure kinds as CT-15 lists; trace and screenshot paths on success.

### T-20 The e2e skill and tester card (CT-16)
- Files: `src/nio/shipped/e2e/skills/e2e/SKILL.md`, `src/nio/shipped/e2e/agents/e2e-tester.md`, `tests/test_talk.py`, `tests/test_extensions_e2e.py`, `tests/fixtures/e2e-app`
- Serves: AC-29, AC-35, AC-38
- Test: TC-29, TC-35, TC-38
- Depends on: T-19
- Parallel: no
- Note: Plain markdown with the "Talking to the human" block word for word and no host-only tool name; the card is tier strong, effort med, tools read, edit, shell.

## E-7 PR fixes
- Tier: strong: fixes from the pr jury
- Effort: med

#### Fixes

### T-21 Fix: T-6: tests/test_spec.py isn't in the epic's diff
- From: J-1 (pr, round 1)
- Files: `tests/test_spec.py`
- Serves: AC-12, AC-13, AC-14
- Test: TC-12
- Depends on: none
- Parallel: no

### T-22 Fix: T-7: tests/test_implement.py isn't in the epic's diff
- From: J-2 (pr, round 1)
- Files: `tests/test_implement.py`
- Serves: AC-15, AC-16, AC-17
- Test: TC-15
- Depends on: none
- Parallel: no

### T-23 Fix: T-11: tests/test_jury.py isn't in the epic's diff
- From: J-3 (pr, round 1)
- Files: `tests/test_jury.py`
- Serves: AC-23
- Test: TC-23
- Depends on: none
- Parallel: no

### T-24 Fix: T-13: tests/test_agents.py isn't in the epic's diff
- From: J-4 (pr, round 1)
- Files: `tests/test_agents.py`
- Serves: AC-25
- Test: TC-25
- Depends on: none
- Parallel: no

### T-25 Fix: T-16: tests/test_tasks.py isn't in the epic's diff
- From: J-5 (pr, round 1)
- Files: `tests/test_tasks.py`
- Serves: AC-32
- Test: TC-32
- Depends on: none
- Parallel: no

### T-26 Fix: T-17: tests/test_implement.py isn't in the epic's diff
- From: J-6 (pr, round 1)
- Files: `tests/test_implement.py`
- Serves: AC-32, AC-33, AC-34, AC-36
- Test: TC-32
- Depends on: none
- Parallel: no

### T-27 Fix: T-18: pyproject.toml isn't in the epic's diff
- From: J-7 (pr, round 1)
- Files: `pyproject.toml`
- Serves: AC-3, AC-37
- Test: TC-3
- Depends on: none
- Parallel: no

### T-28 Fix: A hold set by a failing command fires no waiting-on-human hook
- From: J-9 (pr, round 1)
- Files: `src/nio/flow.py`
- Serves: FR-26, J-9
- Test: new: FR-26
- Depends on: none
- Parallel: no

### T-29 Fix: A step name is not validated, so a step can be unreachable or silently replaced
- From: J-11 (pr, round 1)
- Files: `src/nio/extensions.py`, `src/nio/flow.py`
- Serves: FR-5, J-11
- Test: new: FR-5
- Depends on: none
- Parallel: no

### T-30 Fix: Three e2e ACs have only tests that were skipped
- From: J-14 (pr, round 1)
- Files: `tests/test_extensions_e2e.py`
- Serves: AC-29, AC-34, AC-35
- Test: TC-29
- Depends on: none
- Parallel: no

### T-31 Fix: The no-extensions test fails in the evidence copy
- From: J-15 (pr, round 1)
- Files: `tests/test_extensions.py`
- Serves: AC-48
- Test: TC-48
- Depends on: none
- Parallel: no

### T-32 Fix: AC-8's test is recorded failed although its output line reads ok
- From: J-16 (pr, round 1)
- Files: `tests/test_extensions.py`
- Serves: AC-8
- Test: TC-8
- Depends on: none
- Parallel: no

### T-33 Fix: AC-5 has no passing evidence
- From: J-18 (pr, round 1)
- Files: `tests/test_extensions.py`
- Serves: AC-5
- Test: TC-5
- Depends on: none
- Parallel: no

### T-34 Fix: AC-8 has no passing evidence
- From: J-19 (pr, round 1)
- Files: `tests/test_extensions.py`
- Serves: AC-8
- Test: TC-8
- Depends on: none
- Parallel: no

### T-35 Fix: AC-11 has no passing evidence
- From: J-20 (pr, round 1)
- Files: `tests/test_extensions.py`
- Serves: AC-11
- Test: TC-11
- Depends on: none
- Parallel: no

### T-36 Fix: AC-20 has no passing evidence
- From: J-21 (pr, round 1)
- Files: `tests/test_extensions.py`
- Serves: AC-20
- Test: TC-20
- Depends on: none
- Parallel: no

### T-37 Fix: AC-22 has no passing evidence
- From: J-22 (pr, round 1)
- Files: `tests/test_extensions.py`
- Serves: AC-22
- Test: TC-22
- Depends on: none
- Parallel: no

### T-38 Fix: AC-28 has no passing evidence
- From: J-23 (pr, round 1)
- Files: `tests/test_extensions.py`
- Serves: AC-28
- Test: TC-28
- Depends on: none
- Parallel: no

### T-39 Fix: AC-29 has no passing evidence
- From: J-24 (pr, round 1)
- Files: `tests/test_extensions_e2e.py`
- Serves: AC-29
- Test: TC-29
- Depends on: none
- Parallel: no

### T-40 Fix: AC-34 has no passing evidence
- From: J-25 (pr, round 1)
- Files: `tests/test_extensions_e2e.py`
- Serves: AC-34
- Test: TC-34
- Depends on: none
- Parallel: no

### T-41 Fix: AC-35 has no passing evidence
- From: J-26 (pr, round 1)
- Files: `tests/test_extensions_e2e.py`
- Serves: AC-35
- Test: TC-35
- Depends on: none
- Parallel: no

### T-42 Fix: AC-38 has no passing evidence
- From: J-27 (pr, round 1)
- Files: `src/nio/shipped/e2e/skills/e2e/SKILL.md`, `src/nio/shipped/e2e/agents/e2e-tester.md`, `tests/test_talk.py`, `tests/test_extensions_e2e.py`
- Serves: AC-38
- Test: TC-38
- Depends on: none
- Parallel: no

### T-43 Fix: AC-46 has no passing evidence
- From: J-28 (pr, round 1)
- Files: `src/nio/flow.py`, `src/nio/cli.py`, `src/nio/extensions.py`, `tests/test_flow.py`, `tests/test_extensions.py`
- Serves: AC-46
- Test: TC-46
- Depends on: none
- Parallel: no

### T-44 Fix: AC-48 has no passing evidence
- From: J-29 (pr, round 1)
- Files: `tests/test_extensions.py`
- Serves: AC-48
- Test: TC-48
- Depends on: none
- Parallel: no

### T-45 Fix: The hook line records the effort's stage, not the event's stage
- From: J-30 (pr, round 1)
- Files: `src/nio/extensions.py`
- Serves: CT-11, FR-27, J-30
- Test: TC-26
- Depends on: none
- Parallel: no

### T-46 Fix: nio fails to import on Python 3.11
- From: J-32 (pr, round 1)
- Files: `src/nio/extensions.py`
- Serves: CT-3, FR-6, J-32
- Test: TC-6
- Depends on: none
- Parallel: no

### T-47 Fix: `nio extensions remove` deletes whatever path the name resolves to
- From: J-33 (pr, round 1)
- Files: `src/nio/extensions.py`
- Serves: CT-4, FR-7, J-33
- Test: TC-7
- Depends on: none
- Parallel: no

### T-55 Fix: AC-47's timeout test fails in the evidence run
- From: J-55 (pr, round 2)
- Files: `tests/test_extensions.py`
- Serves: AC-47
- Test: TC-47
- Depends on: none
- Parallel: no

### T-56 Fix: AC-47 has no passing evidence
- From: J-56 (pr, round 2)
- Files: `tests/test_extensions.py`
- Serves: AC-47
- Test: TC-47
- Depends on: none
- Parallel: no
