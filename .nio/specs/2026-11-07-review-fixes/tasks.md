---
slug: 2026-11-07-review-fixes
retired: []                      # task IDs removed from this file; never reused
---
<!-- Tasks template: the spec's work, one epic per user story (a full spec: one per entry of the plan's build order, in
its order; a bug-fix spec: one epic, E-1). A foundational epic, when there is shared setup, comes first. Task IDs run
across the whole spec and are never renumbered or reused. No status or checkbox here: a task's status lives in the CLI's
state. Work added after approval goes under the epic's `#### Fixes` heading, with the next free ID and a `From:` line.
`nio check tasks 2026-11-07-review-fixes` checks all of this and prints the estimate. Remove what doesn't apply; never write N/A. -->
# Tasks: Fix the review's findings in the speed-up PRs

## E-1 Fix the review's findings, all four stories in one bug-fix epic (US-1)

### T-1 Record asked batches, apply refuter verdicts only to them, refuse moved judged versions
- Files: `src/nio/jury.py`, `tests/test_jury.py`, `tests/test_evidence.py`
- Serves: AC-1, AC-2, AC-3, AC-13, AC-14
- Test: TC-1, TC-2, TC-3, TC-11, TC-12, TC-13, TC-15, TC-16
- Depends on: none
- Parallel: no
- Tier: strong: ledger state with clear integration tests, but the forgery cases need care
- Effort: high
- Mode: split: eight tests lead a cross-cutting change in the step flow

### T-2 Save land and shelve patches as raw git bytes
- Files: `src/nio/records.py`, `src/nio/implement.py`, `tests/test_waves.py`
- Serves: AC-4, AC-5, AC-6
- Test: TC-4, TC-5, TC-6, TC-14
- Depends on: none
- Parallel: yes
- Tier: strong: ordinary subprocess byte handling with exact byte-level tests
- Effort: low
- Mode: split: tests state the exact bytes, so a red test comes first

### T-3 Re-run voters on a changed rejected text gate; show the human when no lens remains
- Files: `src/nio/jury.py`, `tests/test_jury.py`
- Serves: AC-7, AC-8, AC-9
- Test: TC-7, TC-8, TC-9
- Depends on: T-1
- Parallel: no
- Tier: strong: round and disposition logic in the jury with clear tests
- Effort: med
- Mode: split: three tests define the rerun and show-human branches

### T-4 Self-check ignores flag words
- Files: `tests/selfcheck.py`, `tests/test_selfcheck.py`
- Serves: AC-10
- Test: TC-10, then `uv run python tests/test_pack.py -v` exits 0 with more than 0 tests run
- Depends on: none
- Parallel: yes
- Tier: cheap: skip argv words starting with "-" in a small script, one test
- Effort: low
- Mode: single: one tiny change and its one test

#### Fixes

### T-5 Fix: A failed `git diff` in `shelve` writes an empty patch, then the work is restored away
- From: J-1 (implementation-E-1, round 1)
- Files: `src/nio/implement.py`
- Serves: CT-5, J-1
- Test: TC-4
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

### T-6 Fix: Implementation rerun with no lens to re-run opens a run instead of showing the human
- From: J-6 (implementation-E-1, round 1)
- Files: `src/nio/jury.py`
- Serves: FR-5, CT-6, J-6
- Test: TC-8
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding
