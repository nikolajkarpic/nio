---
slug: 2026-10-27-implementation-jury
retired: [T-4, T-27, T-28, T-29]                      # task IDs removed from this file; never reused
---
# Tasks: Implementation jury

## E-1 Shared pieces the gate builds on (Foundation)

### T-1 Run commands in a throwaway copy with a time limit and cut long output, and define the results file
- Files: `src/nio/evidence.py`, `tests/test_evidence.py`
- Serves: AC-52, AC-53, AC-55
- Test: direct unit checks calling `in_copy` (a never-ending command stopped at the limit, a deleting command leaving the working tree unchanged, a 1 MB output cut to its first and last 100 KB) and the `RESULTS` reader and writer; TC-40, TC-41 and TC-43 proved later by T-5
- Depends on: none
- Parallel: no
- Tier: max: runs arbitrary commands; a leak out of the copy deletes the real tree
- Effort: high
- Mode: split: clear unit checks lead the code

### T-2 Add the secrets risk flag and bring in the security lens for it at the spec gate
- Files: `src/nio/spec.py`, `tests/test_spec.py`
- Serves: AC-60, AC-61
- Test: direct unit checks in `tests/test_spec.py` calling `spec.check` on a spec with `risk: [secrets]`; TC-48 and TC-49 proved later by T-21
- Depends on: none
- Parallel: yes
- Tier: strong: ordinary logic extending an existing check
- Effort: med
- Mode: split: clear tests lead the code

## E-2 The gate runs only on an implemented epic (US-1)

### T-3 Accept `implementation-E-n` as a gate name and refuse anything but a finished epic
- Files: `src/nio/jury.py`, `src/nio/cli.py`, `tests/test_evidence.py`
- Serves: AC-2, AC-3
- Test: TC-2, TC-3
- Depends on: T-1
- Parallel: no
- Tier: strong: gate-name parsing and a state check with clear tests
- Effort: med
- Mode: split: clear tests lead the code

#### Fixes

### T-34 Keep an unreadable runner's passing suite from blocking every acceptance test
- From: C-261030-gk3z
- Files: `src/nio/evidence.py`, `tests/test_evidence.py`
- Serves: AC-4, AC-6
- Test: TC-4, TC-6, plus a direct check that a suite exiting 0 on an unreadable runner gives no blocker for a matched AC and one exiting non-zero does
- Depends on: T-3
- Parallel: no
- Tier: strong: a small rule in the evidence join
- Effort: low
- Mode: split: a clear test leads the code

### T-35 Fix: test tampering: test_ac29_epic_skipped in tests/test_implement.py is deleted
- From: J-1 (implementation-E-2, round 1)
- Files: `tests/test_implement.py`
- Serves: J-1
- Test: new: J-1
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

### T-36 Fix: Core lenses are not enforced; an approval can skip conformance and correctness
- From: J-2 (implementation-E-2, round 1)
- Files: `src/nio/jury.py collect / compose (`expect`)`
- Serves: FR-14, FR-38, CT-8, J-2
- Test: TC-1
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

### T-37 Fix: `--pick` is accepted when the plan is not over the cap, so one command silently drops risk lenses and the record blames the human
- From: J-3 (implementation-E-2, round 1)
- Files: `src/nio/jury.py plan (`pick`)`, `hooks.ALLOW`, `verdict`
- Serves: FR-16, CT-8, CT-16, J-3
- Test: TC-1
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

### T-38 Fix: An `auto` journey whose steps don't parse is recorded as passed without running anything
- From: J-4 (implementation-E-2, round 1)
- Files: `src/nio/evidence.py journeys / collect`
- Serves: FR-12, CT-3, CT-7, J-4
- Test: TC-4
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

### T-39 Fix: With a test runner the CLI can't address, every scripted attack becomes "not configured" and every test "unknown", and both count as evidence
- From: J-5 (implementation-E-2, round 1)
- Files: `src/nio/evidence.py collect`, `one_test`, `join`
- Serves: FR-12, FR-3, FR-5, CT-3, J-5
- Test: TC-4
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

### T-40 Fix: `results.json` is never tied to the gate's epic or to the commit being judged
- From: J-6 (implementation-E-2, round 1)
- Files: `src/nio/jury.py collect (join)`, `src/nio/evidence.py pack`, `load`
- Serves: FR-6, FR-17, CT-7, CT-9, CT-21, J-6
- Test: TC-4
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

### T-41 Fix: Tampering dispose rule in CT-20 doesn't match the code's fix-task exception
- From: J-7 (implementation-E-2, round 1)
- Files: `src/nio/jury.py dispose (the tampering check before the PLAN_ONLY check)`
- Serves: CT-20, FR-10, J-7
- Test: TC-7
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

### T-42 Fix: The consistency lens's decision check has no decisions in its pack
- From: J-8 (implementation-E-2, round 1)
- Files: `src/nio/evidence.py pack (the consistency lens's pack at implementation)`
- Serves: CT-9, FR-17, J-8
- Test: TC-25
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

### T-43 Fix: A conformance fix-check output with no `## Matches` section re-blocks every AC
- From: J-10 (implementation-E-2, round 1)
- Files: `src/nio/jury.py (collect`, `the call to evidence.join) and src/nio/evidence.py:join`
- Serves: AC-6, FR-5, CT-21
- Test: TC-6
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

### T-44 Fix: An AC proved by a misuse test is judged "didn't run" and gets a blocker
- From: J-11 (implementation-E-2, round 1)
- Files: `src/nio/evidence.py:collect and src/nio/evidence.py:join`
- Serves: FR-5, CT-21, J-11
- Test: TC-4
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

### T-45 Fix: A fix task's `Files:` is built from the juror's free-text `where`, which can create a phantom the next evidence run reports
- From: J-12 (implementation-E-2, round 1)
- Files: `src/nio/tasks.py:append_fix and src/nio/evidence.py:phantoms`
- Serves: FR-26, FR-8, CT-14, J-12
- Test: TC-38
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

### T-46 Fix the ten findings of the branch code review
- From: C-261031-rvfx
- Files: `src/nio/cli.py`, `src/nio/jury.py`, `src/nio/evidence.py`, `src/nio/agents/conformance.md`, `src/nio/agents/correctness.md`, `tests/test_evidence.py`
- Serves: AC-4, AC-6
- Test: TC-4, TC-6, plus direct checks of each finding
- Depends on: none
- Parallel: no
- Tier: strong: small rules across the gate's CLI
- Effort: med
- Mode: single: a fix from a code review

## E-3 The CLI collects observed evidence before any lens runs (US-2)

### T-5 Run the tests, lint, type check, scripted attacks and journey runs and write the results with `nio jury evidence`
- Files: `src/nio/evidence.py`, `src/nio/cli.py`, `tests/test_evidence.py`
- Serves: AC-14, AC-15, AC-52, AC-53, AC-55
- Test: TC-15, TC-16, TC-40, TC-41, TC-43
- Depends on: T-1, T-3
- Parallel: no
- Tier: strong: orchestrates T-1's sandbox over several tools
- Effort: high
- Mode: split: clear tests lead the code

### T-6 Flag phantom completion: a missing file, a file outside the diff, an undefined or unreferenced symbol
- Files: `src/nio/evidence.py`, `tests/test_evidence.py`
- Serves: AC-7, AC-8, AC-9
- Test: TC-7, TC-8, TC-9
- Depends on: T-1
- Parallel: no
- Tier: strong: diff and symbol analysis with clear tests
- Effort: high
- Mode: split: clear tests lead the code

### T-7 Flag test tampering: a deleted test and a newly skipped test
- Files: `src/nio/evidence.py`, `tests/test_evidence.py`
- Serves: AC-11, AC-12
- Test: TC-11, TC-12
- Depends on: T-1
- Parallel: no
- Tier: strong: diff scanning with clear tests
- Effort: med
- Mode: split: clear tests lead the code

### T-8 Raise the hints every pack carries: stubs, uncertain references, tests with no assertion, changed assertions
- Files: `src/nio/evidence.py`, `tests/test_evidence.py`
- Serves: AC-10, AC-16
- Test: direct unit checks calling `hints` on a diff with an empty function, a dynamically called symbol, a test with no assertion and a changed assertion line; TC-10 and TC-17 proved later with the pack by T-14
- Depends on: T-1
- Parallel: no
- Tier: strong: heuristic code analysis with clear tests
- Effort: med
- Mode: split: clear tests lead the code

### T-9 Record the CLI's own findings in the ledger as confirmed, with no refuter, and let only the human accept tampering
- Files: `src/nio/jury.py`, `src/nio/evidence.py`, `tests/test_jury.py`, `tests/test_evidence.py`
- Serves: AC-54
- Test: TC-42, TC-62, TC-63
- Depends on: T-5, T-6, T-7, T-8
- Parallel: no
- Tier: max: ledger trust rule; agents must not self-accept tampering
- Effort: high
- Mode: split: clear tests lead the code

## E-4 Lens cards know the implementation gate (US-7)

### T-10 Ship the conformance and correctness cards and add the implementation section to the risk and rollback card
- Files: `src/nio/agents/conformance.md`, `src/nio/agents/correctness.md`, `src/nio/agents/risk-rollback.md`, `tests/test_evidence.py`
- Serves: AC-41
- Test: TC-60
- Depends on: T-9
- Parallel: no
- Tier: strong: card prose that must be precise, checked by a simple test
- Effort: low
- Mode: single: one worker writes cards and their presence check together

### T-11 Add the implementation section to the security, adversary and consistency cards
- Files: `src/nio/agents/security.md`, `src/nio/agents/adversary.md`, `src/nio/agents/consistency.md`, `tests/test_evidence.py`
- Serves: AC-42
- Test: TC-61
- Depends on: T-10
- Parallel: no
- Tier: cheap: follows the pattern set by T-10
- Effort: low
- Mode: single: one worker writes cards and their presence check together

## E-5 The lens plan has two core lenses, triggered lenses and a cap (US-3)

### T-12 Plan the lenses for an epic: conformance and correctness always, the rest from the trigger table
- Files: `src/nio/jury.py`, `src/nio/cli.py`, `tests/test_evidence.py`
- Serves: AC-1, AC-18, AC-19, AC-20, AC-21
- Test: TC-1, TC-19, TC-20, TC-21, TC-22, TC-67
- Depends on: T-3, T-11
- Parallel: no
- Tier: strong: table-driven planning with clear tests
- Effort: med
- Mode: split: clear tests lead the code

### T-13 Show the runs and their tiers when the plan is over the cap, and record the human's pick and the dropped lenses
- Files: `src/nio/jury.py`, `src/nio/cli.py`, `tests/test_evidence.py`
- Serves: AC-22, AC-23
- Test: direct unit checks calling `plan` over the cap and with `--pick` (a pick that drops a core lens refused); TC-23 proved later by T-20 and TC-24 by T-25
- Depends on: T-12
- Parallel: no
- Tier: strong: ordinary logic with a refusal rule
- Effort: med
- Mode: split: clear tests lead the code

## E-6 Jurors read a focused pack and never run code (US-4)

### T-14 Build a lens's pack from the diff, the items it touches, the results and the hints, and a fix check on a re-review
- Files: `src/nio/evidence.py`, `src/nio/jury.py`, `src/nio/cli.py`, `tests/test_evidence.py`
- Serves: AC-10, AC-16, AC-24, AC-25
- Test: TC-10, TC-17, TC-25, TC-26
- Depends on: T-8, T-13
- Parallel: no
- Tier: strong: assembly from many inputs, per-lens focus
- Effort: high
- Mode: split: clear tests lead the code

### T-15 Read a finding's `run:` field, run a juror's requested test and put its result in the next packs, with three runs per round at most
- Files: `src/nio/jury.py`, `src/nio/evidence.py`, `tests/test_evidence.py`
- Serves: AC-26, AC-27, AC-44, AC-45
- Test: TC-27, TC-28, TC-29, TC-30
- Depends on: T-5, T-14
- Parallel: no
- Tier: max: runs model-requested commands; a limit or sandbox slip is a security hole
- Effort: high
- Mode: split: clear tests lead the code

## E-7 Findings carry a gap type and are grounded in the code (US-5)

### T-16 Read the gap, where, right and tampering fields of a finding, and drop or invalidate the ungrounded ones
- Files: `src/nio/jury.py`, `tests/test_jury.py`, `tests/test_evidence.py`
- Serves: AC-28, AC-29, AC-30, AC-47
- Test: TC-31, TC-32, TC-33, TC-35
- Depends on: T-15
- Parallel: no
- Tier: strong: parsing and grounding rules with clear tests
- Effort: high
- Mode: split: clear tests lead the code

### T-17 Send lens blockers and majors to the refuter, and record a confirmed assertion weakening as tampering
- Files: `src/nio/jury.py`, `tests/test_evidence.py`
- Serves: AC-13, AC-31, AC-43, AC-48, AC-57
- Test: TC-13, TC-14, TC-34, TC-36, TC-45, TC-68
- Depends on: T-9, T-16
- Parallel: no
- Tier: strong: extends the existing refuter path
- Effort: med
- Mode: split: clear tests lead the code

### T-18 Join the conformance lens's matches to the results and record a blocker for each AC without passing evidence
- Files: `src/nio/evidence.py`, `src/nio/jury.py`, `tests/test_evidence.py`
- Serves: AC-4, AC-5, AC-6, AC-17, AC-51
- Test: TC-4, TC-5, TC-6, TC-18, TC-39, TC-73
- Depends on: T-9, T-14, T-16
- Parallel: no
- Tier: strong: join logic with many edge cases, clear tests
- Effort: high
- Mode: split: clear tests lead the code

### T-19 Compose the epic's outcome: rerun for a missing or invalid lens output, minors left out, a noted major to the human
- Files: `src/nio/jury.py`, `tests/test_jury.py`, `tests/test_evidence.py`
- Serves: AC-49
- Test: TC-37
- Depends on: T-16
- Parallel: no
- Tier: strong: outcome rules with clear tests
- Effort: med
- Mode: split: clear tests lead the code

### T-20 Refuse lens outputs while the plan is over the cap and no pick is recorded
- Files: `src/nio/jury.py`, `tests/test_evidence.py`
- Serves: AC-22
- Test: TC-23, TC-66
- Depends on: T-13, T-16
- Parallel: no
- Tier: cheap: one guard on an existing path
- Effort: low
- Mode: split: a clear test leads the guard

### T-21 Prove the secrets flag adds the security lens at the implementation gate and at the spec gate
- Files: `tests/test_evidence.py`
- Serves: AC-60, AC-61
- Test: TC-48, TC-49
- Depends on: T-2, T-12
- Parallel: no
- Tier: cheap: tests only, following existing patterns
- Effort: low
- Mode: direct: only tests are written, no code to lead

## E-8 Findings become appended tasks or change requests, and the outcome follows the spec jury (US-6)

### T-22 Append a fix task to the epic's Fixes for a finding, once, without touching any existing task
- Files: `src/nio/tasks.py`, `src/nio/jury.py`, `tests/test_tasks.py`, `tests/test_evidence.py`
- Serves: AC-33, AC-35, AC-50
- Test: TC-38, TC-51, TC-53, TC-64
- Depends on: T-19, T-21
- Parallel: no
- Tier: max: edits a hand-owned file; must be once-only and never corrupt existing tasks
- Effort: high
- Mode: split: clear tests lead the code

### T-23 Close the loop on a round: approve with no task, reject with fix tasks and back to implement, a new major to the human
- Files: `src/nio/jury.py`, `src/nio/cli.py`, `src/nio/implement.py`, `tests/test_evidence.py`
- Serves: AC-32, AC-34, AC-38, AC-40, AC-56
- Test: TC-44, TC-50, TC-52, TC-56, TC-58, TC-74, TC-75
- Depends on: T-18, T-19, T-22
- Parallel: no
- Tier: max: multi-branch state machine across jury and flow
- Effort: high
- Mode: split: clear tests lead the code

### T-24 Raise a change request for a code-is-right finding and hold the epic until the human rules
- Files: `src/nio/jury.py`, `tests/test_evidence.py`
- Serves: AC-36, AC-58, AC-59
- Test: TC-46, TC-47, TC-54, TC-65, TC-71
- Depends on: T-17, T-22, T-23
- Parallel: no
- Tier: strong: holds state until the human rules; clear tests
- Effort: high
- Mode: split: clear tests lead the code

### T-25 Write the epic's verdict record with its minors and dropped lenses
- Files: `src/nio/jury.py`, `tests/test_evidence.py`
- Serves: AC-23, AC-37, AC-39
- Test: TC-24, TC-55, TC-57
- Depends on: T-13, T-23
- Parallel: no
- Tier: strong: record writing following the spec jury pattern
- Effort: med
- Mode: split: clear tests lead the code

### T-26 Turn the human's fix choice on the end-of-review list into a fix task and hold the final fix check
- Files: `src/nio/jury.py`, `tests/test_evidence.py`
- Serves: AC-46
- Test: TC-59
- Depends on: T-22, T-23
- Parallel: no
- Tier: strong: reuses T-22 with a hold rule
- Effort: med
- Mode: split: clear tests lead the code

#### Fixes

### T-30 Commit each recorded outcome and let `nio flow done implementation-E-n` write the epic line and, after the last epic, the pass line
- From: C-261030-abpr
- Files: `src/nio/flow.py`, `src/nio/jury.py`, `src/nio/cli.py`, `tests/test_flow.py`, `tests/test_evidence.py`
- Serves: AC-32, AC-40
- Test: TC-72, plus direct unit checks that `nio flow done implementation-E-n` writes the epic line and, after the last epic, the pass line and `merge:`; TC-69 proved later by T-33
- Depends on: T-23, T-25
- Parallel: no
- Tier: max: writes flow history and commits; wrong writes can't be undone
- Effort: high
- Mode: split: clear tests lead the code


### T-31 Add the implementation gate to the jury skill and allow `nio jury evidence`
- From: C-261030-abpr
- Files: `skills/jury/SKILL.md`, `src/nio/hooks.py`, `tests/test_hooks.py`
- Serves: AC-1
- Test: TC-1, plus direct checks that `jury evidence` is in `hooks.ALLOW` and that the skill's shared talk block is unchanged (`tests/test_talk.py`)
- Depends on: T-30
- Parallel: yes
- Tier: cheap: skill text and one allow-list entry
- Effort: low
- Mode: direct: docs and wiring, no test can lead


### T-32 Add the `--demo approved|rejected|stale|cap` runs the quickstart scenarios call
- From: C-261030-abpr
- Files: `tests/test_evidence.py`
- Serves: AC-1, AC-22, AC-32, AC-36
- Test: TC-1, TC-23, TC-50, TC-54 as the four demos QS-1 to QS-4 print their expected lines
- Depends on: T-20, T-24, T-30
- Parallel: yes
- Tier: strong: four scripted scenarios over the whole gate
- Effort: med
- Mode: direct: the demos are the test, nothing to lead


### T-33 Make the flow wait on the gate: print it as next, refuse the next claim while it is open, report old skipped epics
- From: C-261030-abpr
- Files: `src/nio/implement.py`, `src/nio/flow.py`, `tests/test_implement.py`, `tests/test_flow.py`, `tests/test_evidence.py`
- Serves: AC-1, AC-40
- Test: TC-69, TC-70
- Depends on: T-3, T-30, T-31, T-32
- Parallel: no
- Tier: strong: flow-state rules across two modules, testable
- Effort: high
- Mode: split: clear tests lead the code

