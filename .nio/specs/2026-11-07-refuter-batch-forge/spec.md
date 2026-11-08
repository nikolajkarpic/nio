---
slug: 2026-11-07-refuter-batch-forge
route: lite
risk: [multi-party]              # auth | pii | money | external-input | data-deletion | migration | multi-party | public-api
retired: [OP-1, OP-2, OP-3, OP-4]
---
<!-- Bugfix spec (Kiro's three sections). Unchanged behaviour is never empty: it is the regression guard.
Each EB-n has an AC that is the test written first (it fails before the fix); each UB-n has a regression AC. -->
# An escalation juror can't forge the refuter's verdict, and `land` stops on a failed git diff

## Summary
#110's fix for #101 records the refuter batch per run (`asked[run]`), not per batch. Escalation jurors are spawned
into the same run after the batch was asked, so one of them can re-raise a peer's confirmed finding (which sends it
back to `pending`) and overwrite `<gate>-refuter.md` in the same collect: the forged file marks the finding `refuted`,
and the real refuter never sees the second batch. A confirmed finding raised by another lens is dismissed by one
juror. Filed as #113 from the independent review of PR #110. [human]
The same review found two minors: `land` drops the exit code of `git diff` (unlike `shelve`), so a failed diff reads
as a task landed with nothing applied; and `test_ac14_epic_commit_changed_while_jurors_ran` in `tests/test_evidence.py`
lacks the `print("ok")` its neighbours have. The missing `print("ok")` is cosmetic: it is added with the fix and has
no behaviour to specify. [human]
The repros become tests that fail before the fix. [human]
Repro (forge): logic raises a major (J-1) and testability a blocker (J-2); the real refuter confirms both, so
`asked[run] = [J-1, J-2]`. `next` says escalate testability; the juror `spec-testability-2` writes its output,
re-raising J-1's finding as a blocker, and also overwrites `spec-refuter.md` with `### J-1 / result: refuted`.
`nio jury next` prints `refuted J-1`, and the ledger ends with `J-1: refuted/refuted` with no refuter batch shown for
it. [human]
Repro (land): `land(root, "s", "T-1", tree, "0"*40)` after editing `a.txt` in the tree returns
`('.nio/runs/R-1/T-1.patch', {}, '')`, and main's `a.txt` is unchanged. [human]

## Current behaviour
- **CB-1** WHEN a lens output merged in a collect sends a finding back to `pending` and the run's refuter file changed in that same collect THEN the system applies that refuter file's verdict to the finding, though no refuter batch listing it was printed since it became pending. [human]
- **CB-2** WHEN `git diff` fails inside `land` THEN the system returns no error, applies nothing, and the task reads as landed. [human]

## Expected behaviour
- **EB-1** IF a refuter output changes after the run's last printed batch was already answered THEN THE SYSTEM SHALL refuse the collect with "refuter output before its batch" and apply none of its verdicts; a finding sent back to `pending` is answered only by a refuter output written after a batch listing it was printed. [human]
- **EB-2** IF `git diff` fails inside `land` THEN THE SYSTEM SHALL return git's error and apply nothing to the main tree, so the caller blocks the task. [human]

## Unchanged behaviour
- **UB-1** WHEN the refuter answers the batch it was shown THE SYSTEM SHALL CONTINUE TO apply each `confirmed` or `refuted` result for the finding IDs that batch listed. [agent]
- **UB-2** WHEN a refuter file appears in a run before any batch was printed for it THE SYSTEM SHALL CONTINUE TO refuse it with "refuter output before its batch". [agent]
- **UB-3** WHEN a refuter output names a finding ID its batch did not list THE SYSTEM SHALL CONTINUE TO ignore that block. [agent]
- **UB-4** WHEN an escalation juror re-raises a finding without touching the refuter file THE SYSTEM SHALL CONTINUE TO send the finding back to `pending` and list it in the next printed refuter batch. [agent]
- **UB-5** WHEN `git diff` succeeds inside `land` THE SYSTEM SHALL CONTINUE TO apply the task's changes to the main tree and return the patch path, the saved bytes and an empty error. [agent]
- **UB-6** WHEN `git apply` fails inside `land` THE SYSTEM SHALL CONTINUE TO return git's error with the main tree untouched, so the task is blocked. [agent]

## Acceptance criteria
- **AC-1** (EB-1) Given the forge repro (J-1 and J-2 confirmed by the real refuter, then `spec-testability-2` re-raises J-1 as a blocker and overwrites `spec-refuter.md` with `### J-1 / result: refuted`), when `nio jury next` collects, then the collect is refused and J-1 is not refuted; once the forged file is removed, the next collect leaves J-1 pending and lists it in the printed refuter batch. [human]
  Observable: the collect raises "refuter output before its batch"; no `refuted J-1` line; after removal the ledger's J-1 validation is `pending` and the batch lists J-1. Level: integration. (written first; fails before the fix)
- **AC-2** (EB-2) Given a worktree where `a.txt` was edited, when `land(root, "s", "T-1", tree, "0"*40)` runs and `git diff` fails, then it returns a non-empty error and main's `a.txt` is unchanged. [human]
  Observable: the third value `land` returns is git's error, not `''`, and main's `a.txt` holds its old bytes. Level: unit. (written first; fails before the fix)
- **AC-3** (UB-1) Given a run whose refuter batch listed J-1 and J-2, when the refuter writes `confirmed` for J-1 and `refuted` for J-2 and `nio jury next` collects, then both results are applied. [agent]
  Observable: the ledger shows J-1 `confirmed` and J-2 `refuted`, and the output prints both lines. Level: integration.
- **AC-4** (UB-2) Given a run with no printed refuter batch, when a refuter file appears and the run is collected, then the collect is refused. [agent]
  Observable: the error says "refuter output before its batch". Level: integration.
- **AC-5** (UB-3) Given a batch that listed J-1 only, when the refuter's output also has a block for J-2, then J-2 is left as it was. [agent]
  Observable: J-2's ledger validation is unchanged. Level: integration.
- **AC-6** (UB-4) Given a confirmed J-1, when an escalation juror re-raises its finding as a blocker and the refuter file is untouched, then J-1 goes back to `pending` and is in the next refuter batch. [agent]
  Observable: the ledger's J-1 validation is `pending` and the printed batch lists J-1. Level: integration.
- **AC-7** (UB-5) Given a worktree where `a.txt` was edited since its claim commit, when `land` runs, then main's `a.txt` holds the edit. [agent]
  Observable: `land` returns an empty error and main's `a.txt` matches the tree's. Level: unit.
- **AC-8** (UB-6) Given a task whose patch does not apply to the main tree, when `land` runs, then it returns git's error and the main tree is unchanged. [agent]
  Observable: the returned error is non-empty and the main tree's files are byte-identical to before. Level: unit.

## Decisions
- The batch is cleared once a refuter output is applied; a refuter file that changes with no batch outstanding refuses the collect (grill Q1, Q2, [agent], RF-1, RF-2).
- `land` returns a failed diff as git's error, which blocks the task, instead of raising (grill Q3, [agent], RF-3).
- Jurors write their own output file (D-261107-pdq4), limited to it only by their card's instruction (D-261107-ldro):
  no host stops an escalation juror from writing `<gate>-refuter.md`, so the guard has to be in `collect`. [agent]
- `land` and `shelve` read `git diff` with `records.git(..., raw=True)` (C-261107-bff2); EB-2 uses the exit code that
  call already returns. [agent]

## Open points
