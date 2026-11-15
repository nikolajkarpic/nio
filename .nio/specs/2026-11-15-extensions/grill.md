# Grill: 2026-11-15-extensions

Session 1 (2026-11-15): delegated by the human ("run full nio flow for this in auto mode from spec to implementation" and "take recommended answers for all questions", intake.md). The agent (grill-driver / claude-code / claude-opus-5-5) looked up every fact point, and took the recommended option on every question, tagged [agent], reason: delegated by the human, 2026-11-15 (recommended option). The human reviews every [agent] answer at the spec gate. Q2 (who may add an extension and whether its commands need approval) is a permissions call the grill would normally hold for the human; it was taken under the same delegation and is flagged for the human's review.

## Lookup · OP-1 · 2026-11-15
Facet: actors
Found: RF-1, RF-2. The only evidence is the intake, #162, #9 and #61; the personas file backs the maintainer (P-3), the effort owner (P-1) and the teammate (P-2), and the flow already has a driver. Patched A-1, A-2, A-4 [research: RF-1], A-5 [research: RF-2]; retired OP-1.

## Lookup · OP-3 · 2026-11-15
Facet: meaning
Found: RF-3. The CLI fires no NIO event today, and `nio flow green` is gone, so #9's `after-task-green` and `before-epic-jury` have no source. The events in FR-26 map to history lines the flow already writes. Retired OP-3; FR-26's list confirmed below.

## Lookup · OP-9 · 2026-11-15
Facet: verification
Found: RF-6. Tasks on a full spec cite the plan's TC-n, and an epic's closing run is built from its TCs' `File:` lines through `tests.suite`. An e2e test written after the plan gate is cited through the TC whose `File:` names it; `nio check tasks` doesn't need the file to be new. FR-31 holds as written; retired OP-9.

## Lookup · OP-10 · 2026-11-15
Facet: data
Found: RF-5. The plan names files in contracts.md `Binding:` and tests.md `File:` lines, in backticks; a trigger rule can read them. FR-15 holds; retired OP-10.

## Lookup · OP-11 · 2026-11-15
Facet: failure
Found: RF-7. No browser runner is on the known-runner list; #61 names Playwright first; Playwright's `webServer` config starts, waits for and stops the app, and its start failures read apart from assertion failures. Feeds Q5 and Q6; retired OP-11 there.

## Lookup · OP-12 · 2026-11-15
Facet: change
Found: RF-8. Shipped cards travel as package data and mods are force-included in the wheel; skills ship as the repo's `skills/` and reach hosts through the plugin or the hosts' own skill folders; `nio agents sync` renders cards. A shipped extension can travel as package data like the cards; how an added extension's skill reaches a host is the plan's to settle from that. Retired OP-12.

## Lookup · OP-13 · 2026-11-15
Facet: change
Found: RF-4. `STAGES` is one ordered dict that `where()` walks on every call; skip lines carry a reason and history names stages by string, so added steps read old histories unchanged while the built-in names and order stay. FR-9, NFR-3 hold; retired OP-13.

## Lookup · OP-14 · 2026-11-15
Facet: actors
Found: RF-9. Under auto the driver's `nio flow done` approves a passing spec, plan or tasks gate; the pr gate always waits for the human. Feeds Q8.

## Asked · Q1 · OP-2 · 2026-11-15
Question: **Pick one:** when an extension's hook fails, should the flow only record it and move on?
Context: Hooks are shell commands an extension runs on flow events, like a linter or a notifier. A step's check command already blocks the flow when it fails (per #162's decisions). #9's research proposed a per-hook "blocking" switch.
Options:
1. Only record it (Recommended): the failure and its output are kept in the effort's record and the flow moves on; checks stay the one way to block. Loses: a hook can't stop a bad step by itself.
2. A per-hook blocking switch: the author picks; a blocking failure stops the flow like a failed check. Costs a second blocking path and more code.
3. Every failing hook blocks: strict, but a broken notifier stops every effort.
Refs: OP-2 · FR-25, FR-27 · #9 research comment

## Q1 · OP-2 · 2026-11-15
Question: When an extension's hook fails, should the flow only record it and move on?
Options:
1. Only record it (recommended)
2. A per-hook blocking switch
3. Every failing hook blocks
Answer: 1. Only record it: the failure and its output are kept in the effort's record and the flow moves on; checks stay the one way to block. Loses: a hook can't stop a bad step by itself. [agent] Reason: delegated by the human, 2026-11-15 (recommended option).
Patched: FR-27, AC-40 (new); retired OP-2; D-261115-ggt2

## Asked · Q2 · OP-4 · 2026-11-15
Question: **Pick one:** when an extension comes from a git URL, what guards the shell commands it brings, and who may add one?
Context: An extension's check and hook commands run later on every teammate's machine. Extensions live in the committed `.nio/extensions` folder (per #162), and the maintainer owns the committed team config (per the personas file).
Options:
1. Add runs nothing and lists every command; the commit is the review (Recommended): whoever may change the committed team config adds it; the team reviews the commands in the commit like any code. Loses: no NIO prompt before the first run.
2. Ask the human to approve each command before its first run: one more stop per extension, including under auto, and a new approval record.
3. Allow only shipped and local-path extensions, no git URLs: safest, but drops a decided source (#162 decision 5).
Refs: OP-4 · FR-1, FR-2, FR-37 · RF-1 · personas.md P-3

## Q2 · OP-4 · 2026-11-15
Question: When an extension comes from a git URL, what guards the shell commands it brings, and who may add one?
Options:
1. Add runs nothing and lists every command; the commit is the review (recommended)
2. Ask the human to approve each command before its first run
3. Allow only shipped and local-path extensions
Answer: 1. Add runs nothing and lists every command; the commit is the review: whoever may change the committed team config adds it; the team reviews the commands in the commit like any code. Loses: no NIO prompt before the first run. [agent] Reason: delegated by the human, 2026-11-15 (recommended option). Permissions call: flagged for the human's review at the spec gate.
Patched: FR-37 (new), AC-39 (new), UJ-1 steps 2 and 3; retired OP-4; D-261115-ggt2

## Asked · Q3 · OP-5 · 2026-11-15
Question: **Pick one:** should an extension in a person's own `~/.nio/extensions` only be a source for `nio extensions add`?
Context: Extensions use the same three layers as agent cards (per #162 decision 5), but a step in the flow changes what every teammate's effort runs. Only `.nio/extensions` is committed.
Options:
1. Only a source (Recommended): `nio extensions add <name>` finds it there before the shipped set; only the project's copy is active, so every teammate runs the same flow. Loses: a personal step can't run without being committed.
2. Active on every project for that person: personal steps and hooks run only on their machine, so two teammates' flows differ.
3. Drop the personal layer: simplest, but a person's own extension must be added by path each time.
Refs: OP-5 · FR-3, FR-8 · RF-11

## Q3 · OP-5 · 2026-11-15
Question: Should an extension in a person's own `~/.nio/extensions` only be a source for `nio extensions add`?
Options:
1. Only a source (recommended)
2. Active on every project for that person
3. Drop the personal layer
Answer: 1. Only a source: `nio extensions add <name>` finds it there before the shipped set; only the project's copy is active, so every teammate runs the same flow. Loses: a personal step can't run without being committed. [agent] Reason: delegated by the human, 2026-11-15 (recommended option).
Patched: FR-3, UJ-1 step 1, Non-goals (catalog line); retired OP-5

## Asked · Q4 · OP-6 · 2026-11-15
Question: **Pick one:** when an extension is removed or replaced, should efforts at or past its step keep their record and carry on?
Context: History lines name the stages an effort passed (per the flow code). Removing an extension deletes its folder, so the flow can no longer run its step.
Options:
1. The record stands (Recommended): past lines stay as written, an effort sitting at the removed step moves on, and one past a replaced step isn't sent back. Loses: a replaced step's new check doesn't re-run on efforts already past it.
2. Refuse the remove while an effort is at or past the step: safe history, but an extension can't go until every effort finishes.
3. Send efforts past a replaced step back to re-run it: re-checks with the new version, at the cost of redoing work.
Refs: OP-6 · FR-7, AC-7 · RF-4

## Q4 · OP-6 · 2026-11-15
Question: When an extension is removed or replaced, should efforts at or past its step keep their record and carry on?
Options:
1. The record stands (recommended)
2. Refuse the remove while an effort is at or past the step
3. Send efforts past a replaced step back to re-run it
Answer: 1. The record stands: past lines stay as written, an effort sitting at the removed step moves on, and one past a replaced step isn't sent back. Loses: a replaced step's new check doesn't re-run on efforts already past it. [agent] Reason: delegated by the human, 2026-11-15 (recommended option).
Patched: FR-7; retired OP-6

## Asked · Q5 · OP-11 · 2026-11-15
Question: **Pick one:** should the e2e extension support Playwright only, for now?
Context: No browser runner is on NIO's known-runner list today, and #61 names Playwright first (per the implement code and #61). Playwright can start and stop the app itself (per its docs).
Options:
1. Playwright only (Recommended): one runner to build and test; its setup errors are told apart from failures in the e2e extension's own check. Loses: Cypress projects can't use it yet.
2. Playwright and Cypress: covers more projects, doubles the runner work.
3. Any runner, by a command the project names: flexible, but setup errors can't be told apart from real failures.
Refs: OP-11 · FR-28, FR-30, FR-32 · RF-7 · Non-goals

## Q5 · OP-11 · 2026-11-15
Question: Should the e2e extension support Playwright only, for now?
Options:
1. Playwright only (recommended)
2. Playwright and Cypress
3. Any runner, by a command the project names
Answer: 1. Playwright only: one runner to build and test; its setup errors are told apart from failures in the e2e extension's own check. Loses: Cypress projects can't use it yet. [agent] Reason: delegated by the human, 2026-11-15 (recommended option).
Patched: FR-32, Non-goals (runner line); retired OP-11

## Asked · Q6 · OP-8 · 2026-11-15
Question: **Pick one:** should the app's start command and ready address live in the project's Playwright config?
Context: Playwright's `webServer` config starts the app, waits until its address answers and stops it after the run (per Playwright's docs), so NIO needs no setting of its own.
Options:
1. In the Playwright config (Recommended): the runner starts, waits for and stops the app; NIO adds no setting and no process handling. Loses: the e2e extension depends on that config being there.
2. In the e2e extension's settings in `.nio/config.json`: NIO starts and stops the app itself; more code, a second place for the same fact.
3. Found by onboarding: no setting to write, but a guess can start the wrong thing.
Refs: OP-8 · FR-32, AC-34 · RF-7

## Q6 · OP-8 · 2026-11-15
Question: Should the app's start command and ready address live in the project's Playwright config?
Options:
1. In the Playwright config (recommended)
2. In the e2e extension's settings in `.nio/config.json`
3. Found by onboarding
Answer: 1. In the Playwright config: the runner starts, waits for and stops the app; NIO adds no setting and no process handling. Loses: the e2e extension depends on that config being there. [agent] Reason: delegated by the human, 2026-11-15 (recommended option).
Patched: FR-32, AC-34; retired OP-8

## Asked · Q7 · OP-7 · 2026-11-15
Question: **Pick one:** should e2e traces and screenshots stay in the runner's own output folder, uncommitted and replaced by the next run?
Context: A failing browser test leaves a trace and screenshots the human looks at. Committing them grows the repo with binaries.
Options:
1. The runner's output folder, uncommitted (Recommended): kept until the next run, and the output says where. Loses: evidence from an older run.
2. Under the effort's folder, committed: kept for good, but binaries in git.
3. Under the effort's folder, ignored, kept per run: history on one machine only, and a cleanup rule to write.
Refs: OP-7 · FR-33, AC-35

## Q7 · OP-7 · 2026-11-15
Question: Should e2e traces and screenshots stay in the runner's own output folder, uncommitted and replaced by the next run?
Options:
1. The runner's output folder, uncommitted (recommended)
2. Under the effort's folder, committed
3. Under the effort's folder, ignored, kept per run
Answer: 1. The runner's output folder, uncommitted: kept until the next run, and the output says where. Loses: evidence from an older run. [agent] Reason: delegated by the human, 2026-11-15 (recommended option).
Patched: FR-33, AC-35; retired OP-7

## Asked · Q8 · OP-14 · 2026-11-15
Question: **Pick one:** under auto, should an extension's jury gate be approved the way the spec, plan and tasks gates are?
Context: Under auto the driver approves a passing spec, plan or tasks gate itself, the pr gate always waits for the human, and the stop rules pause auto at any gate (per the flow code).
Options:
1. Like the spec, plan and tasks gates (Recommended): same rules, same stops; no new case to build. Loses: no extra human stop for extension gates.
2. Every extension gate waits for the human: a stop per extension gate, even under auto.
3. Let each extension choose: flexible, one more manifest field and rule.
Refs: OP-14 · FR-19, FR-23, AC-19 · RF-9

## Q8 · OP-14 · 2026-11-15
Question: Under auto, should an extension's jury gate be approved the way the spec, plan and tasks gates are?
Options:
1. Like the spec, plan and tasks gates (recommended)
2. Every extension gate waits for the human
3. Let each extension choose
Answer: 1. Like the spec, plan and tasks gates: same rules, same stops; no new case to build. Loses: no extra human stop for extension gates. [agent] Reason: delegated by the human, 2026-11-15 (recommended option).
Patched: FR-19; retired OP-14

## Call · remaining [default] items · 2026-11-15
Facet: failure, verification
Answer: every other drafter proposal taken as proposed [agent], reason: delegated by the human, 2026-11-15 (recommended option): UJ-1, UJ-2, FR-5, FR-6, FR-11, FR-17, FR-18, FR-21, FR-22, FR-26 (events per RF-3), FR-34, FR-36, their ACs (AC-5, AC-6, AC-7, AC-11, AC-18, AC-19, AC-21, AC-22, AC-24, AC-27, AC-28, AC-31, AC-36, AC-38), the four [default] table rows, NFR-1 to NFR-3 (300-second timeout), SC-4 and the three non-goals. The manifest's JSON format is backed by RF-12.

## Finish gate · 2026-11-15
Fidelity: re-read every patched item against Q1 to Q8; numbers ("300 seconds"), negatives ("runs none", "never stops", "not sent back", "uncommitted") and the order (personal before shipped) match the answers. Passivity: skipped (delegated session). `nio check spec --gate` passes; the agent chose finish, as delegated. The human sees every [agent] answer at the spec gate.
