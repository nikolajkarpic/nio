# Grill: 2026-11-14-short-lived-drivers

The human answered the three decisions (Q1-Q3); an agent looked up the facts (research.md RF-1 to RF-12) and took
the calls below the bar, each logged with its five no's.

## Q1 · OP-1 · 2026-11-14
Question: How much work should one fresh driver do before it ends?
Context: The driver on effort #49 ran 590 turns at a 432k average context and cost about $177 on 2026-11-08 (RF-4); the smaller the unit, the smaller each driver's context, but each restart costs a brief.
Options:
1. One gate or one epic (recommended): a fresh driver per review stage (the spec, plan and tasks gates) and per epic (its tasks and its implementation jury).
2. One task or one review round: smaller contexts, many more restarts and briefs.
3. A token budget: restart a driver once its context passes a set size, wherever it is in the work.
Answer: 1. One gate or one epic: a fresh driver per review stage (spec, plan, tasks gate) and per epic (its tasks and its implementation jury). [human]
Refs: OP-1, FR-1, FR-2, RF-4, #128
Patched: FR-1, FR-2, Unit of work; retired OP-1

## Q2 · OP-2 · 2026-11-14
Question: Who writes the brief a fresh driver starts from?
Context: Everything a driver needs is saved state today: `nio flow next`, `state.json`, `history.jsonl`, the gate ledgers and `tasks.md` (RF-1 to RF-3).
Options:
1. nio generates it (recommended): a new command (for example `nio flow brief <slug>`) prints the brief from saved state: the stage, the open tasks and findings, the next command and the skill to follow. No free-text notes from the outgoing driver.
2. The outgoing driver writes it: it can carry what saved state misses, but grows with each driver's habits and can't be checked.
3. Both: the generated brief plus a short note from the outgoing driver.
Answer: 1. nio generates it: a new command (e.g. `nio flow brief <slug>`) prints the brief from saved state: stage, open tasks and findings, next command, the skill to follow. No free-text notes from the outgoing driver. [human]
Refs: OP-2, FR-3, RF-1, RF-2, RF-3
Patched: FR-3, FR-14, AC-3, AC-15, Brief; retired OP-2

## Q3 · OP-6 · 2026-11-14
Question: On a host without subagents, how is a unit run?
Context: The repo names Claude Code and Codex as hosts, and what other hosts offer is unknown (RF-7).
Options:
1. Main session does it (recommended): the main session runs the unit itself from the same brief; nothing stops for the human.
2. Ask for a fresh session: the human starts a new session from the brief for each unit; smallest context, but the effort stops at every unit.
3. Main session, and suggest a restart: it runs the unit and tells the human a fresh session would be cheaper.
Answer: 1. Main session does it: on a host without subagents the main session runs the unit itself from the same brief; nothing stops for the human. [human]
Refs: OP-6, FR-13, RF-7
Patched: FR-13, AC-14, FR-5 (scoped to hosts with subagents); retired OP-6

## Research · OP-3, OP-4, OP-5, OP-7, OP-10 · 2026-11-14
OP-3: the handoff state is `nio flow next` over `history.jsonl`, `state.json`, the gate ledgers and `tasks.md`, and it exists at every gate and epic (RF-1, RF-2, RF-3). OP-4: the 2026-11-08 numbers support both journeys (RF-4). OP-5: no driver claim on this branch; the claim is on the unmerged full-auto branch (RF-5, RF-6). OP-7: Claude Code has background runs with completion notices and a 10-minute foreground limit; every other host is unknown (RF-7, RF-8). OP-10: the steps that read juror outputs, packs or test output are listed in RF-10, plus RF-11's timed retry.
Patched: FR-3, FR-5, FR-9, FR-15, A-4, UJ-1, UJ-2, AC-16; retired OP-3, OP-4, OP-5, OP-7, OP-10

## Call · OP-8, FR-10, AC-11, decision table row 3 · 2026-11-14
Blocking-wait timeout: 10 minutes, Claude Code's foreground maximum (RF-8). On a timeout the agent checks once whether the command finished and, if not, waits again; after the third wait that times out it ends the driver with a summary naming the unfinished command and how to continue. A host with neither notices nor a timed wait runs the command in the foreground until it returns. [agent]
Five no's: changes what a user can do: no; what they see: no (only an unfinished long command, which today ends in a loop, now ends in a hand-back they'd see anyway as a waiting effort); who may do it: no; data kept or changed: no; cost: no (it caps waiting; it adds none).
Patched: FR-10, AC-11, decision table row 3; retired OP-8

## Call · OP-9, NFR-2 · 2026-11-14
Brief size: at most 80 lines. [agent]
Five no's: changes what a user can do: no; sees: no (the human never reads the brief); who may do it: no; data: no; cost: no (a cap only lowers it).
Patched: NFR-2, AC-15; retired OP-9

## Call · FR-12, AC-6 · 2026-11-14
One driver at a time is a rule for the main session: it starts a unit's driver only after the previous one has ended (FR-6), and starts none while one it started is running. No lock: none exists on this branch (RF-5), and the full-auto driver claim is unmerged with its staleness rule still pending (RF-6). When that branch merges, each short-lived driver takes and releases the claim for its unit; that is for its plan, not this spec. [agent]
Five no's: changes what a user can do: no; sees: no; who may do it: no; data: no (no new file); cost: no.
Patched: FR-12, AC-6; retired OP-5

## Call · risk flag · 2026-11-14
The drafter set `risk: [public-api]`. The flag only adds the adversary lens (RF-12); skill text is not a public API, and the one new command, `nio flow brief`, is read-only over local saved state and changes no existing command's arguments or output. Set `risk: []`. Every earlier spec in this repo also carries `public-api`, by habit as far as the code shows; nothing in the code makes that a rule. [agent]
Five no's: changes what a user can do: no; sees: no; who may do it: no; data: no; cost: no (one lens fewer at the spec and implementation gates).
Patched: front matter `risk`

## Call · NFR-1, SC-1, SC-2, SC-3, non-goals 3 and 4 · 2026-11-14
Summary at most 15 lines; the success criteria measure against the 2026-11-08 numbers (RF-4); the two non-goals restate today's rules (what is judged or built; only the human grants auto mode or decides a human-only disposition, D-261108-txqj). Taken as drafted. [agent]
Five no's: changes what a user can do: no; sees: no; who may do it: no (it keeps today's rule); data: no; cost: no.
Patched: tagged [agent]

## Derived · UJ-1, UJ-2, FR-11, FR-15, AC-5, AC-6, AC-8, AC-11, AC-12, AC-14, AC-15, AC-16, state table · 2026-11-14
Each follows from the answers, research and calls it cites: the journeys from FR-1 to FR-4 and RF-4; FR-11 and the hand-back steps from FR-4 and RF-9 (the effort already waits for the human there); FR-15 from FR-5 and RF-10; the ACs from their FRs.
Patched: tagged [derived: …]

## Q4 · spec jury round 1 (J-1 to J-25) · 2026-11-14
Question: How should each finding the spec jury confirmed be settled?
Context: The spec jury confirmed 2 blockers and 7 majors (ledger jury/spec.md); each came with a proposed fix.
Options:
1. All as recommended (recommended): fix every finding as proposed; accept as risk only the bundling of the wait rules with the driver change.
2. Rule finding by finding.
3. Accept the majors as risk and fix only the blockers.
Answer: 1. All as recommended: drop "saving a juror's reply" from FR-15; AC-10 bans only interval polling and allows the one check after a timeout; FR-1, FR-2, FR-6, AC-1, AC-2 apply where the host has subagents; a host with no notices and no timed wait hands back to the human with the command still open; drivers run one after another per unit and a resumed unit gets a new one; the brief gives counts, the first items and the command for the rest within 80 lines, and an unknown slug errors with an exit code; AC-12 names a refused `nio flow green` and the skill step it reaches; the minors are fixed; keep the wait rules in this spec. [human]
Refs: J-1, J-2, J-5, J-8, J-9, J-15, J-16, J-18, jury/spec.md
Patched: FR-1, FR-2, FR-6, FR-9, FR-10, FR-12, FR-14, FR-15, FR-16 (new), AC-1, AC-2, AC-4, AC-6, AC-10, AC-11, AC-12, AC-17, AC-18, AC-19 (new), NFR-1, NFR-2, state table, decision table, Decisions

## Q5 · FR-9, FR-10, decision table row 2 · 2026-11-14
Question: How long should a blocking wait last, and how many waits before the driver hands back?
Context: The draft said 10 minutes and at most three waits, but tagged them as the human's without a recorded answer (J-11, J-12).
Options:
1. 10 minutes, three waits (recommended): a driver gives up after about 30 minutes and hands back with the command still running.
2. One wait only: the driver hands back after 10 minutes.
3. Longer waits: fewer wake-ups, but a stuck command holds the driver longer.
Answer: 1. 10 minutes, three waits: confirmed. [human]
Refs: J-11, J-12, FR-9, FR-10
Patched: FR-10 and decision table row 2 tagged [human]

## Q6 · J-10 · 2026-11-14
Question: When a driver hands back while a long command is still running, how does the next driver learn not to start it again?
Context: The brief comes from saved state alone and no driver passes a note (FR-3, FR-14), so the next driver would start the same command a second time (J-10, fix check).
Options:
1. Save it in state (recommended): nio records a running long command with its start time and clears it when it ends; the brief shows it.
2. Main session passes it on: the main session adds the running command to the next driver's start.
3. Accept as risk: a second copy of the command may run.
Answer: 1. Save it in state: when a driver starts a long command, nio records it as running (command, start time), clears it when the command ends, and `nio flow brief` shows "running: <command>, started <time>" so the next driver waits on it. [human]
Refs: J-10, FR-10, FR-14
Patched: FR-10, FR-14, FR-17 (new), AC-20 (new). Not recorded in the jury ledger: `nio jury dispose` refuses because the gate already marks J-10 fixed.
