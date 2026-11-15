# Intake: faster-flow

## The human's words

> would this  https://github.com/nikolajkarpic/nio/issues/151 speed up nio implementation step?

> lets also investiagete and add in here the mod that would background the tasks in claude code, and the full auto approve all flow we're half way done with

> okey see other speedup things in the issues in gh and what acna we add here I want to write spec for this all and finish it up to spead up the flows

> also keep in mind we want to do spec, plan tasks and then we want to pass it all to one agent to implement and run one jury fix all the issues with one agent and be done wiht this speedup

Scope choice (asked, answered): "Everything in one spec": per-epic implementation (#151), cross-epic dependencies (#152, #69), the background mod's coverage and default-on, closing the issues per-epic implementation makes obsolete (#97, #108, #115, #82, #78, #80, #98, #83), the jury-gate stops (#124, #138, #94, #96, #95), robustness (#107, #106, #64), and the full-auto run (#122) folded in.
Left out by the agent's proposal, not contested: #133, #86, #104, #92.

## Source: https://github.com/nikolajkarpic/nio/issues/151

### Per-epic implementation: one agent per epic, tests at epic end, no red/green

## What

Move the implement stage from per-task red/green to **per-epic implementation**:

1. **One agent per epic.** The whole epic (its tasks, their tests and code) goes to one implementation agent, instead of a fresh test worker and a fresh code worker per task.
2. **No red/green per task.** Drop `nio flow red` / `nio flow green` as the per-task gate. A new effort branch starts from `main`, whose suite is taken as green, so there is no per-task "fails before the code" proof.
3. **Tests run at the end of the epic.** When the agent finishes, `nio flow` runs the epic's tests (the tests its tasks name) itself; the epic closes only if they pass. The agent's word still never counts.
4. **No jury per epic.** The epic closes on its tests alone; the existing pr gate (one jury on the whole effort diff, driven by a fresh agent, approved only by the human) stays the only review. Per-epic juries were dropped in 373b3ee (#77, #100) because they took 55–69% of implementing time and the builder approved its own gates.

## Why

Per-task red/green is slow and costly for what it buys. Effort `2026-11-15-effort-drilldown-install` (#142), first epic of 4 tasks:

- Every split-mode task pays for two cold agent starts plus at least three test runs (worker run, `red`, `green`). One pane task's code worker ran ~12 min, mostly re-running `claude plugin test` (>100 s a run).
- Two of three reds were refused on the first try because the `--run` command didn't name the test file: an extra worker and run each.
- One task (T-4) could not go red at all because an earlier task had already built it; it took a change request, a retire and a fix task to get past (C-261115-duou).
- One planned test's fixture couldn't reach its state (C-261115-svvm), stopping the build for a change request and a plan re-check.
- Usage so far: ~39 min agent time, ~8 min shell, ~66 min waiting on the human, much of it for these stops.

One agent holding the whole epic keeps context between related tasks (most of an epic's tasks touch the same files in a chain), and one test run per epic replaces dozens of per-task gates.

## What changes

- `skills/implement/SKILL.md`: a driver claims an epic, not a task; one worker card implements it from an epic pack; then `nio flow` runs the epic's tests and closes the epic if they pass.
- `nio flow claim` / `red` / `green`: per-epic claim and an epic test run replace per-task red/green. Task modes (split/single/direct) and the "tests frozen at red" rule go.
- `nio jury`: unchanged; the pr gate on the whole effort diff remains the one review.
- `tasks.md`: tasks stay as the epic's checklist and the test map (task → AC → test); tier/mode ratings move to the epic.
- NORTH_STAR "Implement" (TDD, test writer, builder) is updated to match.

## Open questions (for the grill)

- What replaces the proof red gave, that a new test actually checks something (a test that passes with no code looks the same as one that does)? Options: none (rely on the pr gate's conformance lens), a mutation/blank-out check at epic end, or the test-proof lens added to the pr gate.
- Epic size: does one agent per epic need a cap (tasks or files) so its context holds?
- What happens to an epic whose tests fail at the end: same agent retries, a fresh one, or fix tasks?
- Waves: do independent epics run in parallel worktrees?
- Migration: efforts already at implementing finish on the current flow.

## Done when

- An approved effort's epic is implemented by one agent and closes only when `nio flow` itself ran the epic's tests and they passed; no jury runs per epic, only the pr gate at the end.
- No `red`/`green` step remains in the implement stage, and the self-checks cover the new flow.


## Related speed-ups this must fit with

Most of the wall-clock time on #142 was the human (about 66 of 87 min), not agents. This issue removes only the stops red/green itself causes. Two other pieces go after the rest, and both have to change with it.

### Background mod (#130, `tools/claude-mods/background-nio-commands/`)

- **State:** built and merged (0d207df). It is opt-in per person (`--plugin-dir` or `CLAUDE_CODE_PLUGIN_DIRS`), and the session that drove #142 didn't have it on, so the 267 min of wait loops it targets (RF-1 of its spec) weren't saved there.
- **What it saves:** time agents spend in `sleep`/poll loops around `nio jury run`, `nio flow green` and `tests.suite`. It doesn't make the commands any faster.
- **Coupling:** it matches `nio flow green` by name. Once this issue drops `green`, the mod must match the new end-of-epic test command instead, or it silently stops backgrounding the longest implement-stage run. Add that command to the mod's long-command list in the same change.
- **To do:** turn it on for every session that drives an effort (an `@nio:install` step, #142, or a line in the driver's start-up).

### Full-auto run (#122, worktree `/home/work/nio-auto`, branch `nio/2026-11-08-full-auto-run`)

- **State:** E-1 and E-2 are closed, and E-3 stopped mid T-7 (direct mode, 2 of 3 attempts). 22 of 29 tasks are left, E-4 to E-8 haven't started, and the branch is 194 commits behind `main`.
- **What it saves:** the waits for the human. The driver runs every gate, and the fixer settles confirmed findings, so the human-wait share (most of the time on #142) goes away for non-risky specs.
- **Conflict:** its approved spec still requires an epic jury after every epic (FR-16, AC-20; "each epic's implementation and epic jury"). That contradicts 373b3ee (one pr gate per effort) and this issue. Before it resumes, it needs a change request: drop FR-16 and AC-20, have the driver run the pr gate once, and drive per-epic implement (this issue) instead of per-task claim/red/green.
- **Order:** land this issue's implement shape first, or at least settle it in the grill. Then rebase #122 onto `main`, file the change request, and finish E-3 to E-8 against the new shape. Building the driver around red/green now means rewriting it.

### Combined estimate (not measured)

| Piece | Cuts |
| --- | --- |
| This issue | agent cold starts, repeated test runs, red refusals, can't-go-red stops (roughly a quarter to a third of agent and shell time) |
| Background mod | wait-loop turns around long commands |
| Full-auto | human waits at gates and rulings, the largest share |

Open question to add to the grill: should the full-auto driver be specified against per-epic implement directly, folding #122's E-3 rework into this issue's scope?


## Source: https://github.com/nikolajkarpic/nio/issues/122

### Full-auto run: after the spec, drive every stage and gate with jury auto-fix

## Want
Once the human has written a spec, an effort can run on its own to the end: spec jury → fix findings → re-jury → plan → plan jury → fix → tasks → tasks jury → fix → implement each epic → epic jury → fix → done. The human approves nothing along the way unless something stops it.

## Already built (flow-state spec, `.nio/specs/2026-10-28-flow-state/spec.md`)
- `state.json` has an `auto` flag. With it on, a gate whose jury approves commits `nio: approve <stage>` itself (FR-18).
- Specs flagged `money`, `data-deletion`, `migration` or `auth` still wait for the human's `--commit` (FR-51).
- Stop list: a gate pauses after 3 jury rounds, or when a round closes none of the last round's findings (FR-39). The effort is suspended at the `budgets.juries` / `budgets.subagents` caps (FR-40), or after the same guard fails 3 times in a row (FR-41). A change that would move it back waits for the human (FR-42).
- A hand-edited auto flag is refused (AC-58).

## Missing
1. **The switch.** Nothing sets the flag. The flow-state spec deferred `nio flow start --auto`, the `nio:auto` label and the history line that records the grant (its Q8).
2. **The driver.** Something has to loop `nio flow next` → run the named skill → `nio flow done` until the effort pauses or is done. That is probably a `skills/auto/SKILL.md` that starts each stage in a fresh subagent where the host can do that.
3. **Auto-fix.** Jury findings go to the human today. In auto mode, refuter-confirmed blockers and majors need a fixer that edits the stage's files and starts the next round. Deferred from flow-state: the jury confirming defaults and turning open points into defaults (its Q2, Q3, Q7).
4. **Notify.** NORTH_STAR says "if the jury approves, the agent proceeds, but the human is always notified." Where and when does that happen?

## Open questions
- Q1 When is auto granted: when the spec is approved, or by a separate command at any stage? Does the spec jury itself run under auto?
- Q2 What can the fixer do on its own, and what still goes to the human (open points, scope cuts, findings that contradict the human's own words)?
- Q3 What do `budgets.*` default to under auto?
- Q4 How does it end: open a PR and stop, or merge?
- Q5 How is the human notified: a report at each gate, one summary at the end, or both?
- Q6 How do long gates fit hosts that push commands to the background (#85)?

Serves NORTH_STAR → "Autonomy is earned through the jury, never assumed" and "I can read why every autonomous decision was allowed."


## Source: https://github.com/nikolajkarpic/nio/issues/130

### Mod: run long nio commands in the background instead of polling

Claude Code mod (dev tooling, Claude-only, not part of the NIO product).

**Problem.** Foreground nio commands get backgrounded after about 3 minutes, so agents sit in polling wait loops. Those loops took about 267 minutes of onboarding (#49) and full-auto (#122) time on 2026-11-08.

**Mod.** A `tool.call` hook on Bash that rewrites long nio commands (`nio jury run`, `nio flow green`, the configured test-suite command) to `run_in_background: true`. The harness then wakes the session when the command exits, so no wait loop is needed.

**Done when.** A jury run during an effort finishes with no `sleep`/poll loop in the transcript.

**Priority.** High: the only mod idea that saves wall-clock time.


## Source: https://github.com/nikolajkarpic/nio/issues/152

### nio flow claim deadlocks when a task depends on a later epic's task

## What

`nio flow claim` deadlocks when a task in the current epic depends on a task in a later epic.

`next_ready` in `src/nio/implement.py` (around line 147) only looks at the first epic that still has undone tasks. If every remaining task of that epic waits on a task in a later epic, the claim refuses forever with `error: no ready task; T-x waits on T-y`, even though `nio flow brief` lists T-y as ready.

## Seen in

Effort `2026-11-15-effort-drilldown-install` (#142): E-5's last task T-10 depends on T-11, which is in E-6. After T-9 (E-5) was done, every claim refused `no ready task; T-10 waits on T-11`. Neither `nio check tasks` nor the tasks jury flagged the cross-epic dependency.

## Expected

Either:
- `nio check tasks` rejects a dependency on a task in a later epic (so the drafter orders epics right), or
- the claim hands out a ready task from a later epic when the current epic's remaining tasks wait on it.

The check is the smaller fix and keeps "one epic at a time" intact.

## Done when

A tasks.md with a task depending on a later epic's task either fails `nio check tasks` with a message naming both tasks, or claims through without deadlock; a self-check covers it.


## Source: https://github.com/nikolajkarpic/nio/issues/69

### Catch a task that's blocked until a later epic

Split out of #65 (item 4).

No check catches a task that blocks the build itself: a rule enforced from an early epic whose only way to clear it is a task in a later epic. In #29, T-4 and T-27 passed both the plan jury and the tasks jury this way, and C-261030-abpr fixed it by hand.

## Open questions: brainstorm all of these before implementing
- Can `nio check tasks` find it from the task fields alone (Files, Test, dependencies), or does it need a juror lens (executability) to read the contracts?
- What counts as "enforced": a guard, a check in the suite, a lint rule?
- At which gate should it fail: plan or tasks?

Refs: #65, #29

## Source: https://github.com/nikolajkarpic/nio/issues/124

### Jury drops real findings as ungrounded when a quote carries a trailing source note

On 2026-11-08-full-auto-run tasks gate (run R-261108-z3y6), the executability juror wrote 5 findings whose quotes looked like `- quote: "- Test: TC-15, ..." (tasks.md, T-11)`. All 5 were dropped as `ungrounded` and the gate composed `approved` with `unresolved: 0`, although the findings were real (wrong task order, a test asserting work from a later task). A silent drop of every finding means the gate approves unread work.

Possible fixes: strip a trailing `(file, ID)` note before grounding; or when every finding of a lens is ungrounded, mark the juror INVALID and ask for a re-run instead of approving.

## Source: https://github.com/nikolajkarpic/nio/issues/138

### Jury: a finding dropped as ungrounded can't be disposed later, and escalation jurors' findings come back as new IDs

Seen at the spec gate of 2026-11-14-effort-jury (run R-261114-z3wj), on main after #137:
- J-14 (logic, with a concrete case) was dropped as "ungrounded". The human later ruled it a real fix, and its fix went into the spec as FR-17 and AC-20, but `nio jury dispose` refuses: "J-14 is dropped; only open findings take a disposition". There's no way to reopen a dropped finding or record a ruling on it.
- The two extra consistency jurors escalated for blocker J-6 returned findings that were recorded as new IDs (J-22 to J-27) and sent through a second refuter pass, instead of only voting on J-6. The second refuter pass overwrote `spec-refuter.md`.
- The step listed J-27 under its round-1 note after the spec text it described had been rewritten.

Proposals: `dispose` accepts a human ruling on a dropped finding (it reopens it); escalation jurors' outputs vote on the blocker, and anything else they raise becomes a note; refuter outputs are numbered per pass.

## Source: https://github.com/nikolajkarpic/nio/issues/94

### A merge that raises a finding's severity sends it back to the refuter as a second batch

## Problem
In the 2026-11-07-fewer-gate-turns spec gate (round 1), the refuter's answer merged a major into a minor (`same-as`): J-3 into J-14 and J-20 into J-5. The kept findings took the major severity, became `pending` again, and `nio jury collect` printed a second refuter batch for them. That cost one more refuter run and 3 orchestrator calls, and the refuter had already judged both halves.

## Proposal
- When the refuter merges a confirmed finding into another, carry its validation over to the kept one (confirmed stays confirmed), or
- keep the kept finding's own validation and only raise the severity, so no second batch is needed.

Refs: #76, #77, src/nio/jury.py `refute`

## Source: https://github.com/nikolajkarpic/nio/issues/96

### A fix made before an escalation round is collected reads as "fix without a change"

## Problem
In the 2026-11-07-fewer-gate-turns plan gate, a re-check raised blocker J-10; the refuter confirmed it, and the orchestrator fixed contracts.md while the two escalation jurors were still running (they read their pack, not the artefact). Collecting the escalation outputs then opened a new round on the already-fixed version, so: (1) the refuter had to confirm J-10 a second time, and (2) after `dispose J-10 plan-fix`, `nio jury check` said `plan-fix without a change to the plan: J-10` because the round's version already held the fix. The only way on was a further real edit to the plan, then a fix check.

## Proposal
- Escalation jurors' outputs join the round of the blocker they judge (version of that round), not a new one, or
- `compose`'s unapplied check compares against the version the finding was *raised* on (`first_round`), not its `last_round`.
- The skill (and `nio jury next` from #76) says: don't edit the artefact until the escalation is collected.

Refs: #76, #77, src/nio/jury.py `collect` retry rule and `compose` `unapplied`

## Source: https://github.com/nikolajkarpic/nio/issues/95

### Plan gate: changed contracts and tests count as section text, so fix-check packs carry whole sections

## Problem
In the 2026-11-07-fewer-gate-turns plan gate, `nio jury changed <slug> plan` printed `changed: nothing` and `sections: Contracts, Acceptance tests, Quality tests, Misuse tests` after edits to CT-1, CT-2 and a few TCs. `jury.parts` recognises spec items (`- **FR-1**`) but not `### CT-n` / `### TC-n` headings, so each changed section went into the fix-check pack whole, before and after: 427 and 449 lines for two lenses, where the changed items were about 60.

## Proposal
- Let `parts` treat a `### <ID> ...` heading and its lines as one item, so a plan fix check shows only the changed contracts and tests and their neighbours.

Refs: #76, #77, src/nio/jury.py `parts`

## Source: https://github.com/nikolajkarpic/nio/issues/107

### Waves: claim races the post-checkout index rebuild and crashes, leaking a worktree

## Problem
Found while implementing the review-fixes effort. `nio flow claim` of a two-task wave crashed with `KeyError: 'D-261107-k2nv'` in `query.search` (`rows[rid]`, `src/nio/query.py:48`), from `worker_pack` → `pack.build` for the second task, and left the first task's worktree behind (each retry leaked one more).

Cause: `claim` creates the first task's worktree with `git worktree add`. That fires the `post-checkout` hook `nio hooks` installs, which runs `nio index` **in the background**. `repo_root()` maps the worktree to the main tree, so that background build rebuilds the main tree's `.nio/cache/index.db` while `claim` builds the second task's pack. `index.build` drops and recreates `nodes`/`edges`/`fts`; Python's sqlite3 runs the DDL outside the `with db:` transaction, so a concurrent reader sees `nodes` with 0 records while `index.load` (files on disk) still yields the record via its `touches` globs. Seen: `nodes` had 0 records at the failure; 217 after.

Workaround used: run the claim with `GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.hooksPath GIT_CONFIG_VALUE_0=/dev/null`.

## Proposal
Cheapest first:
1. `claim` creates worktrees with `-c core.hooksPath=/dev/null` (its own git calls; the hook has nothing to do there).
2. `query.search` skips IDs missing from `rows` instead of indexing them blind.
3. `index.build` writes to a temp DB and renames it over the old one, so readers never see a half-built index.
Also: a failed claim should remove the worktrees it created.

Refs: #87, #101


## Source: https://github.com/nikolajkarpic/nio/issues/106

### A worktree effort runs the main checkout's rendered agents, so jurors can't write their output

## Problem
In the #44 effort (worktree `/home/work/nio-44`, session started in `/home/work/nio`), every `nio-<lens>` juror ran from the main checkout's `.claude/agents/`, rendered before #76: `tools: "Read, Grep, Glob"`. The worktree's own `.claude/agents/nio-scope.md` has `Read, Grep, Glob, Write`. So no juror could write its output file; each returned its output in the hand-back, and the orchestrator had to copy it verbatim (about 15 copies at the spec and plan gates), which is the turn and context cost #76 removed.

Workaround used: run the juror as a general-purpose subagent told to follow `.claude/agents/nio-<lens>.md` and write only its output path, with the card's model.

## Proposal
`nio jury next` already renders the agents; also print a warning when the host's session root differs from the repo root it rendered into (the agents the host loads are not the ones just rendered), or tell the orchestrator in the jury skill to start the host session in the worktree.

Refs: #76, #77

## Source: https://github.com/nikolajkarpic/nio/issues/64

### Stage hand-offs print /nio:* commands that don't exist when the plugin isn't installed

`nio flow next` and `nio flow done` print `next: run /nio:tasks`. In this repo that gave "Unknown command: /nio:tasks", because `.claude-plugin/plugin.json` isn't installed in Claude Code, so no `/nio:*` command exists.

Found right after #56, which added these hand-off lines. The human can't act on the line as printed.

Open question: install the plugin as part of `@nio:install` (or document it), or have the hand-off word the step so it works either way, for example naming `skills/tasks/SKILL.md` when the command isn't available.

Workaround: ask the agent to run the stage; it can follow `skills/<name>/SKILL.md` directly.

## Source: https://github.com/nikolajkarpic/nio/issues/97

### A task that changes shared behaviour can't update the older tests that pin it: one block cycle per test

## Problem
In 2026-11-07-fewer-gate-turns, T-4 gave the juror cards a write tool (FR-9). Two older tests pinned the old read-only tool list: `tests/test_agents.py` (`test_sync`, `test_ac12_test_proof...`) and `tests/test_evidence.py` (`test_it_can_open_any_project_file_and_can_t`). Red froze the test files, so the code worker couldn't update them; the second one surfaced only in the epic-closing review. Each cost a full cycle: `nio flow block` (the worker's code shelved as a patch), a change request, `unblock`, re-claim, a test worker re-applying the patch's tests, red, a code worker re-applying the src part, green — about 8 orchestrator calls and 2 workers each, for a one-line assertion. T-3 hit the same kind of cycle (a test whose assert depended on a later task).

## Proposal
- At claim, list the existing tests that mention the task's `Files:` symbols (or that fail when the planned change is applied), so the test phase updates them before red.
- Or let the code phase propose an edit to a frozen test as part of its handoff (`status: done` with `test_edits:`), which the review shows to the jury instead of a block.
- `nio flow claim` after an unblock could re-apply the shelved patch itself.

Refs: #76, #77, C-261107-tpmk, C-261107-bk6v, C-261107-segr

## Source: https://github.com/nikolajkarpic/nio/issues/108

### A reused, unchanged file in Files: becomes a false 'isn't in the epic's diff' finding, and retiring its fix task re-opens the tasks gate

## Problem
In the #44 effort, the plan had contracts for code reused unchanged (CT-10 `implement.py:red`, CT-11 `jury.py:plan`, "runs unchanged"). `nio check tasks` requires every file a build-order entry delivers to be in some task's `Files:`, so the drafter listed `src/nio/implement.py` and `src/nio/jury.py` on test-only tasks. At implementation-E-1 the free check raised "T-3: src/nio/implement.py isn't in the epic's diff" and "T-4: src/nio/jury.py isn't in the epic's diff" (J-1, J-2), each filing a fix task (T-13, T-14) that can only be done by touching a file that must not change.

Accepting both as risk and retiring the two fix tasks (as the tasks skill says) then moved the effort back to tasks_jury ("tasks.md moved it back"), costing a tasks-gate re-check.

## Proposal
- Let a contract marked `(existing)` with no change (or a `Files:` entry marked `(read)`) be exempt from the "in the epic's diff" free check; or let `nio check tasks` not require reused-unchanged contract files in `Files:`.
- Retiring a fix task whose finding was accepted as risk should not withdraw the tasks approval (fix tasks appended later already don't).

Refs: #77, #98

## Source: https://github.com/nikolajkarpic/nio/issues/115

### Lite path: an unchanged-behaviour AC proved by an existing test always gets an unfinishable 'no passing evidence' fix task

## Problem
On a lite spec, `nio jury evidence` lists only the test functions the epic's commits **add** (#111's EB-2, `src/nio/evidence.py` ~420). A lite spec's unchanged-behaviour ACs (UB-n) are regression guards, and the existing tests often prove them already. Those tests are never listed, so the implementation gate files a CLI blocker "AC-n has no passing evidence" and a fix task for each.

The fix task can't be finished: its test is "new: AC-n", and `nio flow red` refuses a test that already passes, which a regression test does by design. The only way out is the human's override.

Seen twice in real use:
- #111's dogfood (`2026-11-07-lite-gate-fixes`): T-3 and T-4 closed by override, "accepted as risk".
- #113's lite effort (`2026-11-07-refuter-batch-forge`, on #112's branch): J-7 and J-8 for AC-4 and AC-5. Both are proved by existing tests (`test_misuse_forged_refuter_on_a_peer_is_refused`, `test_ac2_refuter_only_for_its_batch`), and the conformance juror matched both to them.

The review of #112 noted the narrower case: a modified (not added) test, or a non-Python test, is missing too.

## Proposal
On a lite spec, also take the tests the conformance lens's `## Matches` names, and run them in the evidence suite, so an existing test can carry a UB AC. Or file no fix task for a UB AC whose matched test passes.

Refs: #44, #111, #112, #113

## Source: https://github.com/nikolajkarpic/nio/issues/82

### `nio flow block` writes a change request that `nio check` rejects

## Problem
In the faster-checks effort (PR #81), `nio flow block` filed change request C-261106-y5tc with section names that `nio check` rejects, so the pre-commit hook refused T-5's commit until the sections were renamed by hand.

## Proposal
Make `flow block` write the change record from the same template `nio check` validates, and add one test that `nio check` passes on a freshly blocked task's record.

## Source: https://github.com/nikolajkarpic/nio/issues/78

### Task commit sweeps untracked files outside the task into T-n

Seen on #65 (T-4, commit c4d5a33): an untracked `.nio/research/2026-11-06-speedup.md` written by another session was in the working tree when `nio flow green` passed. The review listed it under `outside the task's files`, but `implement.commit` still put it into the `T-4:` commit.

Idea: commit only the task's files, the red line's frozen files and the flow files; leave other untracked paths alone (or refuse the commit while they exist). Also seen: the epic-closing review failed once with `the suite exits 1 and its runner is unknown` and no output kept, so the failing test can't be named afterwards (likely a wall-clock assert under load; a sequential rerun passed). Keeping the suite's tail in the review line would make that diagnosable.

## Source: https://github.com/nikolajkarpic/nio/issues/80

### Implementation gate: a plan-rooted finding becomes a fix task no worker can do; retiring it trips check tasks

Seen on #65, implementation-E-3 round 1. J-1 (adversary, confirmed) was about the QS-5 journey command in `quickstart.md`. `nio jury check --record` turned it into fix task T-15 with `Files: tests/test_flow.py`. The worker can't edit plan files, so it handed off blocked. That filed C-261106-mao2, which was rejected.

Two gaps:
1. The implementation gate has no plan-fix or spec-change route. A finding rooted in a plan file still becomes a code fix task, which can only end blocked.
2. Retiring the dead fix task (`retired: [T-15]`) makes `check_fixes` fail for the earlier fix T-14 (`a fix task takes the next free ID, T-16`). The retired ID counts toward `top` before T-14 is checked. Workaround used: T-15 kept in direct mode as a re-run of TC-15.

Also seen: `nio jury dispose ... overruled` is refused outside the final fix check, so accepted-risk was the only way to close J-1.

## Source: https://github.com/nikolajkarpic/nio/issues/98

### Retiring the last fix task makes nio check tasks reject every earlier fix task's ID

## Problem
In 2026-11-07-fewer-gate-turns, the E-4 gate filed fix task T-10 for J-5; the human then accepted J-5 as a risk, so T-10 was pointless. The tasks skill says to remove such a task and list its ID in `retired:`. With `retired: [T-10]`, `nio check tasks` printed `T-6: a fix task takes the next free ID, T-11` for T-6, T-7, T-8 and T-9 (4 errors): the next-free-ID rule counts the retired ID as used before the earlier fix tasks. Leaving T-10 out of `retired:` passes the check but breaks the never-reuse rule.

Also: `dispose ... accepted-risk` on a finding whose fix task was already appended could retire that task itself.

## Proposal
- Check a fix task's ID against the IDs used before it was added (its position under `#### Fixes`), not against the retired list's maximum.

Refs: #77, src/nio/tasks.py fix-ID check

## Source: https://github.com/nikolajkarpic/nio/issues/83

### Retiring a fix task breaks `nio check tasks` numbering and pulls the effort back to tasking

## Problem
In the faster-checks effort (PR #81), retiring one fix task made `nio check tasks` reject the numbering of the remaining fix tasks, and the flow pulled the effort back to tasking until the change was reverted.

## Proposal
Let `check tasks` accept gaps left by retired fix tasks (or keep a retired task as a tombstone line), with a test.
