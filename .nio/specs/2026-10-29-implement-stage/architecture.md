# Architecture: implement stage

Settles only what the plan skill's stop list sends here. Each item follows from the approved spec, the decisions and
change requests it cites, or the existing code, and this file records where. It adds no design of its own. Read-only to
the plan; changing it takes a change request.

## New modules and folders (stop list 2)
- `src/nio/implement.py`: the task machine and its guards (claim, red, green, review, commit, block, unblock,
  baseline, epic hand-off), the known-runner markers (FR-34) and running a command with a time limit (FR-44). It is one
  module per stage family, as `spec.py`, `plan.py`, `tasks.py` and `flow.py` already are (RF-14, RF-21).
  - It reads tasks only through `tasks.parse` and `tasks.show` (RF-15), writes history only through `flow.record`
    under `flow.lock` (RF-14), and reaches git only through `records.git(..., full=True)` (RF-18).
  - `flow.py` calls it for the `implementing` guard, `where` and `next`, replacing the "implement not built" wait
    (FR-30, RF-12).
- `src/nio/agents/worker.md`: the one `nio-worker` card. `nio agents sync` renders it once per tier as
  `nio-worker-<tier>` (FR-6, D-261029-ti54). Every other card still renders once (RF-16).
- `skills/implement/SKILL.md`: the `@nio:implement` skill the orchestrator follows at implementing. `flow.SKILL` names
  it for that state (RF-12). This follows the repo's layout: one folder per skill.
- `tests/test_implement.py`: this spec's tests, a plain script like the others (RF-20).

## Stored data (stop list 3)
- `.nio/specs/<slug>/state.json`: no new key.
  - `claims` holds the one current claim, `{"task": "T-n"}`.
  - `attempts` holds `{"T-n": <count>}`.
  - Both keys are already reserved (FR-18, RF-13).
- `.nio/specs/<slug>/history.jsonl`: new line kinds, each naming its `task` (FR-18). They are written by `flow.record`
  like every other line.
  - `baseline`: the suite command, its exit code, the failing test names, the collected count and the runner
    (FR-16, FR-36).
  - `claim`.
  - `red`: the command, the output hash, the runner, and `frozen: {path: hash}` (FR-10).
  - `green`: the command and the output hash.
  - `review`: passed or failed, the new failures, and the files outside the task's list (FR-15).
  - `refused`: red or green refused, or a time limit hit; each counts an attempt (FR-37, FR-44).
  - `task_done`: the commit made with it (FR-19).
  - `blocked`: the cause, and the change record and handoff hash when a spec problem caused it (FR-24).
  - `unblock` (FR-38).
  - `epic`: the epic gate `skipped: not built` (FR-28).
- New config keys, read through `records.config` (RF-17):
  - `tests.suite`: the full-suite command (FR-35);
  - `tests.timeout`: seconds, 600 when unset (FR-44);
  - `implement.mode`: forces one mode for every task (FR-40).
- `tasks.md` gains the `Mode: <split|single|direct>: <reason>` field. `tasks.py` checks it, the tasks template shows
  it, and the evaluator card rates it (C-261029-4cev, FR-40).
- Change records for spec problems are made with the existing `records.new(root, "change", ...)`, with
  `outcome: pending` (FR-24).
- Git:
  - the effort branch is `nio/<slug>` (FR-20);
  - one `T-n: <title>` commit per done task holds the task's changes and the effort's `history.jsonl` and
    `state.json` (FR-19);
  - nothing is merged (FR-21).

## Interfaces used outside this feature (stop list 4)
- New `nio flow` subcommands, registered under `fsub` in `cli.py` like the others (RF-21). Each writing command takes
  `--by` as today.
  - `nio flow claim [<slug>]`: claims the next ready task and prints its worker pack's path, mode, card and effort.
  - `nio flow red <slug> T-n --run "<command>"` (FR-8).
  - `nio flow green <slug> T-n [--run "<command>"]` (FR-12, FR-41).
  - `nio flow block <slug> T-n --handoff <file>`: files the change record and blocks the task (FR-24).
  - `nio flow unblock <slug> T-n --human "<reason>"`. It takes a reason like `nio flow done --human` (FR-38).
- The worker pack is written by `claim` to `.nio/runs/<run>/packs/T-n.md` (FR-4). It is built from `pack.build`,
  `tasks.show`, the served ACs' text, and the CT-n and TC-n blocks.
- `nio flow next` at implementing names `@nio:implement` and the next ready task. The two flow tests that pin today's
  wait change to the built stage (RF-20).
- `nio agents sync` adds four `nio-worker-<tier>` files per host (FR-6).
- The flow-state rule that a worker never runs `nio flow` gains the single-mode exception for `red` and `green`, in
  the worker card and `@nio:implement` (C-261029-rmbs, FR-5).

## No new dependency (stop list 1)
Commands run through `subprocess.run(..., timeout=...)`, and hashes use `hashlib`. Both are the standard library. The
"no model or HTTP client loaded" check (NFR-1) holds as the code stands (RF-19).
