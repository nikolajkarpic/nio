---
slug: 2026-11-07-refuter-batch-forge
retired: []                      # task IDs removed from this file; never reused
---
# Tasks: An escalation juror can't forge the refuter's verdict, and `land` stops on a failed git diff

## E-1 Refuter verdicts apply only to a printed batch, and `land` returns a failed diff

### T-1 Clear the asked batch once a refuter output is applied, so a refuter file changed with no batch outstanding refuses the collect
- Files: `src/nio/jury.py`, `tests/test_jury.py`
- Serves: AC-1, AC-3, AC-4, AC-5, AC-6
- Test: the forge repro (two findings confirmed, then `spec-testability-2` re-raises the first and overwrites `spec-refuter.md` with `refuted` for it) is refused with "refuter output before its batch", that finding is not refuted, and after the file is removed the next collect leaves it pending and lists it in the batch; plus guards that a refuter answering its printed batch applies confirmed and refuted, a refuter file with no printed batch is refused, a block for an ID the batch did not list is ignored, and a re-raised finding with the refuter file untouched goes to pending and into the next batch
- Depends on: none
- Parallel: yes
- Tier: strong: collect-state change with a guard that must keep four existing behaviours, but the tests spell each one out
- Effort: med
- Mode: split: the forge repro and guards are testable first and fail before the fix

### T-2 Return git's error when `git diff` fails inside `land`, applying nothing
- Files: `src/nio/implement.py`, `tests/test_waves.py`, `tests/test_evidence.py`
- Serves: AC-2, AC-7, AC-8
- Test: with `a.txt` edited in the worktree and `git diff` failing, `land` returns a non-empty error and main's `a.txt` is unchanged; with `git diff` working, main's `a.txt` holds the edit and the error is empty; with a patch that does not apply, `land` returns git's error and the main tree is byte-identical; `test_ac14_epic_commit_changed_while_jurors_ran` gains its missing `print("ok")`
- Depends on: none
- Parallel: yes
- Tier: cheap: check the exit code `git diff` already returns, as `shelve` does
- Effort: low
- Mode: split: the failed-diff test fails before the fix

#### Fixes

### T-3 Fix: A failed git diff force-removes the worktree with no patch saved
- From: J-1 (implementation-E-1, round 1)
- Files: `src/nio/implement.py`
- Serves: AC-2
- Test: new: AC-2
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

### T-4 Fix: AC-4 has no passing evidence
- From: J-7 (implementation-E-1, round 1)
- Files: `src/nio/jury.py`, `tests/test_jury.py`
- Serves: AC-4
- Test: new: AC-4
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding

### T-5 Fix: AC-5 has no passing evidence
- From: J-8 (implementation-E-1, round 1)
- Files: `src/nio/jury.py`, `tests/test_jury.py`
- Serves: AC-5
- Test: new: AC-5
- Depends on: none
- Parallel: no
- Tier: strong: a fix from a jury finding
- Effort: med
- Mode: single: a fix from a jury finding
