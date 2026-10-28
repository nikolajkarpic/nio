# Architecture: flow state

Settles only what the plan skill's stop list sends here. Each item is already decided by the approved spec or the
existing code, and this file records where. It adds no new design. Read-only to the plan; changing it takes a change
request.

## New modules and folders (stop list 2)
- `src/nio/flow.py`: `nio flow` (`next`, `start`, `done`, `status`, `park`, `abandon`, `seen`), one module per stage
  family as `spec.py`, `plan.py` and `tasks.py` already are, wired into `src/nio/cli.py` the same way (spec FR-7 to
  FR-61). It reads the other stages only through their existing functions: `spec.check`, `plan.check`,
  `plan.approved`, `tasks.check`, `tasks.approved`, `jury.load`, `jury.standing`, `jury.blob` and `jury.artefact`,
  and git through `records.git`, which gains an optional mode returning git's exit code and stderr for the gate commit;
  every current caller is unchanged (C-261028-dclz).
- `tests/test_flow.py` already exists for the task refusals of #42. It keeps them waiting, now on #43 (change request
  C-261028-xcg6), and gains this spec's tests.
- No new folder: every file below lives in an effort folder or a run folder that already exists.

## Stored data (stop list 3)
- `.nio/specs/<slug>/state.json`: committed JSON holding only the keys FR-3 lists. Written only by `nio flow` (FR-1),
  refused on any other key or on a hash mismatch with the last history line (FR-6, FR-58).
- `.nio/specs/<slug>/history.jsonl`: committed, append-only, one JSON line per transition, override, skip, park,
  abandon, resume, seen, repair, and in auto mode `fail` (FR-4, FR-5, FR-41, FR-57 to FR-59). Never rewritten
  except for cutting off a torn last line (FR-59).
- The effort's lock file: in the effort folder, ignored by git through a `.gitignore` line, created atomically and
  naming its process and host (FR-54).
- The run folder (`.nio/runs/<run>/`, already git-ignored scratch) records the effort and the stage or task a run
  serves (FR-33).
- Gate approval is read from git, not stored: a `nio: approve <gate>` commit touching the effort folder (FR-55), the
  message form CLAUDE.md already fixes.

## Interfaces used outside this feature (stop list 4)
- `nio run` takes an optional `<slug> <stage|T-n>`; with no arguments it works as today (FR-33, FR-34).
  `records.new_run` keeps its current callers.
- Skills and agent cards: each one that mentions overrides or flow state says that only the human gives `--human`,
  runs `nio flow seen` or asks for `nio flow abandon`, and that no agent edits `state.json` or `history.jsonl`
  (FR-1, FR-52, FR-57). The "Talking to the human" block is unchanged.
- The tasks-stage spec moves its task machine from #45 to #43 through change request C-261028-xcg6 (accepted, Q17).

## No new dependency (stop list 1)
Nothing beyond the Python standard library and `ruamel.yaml`, which the CLI already uses.
