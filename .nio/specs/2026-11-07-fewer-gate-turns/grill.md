# Grill: 2026-11-07-fewer-gate-turns

Session 1 (2026-11-07): delegated to the agent (orchestrator / claude-code / claude-opus-5-5) by the human, with standing authority to take the recommended option. Permissions, deletion and irreversible steps would still go to the human; none came up.

## Lookup · OP-1, OP-2, OP-4, OP-11, OP-12 · 2026-11-07
Facet: meaning, change, verification
Found: RF-1 to RF-6 in research.md. Retired OP-1, OP-2, OP-4, OP-11, OP-12. The baseline (RF-2) is 31 tool calls for scenario A; #92 is not trivial (RF-4) and stays a non-goal.

## Asked · Q1 · OP-3 · 2026-11-07
Question: How does a juror get to write its own output file?
Context: No host can limit a subagent's writes to one path (RF-3); Codex cards are already read-only by instruction only.
Options: 1. Give lens and refuter cards a write tool, limited to the output path by the card's instruction (recommended): one save turn and one copy of each answer less per juror; a juror could write elsewhere against its card. 2. A write tool only on hosts that can limit paths: none can today, so nothing changes. 3. Keep saving in the orchestrator: no saving, the orchestrator still carries every answer.
Refs: OP-3 · FR-9 · RF-3

## Q1 · OP-3 · 2026-11-07
Question: How does a juror get to write its own output file?
Facet: actors
Options:
1. Write tool, limited by the card's instruction (recommended)
2. Write tool only where the host limits paths
3. Keep saving in the orchestrator
Answer: 1. Give lens and refuter cards a write tool, limited to the output path by the card's instruction: one save turn and one copy of each answer less per juror; a juror could write elsewhere against its card. [agent]
Patched: FR-9, AC-8; retired OP-3

## Asked · Q2 · OP-5 · 2026-11-07
Question: Does the line telling a juror where to write its file count as a change to what jurors see?
Context: NFR-2 promises the same pack content; the output path is where the answer goes, not what is judged.
Options: 1. No: the judged content is unchanged, the path line is allowed (recommended). 2. Yes: then jurors can't write their own file. 3. Put the path in the card instead: the card can't know the run.
Refs: OP-5 · NFR-2

## Q2 · OP-5 · 2026-11-07
Question: Does the line telling a juror where to write its file count as a change to what jurors see?
Facet: data
Options:
1. No, the path line is allowed (recommended)
2. Yes
3. Path in the card
Answer: 1. No: the judged content is unchanged, the path line is allowed. [agent]
Patched: NFR-2; retired OP-5

## Asked · Q3 · OP-6 · 2026-11-07
Question: When a lens file's front matter names another lens than its file name, what does collect do?
Context: In #90, 2 of 3 jurors copied `lens: logic` from the template; the orchestrator names each file for its lens.
Options: 1. Take the file name's lens, print one line naming the mismatch, and show `lens: <your card's name>` in the template (recommended): no re-emit. 2. Refuse the output with an error: costs a re-emit each time. 3. Only change the template: a copied name still misfiles.
Refs: OP-6 · FR-10 · issue #90

## Q3 · OP-6 · 2026-11-07
Question: When a lens file's front matter names another lens than its file name, what does collect do?
Facet: failure
Options:
1. File name wins, a line names the mismatch, template fixed (recommended)
2. Refuse the output
3. Only change the template
Answer: 1. Take the file name's lens, print one line naming the mismatch, and show `lens: <your card's name>` in the template: no re-emit. [agent]
Patched: FR-10, AC-9; retired OP-6

## Asked · Q4 · OP-7 · 2026-11-07
Question: How does one dispose call take several findings?
Context: Each disposal is a turn today; an agent's spec-fix note says what changed, which the fix-check pack shows the lens.
Options: 1. Comma-separated IDs with one disposition and `--by`; `--note` given once for all or once per ID in order (recommended): each lens still sees its own note. 2. One shared note only: a lens sees notes about other fixes. 3. A file of dispositions: one more file to write.
Refs: OP-7 · FR-7

## Q4 · OP-7 · 2026-11-07
Question: How does one dispose call take several findings?
Facet: data
Options:
1. Comma-separated IDs, one or per-ID notes (recommended)
2. One shared note only
3. A file of dispositions
Answer: 1. Comma-separated IDs with one disposition and `--by`; `--note` given once for all or once per ID in order: each lens still sees its own note. [agent]
Patched: FR-7; retired OP-7

## Asked · Q5 · OP-8 · 2026-11-07
Question: Does the step command also write the escalation jurors' packs?
Context: Escalation runs only for a blocker the refuter confirmed, which is rare; it already has `nio jury fixcheck --blocker`.
Options: 1. No, escalation stays as it is (recommended): less to build. 2. Yes: one call fewer on the rare blocker. 3. Drop escalation: breaks the 2-of-3 rule.
Refs: OP-8 · FR-1

## Q5 · OP-8 · 2026-11-07
Question: Does the step command also write the escalation jurors' packs?
Facet: change
Options:
1. No (recommended)
2. Yes
3. Drop escalation
Answer: 1. No, escalation stays as it is: less to build. [agent]
Patched: Non-goals; retired OP-8

## Asked · Q6 · OP-9 · 2026-11-07
Question: Does the step command serve the implementation gates too?
Context: The implementation gate has the costliest orchestrator (RF-1); collect and check already take it, and `nio jury pack` already builds its packs (RF-6). Its evidence run stays a separate, long command.
Options: 1. Every gate, implementation included; evidence stays its own call (recommended). 2. Spec, plan and tasks only: the costliest gate keeps every call. 3. Implementation only.
Refs: OP-9 · FR-1 · RF-1, RF-6

## Q6 · OP-9 · 2026-11-07
Question: Does the step command serve the implementation gates too?
Facet: change
Options:
1. Every gate (recommended)
2. Spec, plan and tasks only
3. Implementation only
Answer: 1. Every gate, implementation included; evidence stays its own call. [agent]
Patched: FR-1, FR-12; retired OP-9

## Asked · Q7 · OP-10 · 2026-11-07
Question: When the outcome asks for a re-review, does the step command start the new run itself?
Context: The skill starts a new run for each re-review today: one call (RF-2).
Options: 1. Yes, it starts the run and prints its ID (recommended): one call less per re-review. 2. No, the orchestrator runs `nio run` first. 3. Reuse the same run: the round's files would overwrite the last round's.
Refs: OP-10 · FR-4

## Q7 · OP-10 · 2026-11-07
Question: When the outcome asks for a re-review, does the step command start the new run itself?
Facet: data
Options:
1. Yes (recommended)
2. No
3. Reuse the same run
Answer: 1. Yes, it starts the run and prints its ID: one call less per re-review. [agent]
Patched: FR-4; retired OP-10

## Asked · Q8 · FR-12 · 2026-11-07
Question: Should the step command also write the first review's packs?
Context: Round 1 assembles each pack from 4–6 separate calls (RF-6). Without this, scenario A goes from 31 calls to about 16, barely half; with it, to about 13 (RF-2).
Options: 1. Yes: with no round in the run yet, it plans, starts the run, renders the agents and writes every planned lens's pack with the same content as today (recommended). 2. No: the halving target is at risk. 3. Only at the implementation gate, where `nio jury pack` exists.
Refs: FR-12 · NFR-1 · RF-2, RF-6

## Q8 · FR-12 · 2026-11-07
Question: Should the step command also write the first review's packs?
Facet: verification
Options:
1. Yes (recommended)
2. No
3. Only at the implementation gate
Answer: 1. Yes: with no round in the run yet, it plans, starts the run, renders the agents and writes every planned lens's pack with the same content as today. [agent]
Patched: FR-12, AC-12, UJ-1, Decision table

## Call · AC-4, AC-5, AC-7, AC-10, Decision table
Below the bar (no change to what a user can do or sees, who may do it, data kept, or cost): re-run named lenses with their errors; a repeated call starts no new round; an all-or-nothing several-ID dispose; an escalation juror counts as its lens; the table's default rows follow `nio jury check`'s outcomes. Taken as proposed. [agent]

## Asked · Q9 · J-1 · 2026-11-07
Question: What does the step command do with a lens output whose lens wasn't planned for the gate?
Context: Jurors write their own files and no host limits the path (RF-3); the file name now gives the lens (Q3), so a stray file would file findings under a lens that never ran.
Options: 1. Collect nothing and name the file (recommended): the orchestrator deletes or renames it and runs again. 2. Skip the file with a warning: a real misnamed output is silently lost. 3. Collect it as today.
Refs: J-1 · FR-9, FR-10, FR-14

## Q9 · J-1 · 2026-11-07
Question: What does the step command do with a lens output whose lens wasn't planned for the gate?
Facet: failure
Options:
1. Collect nothing and name the file (recommended)
2. Skip with a warning
3. Collect it
Answer: 1. Collect nothing and name the file: the orchestrator deletes or renames it and runs again. [agent]
Patched: FR-14, AC-16

## Asked · Q10 · J-5 · 2026-11-07
Question: Which lines does the step command print?
Context: The batch body and finding text are what made collect's output long; its one-line results (new, dropped, confirmed) show what happened to each finding (RF-5).
Options: 1. Collect's one-line results, the lens-name mismatch lines, check's lines and one `next:` line; the batch goes to its file (recommended). 2. Only check's lines and `next:`: a dropped finding is invisible. 3. Everything collect prints today: no saving in context.
Refs: J-5 · FR-5, AC-3

## Q10 · J-5 · 2026-11-07
Question: Which lines does the step command print?
Facet: verification
Options:
1. One-line results, mismatch lines, check's lines, next (recommended)
2. Only check's lines and next
3. Everything
Answer: 1. Collect's one-line results, the lens-name mismatch lines, check's lines and one `next:` line; the batch goes to its file. [agent]
Patched: FR-5, AC-3

## Asked · Q11 · J-12 · 2026-11-07
Question: What does a repeated step command do?
Context: The orchestrator may call it twice with nothing new; check already records one verdict per round and outcome (jury.py `check`).
Options: 1. Nothing changes: no pack rewritten, no second run, no second record; it prints the same next action and run (recommended). 2. Rewrite the packs each time: a juror mid-read may see a changed pack. 3. Refuse a repeat: one more turn to recover.
Refs: J-12, J-15 · FR-13, AC-5

## Q11 · J-12 · 2026-11-07
Question: What does a repeated step command do?
Facet: data
Options:
1. Nothing changes, same next action (recommended)
2. Rewrite the packs
3. Refuse a repeat
Answer: 1. Nothing changes: no pack rewritten, no second run, no second record; it prints the same next action and run. [agent]
Patched: FR-13, AC-5

## Asked · Q12 · J-14 · 2026-11-07
Question: What does a several-ID dispose do with a note count that matches neither 1 nor the IDs, or a repeated ID?
Context: Notes are matched to IDs by position (Q4); a wrong count would put a note on the wrong finding.
Options: 1. Refuse the whole call, naming the counts or the ID (recommended). 2. Use the first note for the rest: a note lands on the wrong finding. 3. Apply what matches: half a ruling in the ledger.
Refs: J-14, J-17, J-18 · FR-7, FR-8, AC-7, AC-15

## Q12 · J-14 · 2026-11-07
Question: What does a several-ID dispose do with a note count that matches neither 1 nor the IDs, or a repeated ID?
Facet: failure
Options:
1. Refuse the whole call (recommended)
2. First note for the rest
3. Apply what matches
Answer: 1. Refuse the whole call, naming the counts or the ID. [agent]
Patched: FR-7, FR-8, AC-7, AC-15

## Asked · Q13 · J-13 · 2026-11-07
Question: The spec jury left one finding for you: what does the step command do on a `rerun` when every lens output is usable but the spec didn't change?
Context: `nio jury check` also says `rerun` when the final fix check is owed, or at an implementation gate when a fix has no verdict yet (jury.py `compose`, `composed`); FR-4 named only a changed artefact.
Options: 1. Fix it: every `rerun` with usable outputs starts the new run and writes the fix-check packs of the lenses `nio jury changed` names (recommended). 2. Accept it as a risk: the step prints no action for those cases and the orchestrator falls back to the separate commands.
Refs: J-13 · FR-4, Decision table

## Q13 · J-13 · 2026-11-07
Question: What does the step command do on a `rerun` when every lens output is usable but the spec didn't change?
Facet: failure
Options:
1. Fix it (recommended)
2. Accept it as a risk
Answer: 1. Fix it: every `rerun` with usable outputs starts the new run and writes the fix-check packs of the lenses `nio jury changed` names. [agent]
Patched: FR-4, Decision table
