#113 on PR #110's branch. Problem: escalation jurors added to a run after its refuter batch was recorded can re-raise a finding and forge `spec-refuter.md`. Fix: record the batch per refuter batch, not per run, or refuse refuter output for findings whose batch came before the latest merge. Choose the smallest correct option. Also fix the two cheap minors from the review: `land` should check git diff's exit code like `shelve` does, and the missing `print("ok")`.

Turn the repros into tests that fail before the fix.

## Source: https://github.com/nikolajkarpic/nio/issues/113

## Problem
#110's fix for #101 records the refuter batch per **run** (`asked[run]`), not per batch. Once a run's first batch is asked, any later writer in that run can replace `<gate>-refuter.md`, and `collect` applies it to every asked ID that is pending at that moment. Escalation jurors are spawned into the same run after the batch was asked, so they are such writers.

In one collect, `merge` runs before the refuter file is applied (`src/nio/jury.py` `collect`, around lines 640-662). An escalation juror re-raises a peer's confirmed major as a blocker. `add()` (line ~840) sends that finding back to `pending`, and the forged refuter file in the same collect marks it `refuted`. The real refuter never sees the second batch. A confirmed finding raised by another lens is dismissed by one juror.

## Repro (branch `nio/2026-11-07-lite-path` at df1f46e, which contains #110)
`/tmp/claude-1000/-home-work-nio/d6f51638-95d3-4d54-b8ed-fbf62d4bc994/scratchpad/rvrepro/escalation_forge.py <checkout>`, built with `tests/test_jury.py` helpers:
1. logic raises a major (J-1) and testability raises a blocker (J-2). The real refuter confirms both, so `asked[run] = [J-1, J-2]`.
2. `next` says escalate testability. The juror `spec-testability-2` writes its output, re-raising J-1's finding as a blocker, and **also** overwrites `spec-refuter.md` with `### J-1 / result: refuted`.
3. `nio jury next` prints `refuted J-1`. The ledger ends with `J-1: refuted/refuted`, and no refuter batch was shown for it.

## Proposal
Record the batch's own identity and refuse refuter output that predates it. Options:
- key `asked` by batch: a counter, or the hash of the batch text written into `packs/refuter.md`, which the refuter must echo in its output;
- or clear `asked[run]` once a refuter output is applied, so a refuter file is accepted only while a printed batch is outstanding, and refuse any refuter file that changes after lens outputs were merged in the same collect (apply the refuter before `merge`, or refuse when both are new).
#109's host guard would also block this on Claude Code, but not on Codex.

Refs: #101, #110, #109, #105


## Source: review comment on PR #110 (minors)

Independent review: minor findings. The major one is filed as #113: an escalation juror can still forge the refuter's verdict, because `asked` is keyed by run.

- `src/nio/implement.py:368` (`land`): the exit code of `git diff` is dropped (`raw=True)[1]`), unlike in `shelve`. If the diff fails and `--name-only` fails with it, `names` is empty, the apply is skipped, and `land` returns `err == ""`, so the task reads as landed with nothing applied. Repro: `land(root, "s", "T-1", tree, "0"*40)` after editing `a.txt` in the tree returns `('.nio/runs/R-1/T-1.patch', {}, '')`, and main's `a.txt` is unchanged. This is unlikely while `since` is the claim commit, but give it the same `if code: raise` as `shelve`.
- `tests/test_jury.py` `test_ac2_refuter_only_for_its_batch`: the second half seeds `asked` by writing the ledger directly. That proves the ID filter. It also shows the guard's trust anchor is a file a Write-capable juror can edit, so #109 is a prerequisite for #101's claim, not a nice-to-have.
- `tests/test_evidence.py` `test_ac14_epic_commit_changed_while_jurors_ran` has no `print("ok")`, unlike its neighbours (cosmetic).

