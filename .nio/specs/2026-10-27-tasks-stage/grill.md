# Grill log: 2026-10-27-tasks-stage

Append-only. One entry per question, below-the-bar call or derived item.

## Session 1 · 2026-10-27 · @nio:grill, the human answers one at a time

## Facts · OP-1, OP-2, OP-3, OP-4 · 2026-10-27
Facet: actors (OP-1), meaning (OP-2), change (OP-3), data (OP-4)
Found: RF-1 to RF-16 (research.md). Contradictions raised: tiers (RF-7, RF-8), per-epic gate (RF-9), tasks jury lens (RF-16), state names and "approved" (RF-10, RF-12).
Patched: UJ-1, UJ-2, UJ-3, AC-3, FR-2, AC-4, FR-39, AC-21, two parallel-clash rows; retired OP-1, OP-2, OP-3, OP-4

## Asked · Q1 · contradiction (FR-17, RF-7, RF-8) · 2026-10-27
Question: Difficulty was decided as low/medium/high mapped to "cheap, medium, strong", but the real model tiers are cheap, strong and max. How should difficulty map?
Context: The assistant misstated the tiers during the #42 brainstorm. The agent cards use cheap (Haiku), strong (Sonnet) and max (Opus) (per the agents code). "low, medium, high" also already names the jury's risk tier on verdict records (per the records code), in a different file.
Options: 1. Keep low/medium/high, map to cheap/strong/max (recommended): your words stay; low runs on Haiku, medium on Sonnet, high on Opus. Lost: "medium" means a task difficulty in tasks.md and a jury risk tier in verdicts. 2. Rate directly in tiers (Difficulty: cheap|strong|max): no mapping, no clash. Lost: rates the model, not the task; renaming a tier changes every task. 3. Rename to easy/moderate/hard → cheap/strong/max: no clash. Lost: new words to learn.
Refs: FR-17, AC-26, RF-7, RF-8, agents.py:12,18, records.py:34

## Q1 · contradiction (FR-17, RF-7, RF-8) · 2026-10-27
Question: Difficulty was decided as low/medium/high mapped to "cheap, medium, strong", but the real model tiers are cheap, strong and max. How should difficulty map?
Options:
1. low/medium/high → cheap/strong/max (recommended)
2. Rate in tiers directly
3. Rename: easy/moderate/hard
Answer: free-form: "Okey so there are multiple different coding agents, we should judge the effort and the model, also Claude has fablr as well so we need to have that In here as well" [human]
Patched: none yet; follow-up Q2.

## Asked · Q2 · contradiction (FR-17) follow-up · 2026-10-27
Question: Should each task be rated like an agent card, with a model tier and an effort, and where does Fable fit?
Context: Agent cards already carry a host-neutral tier (cheap, strong, max) and an effort (low, med, high), and each coding agent (Claude, Codex) maps tiers to its own models in config (per the agents code). Claude's tiers today stop at Opus; Fable sits above it.
Options: 1. Tier + effort per task, new top tier for Fable (recommended): each task gets `Tier:` and `Effort:` like a card; a fourth tier `frontier` is added above max (Claude: Fable), and every host maps tiers to its own models. Lost: agent cards and config gain a tier; hosts without a frontier model fall back to max. 2. Tier + effort, Fable replaces Opus as max: no new tier. Lost: no way to pick Opus over Fable. 3. Name the exact model per task: most precise. Lost: tasks.md becomes host-specific; switching coding agent means rewriting tasks.
Refs: FR-15–FR-17, AC-26, agents.py:12-18, RF-7

## Q2 · contradiction (FR-17) follow-up · 2026-10-27
Question: Should each task be rated like an agent card, with a model tier and an effort, and where does Fable fit?
Options:
1. Tier + effort, new top tier (recommended)
2. Tier + effort, Fable as max
3. Name the exact model
Answer: 1. Tier + effort, new top tier: each task gets a Tier and an Effort line, like an agent card; a fourth tier, 'frontier', goes above max (Fable for Claude), and every coding agent maps tiers to its own models. Lost: agent cards and config gain a tier, and agents without a frontier model fall back to max. [human]
Patched: Summary, A-3, A-4, UJ-1, UJ-2, US-2, US-4, AC-8, AC-14, AC-25, AC-26, AC-27, AC-28, FR-7, FR-8, FR-14, FR-15, FR-16, FR-17, FR-18, Key entities, Glossary (Model tier, Effort), Risks; removed the difficulty-to-tier table; Decisions (D-261027-vi67)

## Call · FR-31 (per-epic gate, RF-9) · 2026-10-27
FR-31 fixes the ledger path per epic; the jury code change that accepts an `implementation-E-n` gate belongs to the implementation-jury spec, which builds that gate. [agent] Below the bar: what a user can do or sees, who may, data kept, cost: no change from the decided layout; only which spec delivers the code.

## Asked · Q3 · contradiction (Non-goal tasks jury lenses, RF-16) · 2026-10-27
Question: Should this spec ship the tasks jury's reviewer (executability), or leave it out?
Context: The spec lists the tasks jury's lenses as out of scope, but the lens catalog (#47) and agent set (#36) say the executability lens, a cheap check that each task can be carried out as written, ships with the tasks stage.
Options: 1. Ship executability here (recommended): one cheap lens card with an "At tasks" section, and the jury accepts the tasks gate; the tasks stage gets reviewed as soon as it exists. Lost: a bit more scope in this spec. 2. Leave it to #28: this spec stays smaller. Lost: tasks.md has no jury until #28 is built, so only the free check guards it. 3. Ship the card only, no gate: the lens exists but isn't wired into the jury. Lost: nothing runs it yet.
Refs: Non-goals, RF-16, #47, #36, #28

## Q3 · contradiction (Non-goal tasks jury lenses, RF-16) · 2026-10-27
Question: Should this spec ship the tasks jury's reviewer (executability), or leave it out?
Options:
1. Ship executability here (recommended)
2. Leave it to #28
3. Card only, no gate
Answer: 1. Ship executability here: one cheap reviewer card with a tasks section, and the jury accepts the tasks gate, so tasks.md gets reviewed as soon as this stage exists. Lost: a bit more scope in this spec. [human]
Patched: Non-goals (narrowed), new FR-41, FR-42, AC-40, AC-41

## Asked · Q4 · contradiction (state table, RF-12) + OP-5 · 2026-10-27
Question: Whose task states does this spec use: its own (starting at "planned"), or the state-machine issue's?
Context: The state-machine design (#45) already decided a task's states: pending → ready (its dependencies are done) → claimed → red → green → review → done, with a failed review going back to claimed and a failed task back to ready. This spec's table starts at "planned" and has no "ready". #45 doesn't say what happens when a green task's tests fail again.
Options: 1. Use #45's states; it owns the open cases (recommended): rename to pending and add ready; a failed review goes back to claimed, as #45 says; a green task failing again is left to #45, which builds the machine. Lost: one case stays open until #45 is built. 2. Use #45's states and settle the open case here: a green task whose tests fail again goes back to red. Lost: this spec decides part of #45's machine. 3. Keep this spec's own states: simpler. Lost: two definitions of a task's life that must later be reconciled.
Refs: State table, OP-5, RF-12, #45

## Q4 · contradiction (state table, RF-12) + OP-5 · 2026-10-27
Question: Whose task states does this spec use: its own (starting at "planned"), or the state-machine issue's?
Options:
1. Use #45's states (recommended)
2. #45's states, settle it here
3. Keep this spec's own states
Answer: 1. Use #45's states: rename to pending and add ready; a failed review goes back to claimed, as #45 says; a passing task failing again is left to #45, which builds the state machine. Lost: one case stays open until #45 is built. [human]
Patched: State table (pending, ready, review fails, task fails), FR-25; DF-1; retired OP-5

## Asked · Q5 · contradiction (FR-2, RF-10) · 2026-10-27
Question: Can the tasks stage start on a spec whose jury you closed yourself, rather than one the jury approved?
Context: The tasks stage only starts on an approved spec. The state-machine design (#45) asks for a jury "approve", but the last three specs, including both today, ended with you closing the gate (outcome "human"), each with a "nio: approve spec" commit (per git history and the verdict records).
Options: 1. Either counts: jury approved, or closed by you (recommended): the latest spec verdict is approved or human, so a gate you closed after settling the findings lets work move on. Lost: "approved" no longer always means the jury approved. 2. Jury approval only: strict. Lost: every spec closed by you today, including this one, could never move on without another jury run. 3. Your commit decides: the "nio: approve spec" commit is the signal. Lost: commits can be made by hand without any verdict, so the check is weaker.
Refs: FR-2, RF-10, RF-11, #45, jury.py compose

## Q5 · contradiction (FR-2, RF-10) · 2026-10-27
Question: Can the tasks stage start on a spec whose jury you closed yourself, rather than one the jury approved?
Options:
1. Jury or you (recommended)
2. Jury approval only
3. Your commit decides
Answer: 1. Jury or you: the tasks stage starts when the spec's latest verdict is either approved by the jury or closed by you, so a gate you closed after settling the findings lets work move on. Lost: 'approved' no longer always means the jury approved. [human]
Patched: FR-2 (closed = recorded in the ledger by `--human`; a gate merely handed to the human doesn't count), new AC-42, AC-43

## Asked · Q6 · OP-6 · 2026-10-27
Question: Which model tier and effort should the agent that rates tasks run on?
Context: No rating agent exists yet; it ships with this stage (per the agent-set issue #36), which gives it no tier. Its ratings choose the model for every task, so a bad rating costs either money (too high) or quality (too low). The tasks jury reviews the ratings afterwards.
Options: 1. strong, medium effort (recommended): Sonnet-class judges each task against the spec and code; reasonable cost, one run per spec. Lost: borderline tasks may be misjudged more than with max. 2. cheap, low effort: Haiku-class, cheapest. Lost: rating risky tasks needs judgement it may lack. 3. max, high effort: Opus-class, best judgement. Lost: costs more on every spec.
Refs: OP-6, FR-18, RF-13, #36

## Q6 · OP-6 · 2026-10-27
Question: Which model tier and effort should the agent that rates tasks run on?
Options:
1. strong, medium effort (recommended)
2. cheap, low effort
3. max, high effort
Answer: 1. strong, medium effort: a Sonnet-class model judges each task against the spec and the code, at reasonable cost, one run per spec. Lost: it may misjudge borderline tasks more often than a max model would. [human]
Patched: new FR-43, AC-44; retired OP-6

## Asked · Q7 · OP-7 · 2026-10-27
Question: When you approve the estimate, how is that recorded?
Context: Stage approvals are "nio: approve <stage>" commits (per CLAUDE.md and git history). The state-machine design (#45) commits automatically when the tasks jury passes, and has no separate step for approving the estimate.
Options: 1. One approval: tasks jury passes, then you approve the estimate, then "nio: approve tasks" (recommended): your estimate approval is the tasks stage's approval, recorded as one commit; implement can't start without it. Lost: #45's auto-commit on the jury passing waits for you instead. 2. Two records: "nio: approve tasks" when the jury passes, plus a separate estimate approval. Lost: two approvals for one stage. 3. No record, just a confirmation in the session: lightest. Lost: nothing durable shows you approved the spend.
Refs: OP-7, FR-33, RF-14, CLAUDE.md, #45

## Q7 · OP-7 · 2026-10-27
Question: When you approve the estimate, how is that recorded?
Options:
1. One approval commit (recommended)
2. Two records
3. Session confirmation only
Answer: 1. One approval commit: the tasks jury passes, you approve the estimate, then a single 'nio: approve tasks' commit records both; implementation can't start without it. Lost: #45's automatic commit when the jury passes waits for you instead. [human]
Patched: new FR-44, AC-45; retired OP-7

## Asked · Q8 · OP-8 · 2026-10-27
Question: Setup tasks in the foundational epic don't serve any one requirement. What does their "Serves" line say?
Context: Every task must serve at least one requirement, and the free check fails a task that serves none (coverage both ways, per #42). Setup work (a shared model, a config, a migration) enables several stories without being any story's requirement.
Options: 1. The requirements of the stories it enables (recommended): a setup task cites the ACs whose tasks depend on it, e.g. "Serves: AC-1, AC-4, AC-9"; the coverage check stays strict. Lost: a long Serves line on widely shared setup. 2. A special value "setup": Serves: setup, accepted only in the foundational epic. Lost: one exception in the coverage check, so unneeded setup is harder to spot. 3. The functional requirements instead of ACs: cites FR-n. Lost: two kinds of IDs in Serves.
Refs: OP-8, FR-11, FR-5, #42 Q12

## Q8 · OP-8 · 2026-10-27
Question: Setup tasks in the foundational epic don't serve any one requirement. What does their "Serves" line say?
Options:
1. The ACs it enables (recommended)
2. A special 'setup' value
3. Cite FRs instead
Answer: 1. The ACs it enables: a setup task cites the requirements whose tasks depend on it, e.g. 'Serves: AC-1, AC-4, AC-9', so the coverage check stays strict. Lost: a long Serves line on widely shared setup. [human]
Patched: new FR-45, AC-46; retired OP-8

## Call · OP-9 → FR-46 · 2026-10-27
A story epic depends on the foundational epic only through its tasks' `Depends on:` lines; no epic-level line. [agent] Below the bar: what a user can do, sees, who may, data kept, cost: no (the task field already exists; this adds no new line).

## Call · OP-12 → FR-47 · 2026-10-27
Parallel vs sequential comes only from `Parallel:` and `Depends on:`, never from tier or effort. [agent] Below the bar: each task already states Parallel (Q4 of #42); tier picks only the model. No change to what a user can do, sees, who may, data, or cost.

## Asked · Q9 · OP-10, OP-11 · 2026-10-27
Question: What exactly may run in parallel?
Context: A task marked "Parallel: yes" can run beside others. The free check fails two parallel tasks that share a file (per #42). Spec-kit's parallel mark means "different files and no dependencies". It's open whether the clash check spans the whole spec or one epic, and whether a parallel task may have dependencies.
Options: 1. Spec-kit's rule, checked across the whole spec (recommended): a parallel task has no unfinished dependency when it starts (it may depend on tasks that run before it), and no two parallel tasks anywhere in the spec share a file, since epics can run side by side. Lost: stricter, so fewer tasks qualify as parallel. 2. Within one epic only: epics run one after another, so clashes are only checked inside an epic. Lost: if epics ever run side by side, two tasks could write the same file. 3. Parallel means no dependencies at all: the simplest rule. Lost: tasks after the setup epic could never be parallel.
Refs: OP-10, OP-11, FR-13, FR-37, Rules (parallel clash), #42 Q12

## Q9 · OP-10, OP-11 · 2026-10-27
Question: What exactly may run in parallel?
Options:
1. Whole spec, deps done first (recommended)
2. Within one epic only
3. No dependencies at all
Answer: 1. Whole spec, deps done first: a parallel task may depend on tasks that finish before it starts, and no two parallel tasks anywhere in the spec share a file, since epics can run side by side. Lost: stricter, so fewer tasks qualify as parallel. [human]
Patched: new FR-48, AC-49, AC-50; retired OP-10, OP-11

## Asked · Q10 · OP-13 · 2026-10-27
Question: Who builds the tool that hands a worker just its own task out of tasks.md?
Context: A worker gets one task and its context pack, never the whole spec folder (per the implement-stage issue #43). Cutting one task (with its epic's title) out of tasks.md is a small free command. Workers only exist once the implement stage (#43) is built.
Options: 1. This spec, as `nio task show <slug> T-n` (recommended): it's part of reading tasks.md, sits beside `nio check tasks`, and the tasks jury can use it too. Lost: built before anything consumes it. 2. The implement stage (#43): built when workers exist. Lost: #43 has to learn the tasks.md format separately. 3. No command: the worker's pack quotes the task by hand. Lost: an agent copies text, which can drift.
Refs: OP-13, FR-35, AC-39, #43

## Q10 · OP-13 · 2026-10-27
Question: Who builds the tool that hands a worker just its own task out of tasks.md?
Options:
1. This spec: `nio task show` (recommended)
2. The implement stage (#43)
3. No command
Answer: 1. This spec: `nio task show`: `nio task show <slug> T-n` prints one task with its epic's title; it belongs with reading tasks.md, sits beside `nio check tasks`, and the tasks jury can use it too. Lost: it's built before anything uses it. [human]
Patched: FR-35, AC-39; retired OP-13

## Asked · Q11 · OP-14 · 2026-10-27
Question: A "justify or remove" task exists because the jury found code no requirement asked for. What does its "Serves" line say?
Context: Every task must serve at least one requirement (the free coverage check). By definition, this code serves none. The task's outcome is either a justification (then a change request adds the requirement) or removal.
Options: 1. Cite the finding instead, allowed only under Fixes (recommended): "Serves: J-4"; the coverage check accepts a finding ID only for tasks under the Fixes heading with a From line. Lost: one exception in the coverage rule. 2. Cite the nearest requirement the code touches: no exception. Lost: it claims the code serves a requirement it doesn't. 3. "Serves: none", allowed only under Fixes: honest and simple. Lost: nothing links the task to a requirement or finding in Serves (only in From).
Refs: OP-14, FR-11, FR-27, #29 FR-29

## Q11 · OP-14 · 2026-10-27
Question: A "justify or remove" task exists because the jury found code no requirement asked for. What does its "Serves" line say?
Options:
1. Cite the finding (recommended)
2. Nearest requirement
3. 'Serves: none'
Answer: 1. Cite the finding: 'Serves: J-4'; the coverage check accepts a finding ID only for tasks under Fixes that have a From line. Lost: one exception in the coverage rule. [human]
Patched: new FR-49, AC-51; retired OP-14

## Asked · Q12 · OP-15, OP-16 · 2026-10-27
Question: Once you've approved the estimate, can planned tasks still change, and where do tasks for an accepted change request go?
Context: After approval, added tasks go under each epic's Fixes heading and planned tasks are never edited (per #42). An accepted change request may add or change a requirement, which needs new or different work.
Options: 1. Frozen after approval; new work goes under Fixes, with From naming the change request (recommended): planned tasks never change once approved; a change request's tasks are appended like fixes; a task made pointless is retired, never rewritten. Lost: tasks.md grows by appending rather than staying tidy. 2. Re-draft the affected epic, then re-approve: tidy. Lost: rewriting approved tasks, which breaks the audit trail and needs a new estimate approval. 3. Frozen, and change requests restart the tasks stage for the whole spec: clean slate. Lost: work already done is re-planned.
Refs: OP-15, OP-16, FR-10, FR-29, FR-40, #42 Q9

## Q12 · OP-15, OP-16 · 2026-10-27
Question: Once you've approved the estimate, can planned tasks still change, and where do tasks for an accepted change request go?
Options:
1. Frozen; append under Fixes (recommended)
2. Re-draft the epic, re-approve
3. Restart the tasks stage
Answer: 1. Frozen; append under Fixes: planned tasks never change once approved; a change request's tasks are appended under Fixes, with From naming the change request; a task made pointless is retired, never rewritten. Lost: tasks.md grows by appending rather than staying tidy. [human]
Patched: new FR-50, AC-52, AC-53; Rules (accepted change request row); retired OP-15, OP-16

## Asked · Q13 · OP-17 · 2026-10-27
Question: A bug-fix spec has no user stories, only current, expected and unchanged behaviour with their ACs. How does the tasks stage split it into epics?
Context: Epics are one per user story (per #42). A bug-fix spec is usually small, and its expected-behaviour ACs are the tests written first (per the bug-fix template). The separate lite path (#44: repro, red, fix, jury) may not use the tasks stage at all.
Options: 1. One epic for the whole fix (recommended): a bug-fix spec becomes a single epic E-1 holding all its tasks, so the implementation jury reviews the fix as one unit. Lost: a large multi-part fix is juried in one go. 2. One epic per expected behaviour: each EB-n with its ACs is an epic. Lost: tiny epics, each with its own jury run. 3. Bug-fix specs skip the tasks stage: the lite path (#44) handles them. Lost: depends on #44, which isn't designed; until then a bug fix has no tasks.
Refs: OP-17, FR-4, spec-bugfix template, #44

## Q13 · OP-17 · 2026-10-27
Question: A bug-fix spec has no user stories. How does the tasks stage split it into epics?
Options:
1. One epic for the whole fix (recommended)
2. One epic per expected behaviour
3. Skip the tasks stage
Answer: 1. One epic for the whole fix: a bug-fix spec becomes a single epic, E-1, holding all its tasks, so the implementation jury reviews the fix as one unit. Lost: a large multi-part fix is juried in one go. [human]
Patched: new FR-51, AC-54; retired OP-17

## Call · FR-36, FR-37, AC-13 · 2026-10-27
`Depends on: none` is the empty form; `Parallel:` takes only yes or no. [agent] Below the bar: format details of fields the human already required; no change to what a user can do, sees, who may, data kept, or cost.

## Call · NFR-2 · 2026-10-27
`nio check tasks` finishes in under 2 seconds on 200 tasks. [agent] Below the bar: a free local check; no change to what a user can do, sees, who may, data, or cost.

## Derived · AC-11, AC-12, AC-14, AC-15, AC-30, AC-34, FR-16, FR-24, FR-28, FR-38, FR-40, Non-goal (#45/#43) · 2026-10-27
From: FR-6 (permanent unique IDs, retired never reused), FR-8 and FR-15 (field values), FR-23 (no status in tasks.md), FR-25, FR-27 (From line under Fixes), FR-33 and FR-44 (approval).

## Finish gate · 2026-10-27
`nio check spec --gate`: 0 errors. Fidelity re-read of FR-2, FR-15, FR-17, FR-35, FR-41–FR-51 against Q1–Q13: tier values (cheap, strong, max, frontier), effort (low, med, high), "closed by the human" vs "handed to the human", frozen after approval, whole-spec clash check, one epic for bug fixes all match the answers.
Human chose: finish. Next stage: spec jury.

## Session 2 · 2026-10-27 · jury round 1 findings that change behaviour, the human answers

## Asked · Q14 · J-19 · 2026-10-27
Question: When a coding agent has no model for a tier, what should happen?
Context: Today an agent card whose tier has no model on a host gets a warning and quietly runs on whatever model the session uses (per the agents code). This spec says a host with no frontier model uses its max model instead. It doesn't say whether that rule replaces today's for other tiers too.
Options: 1. Fall back one tier down, for every tier, with a warning (recommended): frontier falls back to max, max to strong, and so on, for cards and tasks alike, so a task never silently runs on an unknown model. Lost: changes today's behaviour for existing cards. 2. Max fallback for frontier only; other tiers keep today's warning-and-inherit: smallest change. Lost: two rules for one problem. 3. Refuse to run: a missing mapping is an error until config names a model. Lost: a new tier breaks every host until configured.
Refs: J-19, FR-17, AC-26, agents.py resolve/render

## Q14 · J-19 · 2026-10-27
Question: When a coding agent has no model for a tier, what should happen?
Options:
1. One tier down, every tier (recommended)
2. Only frontier → max
3. Refuse to run
Answer: 1. One tier down, every tier: frontier falls back to max, max to strong, and so on, with a warning, for agent cards and tasks alike, so nothing silently runs on an unknown model. Lost: it changes today's behaviour for existing cards. [human]
Patched: new FR-52, AC-58

## Session 3 · 2026-10-28 · change request C-261028-7njg (build on the plan stage and the plan jury), accepted by the human

## Patched from C-261028-7njg · 2026-10-28
Points 1, 2, 4, 5 and 7 of the accepted change request: the plan rules apply to full specs and the no-plan rules to bug-fix specs; a full spec's tasks stage also needs `nio check plan --approved`; epics follow the plan's build order with its dependencies; `nio check tasks` checks that each entry's bound files and planned tests land in its epic; a spec or plan change withdraws the tasks approval.
Patched: A-2, FR-2, FR-4, FR-5, FR-9, FR-20, FR-21, AC-5, AC-6; added FR-53, FR-56, AC-59, AC-61, AC-63; removed the non-goal on #41 and the risk on design choices at task time

## Asked · Q15 · C-261028-7njg point 3 · 2026-10-28
Question: Pick one: on a bug-fix spec (which has no plan), may the tasks drafter still make a design choice and log it?
Context: On a full spec the plan settles the design, so the drafter makes none there. A bug fix has no plan stage, so today the drafter picks, logs it as a memory candidate and names it in the epic for the tasks jury to see. Bug fixes are usually small, but some still need a choice.
Options: 1. Yes, logged and judged (Recommended): keep today's rule for bug fixes only. 2. No, ask the human: the drafter stops and asks for any design choice on a bug fix. 3. No, it's a full spec then: a bug fix that needs a design choice is re-routed to a full spec with a plan.
Refs: C-261028-7njg point 3 · FR-22, AC-7

## Q15 · C-261028-7njg point 3 · 2026-10-28
Facet: change
Question: On a bug-fix spec (which has no plan), may the tasks drafter still make a design choice and log it?
Options:
1. Yes, logged and judged (recommended)
2. No, ask the human
3. No, it's a full spec then
Answer: 3. No, it's a full spec then: a bug fix that needs a design choice is re-routed to a full spec with a plan. Cleanest separation, but costs a whole plan stage for what may be a small fix. [human]
Patched: FR-22 and AC-7 retired; added FR-54, AC-60

## Asked · Q16 · C-261028-7njg point 6 · 2026-10-28
Question: Pick one: on a full spec, should each task's `Test:` line cite the plan's test entry (TC-n) instead of describing the test in words?
Context: The plan now lists one concrete test per acceptance criterion, each with a TC-n ID. On 2026-10-27 tests were decided to carry no spec IDs, and linking tasks to the plan's test list was rejected then only because that format wasn't fixed yet (D-261027-b44u). The ID would sit in tasks.md only; test code still carries none.
Options: 1. Cite TC-n on full specs (Recommended). 2. TC-n plus a short phrase. 3. Keep words only.
Refs: C-261028-7njg point 6 · FR-7 · D-261027-b44u

## Q16 · C-261028-7njg point 6 · 2026-10-28
Facet: verification
Question: On a full spec, should each task's `Test:` line cite the plan's test entry (TC-n) instead of describing the test in words?
Options:
1. Cite TC-n on full specs (recommended)
2. TC-n plus a short phrase
3. Keep words only
Answer: 1. Cite TC-n on full specs: `Test: TC-3`, so `nio check tasks` can prove for free that every planned test lands in a task, and the worker gets the exact test. Bug fixes keep words. [human]
Patched: added FR-55, AC-62; FR-9 now also covers `TC-n`; decision record D-261028-scwb

## Fix · J-20, J-21 (jury round 4 notes) · 2026-10-28
The human asked for both notes to be fixed and re-checked. AC-1, AC-2 and AC-42 now name the route: a full spec whose plan is approved. The Decisions line for D-261027-b44u now applies to bug-fix specs, with full specs pointing to D-261028-scwb. Wording only; no behaviour changes.
Patched: AC-1, AC-2, AC-42, Decisions
