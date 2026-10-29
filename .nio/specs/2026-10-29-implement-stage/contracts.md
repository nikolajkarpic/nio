---
slug: 2026-10-29-implement-stage
retired: []                      # CT IDs removed from this plan; never reused
---
# Contracts: implement stage

## Contracts

### CT-1 Run a command with a time limit (FR-44, FR-8, FR-12, FR-14, FR-16) [default]
- Binding: `src/nio/implement.py:run` (new)
- Like: `src/nio/records.py:git`
- Kind: function
- Shape: `run(root, command, limit) -> (code, output, cause)`; `cause` is `""`, `"time limit"` or `"program not found"`
- Accepts: a shell command string from `--run` or `tests.suite`, run with `shell=True` in `root`, stdin closed (`stdin=DEVNULL`), stdout and stderr merged; `limit` in seconds, from `tests.timeout`, 600 when unset (FR-44)
- Returns: the exit code and the merged output as text
- Fails: the limit passes → the whole process group is killed, `(None, output so far, "time limit")`; the shell reports exit 127 → `(127, output, "program not found")`
- Rules: "WHEN a command it runs passes the time limit (`tests.timeout` in the project's NIO config, 10 minutes when unset) or its program isn't found THE SYSTEM SHALL stop it and treat it as a refused red or green, or as a failed review for the full suite, naming the cause." (FR-44)
- Rules: the command is started in its own process group (`start_new_session=True`) so that killing it on the limit leaves no child running (AC-49) [agent]

### CT-2 Known runners and red's right reason (FR-8, FR-9, FR-34, FR-43) [default]
- Binding: `src/nio/implement.py:wrong_reason` (new)
- Like: `src/nio/tasks.py:TIERS`
- Kind: function
- Shape: `RUNNERS = {name: {"match": regex on the command, "error": [markers], "none": [markers]}}`; `runner(command) -> name | None`; `wrong_reason(name, code, output) -> "" | "collection, import or syntax error: <marker>" | "no tests ran"`
- Accepts: the eight runners and markers of research RF-6: pytest, unittest, jest, vitest, mocha, go test, cargo test, rspec. pytest also counts exit 2 and 4 as errors and exit 5 as no tests ran. Maven and Gradle have no entry (FR-34).
- Returns: the runner whose `match` hits the command's own words (`pytest`, `python -m pytest`, `python -m unittest`, `jest`, `npx jest`, `vitest`, `mocha`, `go test`, `cargo test`, `rspec`, `bundle exec rspec`), else `None`; a wrapper such as `npm test` or `bash run.sh` names no runner and reads as unknown
- Rules: "accept red only when it exits non-zero and its output matches none of the known collection, import or syntax error patterns of that command's test runner, nor that runner's report that no tests ran" (FR-8); "IF the command's test runner is not on the known list THEN THE SYSTEM SHALL decide red on the exit code alone and note the unknown runner in the history line" (FR-9)
- Rules: the spec's decision table Red, row by row

### CT-3 Read a full-suite run (FR-14, FR-16, FR-17, FR-36) [default]
- Binding: `src/nio/implement.py:suite` (new)
- Like: `src/nio/tasks.py:parse`
- Kind: function
- Shape: `suite(root, cfg) -> {"command", "code", "cause", "runner", "failing": [names] | None, "collected": int | None, "broken": bool, "output_hash"}`
- Accepts: `tests.suite` from the config (FR-35); the limit as in CT-1
- Returns:
  - for a known runner, the failing test names and the collected count, read from its summary lines; for example pytest's `FAILED <id>` and `collected N items`, or unittest's `FAIL: <name>` / `ERROR: <name>` and `Ran N tests`;
  - `broken` when the output shows a collection or import error marker (CT-2) or `cause` is set;
  - for an unknown runner, `failing` and `collected` are `None`.
- Rules: "the full test suite with no failure missing from the baseline, no collection or import error, and no fewer tests than the baseline collected" (FR-14)
- Rules: the review compares by name (`failing` minus the baseline's) and by count (`collected` against the baseline's); for an unknown runner, a non-zero `code` is a new failure (FR-36)

### CT-4 Task status and the next ready task (FR-1, FR-3, FR-18, FR-31, FR-39, FR-40) [default]
- Binding: `src/nio/implement.py:status` (new)
- Like: `src/nio/flow.py:where`
- Kind: function
- Shape: `tasks_of(root, slug) -> [task]`, in epic order then file order, each with `id, title, epic, fix, deps, files, serves, tests, tier, effort, mode`; `status(root, slug, lines) -> {T-n: state}`; `next_ready(root, slug, lines) -> task | None`
- Accepts: `tasks.md` read with `tasks.parse` (RF-15); the history lines from `flow.load`
- Returns:
  - `status` replays the task lines (`claim`, `red`, `green`, `review`, `refused`, `task_done`, `blocked`, `unblock`) through the spec's state table Task. A task with no line is `ready` when every `Depends on:` task is `done`, else `pending`.
  - `next_ready` is the first `ready` task of the first epic that has a task not `done`, fix tasks included (FR-31). With none ready, it is `None`.
  - `mode` is `implement.mode` from the config when set, else the task's `Mode:` value, else `split` (FR-40, C-261029-nbrg).
- Rules: "THE SYSTEM SHALL derive each task's status from history lines and keep in `state.json` only the current claim and the attempt count" (FR-18)
- Rules: every task line is written through `flow.record` with `from` and `to` both `implementing`, and its own fields under `evidence`: `evidence.task` (`T-n`), plus each line's fields named in architecture.md (`command`, `runner`, `frozen`, `failing`, `collected`, `outside`, `cause`). `record` keeps `evidence` whole, so nothing is dropped and `last_to` still reads `implementing` [agent]
- Rules: a task whose block changed after its `task_done` line comes back under the next free T-n in the re-approved `tasks.md`; the old ID stays `done`, since `status` reads it from its own lines (FR-39)
- State: follows the spec's state table Task

### CT-5 Claim the next task (FR-1, FR-2, FR-3, FR-6, FR-7, FR-16, FR-20, FR-22, FR-35, FR-36, FR-40, FR-46) [default]
- Binding: `src/nio/implement.py:claim` (new)
- Like: `src/nio/flow.py:done`
- Kind: cli
- Shape: `nio flow claim [<slug>] --by "<role> / <host> / <model>"` prints `task: T-n <title>`, `mode: <split|single|direct>`, `card: nio-worker-<tier>`, `effort: <effort>`, `pack: .nio/runs/<run>/packs/T-n.md`, exit 0
- Accepts: an effort at `implementing`, under `flow.lock`
- Fails, in this order, each with a non-zero exit, the message below, and nothing recorded:
  - no `nio: approve tasks` commit for the effort → `error: tasks not approved: no "nio: approve tasks" commit` (FR-2)
  - the current branch isn't `nio/<slug>` and the stage has started → `error: on <branch>, not nio/<slug>` (FR-20)
  - uncommitted changes outside `.nio/specs/<slug>/` → `error: uncommitted changes outside the effort folder:` and one line per file (FR-22)
  - a claim already in `state.json` → `error: T-<n> is claimed` (FR-3)
  - no ready task and some task not done → `error: no ready task; T-<n> waits on T-<m>` (FR-3)
- Rules: the first claim of the stage, when no `baseline` line exists, starts the stage in this order:
  1. creates or switches to `nio/<slug>` (FR-20);
  2. with no `tests.suite`, sets `waiting` to `{"why": "tests.suite not set"}` and stops (FR-35);
  3. runs the suite (CT-3). When it is `broken` (a collection or import error, a time limit or a missing program), it sets `waiting` to `{"why": "the suite is broken before the first task: <error>"}`, writes no `baseline` line and stops (FR-46, C-261029-kubi). When the runner is unknown and the exit is non-zero, it sets `waiting` to `{"why": "the baseline fails and its runner is unknown"}`, writes no `baseline` line and stops (FR-36);
  4. otherwise writes the `baseline` line holding its command, exit code, failing names, collected count and runner (FR-16).
  With no `baseline` line, the next claim starts the stage again, so a fixed suite is run afresh. [agent]
- Rules: on success, writes a `claim` line and `claims: {"task": "T-n"}`, writes the worker pack (CT-6), and names the card for the task's tier and its effort (FR-6, FR-7)

### CT-6 The worker pack (FR-4) [default]
- Binding: `src/nio/implement.py:worker_pack` (new)
- Like: `src/nio/pack.py:build`
- Kind: function
- Shape: `worker_pack(root, slug, task) -> text`, saved to `.nio/runs/<run>/packs/T-n.md`
- Returns: exactly these five parts, each under its own `## ` heading, in this order:
  1. `nio pack "<task title>" --task T-n --path <each Files: entry> --ac <each Serves: AC>`, via `pack.build` with a new optional `worker=False`, which leaves out its closing instructions to the worker (they name `@nio:remember`, which the worker card replaces with the blocked handoff); its own `## ` headings are nested one level down;
  2. the task's section from `tasks.show`;
  3. each served AC's text from `spec.md`, with its Observable line;
  4. each CT-n block the task's TC-n entries cover, from `contracts.md`;
  5. each TC-n entry named in its `Test:` line, from `tests.md`.
- Rules: the mode and the handoff format are not in the pack: `claim` prints the mode, and the worker card carries the handoff format for each mode (CT-15) [agent]
- Rules: "the text of each AC it serves from `spec.md`; the CT-n blocks it binds from `contracts.md`; and the TC-n entries it must make pass from `tests.md`" (FR-4)

### CT-7 Red (FR-8, FR-9, FR-10, FR-11, FR-32, FR-37, FR-41, FR-42, FR-43, FR-44) [default]
- Binding: `src/nio/implement.py:red` (new)
- Like: `src/nio/flow.py:done`
- Kind: cli
- Shape: `nio flow red <slug> T-n --run "<command>" --by "<role> / <host> / <model>"` prints `red: T-n accepted` plus `frozen:` and one line per frozen file, exit 0; or a refusal, exit 1
- Accepts: a task in state `claimed` or `red` (FR-11), in split or single mode. The caller is the orchestrator, or in single mode the worker (FR-42).
- Fails, each refusal as below:
  - the state table forbids it → `error: T-n is <state>` and nothing recorded (FR-32);
  - direct mode → `error: T-n is in direct mode: no red` and nothing recorded (FR-41).
  - The following are guard refusals: each writes a `refused` line and adds 1 to `attempts["T-n"]` (FR-37).
    - the command names no test file from the task's TC-n `File:` entries → `refused: the command doesn't name <file>` (FR-43);
    - exit 0 → `refused: the test passes before the code exists`;
    - `wrong_reason` (CT-2) → `refused: <reason>`;
    - a time limit or a missing program (CT-1) → `refused: <cause>`.
- Rules: on acceptance, writes a `red` line with the command, `output` hash, `runner` (`unknown` when CT-2 finds none, FR-9) and `frozen: {path: sha256}`.
  - At the first red, `frozen` is every file changed between the claim and now, outside `.nio/specs/<slug>/`, read from `git status --porcelain` and the diff against the claim's commit (FR-10).
  - A later red re-hashes the same paths and adds none (FR-11).
- Rules: `attempts` reaching 3 → CT-12

### CT-8 Green and review (FR-12, FR-13, FR-14, FR-15, FR-17, FR-25, FR-32, FR-33, FR-37, FR-41, FR-45, NFR-1) [default]
- Binding: `src/nio/implement.py:green` (new)
- Like: `src/nio/flow.py:done`
- Kind: cli
- Shape: `nio flow green <slug> T-n [--run "<command>"] --by "<role> / <host> / <model>"` prints `green: T-n accepted`, then the review's result, then `done: T-n <sha>` or the failure, exit 0 only when the task is done
- Accepts:
  - a `red` task in split or single mode: `--run` is optional and, when given, must equal the command on its red line (FR-12);
  - a `claimed` task in direct mode: `--run` is required (FR-41).
- Fails:
  - `--run` differs from the red command → `refused: the command recorded at red is <command>`, a `refused` line and an attempt (FR-12);
  - a frozen file's hash differs → `refused: <path> changed since red; prove red again` and an attempt (FR-13);
  - the command exits non-zero, or CT-1 gives a cause → a `refused` line and an attempt;
  - a claimed task in split or single mode → `error: T-n has no failing test first`, nothing recorded (FR-41);
  - any state the table forbids → `error: T-n is <state>` (FR-32).
- Rules: on an accepted green, writes a `green` line, then runs `review` at once with no model call (FR-14). The review checks in the order of the spec's decision table Review:
  1. any change to `spec.md`, `tasks.md` or a plan-stage file (`plan.md`, `contracts.md`, `tests.md`, `quickstart.md`, `architecture.md`) of the effort fails it (FR-25);
  2. a frozen file changed fails it;
  3. the suite (CT-3) with a failing name missing from the baseline, `broken`, a smaller `collected`, or for an unknown runner a non-zero exit, fails it, naming each (FR-14, FR-17, FR-36).
- Rules: a passed review writes a `review` line listing the changed files outside the task's `Files:` (FR-15), then commits (CT-9). A failed review writes a `review` line with its reasons, adds an attempt, and leaves the task `red`, or `claimed` in direct mode (FR-45).
- Rules: green on a `green` task (one whose commit failed, CT-9) runs no guard; it re-runs the review and the commit, so the task leaves `green` through the table's `review passes` or `review fails` [agent]
- Rules: a changed file counts as outside the task's list when it is in neither `Files:` nor the red line's `frozen` (FR-15) [agent]
- Rules: status is never read from a handoff; the CLI reads only its own lines and files (FR-33)

### CT-9 Commit a done task (FR-19, FR-20, FR-21) [default]
- Binding: `src/nio/implement.py:commit` (new)
- Like: `src/nio/flow.py:commit_gate`
- Kind: function
- Shape: `commit(root, slug, task, who) -> sha`
- Rules: in this order:
  1. refuses unless the branch is `nio/<slug>` (FR-20);
  2. writes the `task_done` line and clears `claims`;
  3. stages the task's changes and the effort's `history.jsonl` and `state.json`;
  4. commits `T-n: <title>` through `records.git(..., full=True)`.
- Fails: a non-zero `git commit` → as `flow.commit_gate` does, writes back the bytes of `history.jsonl` and `state.json` kept in memory before step 2 and `read-tree`s the tree saved by `write-tree` before step 3, so no `task_done` line is left and nothing is staged; then writes a `fail` line with git's stderr and sets `waiting` to `{"why": "commit failed: <first stderr line>", "task": "T-n"}`. The task stays `green` (FR-19). [agent]
- Rules: "THE SYSTEM SHALL never merge the effort branch; the human merges it" (FR-21): no merge, rebase or push is ever run

### CT-10 Attempts and the cap (FR-26, FR-37) [default]
- Binding: `src/nio/implement.py:attempt` (new)
- Like: `src/nio/flow.py:stop_line`
- Kind: function
- Shape: `attempt(root, slug, state, task, reason) -> entries`, the lines to write with the refusal or failed review
- Rules: "THE SYSTEM SHALL count one attempt for the claimed task each time its guard refuses red or green and each time its review fails; a task blocked by a spec problem uses no attempt" (FR-37)
- Rules: when `attempts["T-n"]` reaches 3, saves the task's uncommitted changes outside the effort folder (`git diff HEAD` plus untracked files) as `.nio/runs/<run>/T-n.patch`, restores a clean tree, writes a `blocked` line (`cause: attempts`, `evidence.patch`), clears `claims`, and sets `waiting` to `{"why": "T-n blocked after 3 attempts", "task": "T-n"}`. This applies with the auto flag on or off (FR-26).

### CT-11 Block on a spec problem (FR-23, FR-24) [default]
- Binding: `src/nio/implement.py:block` (new)
- Like: `src/nio/records.py:new`
- Kind: cli
- Shape: `nio flow block <slug> T-n --handoff <file> --by "<role> / <host> / <model>"`; the handoff file is markdown with front matter:
  - `status: red-ready | done | blocked`;
  - `command: "<test command>"` (red-ready and done);
  - `change_request:` with `spec_says`, `code_shows` and `smallest_change` (blocked).
- Accepts: a handoff with `status: blocked` and all three `change_request` parts, for the claimed task
- Fails: another status, or a missing part → `error: handoff is not blocked with a change_request` and nothing recorded
- Rules: computes the handoff's sha256 and writes it into the change record's body as `Handoff: <sha256>`. When a pending change record under `.nio/memory/` already holds that line, it is reused: no second record is made, its `C-` ID is printed, and only the steps not yet done (the `blocked` line, `waiting`) are written (AC-48). Otherwise:
  1. creates a change record (`records.new`, `outcome: pending`, `against` the effort's `spec.md`) holding the three parts;
  2. saves the task's uncommitted changes as `.nio/runs/<run>/T-n.patch` and restores a clean tree, as CT-10 does; writes a `blocked` line (`cause: spec`, `change`, `handoff` hash, `evidence.patch`) and clears `claims`;
  3. sets `waiting` to `{"why": "spec problem in T-n", "task": "T-n", "change": "C-..."}` (FR-24).
- Rules: uses no attempt (FR-37)

### CT-12 Unblock (FR-38) [default]
- Binding: `src/nio/implement.py:unblock` (new)
- Like: `src/nio/flow.py:done`
- Kind: cli
- Shape: `nio flow unblock <slug> T-n --human "<reason>" --by human` prints `unblocked: T-n`, exit 0
- Fails: a task that isn't blocked → `error: T-n is <state>`; an empty reason → `error: --human needs a reason`
- Rules: "set the task ready, reset its attempt count to 0 and drop its frozen files, so its next claim starts at the test phase" (FR-38). It writes an `unblock` line with the reason, removes `attempts["T-n"]`, and clears `waiting` when `waiting["task"]` is this task.

### CT-13 Finish an epic and the effort (FR-27, FR-28, FR-29, FR-30, FR-31) [default]
- Binding: `src/nio/implement.py:epic_end` (new)
- Like: `src/nio/flow.py:moves`
- Kind: function
- Shape: `epic_end(root, slug, task, review) -> (entries, report)`, called by `commit` after each `task_done`
- Rules: when every task of the task's epic, fix tasks included, is `done`, and the review just run found no new failure (FR-27):
  1. writes an `epic` line `skipped: not built` for that epic (FR-28);
  2. prints the epic report: one line per done task with its commit, the files outside each task's list, and the baseline failures still failing (FR-29);
  3. prints `notify: the human` with the epic's ID, for the orchestrator to pass on (FR-28, research RF-3).
- Rules: after the last epic, it writes a `pass` line `implementing → done`, so `nio flow next` and `nio flow status` say `done` (FR-30), and prints `merge: nio/<slug>` for the human (FR-21, AC-28)

### CT-14 The implementing stage in `nio flow` (FR-27, FR-30) [default]
- Binding: `src/nio/flow.py:guard` (existing)
- Kind: function
- Shape: `guard(root, slug, "implementing")` as for every stage; `where`, `SKILL`, `INPUTS` and `EXIT` in `src/nio/flow.py` gain the implementing entries below
- Rules:
  - `guard` at `implementing` passes when every task is `done` and every epic has its `epic` line, and otherwise fails, listing what's left.
  - `where` reports `waiting_for_human: <why>` from `state["waiting"]` as for other stages. When `waiting` names a `task`, its command is the one that clears it: `nio flow unblock <slug> T-n --human "<reason>" --by human` for a blocked task, after the change record is decided when `waiting` has a `change`; `nio flow green <slug> T-n --by human` after a failed commit. `talk` gets the matching rows. [agent] Otherwise it reports `working`, with `skill: @nio:implement`, `inputs: tasks.md` and the next ready task.
  - The "implement not built" text goes.
- Rules: the tests `test_guards_pass_and_implementing_never_does` and `test_ac23_implement_not_built` in `tests/test_flow.py` change to the built stage. The three tests waiting on #43 there become this spec's task-refusal tests (research RF-20).

### CT-15 The worker cards (FR-5, FR-6, FR-23, FR-42) [default]
- Binding: `src/nio/agents/worker.md` (new)
- Like: `src/nio/agents/tasks-drafter.md`
- Kind: file
- Shape: frontmatter `name: worker`, `description`, `tier: all`, `effort: med`, `tools: [read, edit, shell]`; the body has the card sections `Job`, `Inputs`, `Output format`, `Stop when`
- Rules: the body tells the worker, by mode:
  - split: in the test phase, write the planned test and hand off `status: red-ready` with the command; in the code phase, write the code and hand off `status: done`;
  - single: write the test, run `nio flow red`, write the code, run `nio flow green`;
  - direct: write the code and hand off `status: done` with the command.
- Rules: the body also tells the worker to stop on a spec problem and hand off `status: blocked` with a `change_request:` holding its three parts, and never to edit `spec.md`, the plan files or `tasks.md` (FR-23). It may never edit `state.json` or `history.jsonl`, and may run no `nio flow` command other than `red` and `green` on its own task in single mode (FR-5, C-261029-rmbs).
- Rules: `sync` renders a card with `tier: all` once per tier in `agents.ORDER`, as `nio-worker-<tier>`, each with the model `resolve` gives that tier on the host (FR-6, D-261029-ti54). Every other card is unchanged.

### CT-16 The task's Mode (FR-40) [default]
- Binding: `src/nio/tasks.py:check` (existing)
- Kind: function
- Shape: `Mode: <split|single|direct>: <reason>` in each task of `tasks.md`; `tasks.FIELDS`, `src/nio/templates/tasks.md` and `src/nio/agents/evaluator.md` change with it
- Rules: `Mode` joins `FIELDS`. On a `tasks.md` whose `nio: approve tasks` commit's committer date is before `tasks.MODE_SINCE` (a constant set to the date this ships), a missing `Mode:` is allowed and the task runs in `split` (C-261029-nbrg). Otherwise `nio check tasks` rejects a missing value, one outside `split`, `single` and `direct`, or one without a reason, as it does for `Tier:`. The template shows the line, and the evaluator rates it with a reason next to `Tier:` and `Effort:` (C-261029-4cev).

### CT-17 The `@nio:implement` skill (FR-5, FR-24, FR-28, FR-40) [default]
- Binding: `skills/implement/SKILL.md` (new)
- Like: `skills/tasks/SKILL.md`
- Kind: file
- Shape: a skill folder like the others: name and description frontmatter, then inputs, outputs, steps and when to stop
- Rules: the orchestrator's steps:
  1. `nio flow claim`;
  2. start the named card on the pack, by mode: split runs the test phase, then reports red from the `red-ready` handoff's command, then a fresh code phase, then reports green; single runs one worker that reports its own red and green; direct runs one worker, then reports green with the handoff's command;
  3. on a `blocked` handoff, `nio flow block`;
  4. pass every `notify:` and `waiting` on to the human.
- Rules: it carries the "Talking to the human" block word for word, and the flow-state line with its single-mode exception (`tests/test_talk.py`)

## Data model
- **Baseline** (spec Key entity) in `src/nio/implement.py:claim` (new): a `baseline` history line with `command`, `code`, `runner`, `failing`, `collected`. "the tests failing before the first task of the effort, recorded on a history line" (FR-16) [default]
- **Frozen test file** (spec Key entity) in `src/nio/implement.py:red` (new): the `red` line's `frozen: {path: sha256}` (FR-10) [default]
- **Attempt** (spec Key entity) in `src/nio/implement.py:attempt` (new): `state.json` key `attempts`, `{"T-n": int}`, already reserved (FR-37) [default]
- **Handoff** (spec Key entity) in `src/nio/implement.py:block` (new): the file `--handoff` names, in the format of CT-11 (FR-24) [default]
- **Effort branch** (spec Key entity) in `src/nio/implement.py:commit` (new): the git branch `nio/<slug>` (FR-20) [default]
- **Epic report** (spec Key entity) in `src/nio/implement.py:epic_end` (new): printed, not stored (FR-29) [default]
- **Worker pack** (spec Key entity) in `src/nio/implement.py:worker_pack` (new): `.nio/runs/<run>/packs/T-n.md` (FR-4) [default]
