---
slug: 2026-11-07-review-fixes
retired: []                      # CT IDs removed from this plan; never reused
---
# Contracts: fix the review's findings in the speed-up PRs

## Contracts

### CT-1 Only a printed batch is asked of the refuter, and only a run with one takes a refuter file (FR-1, FR-2) [agent]
- Binding: `src/nio/jury.py:collect` (existing)
- Also: `src/nio/jury.py:ask_refuter` (new), `src/nio/jury.py:refuter_pack` (existing), `src/nio/jury.py:step` (existing)
- Kind: function
- Shape: `collect(root, slug, gate, run, expect=(), tier=None, ask=True)`; `ask_refuter(root, slug, gate, run, ids)`
- Accepts: `ask`: whether the caller prints the batch `collect` returns. `nio jury collect` prints it, so the default is `True`; `step` passes `False`, since it shows the batch only when no juror must be re-run.
- Returns: as today. With `ask` and a batch to print, `collect` calls `ask_refuter` with the batch's finding IDs before returning. `refuter_pack`, which `step` calls exactly when it shows the batch, calls `ask_refuter` with the `### J-n` IDs of the batch it writes. `ask_refuter` adds the IDs to the ledger's `asked[run]` (see Data model) and saves it. A `<gate>-refuter.md` not yet collected is applied only when `asked[run]` is non-empty, through CT-2 with `asked[run]`.
- Fails: a `<gate>-refuter.md` whose sha the ledger hasn't collected, in a run with no `asked[run]` → `ValueError("refuter output before its batch: <path> was not asked for; delete it and call again")`, raised before the ledger is saved, so no round, finding or outcome is recorded. A run in flight when this lands, whose batch the old code printed, is refused the same way: its refuter file is deleted and the step called again, which prints the batch anew.
- Rules: "The ledger records a batch only in a call that printed it, so a file present before that call is refused by that call, and stays refused until it is deleted." (FR-1)
### CT-2 A refuter output applies only to its batch's IDs, first verdict counting (FR-2) [agent]
- Binding: `src/nio/jury.py:refute` (existing)
- Kind: function
- Shape: `refute(led, path, asked)` (new third argument; its one caller is CT-1)
- Accepts: `asked`, the finding IDs the run's batches listed.
- Returns: the lines it returns today. A block whose ID is not in `asked` is skipped like a block for an unknown ID (no line). The first block for an ID sets its validation; a later block for that ID finds it no longer `pending` and is skipped, as today.
- Rules: "apply verdicts only for the finding IDs the run's batches listed, the first verdict per ID counting; any other ID is ignored, and a listed ID with no verdict stays pending" (FR-2)

### CT-3 Juror outputs are refused when the judged version moved (FR-9) [agent]
- Binding: `src/nio/jury.py:collect` (existing)
- Kind: function
- Shape: `collect(root, slug, gate, run, expect=(), tier=None, ask=True)` (as CT-1)
- Accepts: the run's `jury/packs/step.json`, whose `version` the packs recorded (`packs`, `_begin`).
- Returns: unchanged when no lens output is new (its sha not in the ledger's `collected`), when `step.json` is absent (a run driven by hand with `nio jury collect`), or when `step.json`'s `version` equals `version_now(root, slug, gate)`.
- Fails: a new lens output (not the refuter's) and a `version` different from `version_now` → `ValueError("the <gate> changed after <run>'s packs were written: restore it, or start a new run (nio jury next without --run)")`, before anything is merged or saved. At the implementation gate the check runs before `evidence.current`, which today refuses a moved epic commit with its own message.
- Rules: "IF new lens juror outputs arrive in a run whose judged version changed since the run's packs were written ... THEN THE SYSTEM SHALL collect none of them and refuse" (FR-9)
### CT-4 git's raw output for a patch (FR-3, FR-4) [agent]
- Binding: `src/nio/records.py:git` (existing)
- Kind: function
- Shape: `git(root, *args, full=False, raw=False)`
- Accepts: `raw=True`: run git without text decoding.
- Returns: with `raw` (which implies `full`), `(exit code, stdout as bytes, stderr decoded with errors="replace")`; without it, exactly as today.
- Rules: "keep the patch's bytes as git produced them, with no decoding and no newline translation" (FR-3, FR-4)

### CT-5 land and shelve save the patch as bytes (FR-3, FR-4) [agent]
- Binding: `src/nio/implement.py:land` (existing)
- Also: `src/nio/implement.py:shelve` (existing) changes the same way
- Kind: function
- Shape: unchanged signatures.
- Returns: as today; the patch file is `git diff --binary`'s stdout through CT-4 with `raw=True`, written with `write_bytes` before anything is applied or restored (as today). `shelve`'s patch for no kept path is `b""`.
- Rules: "WHEN `land` saves and applies a wave task's patch THE SYSTEM SHALL keep the patch's bytes as git produced them" (FR-3); "WHEN `shelve` saves a task's patch THE SYSTEM SHALL keep the patch's bytes as git produced them" (FR-4)

### CT-6 No run and no juror line without a juror (FR-5) [agent]
- Binding: `src/nio/jury.py:_begin` (existing)
- Kind: function
- Shape: `_begin(root, slug, gate, run, lenses, fix)`; `run` may be `""`
- Accepts: `run` `""`: `_begin` takes `_reusable(...)` or `records.new_run(root)` itself, only once it knows `lenses` is non-empty. `step`'s two callers (no outputs yet; outcome `rerun`) pass the run they have, or `""`, and no longer allocate one.
- Returns: with an empty `lenses`, `["next: show the human: the <gate> changed but no lens has a fix to check"]`: no `run:` line, no run folder, no pack or `step.json`. Otherwise as today.
- Rules: "IF a gate's outcome is `rerun` and no lens is named to re-run THEN THE SYSTEM SHALL name no juror and print a `next:` line that says to show the human." (FR-5)
### CT-7 A changed text gate with nothing to fix-check re-runs every lens that voted (FR-10) [agent]
- Binding: `src/nio/jury.py:changed` (existing)
- Kind: function
- Shape: `changed(root, slug, gate)` (unchanged)
- Returns: as today, except the branch that re-runs every lens that voted (`set(votes(led))`) when no lens is named and the artefact changed also applies at the spec, plan and tasks gates (`gate in GATES`) once any round was recorded `rejected`. The implementation gate keeps today's rule (conformance re-runs, CT-20 of the implementation-jury spec). "Changed" is `diff`'s changed IDs or sections, whitespace-normalised, the front matter being a section (`parts`).
- Rules: "re-run every lens that voted in that round on what changed, as it does for an approved gate that changed" (FR-10)
### CT-8 Self-check flags are not test names (FR-6) [agent]
- Binding: `tests/selfcheck.py:main` (existing)
- Kind: function
- Shape: `main(tests)` (unchanged)
- Returns: as today, with the words of `sys.argv[1:]` that start with `-` left out of the test names.
- Rules: "let a self-check script run with flag words such as `-v` and not read them as test names" (FR-6)

## Data model
- **Gate ledger** in `src/nio/jury.py:load` (existing), saved by `save` as each spec's `jury/<gate>.json` [agent]
  - asked: `{run ID: [finding IDs]}`, new, optional (a ledger without it has asked for no batch). Written only by CT-1 in the call that prints a batch.
