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

### T-30 Fix: the six project-doc templates under `src/nio/templates/project/` don't exist, and headings differ from `HEADINGS` (J-1 to J-6, J-34; also T-31 to T-35, T-50)
- From: J-1 (implementation-E-2, round 5)
- Files: `CLAUDE.md`, `skills/install/SKILL.md`, `src/nio/cli.py`, `src/nio/onboard.py`, `src/nio/spec.py`, `tests/test_onboard.py`, `tests/test_onboard_e2e.py`, `tests/test_spec.py`
- Serves: AC-30
- Test: new: a test that fails while any of the six `src/nio/templates/project/*.md` is missing or its headings differ from CT-12's `HEADINGS`
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

### T-36 Fix: `start --empty` overwrites existing docs and writes all six, not only stack, architecture and infra when missing (J-7, J-23, J-33; also T-44, T-49)
- From: J-7 (implementation-E-2, round 5)
- Files: `src/nio/onboard.py`
- Serves: CT-4, J-7
- Test: new: a test that `start --empty` writes only missing stack.md, architecture.md and infra.md and leaves an existing doc byte-for-byte unchanged (CT-4)
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

### T-37 Fix: `confirm` walks all six docs, never checks the doc file or headings, and the last confirm never sets `done` or saves `seen` (J-10, J-17, J-20, J-22; also T-40, T-42, T-43)
- From: J-10 (implementation-E-2, round 5)
- Files: `src/nio/onboard.py`
- Serves: CT-4, J-10
- Test: new: a test that confirm refuses a missing or heading-less doc, walks only the expected docs, and the last confirm leaves state `done` with `seen` saved so a full spec starts (CT-4)
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

### T-38 Fix: the progress file is written non-atomically, and a torn file crashes `nio status` (J-11)
- From: J-11 (implementation-E-2, round 5)
- Files: `src/nio/onboard.py`, `src/nio/cli.py`
- Serves: CT-3, CT-8, J-11
- Test: new: a test that a torn onboarding.json makes every reader stop naming the file instead of crashing, and that saves go through a temp file and rename (CT-3)
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

### T-41 Fix: the state table's ignore and reject cells aren't followed (paused can't resume; start or skip work on done), and a test expects exit 1 where the table says 0 (J-19, J-25, J-29, J-35; also T-46, T-48, T-51)
- From: J-19 (implementation-E-2, round 5)
- Files: `src/nio/onboard.py`
- Serves: CT-4, AC-15
- Test: new: a table-driven test over every state-table cell: ignore exits 0 with `ignored:`, reject exits 1, paused resumes (CT-4)
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

### T-45 Fix: the onboard commands use the current directory instead of the repo root (J-24, J-28; also T-47)
- From: J-24 (implementation-E-2, round 5)
- Files: `src/nio/cli.py`
- Serves: CT-4, CT-5, AC-16
- Test: new: a test that running the onboard commands from a subdirectory reads and writes `.nio/project/` at the repo root (CT-4)
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

### T-52 Fix: add next_doc(p) per CT-3/CT-4; start and confirm print the next doc from it
- From: J-20 (implementation-E-2, round 6)
- Files: `src/nio/onboard.py`, `tests/test_onboard.py`
- Serves: CT-3, CT-4, J-20
- Test: new: next_doc(p) returns the first expected doc not confirmed, and None when all are confirmed (CT-3)
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: low
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

#### Fixes

### T-53 Fix: A damaged onboarding.json stops every pack, but the docs must never block the stage
- From: J-1 (implementation-E-3, round 2)
- Files: `src/nio/onboard.py`, `src/nio/pack.py`, `src/nio/implement.py`, `tests/test_onboard.py`
- Serves: CT-9, CT-10, CT-19, J-1
- Test: new: with a corrupt `.nio/project/onboarding.json`, `docs_for` (and so `nio pack --reader worker` and the worker pack) does not raise; it emits a line `onboarding: unreadable: fix .nio/project/onboarding.json` and no docs (CT-9)
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

### T-54 Fix: A symlinked project doc is read and sent to the model
- From: J-2 (implementation-E-3, round 2)
- Files: `src/nio/onboard.py`, `tests/test_onboard.py`
- Serves: CT-9, CT-22, CT-1, J-2
- Test: new: a `.nio/project/stack.md` that is a symlink (to a file inside or outside the repo) is not read into the pack; `docs_for` names it on a `missing:` line instead (CT-9, CT-1)
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

### T-55 Fix: The apps line is read from anywhere in the spec, in one form only, and a wrong read drops docs silently
- From: J-3 (implementation-E-3, round 2)
- Files: `src/nio/onboard.py`, `tests/test_onboard.py`
- Serves: CT-9, CT-16, J-3
- Test: new: `_pairs` reads `apps` only from the spec's front matter, accepts both `apps: [a, b]` and the block list form, ignores an `apps:` line in the body, and an app named but not onboarded gets a `not onboarded: <app>` line (CT-9, CT-16)
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

### T-57 Fix: Quotes from project docs never ground
- From: J-8 (implementation-E-3, round 2)
- Files: `src/nio/jury.py`, `tests/test_onboard.py`
- Serves: CT-22, J-8
- Test: new: at the plan gate a finding by the architecture-fit lens that quotes `.nio/project/principles.md` is grounded (`grounding`/`grounded` given the lens's sources), while the same quote from a lens with no docs is not (CT-22)
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

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
