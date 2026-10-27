# Intake

## Human, 2026-10-27

> yes start the #42 brainstorm

> Okey run spec for it

(The human answered #42's 12 questions in a grill session; each answer is a comment below.)

## Source: https://github.com/nikolajkarpic/nio/issues/42

### What needs designing

**The tasks stage of the flow (#19).** It breaks the approved plan into **epics and tasks** (NORTH_STAR: an effort holds epics, which hold tasks). Each task is small enough for one worker and one context pack (`nio pack`).

### What the design must define

- **Task format** (with #8 IDs). Each task names: its files, the AC it serves, its test, its dependencies, and whether it can run in parallel (spec-kit `[P]`: different files and no dependencies).
- **Grouping:** epics as independently shippable increments (like spec-kit's per-story phases), plus foundational work.
- **Difficulty rating** per task by the evaluator agent, which drives model and worker choice and parallel vs sequential execution. The usage estimate is #16.
- **Scope per task** (#18). Does the planner work out each task's files, or does the research skill?
- Output for the tasks jury (#28). Deterministic coverage checks run first.
- **When to stop:** every AC has at least one task, every task has an AC, the dependency graph has no cycles, and the human has seen the estimate.


## Decided (2026-10-27)

| # | Question | Decision |
|---|---|---|
| Q3 | What an epic is | One epic per user story, plus a foundational epic for shared setup when needed |
| Q5 | Status and "finished" | Status lives only in the CLI's state (#45). A task is finished when it reaches `done` through the guards, and an epic when all its tasks are `done` |
| Q1 | Where tasks live | One `.nio/specs/<slug>/tasks.md`, one section per epic |
| Q2 | IDs | `E-n` and `T-n`, numbered per spec, never reused, with removed ones listed as `retired:` |
| — | Jury records per epic | `jury/implementation-E-n.json`, one ledger per epic (settles #29 DF-2) |
| Q4 | Task fields | Six labelled lines, all required: Files, Serves, Test, Depends on, Parallel, Difficulty |
| Q6 | Difficulty | `low`, `medium` or `high` with a reason, mapped to the cheap, medium and strong model tiers |
| Q7 | Files per task | The tasks stage names them; the research skill (#18) re-checks later |
| Q8 | Task size | Judgement only, reviewed by the tasks jury |
| Q9 | Added tasks | A `#### Fixes` heading in the epic; each carries a `From:` line naming its finding or change request |
| Q10 | Input | The approved spec and the code now; the plan once #41 exists, and tasks must follow it. Design choices made at task time are recorded as decisions |
| Q11 | Estimate | Counts by epic, difficulty and tier, plus which tasks run in parallel. The human approves before implement |
| Q12 | Who runs it | A `@nio:tasks` skill (tasks-drafter agent plus evaluator) and `nio check tasks` (fields, IDs, coverage, cycles, parallel clashes, estimate) |

All open questions are settled.



### Comments

## Open questions: brainstorm all of these before implementing (2026-10-27)

Started so the implementation jury (spec `2026-10-27-implementation-jury`, #29) can be built. That spec's deferred points DF-1 (what an epic, a task and "finished" are, and where their files live) and DF-2 (how an epic's jury rounds are stored) are answered here. #45's open folder-layout question is answered here as well.

1. **Where tasks live:** one `tasks.md` per spec, one file per epic, or one file per task, and where in `.nio/specs/<slug>/` (#45 layout).
2. **IDs:** the task ID and epic ID format (#8). Are they numbered per spec, never reused, with retired IDs listed as in the spec?
3. **What an epic is:** grouped by user story (spec-kit's per-story phases, each shippable), by layer, or by the planner's judgement. Is there a separate foundational epic?
4. **Task fields:** files, the ACs it serves, its test, its dependencies, whether it runs in parallel, difficulty. Which are required, and is the format markdown or structured?
5. **Status:** is it a checkbox in the task file, or only in `state.json` (#45: the CLI owns transitions, a single writer)? What exactly is "finished" (#45's task `done`, after the `red → green → review` guards)?
6. **Difficulty:** the scale, who rates it (the evaluator agent), and what it drives (model tier, worker, parallel or not).
7. **Scope per task:** does the tasks stage work out each task's files, or the research skill (#18)?
8. **Size bound:** what makes a task small enough for one worker and one pack (a file count, one AC, or judgement)?
9. **Fix tasks:** how a task appended later (implementation jury fix tasks, "justify or remove", a rejected change request) is marked and linked to its finding.
10. **Input before the plan stage exists (#41):** what the tasks stage reads until a plan exists (the spec only, or a placeholder).
11. **The human's estimate:** what the human sees before implementing, given that the usage estimate (#16) is a nice-to-have (for example task counts by difficulty and tier).
12. **Who runs it:** an `@nio:tasks` skill plus a `nio check tasks` coverage check (#28, #50). What does the CLI check, and what does the agent do?

---

**Decided (2026-10-27), Q3: one epic per user story.**
- Each user story (US-n, with its priority and independent test) becomes one epic, so an epic is exactly what the spec says can ship by itself.
- When shared setup is needed, a **foundational epic** comes first, and the story epics depend on it.
- The implementation jury (#29) reviews one epic at a time, so each review covers one coherent slice.
- Cost: a tiny story still gets its own epic and its own jury run.

---

**Decided (2026-10-27), Q5: status lives only in the CLI's state, and "finished" means `done` reached through the guards.**
- The task file holds the plan only: no checkboxes and no status.
- Status lives in the state file #45 owns, and only `nio flow` changes it.
- A task is finished when it reaches `done` through #45's guarded steps (`claimed → red → green → review → done`), never on an agent's claim.
- An epic is finished, and ready for the implementation jury, when every task in it is `done`. This settles DF-1's "finished" for #29.
- Cost: status is read with a command, not seen in the file.

---

**Decided (2026-10-27), Q1: one `tasks.md` per spec.**
- `.nio/specs/<slug>/tasks.md` holds one section per epic, with that epic's tasks listed under it, in the same style as `spec.md`.
- The tasks jury and the coverage checks read one file.
- A worker's pack cuts out its own task.
- Cost: the file gets long on big specs.

---

**Decided (2026-10-27), Q2: epics are `E-n` and tasks are `T-n`, numbered per spec.**
- Tasks are numbered across the whole spec, not per epic. A task keeps its ID if it moves to another epic.
- IDs are never renumbered or reused. Removed IDs go in a `retired:` list, as in `spec.md`.
- Fix tasks the implementation jury appends take the next free `T-n` (#29 FR-27).
- This fixes the task ID format that `MEMORY_NORTH_STAR.md` left free-form (#8, D-261024-4xsd).

---

**Decided (2026-10-27): one jury ledger per epic.** This settles #29's DF-2.
- `.nio/specs/<slug>/jury/implementation-E-n.json` (and its `.md`) sits next to `jury/spec.json`.
- Each epic has its own rounds, findings and verdicts.
- The existing jury code works unchanged, with the gate named per epic.
- The verdict subject is `implementation-E-n:<slug>`.

---

**Decided (2026-10-27), Q4: every task states all six fields as labelled lines in plain markdown.**
```
### T-3 Reject an empty cart at checkout
- Files: src/checkout.py, tests/test_checkout.py
- Serves: AC-4, AC-5
- Test: checkout with an empty cart returns 400 "cart is empty"
- Depends on: T-1
- Parallel: no
- Difficulty: <scale from Q6>
```
- The CLI checks that every line is present and that every cited ID exists.
- Cost: small tasks still carry six lines.

---

**Decided (2026-10-27), Q6: difficulty is `low`, `medium` or `high`, with a one-line reason.**
- Format: `Difficulty: medium: touches the payment state machine`.
- `low` uses the cheap model tier, `medium` the medium tier and `high` the strong tier, the same three tiers the agent cards use.
- The evaluator agent rates each task, and the tasks jury reviews the ratings (NORTH_STAR).
- Cost: the scale is coarse, so a borderline task may get a bigger model than it needs.

---

**Decided (2026-10-27), Q7: the tasks stage names each task's files.**
- The tasks agent works out `Files:` from the spec and the code at planning time, so the coverage and parallel-conflict checks can see the files.
- Once the research skill (#18) exists, it re-checks a task's scope just before the worker starts and flags a mismatch.
- Cost: file lists can go stale between planning and running.

---

**Decided (2026-10-27), Q8: task size is a judgement call, with no fixed limits.**
- The tasks agent sizes each task for one worker and one context pack (NORTH_STAR's examples: "implement this class from this interface", "add this event in this file").
- The tasks jury reviews the sizes, and the CLI has no file-count or AC-count limit.
- Cost: catching an oversized task costs a jury finding, and runs may size tasks differently.

---

**Decided (2026-10-27), Q9: tasks added later go under a `Fixes` heading in their epic's section.**
```
## E-2 <story title>
### T-5 …            (planned tasks)
#### Fixes
### T-12 Reject a negative quantity
- From: J-4 (implementation-E-2, round 1)
- Files: …  (the same six lines as any task)
```
- Implementation jury fix tasks, "justify or remove" tasks and tasks from a rejected change request all go there.
- Each one carries a `From:` line citing its finding or change request.
- They take the next free `T-n`, and planned tasks above the heading are never edited.
- The coverage and parallel checks treat them like any other task.

---

**Decided (2026-10-27), Q10: tasks come from the approved spec and the code now, and from the plan once it exists.**
- Until the plan stage (#41) lands, the tasks agent derives tasks from the approved `spec.md` and the codebase.
- Any design choice the tasks agent makes is recorded as a decision (`@nio:remember`), so the tasks jury can see it.
- Once `plan.md` exists for a spec, the tasks stage reads it and must follow it.
- Cost: until then, design choices are made at task time and reviewed only by the tasks jury.

---

**Decided (2026-10-27), Q11: the human sees counts by epic, difficulty and tier, and approves before implementation starts.**
- A short table, computed free from `tasks.md`, shows each epic with:
  - its task count;
  - how many tasks are `low`, `medium` and `high` (cheap, medium and strong models);
  - which tasks can run in parallel.
- The human approves it before the implement stage starts. That meets NORTH_STAR's "see the estimate before anything is spent".
- There's no token or money figure until #16.

---

**Decided (2026-10-27), Q12: a `@nio:tasks` skill plus a free `nio check tasks`.**
- The skill runs a tasks-drafter agent that writes `tasks.md` from the approved spec (and the plan once it exists). An evaluator agent then rates each task's difficulty.
- `nio check tasks <slug>` checks, with zero model calls:
  - every task has the six fields;
  - cited AC, task and epic IDs exist;
  - coverage both ways (every AC has a task, every task serves an AC);
  - no dependency cycles;
  - no two parallel tasks share a file.

  It also prints the estimate table (Q11).
- This mirrors the spec stage: `@nio:spec` with `nio check spec`. The tasks jury (#28) runs after the check passes.

---

