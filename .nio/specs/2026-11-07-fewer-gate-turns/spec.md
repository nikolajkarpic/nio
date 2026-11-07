---
slug: 2026-11-07-fewer-gate-turns
route: full
epic: ""                         # "<epic slug>/R-<n>" when this is a slice of an epic
risk: [public-api]               # auth | pii | money | external-input | data-deletion | migration | multi-party | public-api
retired: [OP-1, OP-2, OP-3, OP-4, OP-5, OP-6, OP-7, OP-8, OP-9, OP-10, OP-11, OP-12] # IDs removed from this spec; never reused
---
<!-- Spec template. WHAT and WHY only, never HOW. Every item ends with its provenance: [human] (the grill
confirmed it), [research: RF-n] (a finding in research.md) or [default] (your proposal; the grill must confirm it).
IDs are permanent: number new items after the highest ever used, never renumber, list removed IDs in `retired`.
Remove a section that doesn't apply; never write N/A. `nio check spec 2026-11-07-fewer-gate-turns` checks all of this. -->
# Drive a jury gate in fewer orchestrator calls

## Summary
At every jury gate the orchestrator (the main session, on the frontier model with a large context) spends more time
and money on its own calls than the jurors do. This delivers one command that runs a gate step end to end and prints
only what to do next, a dispose that takes several findings in one call, and jurors that write their own output file,
so the orchestrator's calls per gate are at least halved with no change to what jurors judge. It also stops a juror's
copied example lens name from filing its findings under another lens (#90). [human]

## Actors and journeys
- **A-1 Orchestrator**: the main agent session running the jury skill; drives the CLI, runs the jurors, relays the outcome; every call it makes is expensive because of its context size. [human]
- **A-2 Juror**: a lens or refuter subagent with a fresh pack; judges and returns findings in the lens output format. [human]
- **A-3 Human**: reads the outcome and rules on what is theirs; reads the before/after turn count in the PR. [human]

**UJ-1 One gate round** (A-1, A-2) [derived: FR-12, FR-9, FR-2, FR-4, FR-7]
1. The orchestrator runs the step command; it plans the lenses, starts the run and writes each lens's pack. It runs each juror in parallel; each juror writes its own output file.
2. The orchestrator runs the one step command; it says whether the refuter must run and where its batch is.
3. After the refuter writes its file, the orchestrator runs the step command again; it prints the outcome and, on a re-run, where each fix-check pack was written.
4. The orchestrator disposes of the open findings in one call and reports to the human.
- Misuse: a juror copies the template's example lens name, or writes outside its output file; the orchestrator keeps calling collect and check separately out of habit.
- Evidence: #76 (session 322a1614 measurements), #90.

## User stories

### US-1 One command runs a gate step (P1) [human]
- **Why this priority:** the separate collect, re-collect, check, changed and fix-check calls are most of the orchestrator's turns per gate (#76).
- **Independent test:** on a fixture gate with lens outputs in a run folder, one call collects, reports the refuter batch, and after a refuter file, a second call prints the outcome and writes the fix-check packs.

- **AC-1** (FR-1, FR-2) Given a run with valid lens outputs that leave blocker or major findings unvalidated, when the orchestrator runs the step command, then the findings are in the ledger and the refuter batch is written to a file whose path is printed as the next action. [human]
  Observable: ledger holds the findings; the batch file exists and lists each pending finding; output names that path. Level: integration.
- **AC-2** (FR-3, FR-4) Given the refuter's output is in the run and the outcome is `rerun`, when the step command runs, then the outcome is composed and recorded, and a fix-check pack per named lens is written under `.nio/runs/<run>/jury/packs/`. [human]
  Observable: verdict record written once; one pack file per lens to re-run, each matching what `nio jury fixcheck` prints for it. Level: integration.
- **AC-3** (FR-5) Given any state, when the step command runs, then its output is collect's one-line results, the lens-name mismatch lines, `nio jury check`'s lines (when it composed an outcome) and the next action with the paths it needs, never a finding's quote, situation or fix, nor the refuter batch's body. [agent]
  Observable: output holds a `next:` line; no `- quote:`, `- situation` or `- fix:` line; a dropped finding still shows its one `dropped` line. Level: integration.
- **AC-12** (FR-12) Given a gate whose lenses have no output in a new run, when the step command runs, then each planned lens has a pack file holding what the skill puts in its pack today and the path its output goes to, and the output names each lens with its pack and output path. [agent]
  Observable: one `packs/<lens>.md` per planned lens; the spec gate's packs hold the `nio check spec` output and the lens output format; the output lists each lens, pack and output path. Level: integration.
- **AC-4** (FR-6) Given one expected lens has no output file and another's is invalid, when the step command runs, then it names both lenses to re-run with the errors to add to their packs. [agent]
  Observable: output names each lens and its collect errors; no outcome is composed. Level: integration.
- **AC-13** (FR-6) Given a valid lens output with `context: needs-more`, when the step command runs, then it names that lens to re-run. [agent]
  Observable: `next:` names the lens; no outcome is recorded. Level: integration.
- **AC-14** (FR-3, FR-5) Given all outputs collected and validated, when the outcome is `rejected`, `human` or `approved`, then the `next:` line says, in that order: dispose of the open findings then run the step command again; show the human the listed findings; tell the human and run `nio flow next`. [agent]
  Observable: one fixture per outcome; its `next:` line holds `dispose`, `human` or `nio flow next`. Level: integration.
- **AC-5** (FR-1, FR-3, FR-13) Given the step command already ran and nothing new is in the run, when it runs again, then no new round starts, no pack is rewritten, no second run is started and no second verdict record is written, and it prints the same next action. [agent]
  Observable: ledger round and recorded verdicts unchanged; pack files' bytes unchanged; no new run folder; same `next:` line, naming the same run. Level: integration.

### US-2 Dispose several findings in one call (P1) [human]
- **Why this priority:** disposing one by one is a turn per finding (#76).
- **Independent test:** on a fixture ledger with three open findings, one dispose call sets all three.

- **AC-6** (FR-7) Given three open findings, when the orchestrator disposes all three in one call, then each carries the disposition. [human]
  Observable: ledger shows all three disposed, with their `by` and note. Level: integration.
- **AC-7** (FR-8) Given one of the IDs would be refused (unknown ID, or a human-only disposition without `--by human`), or the call has a duplicate or empty ID, or a `--note` count that is neither 1 nor the ID count, when the call runs, then no finding changes and the error names the ID or the counts. [agent]
  Observable: ledger file bytes unchanged; error names the ID and why, or both counts. Level: integration.
- **AC-15** (FR-7) Given three open findings and three `--note` values, when they are disposed in one call, then each finding carries its own note, in order. [agent]
  Observable: J-a has note 1, J-b note 2, J-c note 3. Level: integration.

### US-3 Jurors write their own output file (P2) [human]
- **Why this priority:** saves one turn per juror, and the orchestrator no longer carries each answer in its context; smaller saving than US-1.
- **Independent test:** run one lens on a fixture; its output file appears at its path without the orchestrator writing it.

- **AC-8** (FR-9) Given a juror's pack names its output path, when it finishes, then its output is at `.nio/runs/<run>/jury/<gate>-<lens>.md` and no other project file changed. [human]
  Observable: static: each lens and refuter card grants a write tool and its Output format says to write only the path its pack names. e2e: the file exists and parses, and a listing of the project tree (`.nio/` included, ignored files too) before and after differs only by that file. Level: e2e.

### US-4 A copied lens name no longer misfiles findings (P2) [human]
- **Why this priority:** #90 cost two re-emits and duplicate ledger entries in one gate; it touches the same juror output path and template.
- **Independent test:** collect a fixture file `spec-testability.md` whose front matter says `lens: logic`.

- **AC-9** (FR-10) Given `spec-testability.md` with `lens: logic` in its front matter, when it is collected, then its findings are filed under testability, testability is not reported as having no output, and one output line names the file and the mismatch. [agent]
  Observable: every finding from that file has lens testability; the output has one line naming `spec-testability.md` and `logic`. Level: integration.
- **AC-10** (FR-10) Given an escalation juror's file `spec-logic-2.md`, when it is collected, then it counts as the logic lens. [agent]
  Observable: the juror is recorded under lens logic. Level: integration.
- **AC-16** (FR-14) Given a run holding `spec-security.md` while security is not a planned lens, when the step command runs, then nothing is collected and the error names the file. [agent]
  Observable: ledger unchanged; error names `spec-security.md` and the planned lenses. Level: integration.

### US-5 The jury skill uses the shorter path (P1) [human]
- **Why this priority:** the command saves nothing unless the skill's steps call it.
- **Independent test:** count the tool calls the skill's steps require for one spec gate round, before and after.

- **AC-11** (FR-11) Given scenario A of RF-2 (31 orchestrator tool calls today), when the tool calls the jury skill's steps require are counted for it, then they are at most 15. [human]
  Observable: a counted call is any orchestrator tool call (a CLI call, a file write, a juror launch), not counting edits to the artefact itself; the before and after lists of calls are stated in the PR. Level: e2e.

## Functional requirements
- **FR-1** WHEN the orchestrator runs the gate step command for a slug, gate and run THE SYSTEM SHALL collect the run's lens and refuter outputs as `nio jury collect` does. [human]
- **FR-2** IF findings still need validating after collecting THEN THE SYSTEM SHALL write the refuter batch to a file in the run's jury folder and print that the refuter must run on it. [human]
- **FR-3** WHEN no finding needs validating THE SYSTEM SHALL compose and record the gate outcome as `nio jury check --record` does. [derived: FR-1, RF-5]
- **FR-4** WHEN the outcome is `rerun` while every lens output is usable (the artefact changed since the round judged it, the final fix check is owed, or a fix has no verdict yet) THE SYSTEM SHALL start a new run and write each lens `nio jury changed` names its fix-check pack to `.nio/runs/<new run>/jury/packs/<lens>.md`, printing the new run's ID. [agent]
- **FR-5** THE SYSTEM SHALL print only collect's one-line results, the lens-name mismatch lines, `nio jury check`'s lines when it composed an outcome, and a `next:` action with the paths it needs; the refuter batch goes to its file. [agent]
- **FR-6** IF an expected lens output is missing, invalid or `needs-more` THEN THE SYSTEM SHALL name that lens as the next action, with the errors to add to its pack. [agent]
- **FR-7** WHEN dispose is given several comma-separated finding IDs THE SYSTEM SHALL set the one disposition and `--by` on each, with the one `--note` for all or one `--note` per ID in order, and write the ledger once. [agent]
- **FR-8** IF any finding in a several-ID dispose would be refused, an ID is repeated or empty, or the `--note` count is neither 1 nor the ID count THEN THE SYSTEM SHALL change none of them and name each refused ID with its reason, or the counts; all or nothing keeps the ledger from holding half a ruling. [agent]
- **FR-9** THE SYSTEM SHALL let a lens or refuter juror write its own output file, `.nio/runs/<run>/jury/<gate>-<lens>.md`, through a write tool its card limits to that path by instruction. Today the refuter card already names its file but has only read tools, so the orchestrator saves every answer; the change is the write tool and the path in the pack. [agent]
- **FR-10** THE SYSTEM SHALL file each lens output's findings under the lens its file name gives, print one line when the front matter names another lens, and show `lens: <your card's name>` in the lens output format. [agent]
- **FR-12** WHEN the step command runs on a run with no lens output for the gate yet THE SYSTEM SHALL plan the gate, render the agents and write each planned lens's pack to `.nio/runs/<run>/jury/packs/<lens>.md` with the content the skill gives it today plus its output path. This goes beyond the step #76 names: without it, scenario A of RF-2 saves about half the calls and no more (grill Q8). [agent]
- **FR-13** WHEN the step command runs again on a run whose packs it already wrote, or on the run whose re-review it already started THE SYSTEM SHALL write no pack, start no run and record no verdict again, and SHALL print the same next action with the run it started. [agent]
- **FR-14** IF the run holds a lens output of the gate whose lens is not planned (the refuter's and escalation jurors' files aside) THEN THE SYSTEM SHALL collect nothing and name that file. [agent]
- **FR-11** THE jury skill SHALL drive each gate step with the step command and dispose several findings per call, in place of separate collect, check, changed and fix-check calls. [human]

## Rules
### Decision table: what the step command prints next
| Lens outputs (none yet in the run, all valid, some not usable) | Findings needing validation (yes, no) | Outcome (rerun, pending, rejected, human, approved) | → next action | Src |
| --- | --- | --- | --- | --- |
| none yet in the run | - | - | write the packs; run every planned lens | [agent] |
| some not usable | - | - | re-run the named lenses (missing, invalid or `needs-more`) with their errors | [agent] |
| all valid | yes | - | run the refuter on the batch file | [human] |
| all valid | no | rerun | (every `rerun` with all outputs usable: a changed artefact, the final fix check, a fix without a verdict) run each lens `nio jury changed` names on its written fix-check pack in the new run | [human] |
| all valid | no | pending | cannot occur: `pending` means a finding needs validating, so the yes row applies | [agent] |
| all valid | no | rejected | dispose of the open findings, then run the step command again | [agent] |
| all valid | no | human | show the human the listed findings | [agent] |
| all valid | no | approved | tell the human; run `nio flow next` | [agent] |

## Non-functional requirements
- **NFR-1** THE jury skill SHALL require at most 15 orchestrator tool calls for scenario A of RF-2, against 31 before this change, counting every orchestrator tool call except edits to the artefact. [human]
- **NFR-2** THE SYSTEM SHALL give each juror the same pack content as before, apart from the line naming where it writes its output. [human]

## Success criteria
- **SC-1** The PR states the orchestrator tool calls scenario A needs before (31) and after, and after is at most 15. [human]

## Non-goals
- Building a gate-driver subagent; a host may run the gate in one, mentioned only as an optional note. [human]
- Fixing #92 (a merged finding produced a wrong fix task), unless it proves trivial. [human]
- Changing what jurors judge, their cards' judging instructions, or the outcome rules `nio jury check` applies. [human]
- Cutting re-emits from a lenient parser (#74). [agent]
- Writing escalation jurors' packs in the step command; escalation keeps `nio jury fixcheck --blocker` (grill Q5). [agent]

## Glossary
- **Orchestrator turn**: one tool call the main session makes while driving a gate. Never "round trip" alone.
- **Gate step**: the work between the jurors returning and the orchestrator's next action (collect, refuter batch, check, fix-check packs).

## Decisions
- Jurors get a write tool and write only their output path, by the card's instruction; no host can limit paths (grill Q1, [agent], RF-3).
- The output path line is not a change to what jurors judge (grill Q2, [agent]).
- The file name gives the lens; a mismatched front matter is reported, not refused (grill Q3, [agent]).
- Several-ID dispose: comma-separated IDs, one disposition, one or per-ID notes (grill Q4, [agent]).
- Escalation stays as it is (grill Q5, [agent]).
- The step command serves every gate; evidence stays its own call (grill Q6, [agent]).
- The step command starts a re-review's run (grill Q7, [agent]) and writes the first review's packs (grill Q8, [agent]).
- #92 is not trivial and stays out (RF-4).
- A lens file of an unplanned lens stops the step (grill Q9, [agent]); the step prints collect's one-line results too (grill Q10, [agent]); a repeated step changes nothing (grill Q11, [agent]); a several-ID dispose refuses a bad note count or repeated ID whole (grill Q12, [agent]).
