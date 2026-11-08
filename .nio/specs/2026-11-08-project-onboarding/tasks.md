---
slug: 2026-11-08-project-onboarding
retired: [T-8]
---
# Tasks: project onboarding

## E-1 Scan lists what the repo has (US-1)

### T-1 `nio onboard scan` lists candidate files with category and hash
- Files: `src/nio/onboard.py`, `src/nio/cli.py`, `tests/test_onboard.py`, `CLAUDE.md`
- Serves: AC-1, AC-2, AC-3, AC-4
- Test: TC-1, TC-2, TC-3, TC-4
- Depends on: none
- Parallel: no
- Tier: strong: new scanner with clear tests
- Effort: med
- Mode: split: new logic with clear tests

#### Fixes

### T-26 Fix: Outside a git repo the scan reports success with "nothing found"
- From: J-2 (implementation-E-1, round 1)
- Files: `src/nio/onboard.py`, `src/nio/cli.py`
- Serves: CT-2, J-2
- Test: TC-1
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

### T-27 Fix: Non-ASCII or quoted paths are dropped silently
- From: J-3 (implementation-E-1, round 1)
- Files: `src/nio/onboard.py`
- Serves: CT-1, J-3
- Test: TC-1
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

### T-28 Fix: Output order and the CLI shape don't match the contract, and the contract tests are missing
- From: J-5 (implementation-E-1, round 1)
- Files: `src/nio/onboard.py`, `tests/test_onboard.py`, `src/nio/cli.py`
- Serves: CT-1, CT-2, J-5
- Test: TC-1
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

### T-29 Fix: The category table is narrower than CT-1, and `docs/*.md` is in the wrong category
- From: J-7 (implementation-E-1, round 1)
- Files: `src/nio/onboard.py`
- Serves: CT-1, FR-1, J-7
- Test: TC-1
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

## E-2 Spec waits for onboarding (US-4)

### T-2 Onboarding progress, `start|confirm|pause|skip` and the six doc templates
- Files: `src/nio/onboard.py`, `src/nio/cli.py`, `tests/test_onboard.py`, `src/nio/templates/project/product.md`, `src/nio/templates/project/personas.md`, `src/nio/templates/project/stack.md`, `src/nio/templates/project/architecture.md`, `src/nio/templates/project/infra.md`, `src/nio/templates/project/principles.md`
- Serves: AC-30
- Test: TC-28, TC-56
- Depends on: T-1
- Parallel: no
- Tier: strong: ordinary state commands plus templates
- Effort: low
- Mode: split: logic with clear tests

### T-3 A full or epic spec refuses until onboarding is done or skipped
- Files: `src/nio/spec.py`, `tests/test_onboard.py`
- Serves: AC-15, AC-29
- Test: TC-25, TC-26, TC-53
- Depends on: T-2
- Parallel: no
- Tier: strong: one gate in spec.py
- Effort: low
- Mode: split: gate behaviour has clear tests

### T-4 Source records, staleness and onboarding lines in `nio status`
- Files: `src/nio/onboard.py`, `src/nio/cli.py`, `tests/test_onboard.py`
- Serves: AC-16
- Test: TC-27, TC-50
- Depends on: T-2, T-3
- Parallel: no
- Tier: strong: hash staleness logic with clear tests
- Effort: med
- Mode: split: logic with clear tests

### T-5 `@nio:install` ends by pointing at onboard
- Files: `skills/install/SKILL.md`, `tests/test_onboard_e2e.py`, `CLAUDE.md`
- Serves: AC-17
- Test: TC-29
- Depends on: T-4
- Parallel: no
- Tier: cheap: one closing line in a skill
- Effort: low
- Mode: direct: skill text, e2e test checks it after

#### Fixes

### T-30 Fix: T-2: src/nio/templates/project/product.md doesn't exist
- From: J-1 (implementation-E-2, round 5)
- Files: `CLAUDE.md`, `skills/install/SKILL.md`, `src/nio/cli.py`, `src/nio/onboard.py`, `src/nio/spec.py`, `tests/test_onboard.py`, `tests/test_onboard_e2e.py`, `tests/test_spec.py`
- Serves: AC-30
- Test: TC-28
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

### T-31 Fix: T-2: src/nio/templates/project/personas.md doesn't exist
- From: J-2 (implementation-E-2, round 5)
- Files: `CLAUDE.md`, `skills/install/SKILL.md`, `src/nio/cli.py`, `src/nio/onboard.py`, `src/nio/spec.py`, `tests/test_onboard.py`, `tests/test_onboard_e2e.py`, `tests/test_spec.py`
- Serves: AC-30
- Test: TC-28
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

### T-32 Fix: T-2: src/nio/templates/project/stack.md doesn't exist
- From: J-3 (implementation-E-2, round 5)
- Files: `CLAUDE.md`, `skills/install/SKILL.md`, `src/nio/cli.py`, `src/nio/onboard.py`, `src/nio/spec.py`, `tests/test_onboard.py`, `tests/test_onboard_e2e.py`, `tests/test_spec.py`
- Serves: AC-30
- Test: TC-28
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

### T-33 Fix: T-2: src/nio/templates/project/architecture.md doesn't exist
- From: J-4 (implementation-E-2, round 5)
- Files: `CLAUDE.md`, `skills/install/SKILL.md`, `src/nio/cli.py`, `src/nio/onboard.py`, `src/nio/spec.py`, `tests/test_onboard.py`, `tests/test_onboard_e2e.py`, `tests/test_spec.py`
- Serves: AC-30
- Test: TC-28
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

### T-34 Fix: T-2: src/nio/templates/project/infra.md doesn't exist
- From: J-5 (implementation-E-2, round 5)
- Files: `CLAUDE.md`, `skills/install/SKILL.md`, `src/nio/cli.py`, `src/nio/onboard.py`, `src/nio/spec.py`, `tests/test_onboard.py`, `tests/test_onboard_e2e.py`, `tests/test_spec.py`
- Serves: AC-30
- Test: TC-28
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

### T-35 Fix: T-2: src/nio/templates/project/principles.md doesn't exist
- From: J-6 (implementation-E-2, round 5)
- Files: `CLAUDE.md`, `skills/install/SKILL.md`, `src/nio/cli.py`, `src/nio/onboard.py`, `src/nio/spec.py`, `tests/test_onboard.py`, `tests/test_onboard_e2e.py`, `tests/test_spec.py`
- Serves: AC-30
- Test: TC-28
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

### T-36 Fix: `start --empty` overwrites docs the dev already wrote
- From: J-7 (implementation-E-2, round 5)
- Files: `src/nio/onboard.py`
- Serves: CT-4, J-7
- Test: TC-6
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

### T-37 Fix: `confirm` accepts any doc with no file and never reaches `done` for `--empty`
- From: J-10 (implementation-E-2, round 5)
- Files: `src/nio/onboard.py`
- Serves: CT-4, J-10
- Test: TC-6
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

### T-38 Fix: The progress file is written non-atomically, and one bad file crashes `nio status`
- From: J-11 (implementation-E-2, round 5)
- Files: `src/nio/onboard.py`, `src/nio/cli.py`
- Serves: CT-3, CT-8, J-11
- Test: TC-6
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

### T-39 Fix: AC-17 has no run result: its e2e test only runs under NIO_E2E
- From: J-12 (implementation-E-2, round 5)
- Files: `tests/test_onboard_e2e.py`
- Serves: AC-17
- Test: TC-17
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

### T-40 Fix: Confirming the last doc never reaches done
- From: J-17 (implementation-E-2, round 5)
- Files: `src/nio/onboard.py`
- Serves: CT-4, CT-5, J-17
- Test: TC-6
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

### T-41 Fix: Pause, skip, start and confirm do not follow the state table
- From: J-19 (implementation-E-2, round 5)
- Files: `src/nio/onboard.py`
- Serves: CT-4, AC-15
- Test: TC-6
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

### T-42 Fix: Confirm walks all six docs, not the expected ones, and the progress save is not atomic
- From: J-20 (implementation-E-2, round 5)
- Files: `src/nio/onboard.py`
- Serves: CT-3, CT-4, J-20
- Test: TC-6
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

### T-43 Fix: Last confirm prints "done" but the state stays "in progress", so full and epic specs stay blocked
- From: J-22 (implementation-E-2, round 5)
- Files: `src/nio/onboard.py`
- Serves: CT-4, CT-5, AC-15
- Test: TC-6
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

### T-44 Fix: `start --empty` overwrites confirmed docs, and writes three docs more than the spec asks
- From: J-23 (implementation-E-2, round 5)
- Files: `src/nio/onboard.py`
- Serves: CT-4, AC-30
- Test: TC-6
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

### T-45 Fix: The CLI uses the current directory as the project root, so a subdirectory run records state in the wrong place
- From: J-24 (implementation-E-2, round 5)
- Files: `src/nio/cli.py`
- Serves: CT-4, CT-5, AC-16
- Test: TC-6
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

### T-46 Fix: Pause is a dead end, and start and skip are accepted on a done onboarding
- From: J-25 (implementation-E-2, round 5)
- Files: `src/nio/onboard.py`
- Serves: CT-4, J-25
- Test: TC-6
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

### T-47 Fix: Start, confirm, pause and skip write under the current directory, not the repo root
- From: J-28 (implementation-E-2, round 5)
- Files: `src/nio/cli.py`
- Serves: AC-16, AC-30, CT-4
- Test: TC-27
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

### T-48 Fix: `done` is not protected, and `ignore` cells are not honoured
- From: J-29 (implementation-E-2, round 5)
- Files: `src/nio/onboard.py`
- Serves: CT-4, J-29
- Test: TC-6
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

### T-49 Fix: `start --empty` overwrites edited docs and writes six docs, not three
- From: J-33 (implementation-E-2, round 5)
- Files: `src/nio/onboard.py`
- Serves: CT-4, FR-12, J-33
- Test: TC-6
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

### T-50 Fix: Code's section headings and constant name differ from the spec's `HEADINGS`
- From: J-34 (implementation-E-2, round 5)
- Files: `src/nio/onboard.py`
- Serves: CT-12, CT-3, J-34
- Test: TC-6
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

### T-51 Fix: Test asserts exit 1 for confirm while paused, which the spec says exits 0
- From: J-35 (implementation-E-2, round 5)
- Files: `tests/test_onboard.py`
- Serves: CT-4, J-35
- Test: TC-6
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

## E-3 Stages read the project docs (US-5)

### T-6 `docs_for` and `nio pack --reader/--slug`: the project docs a reader gets, with state, stale, missing and size lines
- Files: `src/nio/onboard.py`, `src/nio/pack.py`, `src/nio/cli.py`, `tests/test_onboard.py`
- Serves: AC-19, AC-20, AC-47
- Test: TC-32, TC-33, TC-34
- Depends on: T-4
- Parallel: no
- Tier: strong: reader-to-docs selection with several line kinds
- Effort: med
- Mode: split: logic with clear tests

### T-7 The worker pack and the jury's scope and architecture-fit packs carry the docs and ground their quotes
- Files: `src/nio/implement.py`, `src/nio/jury.py`, `src/nio/onboard.py`, `tests/test_onboard.py`
- Serves: AC-18
- Test: TC-31, TC-55
- Depends on: T-6
- Parallel: no
- Tier: strong: wiring docs_for into existing packs plus quote grounding
- Effort: low
- Mode: split: pack output has clear tests

### T-9 The spec skill and drafter use personas and apps
- Files: `skills/spec/SKILL.md`, `src/nio/agents/spec-drafter.md`, `tests/test_onboard_e2e.py`
- Serves: AC-32
- Test: TC-30
- Depends on: T-7
- Parallel: no
- Tier: cheap: prose edits to a skill and a card
- Effort: low
- Mode: direct: skill/card text, e2e test checks it after

## E-4 Onboard an existing repo through a grill (US-2)

### T-10 A spec names its apps and `nio check spec` enforces it
- Files: `src/nio/spec.py`, `src/nio/templates/spec.md`, `src/nio/templates/spec-epic.md`, `src/nio/templates/spec-bugfix.md`, `tests/test_onboard.py`
- Serves: AC-45
- Test: TC-46
- Depends on: T-7
- Parallel: no
- Tier: strong: new spec check plus three templates
- Effort: low
- Mode: split: check has a clear test

### T-11 Multi-app packs hold the right apps' docs, labelled
- Files: `src/nio/onboard.py`, `tests/test_onboard.py`
- Serves: AC-34, AC-35, AC-46
- Test: TC-15, TC-16, TC-47
- Depends on: T-7, T-10
- Parallel: no
- Tier: strong: multi-app selection and labelling logic
- Effort: med
- Mode: split: logic with clear tests

### T-12 `nio onboard backup` keeps a restorable copy
- Files: `src/nio/onboard.py`, `src/nio/cli.py`, `tests/test_onboard.py`
- Serves: AC-37
- Test: TC-52
- Depends on: T-2
- Parallel: no
- Tier: strong: copy and restore with a clear test
- Effort: low
- Mode: split: clear test

### T-13 Secret and symlink scan cases
- Files: `src/nio/onboard.py`, `tests/test_onboard.py`
- Serves: AC-28, AC-38, AC-48
- Test: TC-13, TC-19, TC-48
- Depends on: T-1
- Parallel: no
- Tier: max: secret leaks and symlink escapes are security
- Effort: med
- Mode: split: tests lead the edge cases

### T-14 Project docs hold their headings and source hashes
- Files: `src/nio/onboard.py`, `tests/test_onboard.py`
- Serves: AC-6, AC-8
- Test: TC-6, TC-8
- Depends on: T-4
- Parallel: no
- Tier: strong: heading and hash checks with clear tests
- Effort: low
- Mode: split: clear tests

### T-15 `@nio:onboard` skill
- Files: `skills/onboard/SKILL.md`, `tests/test_onboard.py`, `tests/test_onboard_e2e.py`
- Serves: AC-5, AC-41
- Test: TC-5, TC-22
- Depends on: T-9, T-12, T-14
- Parallel: no
- Tier: strong: a multi-step skill with a grill flow
- Effort: med
- Mode: single: skill text and its checks written together

### T-16 Onboard e2e: unknown fields, resume and finished repo
- Files: `skills/onboard/SKILL.md`, `tests/test_onboard_e2e.py`
- Serves: AC-7, AC-10, AC-11
- Test: TC-7, TC-10, TC-11
- Depends on: T-15
- Parallel: no
- Tier: strong: skill wording tuned against an e2e test
- Effort: low
- Mode: single: e2e test and skill fix together

### T-17 Onboard e2e: secrets and planted instructions
- Files: `skills/onboard/SKILL.md`, `tests/test_onboard_e2e.py`
- Serves: AC-12, AC-39, AC-40
- Test: TC-12, TC-20, TC-21
- Depends on: T-15
- Parallel: no
- Tier: max: secrets and prompt-injection handling in a skill
- Effort: med
- Mode: single: e2e test and skill fix together

### T-18 Onboard e2e: patches, agent files and several apps
- Files: `skills/onboard/SKILL.md`, `tests/test_onboard_e2e.py`
- Serves: AC-9, AC-33, AC-36, AC-37, AC-43
- Test: TC-9, TC-14, TC-17, TC-18, TC-42
- Depends on: T-15
- Parallel: no
- Tier: strong: five e2e cases, skill wording
- Effort: low
- Mode: single: e2e test and skill fix together

## E-5 Onboard an empty repo (US-3)

### T-19 The first full spec's grill fills blank tech fields
- Files: `skills/grill/SKILL.md`, `tests/test_onboard_e2e.py`
- Serves: AC-14
- Test: TC-24
- Depends on: T-15
- Parallel: no
- Tier: strong: skill change checked by one e2e
- Effort: low
- Mode: single: e2e test and skill fix together

### T-20 An empty repo grills three docs and is done
- Files: `skills/onboard/SKILL.md`, `tests/test_onboard_e2e.py`
- Serves: AC-13
- Test: TC-23
- Depends on: T-15
- Parallel: no
- Tier: strong: skill branch checked by one e2e
- Effort: low
- Mode: single: e2e test and skill fix together

## E-6 Flag stale docs and reconcile them (US-6)

### T-21 Changed, deleted and new sources: `changed`, `to_reconcile`, `reconciled`, `close_lines`
- Files: `src/nio/onboard.py`, `src/nio/cli.py`, `tests/test_onboard.py`
- Serves: AC-25
- Test: TC-54
- Depends on: T-14
- Parallel: no
- Tier: strong: changed/deleted/new diffing with four functions
- Effort: med
- Mode: split: logic with clear test

### T-22 Stale flags in status and packs
- Files: `tests/test_onboard.py`
- Serves: AC-21, AC-22, AC-24, AC-31
- Test: TC-35, TC-36, TC-37, TC-39, TC-49, TC-51
- Depends on: T-21
- Parallel: no
- Tier: cheap: tests only over existing behaviour
- Effort: low
- Mode: single: tests only, may pass already

### T-23 `@nio:reconcile-onboarding` skill
- Files: `skills/reconcile-onboarding/SKILL.md`, `tests/test_onboard.py`
- Serves: AC-41
- Test: TC-22
- Depends on: T-21, T-15
- Parallel: no
- Tier: strong: new skill with a form check
- Effort: low
- Mode: single: skill and its check together

### T-24 Reconcile e2e: changed files, nothing to do, declines and deletions
- Files: `skills/reconcile-onboarding/SKILL.md`, `tests/test_onboard_e2e.py`
- Serves: AC-23, AC-42, AC-44
- Test: TC-38, TC-40, TC-41, TC-43
- Depends on: T-23
- Parallel: no
- Tier: strong: four e2e cases, skill wording
- Effort: low
- Mode: single: e2e test and skill fix together

## E-7 An effort's changes reach the project docs (US-7)

### T-25 The effort's close names changed sources
- Files: `src/nio/flow.py`, `tests/test_onboard.py`
- Serves: AC-26, AC-27
- Test: TC-44, TC-45
- Depends on: T-21
- Parallel: no
- Tier: strong: touches flow close, clear tests
- Effort: low
- Mode: split: clear tests
