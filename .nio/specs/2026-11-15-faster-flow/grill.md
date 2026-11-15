# Grill: 2026-11-15-faster-flow

Session 1 (2026-11-15): the human answered one question (the risk flags) and then delegated the rest to the agent (grill / claude-code / opus): "Delegate to agent". Each call below takes the recommended option and is tagged [agent]; the human reviews them at the spec gate. Permissions, deletion, money, irreversible steps and breaking changes still go to the human. The only breaking change, dropping per-task red/green, is the human's own ask (#151, intake).

## Q1 · risk flags · 2026-11-15
Question: Should this effort carry the "auth" and "migration" risk flags?
Options:
1. Keep migration only (recommended)
2. Keep both
3. Drop both
Answer: 1. Keep migration only: still checks how in-flight efforts move over and how that's rolled back; drops the security lens; this effort can run on auto. [human]
Patched: risk: [migration]

## Lookup · OP-1, OP-17, OP-19, OP-20, OP-21, OP-23 · 2026-11-15
Facet: meaning, actors, change, verification
Found: RF-1 to RF-21 in research.md. OP-1: actors rest on the intake, #151, #130, #122 and personas P-1/P-3 (RF-1 to RF-4); P-2 Teammate (rules a capped batch) is untouched by this change, so not added. OP-17: neither the mod nor 74b529e settles it; `nio jury run` doesn't exist, the long commands are `nio jury evidence`, `nio flow green` and the suite (RF-5 to RF-10) → FR-13, AC-14 patched. OP-19: grant, `[auto]` tag and driver claim exist only on #122's branch; `main` has the auto key, the stop list and the risky-commit rule (RF-11 to RF-14) → FR-20, FR-21 retired as already on `main`, FR-17 patched. OP-20: the pr gate still appends fix tasks (RF-15, RF-16) → FR-35, FR-36, FR-39 hold. OP-21: the "isn't in the diff" check still runs at the pr gate (RF-17, RF-18) → FR-40 holds. OP-23: every task needs a Test field, but nothing checks an epic has one (RF-19 to RF-21) → FR-10 holds.

## Lookup · OP-12, OP-13, OP-14, OP-15, OP-16 · 2026-11-15
Facet: permissions, failure
Found: RF-22: #122's approved spec already settles when auto is granted, what the fixer may change alone, budgets, how the run ends (PR, never merge) and how the human is told. Patched FR-16, FR-19, FR-22, AC-23 to point at it; retired the five OPs.

## Call · OP-2 · FR-41, AC-42
Question: What replaces red's proof that a new test checks something?
Options: 1. The test-proof lens at the pr gate (recommended): a juror that already exists at the plan gate judges each added test, at the cost of one lens run per effort. 2. A blank-out check at epic end: mechanical, but new code and slow test runs. 3. Nothing: the conformance lens only checks that a test exists.
Answer: 1 [agent]. Changes what it costs (one lens), so logged as a call for the human's review.

## Call · OP-3 · Risks
Answer: no size cap on an epic; the tasks drafter keeps an epic to one user story. [agent] Below the bar: changes nothing a user can do or see, no data, cost only if an epic overflows.

## Call · OP-4 · FR-42, AC-43
Options: 1. A fresh agent with the failing tests and output tail, 3 failed runs then blocked for the human (recommended): fits short-lived drivers and the existing 3-attempt rule. 2. The same agent retries: keeps context but grows it. 3. Fix tasks: the per-task loop this effort removes.
Answer: 1 [agent].

## Call · OP-5 · FR-43, AC-44
Options: 1. Independent epics in parallel through the existing waves (recommended): E-2 to E-6 of #142 were independent and ran in parallel drivers. 2. One epic at a time: simpler, slower.
Answer: 1 [agent].

## Call · OP-6 · FR-44, AC-45
Options: 1. In-flight efforts move to per-epic at their next claim; done tasks stay done (recommended): no old red/green code kept. 2. They finish on the old flow: keeps two implement stages in the code.
Answer: 1 [agent]. Rollback (migration flag): revert the change; done tasks' commits are untouched either way.

## Call · OP-7 · FR-1
Answer: one agent per epic (#151), not one for the whole effort. [agent] The human's "pass it all to one agent to implement" is about how this effort itself is built (recorded as the build plan below), not a product rule.

## Call · OP-8, OP-9, OP-10 · FR-12, FR-45, AC-46
Answer: `nio check tasks` catches explicit cross-epic dependencies from task fields (FR-12); the subtler case, a guard or suite check from an early epic that only a later task can satisfy, goes to the executability lens at the tasks gate (FR-45). [agent]

## Call · OP-11 · FR-14, AC-15
Answer: the mod comes on through `@nio:install`, which #142 (in flight) makes install the Claude Code mods; this effort adds only the coverage (FR-13) and the warning (FR-15). [agent]

## Call · OP-18 · FR-17, Risks
Options: 1. Carry #122's built work over (grant, `[auto]` tag, driver claim) and build the rest here, with this spec replacing #122's epic jury (recommended). 2. Rebuild everything from `main`: throws away 18 commits.
Answer: 1 [agent].

## Call · OP-22 · FR-34, AC-35
Answer: the hand-off names both `/nio:<stage>` and `skills/<stage>/SKILL.md`. [agent] Below the bar except what a user sees; it only adds text.

## Call · remaining [default] items
Answer: every other drafter proposal (FR-2, FR-4, FR-9, FR-11, FR-15, FR-23 to FR-33, FR-37, FR-38, their ACs, AC-3, AC-13, NFR-1, NFR-2, SC-1, SC-3, SC-4, the state and decision tables, the key entities, actors, journeys, non-goals and risks) taken as proposed. [agent]

## Build plan (the human's words, not a spec item)
"we want to do spec, plan tasks and then we want to pass it all to one agent to implement and run one jury fix all the issues with one agent and be done with this speedup": after tasks, one implementation agent builds the whole effort, one pr-gate jury reviews it, one fix agent settles the findings, then a PR.

## Call · J-1 · decision table, UJ-2
Answer: the gate-outcome table gains a gate column; the pr gate always waits for the human, matching FR-22 and AC-23; UJ-2 step 2 names the exception. [agent] No behaviour change: FR-22 already said it.

## Call · J-2 · state table, key entities
Answer: the epic gains a `blocked` state after its 3rd failed run (FR-42), whose claim is refused; the human unblocking it sends it back to `waiting` and resets its failed-run count. [agent]

## Call · J-3 · FR-44, AC-45, state table
Options: 1. An in-flight epic whose tasks are all done goes through one flow test run and closes only if it passes (recommended): keeps FR-3's "no close without the flow's run". 2. Close it as a named exception to FR-3: faster, but trusts the old per-task runs.
Answer: 1 [agent].

## Call · J-6 · Decisions (FR-41)
Answer: the Decisions line now says the test-proof lens is the delegated grill's call on OP-2, for the human's review at this gate. [agent] Scope unchanged.

## Call · J-8 · Decisions (FR-44)
Answer: a Decisions line records converting in-flight efforts as the delegated grill's call on OP-6 (no per-task path survives FR-5), for the human's review at this gate. [agent] Scope unchanged.

## Call · J-11 · SC-1
Answer: SC-1 names the measure: replay #142's first epic unchanged on the new implement stage; at most 29 min agent and 6 min shell by the usage record. [agent]

## Call · J-13 · AC-32
Answer: AC-32's Observable is now deterministic: a deleted record is skipped, and a half-way rebuild leaves the whole old index readable. [agent]

## Call · J-15 · FR-4, AC-47, state table
Options: 1. A run that errors, collects no test, or passes 30 minutes is a failed run and counts toward the 3 (recommended): no epic sits in `testing` for good. 2. Such a run blocks the epic for the human at once: safer, more stops.
Answer: 1 [agent]. Also sets the recorded output tail at 50 lines.

## Call · J-4 · FR-1, FR-9
Answer: a claim picks the first epic that is waiting or failed and whose dependencies are closed; it is refused only when a named epic is already claimed or none is left. [agent] Reconciles AC-9 with AC-44.

## Q2 · auto approvals · 2026-11-15
Question: When an effort is in auto mode, which of today's "by human" steps should the flow do by itself?
Options:
1. Every gate except the PR (recommended)
2. Everything, PR gate too
3. Only non-risky gates
Answer: 1. Every gate except the PR: auto approves the spec, plan and tasks gates (risky specs too), and does unblocks, overrides and 'seen' by itself. It still stops at the final PR: the merge stays yours. You lose the stop on risky specs (money, migration, deletion, auth). [human]
The human's words before it: "I also want this approve by human to run auto when i set the nioflow in auto mode".
Patched: FR-46, FR-47, AC-48, AC-49, UJ-2 step 4, US-4 independent test, Gate-outcome table, SC-3, Glossary "Auto", Decisions.

## Q3 · auto loop · 2026-11-15
Question: Under auto, what happens when an epic gets blocked after 3 failed test runs?
Options:
1. Stop for me (recommended)
2. One auto retry, then stop
3. Leave it as is
Answer: 1. Stop for me: an epic blocked by its own 3 failed runs pauses the auto run until you look. Other unblocks stay automatic. Costs you one stop, but only when an epic is really stuck. [human]
Raised by the logic juror's aside in round 3 (unblock resets the failed-run count, so auto could retry forever). AC-49 also now tests all four auto steps (J-16).
Patched: FR-47, AC-49.
