# Grill: 2026-11-07-review-fixes

Session 1 (2026-11-07): delegated to the agent (orchestrator / claude-code / claude-opus-5-5) by the human, with standing authority to take the recommended option. Permissions, deletion and irreversible steps would still go to the human; none came up (the fixes stop data loss, they delete nothing).

## Lookup · OP-5, OP-6, OP-7 · 2026-11-07
Facet: meaning, actors, data, change, verification
Found: RF-1 to RF-12 in research.md. Retired OP-5 (RF-1, RF-2: `collect` prints the batch on both paths, so the batch is known where it is printed), OP-6 (RF-5: only `land` and `shelve`), OP-7 (RF-11, RF-12 back A-1, A-3, UJ-1; RF-4 backs UJ-2).

## Asked · Q1 · OP-1 · 2026-11-07
Question: Besides the refuter check, should the jury refuse juror outputs when something changed while the jurors ran?
Context: Jurors can write any file, including the spec they judge (issue #101). The step already records the judged version when it writes the packs (RF-3). A whole-repo git snapshot would also trip on the ledger, verdict records and evidence the step itself writes.
Options: 1. Refuse new juror outputs when the judged spec, plan, tasks or epic commit changed since the packs were written (recommended): three lines on a value already recorded; edits elsewhere are not caught. 2. Record HEAD and git status and refuse on any change outside the run's jury folder: catches more, but trips on the step's own writes. 3. The refuter check alone: a juror can still edit what it judges and the edit is recorded as judged.
Refs: OP-1 · FR-1 · RF-3 · issue #101

## Q1 · OP-1 · 2026-11-07
Question: Besides the refuter check, should the jury refuse juror outputs when something changed while the jurors ran?
Facet: failure
Options:
1. Refuse when the judged version changed (recommended)
2. Whole-repo git snapshot
3. The refuter check alone
Answer: 1. Refuse new juror outputs when the judged spec, plan, tasks or epic commit changed since the packs were written: three lines on a value already recorded; edits elsewhere are not caught. [agent]
Patched: FR-9, AC-13; Non-goals; retired OP-1

## Asked · Q2 · OP-2 · 2026-11-07
Question: When a rerun has no lens with a fix to check, what should `nio jury next` do?
Context: Today it prints "run each juror" with none listed and loops (RF-6). An approved gate that changed already re-runs every lens that voted (RF-7).
Options: 1. Both (recommended): when the spec's items or sections changed, every lens that voted re-checks the change, as for an approved gate; when nothing a lens could see changed, end with "show the human". 2. Always show the human: the human must close the gate by hand after every accepted risk plus a wording edit. 3. Always re-run every voting lens: a whitespace-only edit would start a run with nothing to judge.
Refs: OP-2 · FR-5 · RF-6, RF-7 · issue #103

## Q2 · OP-2 · 2026-11-07
Question: When a rerun has no lens with a fix to check, what should `nio jury next` do?
Facet: change
Options:
1. Both (recommended)
2. Always show the human
3. Always re-run every voting lens
Answer: 1. Both: when the items or sections changed, every lens that voted re-checks the change, as for an approved gate; when nothing a lens could see changed, end with "show the human". [agent]
Patched: FR-5, FR-10, AC-7, AC-8; retired OP-2

## Asked · Q3 · OP-3 · 2026-11-07
Question: Should a covered journey's `Expected:` be checked in this effort?
Context: Every quickstart step has an `Expected:` block (RF-9), so "covered only when Expected is empty" would turn off the covered-journey speed-up and change its test; matching against the suite's own output is a larger change.
Options: 1. Leave it in #104 with a note (recommended): a covered journey still passes on the suite's exit code. 2. Covered only when Expected is empty: every journey runs again, costing a test-file run each. 3. Match the suite's own output: new plumbing for the suite's output.
Refs: OP-3 · FR-8, AC-12 · RF-9 · issue #104

## Q3 · OP-3 · 2026-11-07
Question: Should a covered journey's `Expected:` be checked in this effort?
Facet: verification
Options:
1. Leave it in #104 with a note (recommended)
2. Covered only when Expected is empty
3. Match the suite's own output
Answer: 1. Leave it in #104 with a note: a covered journey still passes on the suite's exit code. [agent]
Patched: retired FR-8, AC-12, OP-3; SC-3

## Asked · Q4 · FR-7 · 2026-11-07
Question: Should evidence run misuse tests on a self-check suite in this effort?
Context: A per-test command needs the suite's per-file prefix parsed from an `xargs`/`sh -c` line and a rule for which runners accept test names (RF-10): a design call, not a small fix.
Options: 1. Leave it in #104 with a note (recommended): misuse tests on this repo's suite stay "attack not run". 2. Build it here: a prefix parser and a runner rule, untested on other projects. 3. Read misuse results from the suite's ok/FAIL lines: misuse tests must then be in the suite.
Refs: FR-7, AC-11 · RF-10 · issue #104

## Q4 · FR-7 · 2026-11-07
Question: Should evidence run misuse tests on a self-check suite in this effort?
Facet: verification
Options:
1. Leave it in #104 with a note (recommended)
2. Build it here
3. Read misuse results from the suite's ok/FAIL lines
Answer: 1. Leave it in #104 with a note: misuse tests on this repo's suite stay "attack not run". [agent]
Patched: retired FR-7, AC-11; SC-3

## Asked · Q5 · OP-4 · 2026-11-07
Question: How should `test_pack.py -v` work again?
Context: selfcheck reads `-v` as a test name (RF-8); CLAUDE.md documents the flag (RF-12).
Options: 1. selfcheck skips words that start with `-` (recommended): one line, the documented flag keeps working. 2. Drop `-v` from test_pack.py and CLAUDE.md: loses the pack printout.
Refs: OP-4 · FR-6, AC-10 · RF-8, RF-12 · issue #104

## Q5 · OP-4 · 2026-11-07
Question: How should `test_pack.py -v` work again?
Facet: change
Options:
1. selfcheck skips words that start with `-` (recommended)
2. Drop `-v`
Answer: 1. selfcheck skips words that start with `-`: one line, the documented flag keeps working. [agent]
Patched: FR-6, AC-10; retired OP-4

## Call · AC-2, AC-3, AC-5, AC-6, AC-9 · 2026-11-07
The drafter's proposals, taken as written (below the bar: none changes what a user can do or sees, who may do it, what data is kept, or what it costs). [agent]

## Asked · Q6 · J-2 · 2026-11-07
Question: When the jury refuses outputs because the judged spec changed while jurors ran, how does the run go on?
Context: The spec jury found the refusal leaves the orchestrator with no next step. The judged version is already recorded when packs are written (RF-3).
Options: 1. The refusal names both ways on: restore the judged version, or start a new run (recommended): nothing new to build; the outputs of a discarded run are never collected. 2. Rewrite the packs in the same run automatically: a juror's edit silently becomes the new baseline. 3. Leave the message as is: the orchestrator guesses.
Refs: J-2 · FR-9, AC-13 · RF-3

## Q6 · J-2 · 2026-11-07
Question: When the jury refuses outputs because the judged spec changed while jurors ran, how does the run go on?
Facet: failure
Options:
1. Name both ways on (recommended)
2. Rewrite the packs automatically
3. Leave the message as is
Answer: 1. The refusal names both ways on: restore the judged version, or start a new run: nothing new to build; the outputs of a discarded run are never collected. [agent]
Patched: FR-9, AC-13, AC-14
