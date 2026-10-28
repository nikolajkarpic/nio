# Intake: 2026-10-28-flow-state

## The human's words (2026-10-28)

> we need to do research on #45 the state machine to betther represent what is happening in the curernt run

> this state machine should best help with when an issue is wirtten in a suffiecnt manner or when a prompt is deailed enough that we can go from spec to implemenatniion by itself

> yes post it and start the brainstorm and the deep researhc

> yes open the worktree issue, then fix #55 and #58

> Yes let's do it

Answer to "should `nio flow` go through NIO's own pipeline first": Spec + jury, then build.

"Yes let's do it" answered this proposal: "Next in the order agreed on #45 is building `nio flow`: the status view, park, the stop list, overrides, and reopening on change requests." The `[guess]` tag, the auto switch and `nio flow run` come after it (Brainstorm Q17's order).

## Source: https://github.com/nikolajkarpic/nio/issues/45

### Flow state machine: nio flow next/done, guards, single writer, committed state

### What needs designing

**Flow state as a state machine** (#19), so no agent has to keep "where am I" in context. After a compaction, a new session or a host switch, the agent runs `nio flow next` and carries on.

### Decided (2026-10-25)

1. **The CLI owns transitions.** Only `nio flow` writes state. Agents never edit the state file.
   - `nio flow next` prints the current state, the skill to run, the input files, the exit criteria and the command to report done (about 10 lines).
   - `nio flow done <stage|task>` runs the **guards** (deterministic checks, never agent claims), then moves to the next state or prints what is still missing.
2. **Single writer: the orchestrator.** Workers (worktrees, other hosts) never touch state. They write their handoff (result, evidence, test output), and the orchestrator calls `nio flow done T-x`. Guards run outside the worker's context, so a worker can't attest its own completion.
3. **Committed state, auto-commit at gates only.** `state.json` lives in `.nio/specs/<slug>/` and is committed. `nio flow` commits automatically only when a gate passes (`nio: approve spec`, `nio: approve plan` …, the form in CLAUDE.md). Transitions between gates ride along with normal commits. Run scratch (packs, raw juror output) stays in `.nio/runs/`.

### The machines

**Flow, one per effort:**
```
intake → drafting → researching → advocate_walking → grilling → spec_jury
       → arch_grilling → planning → plan_jury → tasking → tasks_jury → implementing → done

loops:  spec_jury  ─reject→ grilling            plan_jury ─reject→ arch_grilling | planning
        tasks_jury ─reject→ tasking             implementing ─change request (#30)→ the stage it's against
flags:  waiting_on_human: <question ID>         (the state stays put; the next agent sees the pending question)
any → paused | abandoned (human only)

lite (#44):  intake → mini_spec → grilling (skipped if nothing is ambiguous) → repro → red → fix → jury → done
```

**Epic:** `building → evaluating (#29) → epic_jury → done`

**Task, one per task during implement:**
```
pending → ready (deps done) → claimed (worker, host, pack path) → red (failing test observed)
        → green (tests ran and passed) → review (jury on the diff) → done
side:   blocked (human or change request)    rejected → claimed    failed → ready (retry count, capped)
```

**Example guards:**

| Transition | Guard |
|---|---|
| drafting → researching | `spec.md` exists; every template section is filled or has an open point |
| grilling → spec_jury | `nio check spec` passes: no open points, no unconfirmed `default` (#21) |
| spec_jury → arch_grilling | a verdict record with `approve` and `unresolved: 0` (#27) |
| tasking → tasks_jury | coverage matrix complete: every AC has a task and every task has an AC (#28) |
| claimed → red | the named test command ran and failed |
| red → green | the same command ran and passed, and no test was deleted or weakened in the diff (#29) |

**History:** every transition is appended with who (role, host, model), when, from, to and the evidence (paths, verdict ID, test output hash). This is the audit trail NORTH_STAR wants, and it's enough to replay the state.

### Open questions: brainstorm all of these before implementing

When work on this issue starts, the first step is a grill/brainstorm session that settles every question below and records each answer here. Only then does implementation begin.


- The exact `state.json` schema, and whether history goes inside it or in an append-only `history.jsonl` next to it.
- The full guard table for every transition, and which guards the human can override (and how an override is recorded).
- Scheduling: how `next` picks from the ready set for parallel tasks, and limits from budgets (NORTH_STAR).
- Grill sub-state: the frontier and pending question live in `grill.md`. Does `next` read them, or does the grill keep its own small state?
- Notification hooks: entering `waiting_on_human`, any jury reject, and `done` notify the human (#7).
- Folder layout of `.nio/specs/<slug>/` (intake, spec, research, grill, architecture, plan, tasks, jury reports).



### Comment, 2026-10-27

Folder layout, partly settled by #42 on 2026-10-27: `.nio/specs/<slug>/tasks.md` (one file per spec, a section per epic) and `jury/implementation-E-n.json` (one jury ledger per epic). Task status lives only in this issue's state file.

### Comment, 2026-10-27

## Research (2026-10-28): input for the brainstorm on the open questions

Nothing is built yet: no `state.json`, no `nio flow`. The CLI's verbs are new/check/index/query/get/pack/hooks/status/run/agents/jury. Below is a recommended answer for each open question, with the evidence behind it, for when the brainstorm starts.

**1. `state.json` schema, and history inside or beside it.** Recommend **`history.jsonl` beside it**, append-only, with `state.json` as a small snapshot. Reasons:
- Appending one line per transition merges cleanly in git: two branches appending different lines give a trivial conflict at worst. A rewritten JSON array conflicts on every concurrent change.
- The snapshot can be rebuilt by replaying history, which #45 already says should be possible. Then `nio flow` can always refuse a `state.json` that doesn't match the replay, so a hand edit gets caught.
- Same pattern as memory: files are the source of truth, the index is rebuildable (MEMORY_NORTH_STAR).

Minimal snapshot: `{"flow": "<state>", "waiting_on_human": null|"<question id>", "epics": {"E-1": "<state>"}, "tasks": {"T-3": {"state": "...", "attempts": n, "worker": "...", "pack": "..."}}, "seq": <last history line no.>}`.

**2. Guard table and human overrides.** Overrides are already a NIO pattern: `nio jury check --human REASON` closes a gate with outcome `human` and records the reason. Reuse that shape: `nio flow done <stage> --human "<reason>"` skips the failing guards, writes the guard output and the reason into the history line, and is refused in delegated sessions. #55 showed the danger: an override that doesn't produce its own record. Make the override line mandatory evidence, not a dedupable outcome.

**3. Scheduling the ready set.** Use Kahn's topological order over `Depends on:`. Among ready tasks, put **`Parallel: yes` tasks on disjoint files first** (`nio check tasks` already forbids parallel tasks sharing a file, #42), then the higher tier first, so strong models start early. Cap concurrency from config (`budgets.parallel`, default 1 until a worktree adapter exists). Codex caps the same thing with `[agents] max_threads` ([Codex subagents](https://developers.openai.com/codex/subagents)). Retry cap per task: 2, matching the jury's 2-round rule.

**4. Grill sub-state.** Let **`next` read `grill.md`**; don't duplicate it. The grill already logs every question and answer in a parseable shape (`nio jury answers` reads it). `next` only needs "is there an unanswered `Question:` entry". A second state store for the grill would create two writers, which decision 2 forbids. #51's J-21 lists the grill states the spec doesn't model (15-question pause, delegated, finish gate, partial round). Fold those in here as substates derived from `grill.md`.

**5. Notifications.** Fire on enter `waiting_on_human`, any reject, and `done`. That should be a **config-driven command hook** (`notify: "curl -d @- ntfy.sh/<topic>"`). Details are in #7.

**6. Folder layout** (partly settled by #42):
```
.nio/specs/<slug>/
  intake.md  spec.md  research.md  grill.md
  architecture.md (optional)  plan.md  contracts.md  tests.md  quickstart.md
  tasks.md
  state.json  history.jsonl
  jury/{spec,plan,tasks,implementation-E-n}.{json,md}
.nio/runs/<run>/   packs, raw juror output (scratch)
```

**Prior art**
- Spec-kit has no persisted flow state; each command re-derives it from which files exist.
- **Kiro** tracks tasks as checkboxes in `tasks.md`. #42 Q5 rejected that on purpose: status only through guards.
- **Claude Code itself** keeps work state outside the context and relies on re-reading files after compaction. That's the same motivation as `nio flow next`.

Refs: src/nio/cli.py (no flow verb yet) · src/nio/jury.py (check --human) · #42 · #51 · #55 · #7


### Comment, 2026-10-28

## Research 2 (2026-10-28): the machine's job is to run unattended when the input is good enough

**Goal (the human, 2026-10-28):** when an issue or prompt is detailed enough, the machine takes it from spec to implementation by itself. The human is only pulled in when something really needs them.

Evidence: the 8 efforts in `.nio/specs/`, their jury ledgers, their grill logs, the 34 runs and `git log`.

### Where the real runs needed the human

| Effort | Intake (words) | Grill questions | Spec gate |
|---|---|---|---|
| plan-jury | 1617 | 13 (7 from open points, 4 from jury findings) | closed by human, r3 |
| tasks-stage | 1986 | 16 + a change request | approved, r5 |
| implementation-jury | 1668 | 21 (13 open points, 8 jury findings) | closed by human, r3 |
| jury-convergence | 593 | 10 | closed by human, r3 |

Three findings:

1. **A long intake still produced 13–21 questions.** Length doesn't measure sufficiency. What the questions came from does: the drafter's open points (`OP-n`) and jury findings that change behaviour (`J-n`). So "sufficient" is a fact the drafter produces: **zero open points and zero unconfirmed defaults after drafting.** The machine can check that, and an intake can't fake it.
2. **The human closed gates because the jury tooling broke, not because the spec was wrong.** The recorded reasons: "the final pack didn't show those lines" (#58), "retry rejected because another lens closed J-6 in the same round (pack bookkeeping bug)" (#55), "its pack lacked the table". An unattended run would have stalled at every one of these gates. **Gate convergence is the main blocker to autonomy**, ahead of the state machine itself.
3. **Change requests come from outside.** C-261028-7njg reopened tasks-stage's approved spec because another effort (plan-jury) had landed. An unattended run has to notice that and stop. It can't carry on against a stale spec.

### What the machine needs for unattended runs

**A. Autonomy is set per effort, at intake.** `nio flow start <slug> --auto` (or the issue carries a label). Without it, every gate waits for the human, as today. NORTH_STAR says "autonomy is earned through the jury, never assumed", so the human opts in each time.

**B. A sufficiency gate after drafting** (`drafting → grilling | spec_jury`):
- Guard: `nio check spec` finds no open point and no unconfirmed `[default]`, and the scope lens finds nothing the intake doesn't ask for.
- Passes → skip the grill and go straight to the spec jury. Fails in auto mode → stop and ask the questions as one round, then carry on unattended once they're answered. The lite path (#44) already does this ("grilling skipped if nothing is ambiguous").
- Open: in auto mode, can the jury confirm a drafter's `[default]` instead of the human (#21)? Recommend no: a default goes to the human. Otherwise the drafter's guesses become decisions, which NORTH_STAR names as the main source of hallucination.

**C. The stop list is the only list that pauses an auto run.** Everything else proceeds and notifies (#7):
- a NORTH_STAR always-human item: DB scripts, secrets, breaking changes, anything irreversible, anything that can cost money
- the jury can't agree, or hits the round cap (2 rounds, then stop instead of looping)
- a change request against the effort, or an approved input whose version hash changed under it
- a budget count is used up (juries, subagents)
- a guard on a stage that isn't built yet (stop with "not built"; don't skip silently)

Each pause sets `waiting_on_human: <reason>`, and `nio flow next` prints that reason in the "Talking to the human" shape.

**D. A driver that needs no open session.** The run is a loop: `nio flow next` → run the named skill headless (`claude -p`, `codex exec`) → `nio flow done` → repeat until a pause or `done`. The driver is the single writer from decision 2. It can be a skill-less shell loop in `nio flow run <slug>`, because the guards decide, not the agent.

**E. Finding out what a run is doing without watching it.** You can't tell today:
- runs don't name their effort: `promote.md` has only the run ID, and implement runs (R-261028-jvdk, R-261028-mq6i) have no link anywhere
- nothing marks a parked effort (implementation-jury has sat since 10-27 22:06)
- several efforts run at once

Fix: `nio run` takes the slug and the stage or task. `nio flow status` gives one line per effort: state, auto or not, what it's waiting on, and last activity. History lines carry the run ID.

**F. Derive state, don't copy it.** Gate outcome, round and judged version (`jury/<gate>.json`), the pending question (`grill.md`), and pending change requests (`C-*` with `outcome: pending`) are already in files. `state.json` keeps only what no file holds: auto flag, pause reason, waiting-on, task claims and attempts, and the current run. History stays in `history.jsonl`. This keeps the single writer, and an approval withdrawn by a version change shows up without anyone updating the state.

### Order this suggests

1. Fix gate convergence (#55, #58): without it, no auto run gets past the spec gate.
2. `nio flow` with derived state, `status` and the stop list (this issue).
3. The sufficiency gate and the `--auto` flag.
4. The headless driver, once implement (#43) exists.

### Changes to the open questions

- **Q1 schema:** smaller, per F.
- **Q2 overrides:** the human closing a gate with a reason stays a normal exit, but in auto mode it's always a pause, never a skip.
- **New:** the auto flag (A), the sufficiency guard (B), the stop list (C), the driver (D), run → effort links (E).

Refs: `.nio/specs/*/jury/spec.json` (`closed` reasons) · `.nio/specs/*/grill.md` (`## Asked` sources) · `.nio/memory/project/C-261028-7njg-*` · `.nio/runs/*/promote.md` · #7 #21 #43 #44 #55 #58


### Comment, 2026-10-28

**Brainstorm Q1 (2026-10-28): state is read from files, and only the rest is stored.** `nio flow` reads gate outcomes, rounds and judged versions from `jury/<gate>.json`, pending questions from `grill.md`, and pending change requests from `C-*` records on every call. `state.json` stores only what no file holds: the auto flag, the pause reason, waiting-on, task claims and attempts, and the current run. History goes in `history.jsonl` beside it.

### Comment, 2026-10-28

**Brainstorm Q2 (2026-10-28): in auto mode the jury can confirm a drafter's `[default]`, as well as the human.** Each confirmation is recorded with who confirmed it (jury lens or human), so a jury-confirmed default stays visible and traceable. A default that falls under the NORTH_STAR always-human list (DB scripts, secrets, breaking changes, irreversible, money) still pauses for the human, because the stop list covers it. Outside auto mode nothing changes: only the human confirms (#21).

### Comment, 2026-10-28

**Brainstorm Q3 (2026-10-28): in auto mode the drafter turns every open point into a `[default]`, and the jury confirms it (Q2).** An auto run doesn't pause for gaps. A gap that falls under the always-human list still pauses through the stop list.

### Comment, 2026-10-28

**Brainstorm Q4 (2026-10-28): forced guesses are marked and checked harder.** A default the drafter invented for an open point gets its own tag (working name `[guess]`). Each one must be confirmed by a jury lens that's told it is a guess, and the end-of-run report lists every guess for the human.

### Comment, 2026-10-28

**Brainstorm Q5 (2026-10-28): an auto run spends at most 3 jury rounds on a gate, and stops sooner if a round closes no finding.** On either stop it pauses for the human and shows the open findings. A stuck jury (e.g. a tooling bug like #55 or #58) costs at most one wasted round.

### Comment, 2026-10-28

## Research 3 (2026-10-28): prior art for unattended spec → implementation runs

Web research, primary docs where possible. Points marked *unverified* rest on secondary sources.

**Readiness checks.** No tool refuses a vague issue.
- Spec Kit's `/clarify` rates 10 categories Clear, Partial or Missing and asks at most 5 questions per session. [clarify.md](https://github.com/github/spec-kit/blob/main/templates/commands/clarify.md)
- `/specify` keeps at most 3 `[NEEDS CLARIFICATION]` markers and guesses the rest into Assumptions. [specify.md](https://github.com/github/spec-kit/blob/main/templates/commands/specify.md)
- Devin 2.1 rates its confidence green, yellow or red before starting, and green tasks merge about 2× as often. [Devin 2.1](https://cognition.com/blog/devin-2-1)
- Kiro and OpenHands start from a label, with no readiness check.
- All of these use the model's own judgement. NIO's deterministic count (open points and unconfirmed defaults) has no equivalent.

**Stop policies.**
- Claude Code `-p` has `--max-budget-usd`, reports `total_cost_usd`, and `--permission-prompts none` denies actions instead of asking. [headless](https://code.claude.com/docs/en/headless)
- SWE-agent caps each task at $3. [config](https://swe-agent.com/latest/reference/model_config/)
- OpenHands' stuck detector trips on 3–4 identical repeats. [stuck detector](https://docs.openhands.dev/sdk/guides/agent-stuck-detector)
- Copilot's agent times out after 1 hour stuck, and Actions don't run on its pushes until a human approves. [troubleshoot](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/cloud-agent/troubleshoot-cloud-agent)
- Devin suspends with a reason: `inactivity`, `usage_limit_exceeded`, `out_of_credits`.

**Persisted state.**
- Temporal keeps no snapshot: it replays the event history, and human approval is a signal the workflow waits on.
- LangGraph keeps a checkpoint per thread, and a resumed node re-runs from its start, so steps must be idempotent. [interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts)
- Anthropic's long-running harness uses only files and git: a JSON feature list where agents may only flip `passes`, a progress file, a commit per session, and no editing of tests. [harness](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
- Kiro runs tasks in dependency waves. [specs](https://kiro.dev/docs/specs/)

**Driver loops.**
- Ralph is `while :; do cat PROMPT.md | claude; done`, with its state in files and git. [ghuntley.com/ralph](https://ghuntley.com/ralph/)
- Reported failures: duplicate work, placeholder code, a broken tree by morning, build pile-ups.
- Self-attestation is the documented risk: agents edit tests or scoring to pass. METR on o3; GSO found up to 30% reward hacks that tests missed. [METR](https://evaluations.metr.org/openai-o3-report)

**Observability.**
- Devin's status values: `working`, `waiting_for_user`, `waiting_for_approval`, `finished`.
- Cursor marks Slack threads ⏳/✅/❌ and posts a completion notice with the PR link.
- Claude Code and Codex stream JSON lines that end with a result and its cost.

### What to adopt for #45 (fits brainstorm Q1–Q5)

1. **State (Q1):** event log first, like Temporal and Anthropic's harness. `nio flow done` must be safe to repeat (LangGraph's re-run lesson).
2. **Guesses (Q3, Q4):** Spec Kit's "guess into Assumptions" is the same move Q3 chose. Q4's `[guess]` tag plus a harder jury check is the safeguard Spec Kit lacks.
3. **Stop list, numeric caps** to add beside Q5's round cap:
   - a cost cap per task and per effort (`--max-budget-usd`)
   - a wall-clock timeout per step
   - "the same guard failing with the same output 3 times" counts as stuck
4. **Driver:** a Ralph-shaped loop whose exit is NIO's guards, never what the agent says.
   - Workers run with permission prompts off, and a denied action counts as a stop-list pause.
   - The CLI, not the worker, runs the tests and records the cost in history.
5. **Anti-gaming guard:** in auto mode, a change to `tests.md` or to the tests after the plan is approved is a change request, and pauses the run.
6. **Status and notifications (#7):** `working`, `waiting_for_human:<reason>`, `suspended:<budget|stuck|timeout>`, `done`. Notify on wait, suspend and done only, never on progress.
7. **Scheduling:** Kiro-style waves once a worktree adapter exists.

Unverified: Copilot best-practice details, Factory's autonomy levels, OpenHands' 500-iteration default, whether Kiro asks questions before starting.


### Comment, 2026-10-28

**Brainstorm Q6 (2026-10-28): an auto run is capped by counts plus a stuck rule.** Per-effort count caps on juries and subagent runs come from config (`budgets`). The run pauses if the same guard fails with the same output 3 times. On either stop it pauses and reports what it used. There's no dollar cap and no time limit per step.

### Comment, 2026-10-28

**Brainstorm Q7 (2026-10-28): in auto mode, a change to a planned test after plan approval goes to a jury lens.** It covers the plan's test list and the existing planned tests; new tests are free. If the lens approves, the run continues. If it rejects, the change isn't applied. The red → green diff guard (no test deleted or weakened) stays. Known risk, accepted: the judging models are from the same family as the worker.

### Comment, 2026-10-28

**Brainstorm Q8 (2026-10-28): auto is switched on by `nio flow start <slug> --auto` or by an `nio:auto` label on the source issue.** Either way, the grant is written to the history with its source (flag or label, and who). Without one, every gate waits for the human.

### Comment, 2026-10-28

**Brainstorm Q9 (2026-10-28): notify on wait, stop and done; gate approvals go to the log.** The notify hook (#7) fires when the run enters `waiting_for_human`, when it is suspended by a cap or the stuck rule, and on `done`. Gate approvals are recorded in `history.jsonl` and listed in the end-of-run report, along with every `[guess]` and every jury-confirmed default. This narrows NORTH_STAR's 'human is always notified' to 'always told, in the report'; #46 should update the wording.

### Comment, 2026-10-28

**Brainstorm Q10 (2026-10-28): auto runs are driven by `nio flow run <slug>`, a CLI loop.** Each pass runs `next`, starts one fresh headless agent for the step (through the host adapter: `claude -p`, `codex exec`, …), then `done`. It stops on a pause, a cap or `done`. The CLI is the only writer, and it runs the guards and tests itself; the agent's own claim never counts. Workers run with permission prompts off, and a denied action is a stop-list pause. It lives as long as its terminal or CI job, so there's no daemon. Manual (non-auto) work keeps using `next`/`done` from a chat session.

### Comment, 2026-10-28

**Brainstorm Q11 (2026-10-28): unbuilt stages are skipped, logged and reported.** The flow keeps a list of which stages are built. A run that reaches an unbuilt stage records `skipped: not built` in `history.jsonl`, lists it in the end-of-run report, and moves to the next built stage. This holds in manual and auto mode, so the replay of past efforts (no advocate walk, no tasks stage) is valid. Implement is the exception: until it exists, an auto run ends at `implementing` and waits for the human.

### Comment, 2026-10-28

**Brainstorm Q12 (2026-10-28): the human can push any check through, with a reason.** `nio flow done <stage|task> --human "<reason>"` passes a failing guard. The history line keeps the failing guard output and the reason; it is its own record and never merged with another (#55's lesson). It is refused when called from inside `nio flow run` (an auto run). Closing a jury gate with a reason (`nio jury check --human`) counts as the same kind of exit.

### Comment, 2026-10-28

**Brainstorm Q13 (2026-10-28): runs are linked to their effort, and status is one line per effort.**
- `nio run <slug> <stage|T-n>` writes the effort and the stage or task into the run folder, and every history line carries its run ID.
- `nio flow status` prints one line per effort, newest first: state, auto or not, `working` / `waiting_for_human: <why>` / `suspended: <cap|stuck>` / `parked: <why>` / `done`, and last activity.
- `nio flow park <slug> "<why>"` marks an idle effort, and `nio flow start` or `next` resumes it.
- Efforts without the layout (`grilling/`, `jury/`) show as `legacy` and are left alone.

### Comment, 2026-10-28

**Brainstorm Q14 (2026-10-28): a change from any state sends the effort back to the stage that owns the changed file.** Two triggers:
- a pending `C-*` record against one of the effort's files
- an approved file whose content no longer matches the version its gate judged

Either one, from any state, moves the effort back to the owning stage, and the history line names the change. An auto run pauses for the human first. This replaces 'implementing ─change request→ the stage it's against' with 'any state ─…→'.

### Comment, 2026-10-28

**Brainstorm Q15 (2026-10-28): one task at a time for now.** `nio flow run` takes one ready task at a time, in `Depends on:` order, higher model tier first. `budgets.parallel` exists in config but stays at 1. Worktree-based waves are deferred until a worktree adapter exists, as a separate issue.

**Q16 and Q17, settled by earlier answers (2026-10-28):**
- **Grill sub-state:** `next` reads `grill.md` (an `## Asked` with no answer is the pending question). The grill keeps no state of its own (Q1).
- **Folder layout:** as in research comment 1, point 6, with `state.json` and `history.jsonl` in `.nio/specs/<slug>/`, both committed (decision 3). Which effort is current is a local pointer and isn't committed.

**All open questions are settled.** Implementation order (research comment 2): fix #55 and #58 → `nio flow` (derived state, `status`, `park`, the stop list, overrides, change-request reopening) → `[guess]` and the auto switch → `nio flow run`, which ends at `implementing` until #43 exists.

