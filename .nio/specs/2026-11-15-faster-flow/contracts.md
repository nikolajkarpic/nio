---
slug: 2026-11-15-faster-flow
retired: []                      # CT IDs removed from this plan; never reused
---
# Contracts: Faster flow

`#122` below is the approved spec at `/home/work/nio-auto/.nio/specs/2026-11-08-full-auto-run/`; its contracts are
reused where this file says so, never restated. Its built code (branch `nio/2026-11-08-full-auto-run`) is carried
over by CT-34.

## Contracts

### CT-1 Claim a whole epic (FR-1, FR-2, FR-9, FR-43, FR-44, NFR-2) [agent]
- Binding: `src/nio/implement.py:claim` (existing)
- Kind: cli
- Shape: `nio flow claim [<slug>] [E-n] --by "<role> / <host> / <model>"` → `claim(root, slug, by, epic=None)`. Picks the first epic, in file order, that is `waiting` or `failed` and whose tasks' dependencies outside the epic are all done (FR-1), or the named one; a dependency between two tasks of the same epic never holds the claim, since one agent builds both. Writes one `claim` line `{"epic": "E-n", "tasks": [undone T-IDs], "commit": HEAD, "run", "plans": {plan file: sha256}[, "worktree"]}` and `claims` `{"epics": {"E-n": {"run", ["worktree"]}}}`. Prints `epic: E-n <heading>`, `tasks: T-a, T-b`, `card: nio-worker-<epic tier>`, `effort: <epic effort>`, `pack: <path>`, `then: nio flow finish <slug> E-n --by "<...>"`, plus `worktree: <path>` when another epic's work holds the main tree (FR-43): one claimed there, or a failed or blocked one whose last claim worked there. A failed epic is claimed again where its work is: its own worktree, or the main tree; a converted epic keeps its old wave worktrees until it closes. The pack is `implement.worker_pack` widened to the epic: its undone tasks, the ACs and contracts they cite, the TCs they name, and, after a failed run, CT-2's failing tests and output tail (FR-42).
- Accepts: an effort at implementing with a `nio: approve tasks` commit; a second epic only while no task of it depends on a task of a claimed one, up to `budgets.parallel` (default 2).
- Returns: `(0, lines)`.
- Fails: named epic claimed → `E-n is claimed` (non-zero, state unchanged); no epic ready → `no epic left: every epic is closed` or `no epic ready; E-3 waits on E-2`; `blocked` epic → `E-n is blocked: nio flow unblock <slug> E-n --human "<reason>" --by human`; the existing guards (branch, dirty tree, approve commit) as today.
- Rules: "one agent per epic, not one for the whole effort" (FR-1). An epic whose tasks are all done and that has no passing CT-2 run enters at `testing`: the claim prints `epic: E-n (every task done: run its tests)` and the `then:` line, and the pack lists no task (FR-44). An old `claims.task` or `claims.wave` is read as the claim of its epic: the claim prints that epic as already claimed, with its run and any old wave worktrees, and CT-2 lands each such worktree before it runs (FR-44).
- State: follows the spec's state table "Epic" (waiting → claimed, failed → claimed)

### CT-2 Hand an epic back and run its tests (FR-3, FR-4, FR-6, FR-10, FR-42, FR-44, NFR-1) [agent]
- Binding: `src/nio/implement.py:finish` (new)
- Like: `src/nio/implement.py:green`
- Kind: cli
- Shape: `nio flow finish <slug> E-n --by "<...>"`, wrapped in `cli.long` so `running.json` names it while it runs. The command is the flow's own, never the agent's (FR-3): the epic's TCs joined through `evidence.one_test`, else (a fix epic, a lite spec, a runner it can't address) the configured `tests.suite`. Before the run: when the epic (or an old wave task of it) has a worktree, its changes since the commit that worktree was made from are landed on the main tree with the existing `land()` (refused when they touch a path with uncommitted changes there, another epic's work), and put back with `restore()` on a fail, a refusal or an interrupted run; a change to spec.md, the plan files or tasks.md is refused as today's `review` refuses it (`review`'s plan-file check moves here; its frozen-file check goes); a second `finish` while `running.json` names one for this epic → `E-n's tests are running` (state `testing`). It runs once (NFR-1) on the main tree with `EPIC_LIMIT = 1800` seconds. Pass: one `epic_test` line `{"epic", "command", "passed": true, "runner"}`, then one commit `E-n: <heading>` holding the files CT-3 picks, with one `task_done` line per undone task; the last epic also writes `pass` implementing → pr as today. No jury runs and no `implementation-E-n` ledger is made (FR-6); `open_gate` stays only for an epic already in its old jury. Fail: one `epic_test` line `{"epic", "command", "passed": false, "cause", "failing": [names], "tail": <last 50 lines>}`, `attempts["E-n"] += 1`, the claim released; at the 3rd failed run a `blocked` line `{"epic", "cause": "runs"}` and `waiting` `E-n blocked after 3 failed test runs`.
- Accepts: a claimed epic (or one at `testing`, FR-44) of the caller's effort.
- Returns: pass → `(0, ["closed: E-n <sha>", ...])`; fail → `(1, ["E-n failed (run n of 3): <cause>", "failing: …", *tail])`.
- Fails: the epic's tasks name no test (no TC on a full spec; no `Test:` other than `none` on a lite spec or a fix epic) → `E-n has no test to run` (non-zero, nothing run or written, FR-10); epic not claimed → `E-n is not claimed`. A run that exits non-zero, matches a runner's collection error, collects no test (`implement.wrong_reason`), or hits the limit is a failed run (FR-4).
- Rules: "the agent's report never counts" (FR-3); "record the failing tests and the last 50 lines of the run's output, and count it as one failed run toward FR-42's 3" (FR-4).
- State: follows the spec's state table "Epic" (claimed → testing → closed | failed | blocked)

### CT-3 The epic's commit leaves other paths out (FR-11) [agent]
- Binding: `src/nio/implement.py:commit` (existing)
- Kind: function
- Shape: `commit(root, slug, epic, ...)` stages the changed paths, tracked or untracked, that the epic's tasks list under `Files:` or that sit under a listed folder, the test files its TCs' `File:` lines name (`implement.test_files`), or for a worktree epic the paths it landed, and `history.jsonl` and `state.json`; nothing else: another epic's work and the human's edits stay uncommitted.
- Fails: as today (a git error rolls back and waits for the human).
- Rules: "commit only the epic's files and the flow files, leaving other untracked paths out" (FR-11).

### CT-4 Epic state from history, unblock and the auto refusal (FR-42, FR-47, FR-44) [agent]
- Binding: `src/nio/implement.py:unblock` (existing)
- Kind: cli
- Shape: `implement.status` gains the epic view `epics(root, slug) -> {E-n: (state, failed_runs)}` read from `claim`, `epic_test`, `blocked`, `unblock` and `task_done` lines; closed = every task done and a passing `epic_test` after its last claim (FR-44's done epics with no run read `testing`). `nio flow unblock <slug> E-n --human "<reason>" --by` writes `unblock` `{"epic", "reason"}`, drops `attempts["E-n"]`, clears `waiting` → `waiting` state.
- Fails: epic not blocked → `E-n is not blocked`; under auto, `--by` other than `human` on an epic blocked with `cause: runs` → `(1, ["E-n was blocked by its own 3 failed test runs; only the human unblocks it"])`, nothing written, the effort stays waiting (FR-47).
- Rules: an agent that hands back `blocked` (a spec problem) is reported with the existing `nio flow block <slug> T-n --handoff <file>`: it files the change request, blocks that task and the effort waits for the human; the epic stays `claimed` with its claim kept. After `nio flow unblock <slug> T-n`, a fresh driver's `nio flow brief` prints the claimed epic's `pack:` and `then:` lines again, and a fresh agent resumes it on that claim; no re-claim is needed. That is a task block, not the epic's `blocked` state.
- State: follows the spec's state table "Epic" (blocked → waiting)

### CT-5 No red, green or task modes (FR-5) [human]
- Binding: `src/nio/cli.py` (existing)
- Kind: cli
- Shape: the `nio flow red` and `nio flow green` subparsers and `implement.red`, `implement.green`, `review`'s frozen-file check and `MODES` are removed; `tasks.FIELDS` drops `Mode`, and a `Mode:` line left in an old tasks.md is ignored, not an error.
- Rules: "`nio flow red` and `nio flow green` no longer gate a task, and task modes (split, single, direct) and the tests-frozen-at-red rule are gone" (FR-5).

### CT-6 Tier per epic, tasks keep their map (FR-7) [human]
- Binding: `src/nio/tasks.py:check` (existing)
- Kind: function
- Shape: each `## E-n` carries `- Tier: <cheap|strong|max|frontier>: <why>` and `- Effort: <low|med|high>` before its first task; `FIELDS` becomes `Files, Serves, Test, Depends on, Parallel`. Errors: `E-n: needs \`- Tier:\``; the existing `T-n serves no AC` and `T-n: on a full spec \`Test:\` cites the plan's \`TC-n\`` stay. The `E-n: needs` check applies only to a tasks.md whose `nio: approve tasks` commit is after the change (`TIER_SINCE`, as `MODE_SINCE` exempts `Mode` today); an epic with no Tier line, approved before it, takes the highest tier and effort of its tasks. `src/nio/templates/tasks.md`, `src/nio/agents/evaluator.md` and `src/nio/agents/tasks-drafter.md` rate and write the tier per epic; `one_fix` writes no Tier, Effort or Mode on the task, and when it opens a new `## E-n PR fixes` epic writes `- Tier: strong: fixes from the pr jury` and `- Effort: med` under it.

### CT-7 A task can't depend on a later epic (FR-12) [human]
- Binding: `src/nio/tasks.py:check` (existing)
- Kind: function
- Shape: for each `Depends on` ID in a later epic than the task: `T-10 (E-5) depends on T-11 (E-6), a later epic`.

### CT-8 The implement skill per epic (FR-8, FR-18, FR-42, FR-43) [human]
- Binding: `skills/implement/SKILL.md` (existing)
- Kind: file
- Shape: Steps: claim (CT-1); start one fresh agent of the printed card on the pack (a second claimed epic gets its own agent in its worktree); on its `done` hand-off run the `then:` command; on a failed run, claim again (a fresh agent gets the failure in its pack); on `blocked`, stop for the human. No red, green, mode, test writer or builder. The "Drivers and waiting" main-session text allows one driver per claimed epic at once, instead of "never two at once", and keeps every other sentence `tests/test_talk.py` pins. Its "Waiting for long work" list, here and in `skills/jury/SKILL.md`, names `nio flow finish` in place of `nio flow green`.

### CT-9 The worker card per epic (FR-2, FR-5) [agent]
- Binding: `src/nio/agents/worker.md` (existing)
- Kind: file
- Shape: Job: implement every task of the epic in the pack, tests and code, in task order; hand back `status: done` with `command:` the one command that runs the epic's tests (the driver passes it as `--run` when the `then:` line asks for it), or `blocked` with a change request. No split, single or direct, no `red-ready`, no `nio flow red`/`green`.

### CT-10 NORTH_STAR's Implement section (FR-8) [human]
- Binding: `NORTH_STAR.md` (existing)
- Kind: file
- Shape: "### Implement" says: one agent per epic implements its tasks' tests and code; `nio flow` runs the epic's named tests and closes it only if they pass; independent epics run in parallel; the pr gate's jury reviews the whole effort diff. It names no TDD, test writer or builder.

### CT-11 The background mod's long commands (FR-13) [research: RF-31]
- Binding: `tools/claude-mods/background-nio-commands/hooks/register.ts:LONG_NIO` (existing)
- Kind: config
- Shape: `/^(?:uv\s+run\s+)?nio\s+(?:jury\s+evidence|flow\s+finish)(?:\s|$)/`; the suite match stays; README and `register.test.ts` list `nio jury evidence` and `nio flow finish`, and no `nio jury run` or `nio flow green`.

### CT-12 The mod on through install (FR-14) [agent]
- Binding: `skills/install/SKILL.md` (existing)
- Kind: file
- Shape: the mods step #142 adds (`nio mods install`, local scope, RF-32) is what turns the mod on; this effort adds nothing to it. This branch merges `main` once #142 has landed, before US-3 is built.

### CT-13 Say when the mod is off (FR-15) [agent]
- Binding: `src/nio/flow.py:brief` (existing)
- Kind: function
- Shape: when `CLAUDECODE` is set and neither `.claude/settings.local.json` nor `.claude/settings.json` has `enabledPlugins["background-nio-commands@nio-mods"]` true, and `CLAUDE_CODE_PLUGIN_DIRS` names no `background-nio-commands`, the brief's first line is `warning: the background mod is off, so long commands block this session: run nio mods install (ignore if you loaded it with --plugin-dir)`. Elsewhere nothing.

### CT-14 Grounding ignores a trailing source note (FR-23) [agent]
- Binding: `src/nio/jury.py:unquote` (existing)
- Kind: function
- Shape: before stripping the quote marks, a trailing `\s*\([^()]*,\s*[A-Z]+-\d+\)$` after the closing `"` is cut.

### CT-15 A lens with every finding ungrounded is re-run (FR-24) [agent]
- Binding: `src/nio/jury.py:collect` (existing)
- Kind: function
- Shape: a juror output with one or more findings, each dropped `ungrounded`, is stored `valid: false` with `errors: ["every finding is ungrounded"]`; `compose` then reads it as a lens to re-run (`retry`, `stuck` after 2), never `approved`.

### CT-16 The human's ruling reopens a dropped finding (FR-25) [agent]
- Binding: `src/nio/jury.py:_dispose_one` (existing)
- Kind: cli
- Shape: `nio jury dispose <slug> <gate> J-n reopen --by human --note "<ruling>"`: only on a `dropped` finding; sets `status: open`, `validation: pending`, `ruling: <note>`.
- Fails: `reopen` on any other status → `J-n is <status>; reopen takes a dropped finding`; `--by` not human → `reopen is the human's call (--by human)`.

### CT-17 Escalation jurors vote, they don't add findings (FR-26) [agent]
- Binding: `src/nio/jury.py:add` (existing)
- Kind: function
- Shape: from a `<gate>-<lens>-2.md`/`-3.md` output collected while a blocker of that lens is escalated, a finding that is `same` as the blocker votes on it (sources appended, as today); any other finding goes to the ledger's `notes` as `{"juror", "title", "round"}` and gets no J- ID.

### CT-18 Each refuter pass keeps its own file (FR-27) [agent]
- Binding: `src/nio/jury.py:step` (existing)
- Kind: function
- Shape: the n-th refuter batch of a run is written to `packs/refuter-<n>.md` and asks for `<gate>-refuter-<n>.md`; `collect` reads the file of the batch it asked for. n is the count of batches asked in that run.

### CT-19 A merge that raises severity keeps the confirmation (FR-28) [agent]
- Binding: `src/nio/jury.py:refute` (existing)
- Kind: function
- Shape: on `same-as`, a target already `confirmed` stays `confirmed` when `worst()` raises its severity; only a `grounded`/`pending` target goes back to `pending`. No refuter batch lists it again.

### CT-20 The fix check compares with the version the finding was raised on (FR-29) [agent]
- Binding: `src/nio/jury.py:compose` (existing)
- Kind: function
- Shape: "fix without a change" compares `version(led, f["first_round"])` with the current version, instead of `version(led, f["last_round"])`.

### CT-21 Plan items are whole `### <ID>` blocks (FR-30) [agent]
- Binding: `src/nio/jury.py:parts` (existing)
- Kind: function
- Shape: an item started by `### <ID>` runs to the next `### ` or `## ` heading, its `- ` lines included, so `changed` and `fixcheck` name `CT-1` and `TC-n`, not the section.

### CT-22 Root mismatch warning (FR-33) [agent]
- Binding: `src/nio/jury.py:step` (existing)
- Kind: function
- Shape: after `agents.sync(root)`, when `CLAUDE_PROJECT_DIR` is set and resolves to another path than `root`: `warning: agents were rendered into <root>, but this session loads them from <CLAUDE_PROJECT_DIR>; start the session in <root>`.

### CT-23 The index is replaced in one step, and a missing record is skipped (FR-31) [agent]
- Binding: `src/nio/index.py:build` (existing)
- Kind: function
- Shape: `build` copies `index.db` to `index.db.new` (when it exists), rebuilds the copy, and `os.replace`s it over `index.db`; `pack.build` skips a full-tier record whose file is gone (no `IndexError`).

### CT-24 A failed claim leaves no worktree (FR-32) [agent]
- Binding: `src/nio/implement.py:claim` (existing)
- Kind: function
- Shape: every step after the first `git worktree add` runs in a `try`; on any exception each worktree this call made is removed (`git worktree remove --force`) before the error is re-raised.

### CT-25 The hand-off names the skill file (FR-34) [agent]
- Binding: `src/nio/flow.py:typed` (existing)
- Kind: function
- Shape: `typed("@nio:<stage>")` → `/nio:<stage> (skills/<stage>/SKILL.md)` under `CLAUDECODE`, else `the nio:<stage> skill (skills/<stage>/SKILL.md)`.

### CT-26 Fix tasks around a retired one (FR-35, FR-36) [research: RF-28]
- Binding: `src/nio/tasks.py:retire` (existing)
- Kind: function
- Shape: unchanged: a retired fix ID stays in `retired:`, the other fix tasks keep their IDs (`check_fixes`), and the tasks gate stays approved. Tests guard it.

### CT-27 An existing passing test is an AC's evidence (FR-37) [agent]
- Binding: `src/nio/evidence.py:join` (existing)
- Kind: function
- Shape: a tests.md entry whose `File:` is marked `(existing)` and whose test passed in the gate's suite run counts as its AC's evidence, whether or not the diff touches the file; no `has no passing evidence` finding is raised for that AC.

### CT-28 A change request the flow writes passes `nio check` (FR-38) [agent]
- Binding: `src/nio/jury.py:raise_change` (existing)
- Kind: function
- Shape: unchanged shape (`records.new(root, "change", …)`); the record and `implement.block`'s both lint clean under `records.lint`. A test guards it.

### CT-29 A pr finding rooted in the spec or plan asks for a change, not a fix task (FR-39) [agent]
- Binding: `src/nio/jury.py:to_task` (existing)
- Kind: function
- Shape: at the pr gate, a confirmed finding whose cited file is under `.nio/specs/<slug>/` (spec.md, plan.md, contracts.md, tests.md, quickstart.md) is not a task: `check` raises a change request against that file (`raise_change`) and the outcome names `change asked: J-n`.

### CT-30 A file a task reuses unchanged is no phantom (FR-40) [agent]
- Binding: `src/nio/evidence.py:phantoms` (existing)
- Kind: function
- Shape: a `Files:` entry written `` `path` (unchanged) `` raises no "isn't in the epic's diff" finding; the tasks-drafter card writes that mark for a file a task only reads.

### CT-31 The test-proof lens at the pr gate (FR-41) [agent]
- Binding: `src/nio/jury.py:PR_CORE` (existing)
- Kind: config
- Shape: `PR_CORE` gains `test-proof`; `src/nio/agents/test-proof.md` gains `## At the pr gate`: for each test the effort's diff adds, say whether it would still pass with the code it proves left out, citing the test's assert line.

### CT-32 Executability flags a task blocked until a later epic (FR-45) [agent]
- Binding: `src/nio/agents/executability.md` (existing)
- Kind: file
- Shape: a rule: flag a task whose guard or suite check only a later epic's task can satisfy, citing both task IDs.

### CT-33 Grant and revoke auto (FR-16) [research: RF-22]
- Binding: `src/nio/flow.py:manual` (new)
- Like: `src/nio/flow.py:park`
- Kind: cli
- Shape: the grant is #122's CT-1 and CT-2 (`nio flow start <slug> --auto --by human`, `nio flow done drafting <slug> --auto --by human`, `grant` line), carried over by CT-34. The revoke is #122's CT-3 without its restore lines: `nio flow manual <slug> --by human` writes one `switch_off` line and `auto: false`.
- Fails: `--by` other than `human` → `only the human switches auto off (--by human)`, nothing written; already manual → `<slug> is already manual`.

### CT-34 Carry #122's built code over (FR-17) [agent]
- Binding: `src/nio/flow.py:drive` (new)
- Like: `src/nio/flow.py:lock`
- Kind: cli
- Shape: cherry-pick, without committing, #122's code commits `a53bfac`, `1e20da3`, `c15c817`, `fdb1125`, `424fddc`, `349d45c`, `a40f392`, `646d342`, `ad02301` (not `bc1f267`, already on `main`), dropping every change under `.nio/specs/2026-11-08-full-auto-run/`. Resolve the three conflicts RF-37 names: `driver.lock*` joins `ignore()`; `done` takes both `terminal=False` and `auto=False`; cli.py keeps the `brief` parser and the `--auto` flags. The `--by human` ban line (#122's CT-19) goes into all 30 skills and cards and the tests' counts. `drive` is #122's CT-5 as built (`nio flow drive <slug> --by [--token] [--release]`).

### CT-35 Every gate but pr approves itself under auto (FR-46, FR-22) [human]
- Binding: `src/nio/flow.py:done` (existing)
- Kind: function
- Shape: the two `risky(root, slug)` conditions on `--commit` and on the auto commit are dropped: under auto a passing spec, plan or tasks gate commits `nio: approve <gate>` itself; its `pass` line's evidence gains `"auto": {"grant": <1-based history line of the grant>}` and the output says `approved <gate> under auto (grant, history line n)`. `where` reads such a gate as `working` with `nio flow done <stage> <slug>` (#122's CT-20 without its risky exception). The pr gate is unchanged: only `nio flow approve` at a terminal.

### CT-36 The `--by human` steps under auto (FR-47) [human]
- Binding: `src/nio/flow.py:who` (existing)
- Kind: function
- Shape: `who(by, root, slug)` returns `{"role", "host", "model", "auto": <grant line>}` when the effort is auto and `by` isn't `human`; `implement.unblock` (a task blocked on a change request), `done --human` (an override), `seen` and `jury rule` then each succeed and write their line with that `auto` field. `jury rule` gains `--by` and under auto records `by: auto` in the ledger plus a `ruling` history line `{"gate", "ids", "auto"}`. Refused: `nio flow manual` (CT-33), `nio flow done pr`/`approve` (existing terminal check), an epic unblock after 3 failed runs (CT-4); each refusal leaves the effort waiting with the reason.

### CT-37 Dispositions and the composer under auto (FR-19) [research: RF-22]
- Binding: `src/nio/jury.py:composed` (existing)
- Kind: function
- Shape: #122's CT-11 (`BY` gains `auto`, `held` disposition) and CT-12 (under auto minors and refuted findings are left out and accepted as the gate's risk; a confirmed blocker or major composes `rejected`, so the fix agent acts; `held` composes `human`), at the spec, plan and tasks gates. At the pr gate the confirmed findings become the closing `PR fixes` epic, which one implementation agent builds (CT-1), so that epic is the round's one fix agent.
- Rules: `nio jury dispose --by auto` (auto on) takes `accepted-risk` only on a minor, never `out-of-scope` or `overruled`, and a capped-batch finding only through `jury rule` (FR-19, FR-47).

### CT-38 The round check (FR-19) [research: RF-22]
- Binding: `src/nio/jury.py:cuts` (new)
- Like: `src/nio/jury.py:changed`
- Kind: function
- Shape: #122's CT-13 as written: compares the gate's artefact with the version its last round judged and returns `[human] line changed: <ID>`, `[human] line gone: <ID>`, `removed: <ID>`, `non-goal added: <text>`, `risk changed: <old> → <new>`; any hit composes `human` before the next round.

### CT-39 The fix agent and the driver loop under auto (FR-17, FR-18, FR-19, FR-22) [agent]
- Binding: `skills/jury/SKILL.md` (existing)
- Kind: file
- Shape: a `## Under auto` section: a `rejected` round goes to one fresh fix agent (a general-purpose subagent where the host has them) given every confirmed blocker and major ID of the round; it edits the gate's files for each, disposes `--by auto`, and disposes `held --by auto` instead of editing when a fix would change a `[human]` line, cut scope or change `risk:`; then the next round starts. The "Drivers and waiting" main-session text, in this skill and in `skills/implement/SKILL.md`, says: under auto, start the next driver without asking the human, and stop only when `nio flow next` waits for the human, is suspended, or reaches the pr gate's approval; on a stop tell the human the reason and the command it prints. `nio flow drive` takes and refreshes the driver claim (CT-34).

### CT-40 The run report is the pull request's body (FR-22) [agent]
- Binding: `src/nio/flow.py:report` (new)
- Like: `src/nio/usage.py:report`
- Kind: function
- Shape: #122's CT-14 report (gates and their auto approvals with the grant line, accepted risks, fixes by the run, `[auto]` defaults), read from history and the ledgers. Under auto `jury.publish` uses it as the body of the pull request it creates and, on a reused one, runs `gh pr edit <n> --body-file <tmp>`. It never merges.

### CT-41 The pause message (FR-22) [research: RF-12]
- Binding: `src/nio/flow.py:talk` (existing)
- Kind: function
- Shape: unchanged: a paused or suspended effort prints the reason and `nio flow start <slug> --by human`. A test guards it under auto.

## Data model
- **Epic claim** (spec Key entity) in `src/nio/flow.py:defaults` (existing) [agent]
  - `claims.epics`: `{E-n: {"run", "worktree"?}}` in state.json, and `attempts["E-n"]`: the failed-run count. "Unblocking resets the failed-run count." (state table Epic)
- **Epic test result** (spec Key entity) in `src/nio/implement.py:entry` (existing) [agent]
  - an `epic_test` history line: `epic`, `command`, `passed`, `runner`, and on a fail `cause`, `failing`, `tail` (at most 50 lines). "record the failing tests and the last 50 lines of the run's output" (FR-4)
- **Auto grant** (spec Key entity) in `src/nio/flow.py:record` (existing) [research: RF-22]
  - the `grant` and `switch_off` history lines of #122's data model; every line written under auto by a non-human carries `auto: <grant line>`.
