# Intake

## The human's words (via the delegating orchestrator session)

Goal: one NIO effort implementing GitHub issue #76 ("Orchestrator turns cost more than the jury: drive a gate in fewer, smaller calls"). Read it plus #77 (roadmap), #90 (jurors copy `lens: logic` from the template) and #92 (a merged finding produced a wrong fix task). Fold in #90 if it fits the same change (the juror output path/template); leave #92 unless it is trivial. Target: halve orchestrator turns per gate with no change to what jurors see. Measure turns per gate before/after (count the tool calls the jury skill requires for one gate round, on a test fixture or a dry run) and put it in the PR.

Lazy and minimal: smallest diff that works. Skills stay plain markdown any agent can follow (CLAUDE.md rule); host-specific features (e.g. a gate-driver subagent) are optional notes only.

## Source: https://github.com/nikolajkarpic/nio/issues/76

# Orchestrator turns cost more than the jury: drive a gate in fewer, smaller calls

## Problem
At every gate, the orchestrator's own turns cost more time and money than the jurors do. The orchestrator is the main session: it is on the frontier model and carries 200–400k tokens of context.

Measured on implement-followups (session 322a1614, 2026-11-05; costs estimated from list prices):

| Gate | Wall | Orchestrator turns | Avg context | Orchestrator $ | Juror + refuter $ |
| --- | --- | --- | --- | --- | --- |
| spec | 10.2 min | 41 | 212k | 6.29 | 1.45 |
| plan | 5.5 min | 16 | 317k | 3.23 | 2.95 |
| tasks | 3.7 min | 15 | 351k | 2.98 | 0.32 |
| implementation E-1 | 95 min | 33 | 397k | 9.32 | 0.97 |

The jurors run in parallel and finish in about 1 minute (median 0.4–0.9 min per lens, refuter 0.5 min). So roughly 70% of a spec, plan or tasks gate's wall time is orchestrator turns. These are the calls to collect, collect again after the refuter, check, changed, building each fix-check pack, saving each juror's answer to a file, dispose one by one, and reading their outputs. On implementation-jury, the orchestrator also spent $47 against the workers' $30 while implementing.

## Proposal
1. **Fewer round trips.** Add one command that runs a gate step end to end, for example `nio jury next <slug> <gate> --run <run>`. It collects, says whether the refuter must run (and writes its batch), checks, and on `rerun` writes every fix-check pack to `.nio/runs/<run>/jury/packs/`. It prints only what the orchestrator must do next. Let `dispose` take several findings in one call.
2. **Jurors write their own output file.** The lens cards stay read-only on the project, but let them write to `.nio/runs/<run>/jury/<gate>-<lens>.md` only. The orchestrator then no longer pastes each answer back.
3. **Optional:** let a host run a gate in a fresh, cheaper "gate driver" subagent that gets the slug and gate and returns the outcome and the list for the human. The main context then doesn't grow by 100k+ tokens per gate.

Target: halve the orchestrator's turns per gate. That's about 15–20 min and about $15 per 5-epic effort, with no change to what the jurors see.

Refs: #74 (re-emits add turns too) · .nio/research/2026-11-06-speedup.md


## Source: https://github.com/nikolajkarpic/nio/issues/90

# Jurors copy `lens: logic` from the jury template, so collect reads their output as another lens

## Problem
In the 2026-11-07-scoped-task-commands spec gate, 2 of 3 jurors (testability, consistency) copied `lens: logic` from `nio jury template`'s example front matter. `nio jury collect` filed all their findings under logic and reported `testability: no output`, `consistency: no output`, costing two re-emits and duplicate ledger entries.

## Proposal
- Print the template with `lens: <your card's name>` (no real lens name), or have collect take the lens from the file name `<gate>-<lens>.md` and refuse a mismatch with a clear error.

Refs: #74 (lenient parser), #77

