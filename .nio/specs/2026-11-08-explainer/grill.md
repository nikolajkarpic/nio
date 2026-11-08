# Grill: 2026-11-08-explainer

Session 1 (2026-11-08): delegated to an agent by the human. Deletion and overwrite points go to the human. Facts researched first.

## Lookup · OP-1, OP-7, OP-8, OP-9 · 2026-11-08
Facet: verification, change from today
Found: RF-1 to RF-5. Retired OP-1 (RF-5), OP-7 (RF-1), OP-8 (RF-3, RF-4), OP-9 (RF-2).

## Asked · Q1 · OP-4 · 2026-11-08
Question: When an out-of-date plan explainer is re-run, what happens to the drill-down sections you asked for?
Context: Drill-down sections are added one by one when you zoom in. A re-run redraws the core diagrams from the changed plan; your sections may describe the old plan. Asked of the human: it deletes data.
Options: 1. Keep, mark for review (recommended): sections stay, each marked for re-check. 2. Replace the whole file: drill-downs gone (still in git). 3. Keep unchanged: no marker.
Refs: OP-4, US-4, FR-13

## Q1 · OP-4 · 2026-11-08
Facet: data
Question: When an out-of-date plan explainer is re-run, what happens to the drill-down sections you asked for?
Options:
1. Keep, mark for review (recommended)
2. Replace the whole file
3. Keep unchanged
Answer: 1. Keep, mark for review: core diagrams are redrawn; drill-down sections stay below them, each marked 'written for the old plan, re-check'. Nothing asked for is lost; a section may no longer fit until redone. [human]
Patched: FR-25, AC-32; retired OP-4

## Asked · Q2 · OP-5 · 2026-11-08
Question: When a re-run no longer draws a diagram, is its old SVG image deleted?
Context: Each diagram is rendered to an SVG next to the explainer. If the plan loses a journey its flow diagram goes away but its image would stay. Asked of the human: deletion.
Options: 1. Delete images it made (recommended): only SVGs the previous run listed as its own. 2. Leave them. 3. Ask each time.
Refs: OP-5, FR-9

## Q2 · OP-5 · 2026-11-08
Facet: data
Question: When a re-run no longer draws a diagram, is its old SVG image deleted?
Options:
1. Delete images it made (recommended)
2. Leave them
3. Ask each time
Answer: 1. Delete images it made: before writing, the re-run deletes only the SVGs the previous run listed as its own, then renders the new set. No stray pictures; deleted images stay in git history. Never touches files it didn't make. [human]
Patched: FR-26, AC-33; retired OP-5

## Asked · Q3 · OP-6 · 2026-11-08
Question: When you explain the same topic twice on the same day, what happens to the first file?
Context: Topic explainers are saved under the research folder with date and topic in the name, so a second run the same day hits the same name. Asked of the human: overwrite.
Options: 1. Continue the same file (recommended). 2. Write a new numbered file. 3. Overwrite.
Refs: OP-6, FR-14

## Q3 · OP-6 · 2026-11-08
Facet: failure
Question: When you explain the same topic twice on the same day, what happens to the first file?
Options:
1. Continue the same file (recommended)
2. Write a new numbered file
3. Overwrite
Answer: 1. Continue the same file: the second run reads the file, shows its overview and offers new things to zoom into, adding sections. Nothing lost; no fresh take without deleting it by hand. [human]
Patched: FR-27, AC-34; retired OP-6

## Call · OP-2 · 2026-11-08
Facet: actors
Answer: Plan mode on a slug whose plan gate is still open refuses, says the plan jury comes first, and offers topic mode instead. Reason: drawing an unapproved plan makes pictures that the jury may soon invalidate; topic mode still serves a curious human. [agent]
Patched: FR-23, AC-30; retired OP-2

## Call · OP-3 · 2026-11-08
Facet: change
Answer: Stale = spec.md, plan.md or contracts.md changed or gone, by a SHA-256 prefix recorded per source in the explainer (the hash form the onboarding plan designs, RF-1). quickstart.md is excluded because explain itself edits it; tests.md is not drawn. Reason: same mechanism as onboarding, no false stale from explain's own edit. [agent]
Patched: FR-16, FR-24, AC-31; retired OP-3

## Call · drafter proposals · 2026-11-08
Facet: meaning, verification
Answer: Confirmed as proposed, delegated session: A-3, FR-7/NFR-1/AC-5 (20-node cap, top of the 15-20 range), AC-10, AC-11, AC-18/FR-14 and the Topic explainer entity, FR-15/AC-20, AC-25, FR-20/FR-21/AC-27/AC-28 and their table rows, the explain.format entity, SC-1, the PNG and topic-stale non-goals, the drift risk. The npx risk is now backed by RF-3, RF-4. [agent]
Patched: all of the above tagged [agent]

Session 2 (2026-11-08): spec jury round 1 findings that change behaviour, asked of the human.

## Asked · Q4 · J-1, J-11 · 2026-11-08
Question: Which old images may a re-run delete?
Context: The re-run deletes images the last run listed as its own, but that list sits in a file anyone can edit, and drill-down sections (which re-runs keep) have images too.
Options: 1. Own names, own folder, never drill-down images (recommended). 2. Only the list, as now. 3. Never delete.
Refs: J-1, J-11, FR-26, FR-25

## Asked · Q5 · J-6, J-13, J-22, J-16 · 2026-11-08
Question: When config picks another diagram tool, which checks still run?
Context: Today the check skips its diagram checks entirely, so an explainer missing a contract could pass.
Options: 1. Only rendering skipped (recommended). 2. Skip everything, as now. 3. Drop the config switch.
Refs: J-6, J-13, J-22, J-16, FR-20, FR-21, AC-27

## Asked · Q6 · J-4, J-19 · 2026-11-08
Question: Should the check enforce the 20-node limit per diagram?
Context: The cap is a rule nothing checks.
Options: 1. Check fails over 20 (recommended). 2. Warn only. 3. Drop the cap.
Refs: J-4, J-19, FR-7, NFR-1, AC-5

## Asked · Q7 · J-5 · 2026-11-08
Question: How locked-down should rendering be?
Context: Rendering downloads and runs a third-party tool via npx, unpinned, and a network failure may look like "no Node".
Options: 1. Pin the version, tell the failures apart (recommended). 2. Pin only. 3. Leave as is.
Refs: J-5, FR-9, FR-11, RF-3

## Asked · Q8 · J-2 · 2026-11-08
Question: How is a topic turned into a file name?
Context: The topic text goes straight into a path.
Options: 1. Safe slug (recommended). 2. Agent picks a name. 3. Human names it.
Refs: J-2, FR-14

## Asked · Q9 · J-20 · 2026-11-08
Question: How long is a "short" walk-through?
Context: No number, so it can't be tested.
Options: 1. At most 120 words (recommended). 2. At most 5 sentences. 3. No limit.
Refs: J-20, FR-6, AC-1

## Q4 · J-1, J-11 · 2026-11-08
Facet: data
Question: Which old images may a re-run delete?
Options: see Asked · Q4
Answer: 1. Own names, own folder only: delete only files in the explainer's own folder whose names carry the explainer's prefix and that the last run listed; never images of drill-down sections; any other listed path is ignored with a warning. [human]
Patched: FR-26, AC-33

## Q5 · J-6, J-13, J-22, J-16 · 2026-11-08
Facet: verification
Question: When config picks another diagram tool, which checks still run?
Options: see Asked · Q5
Answer: 1. Only rendering skipped: explainer.md keeps its section headings and lists the contracts in the component map's text, so the core-diagram and contract checks still run; only the SVG render is skipped. Missing skill: fall back to Mermaid and say so. [human]
Patched: FR-20, FR-21, FR-8, AC-27, AC-28, images table

## Q6 · J-4, J-19 · 2026-11-08
Facet: verification
Question: Should nio check explainer enforce the 20-node limit per diagram?
Options: see Asked · Q6
Answer: 1. Check fails over 20: the check counts each diagram's distinct nodes and fails naming any diagram above 20. [human]
Patched: FR-7, FR-8, NFR-1, AC-5

## Q7 · J-5 · 2026-11-08
Facet: failure
Question: How locked-down should rendering be?
Options: see Asked · Q7
Answer: 1. Pin and tell failures apart: nio names one exact mermaid-cli version; the note says which failed: no Node, tool couldn't be fetched, or the diagram is broken. Only a broken diagram fails the check. [human]
Patched: FR-9, FR-11, AC-14

## Q8 · J-2 · 2026-11-08
Facet: data
Question: How is a topic turned into a file name?
Options: see Asked · Q8
Answer: 1. Safe slug: lowercase letters, digits and dashes only, at most 40 characters; anything else becomes a dash; an empty result is refused. [human]
Patched: FR-14, AC-18

## Q9 · J-20 · 2026-11-08
Facet: verification
Question: How long is a 'short' walk-through after each diagram?
Options: see Asked · Q9
Answer: 1. At most 120 words: each walk-through is 1-120 words; the check fails a missing or longer one. [human]
Patched: FR-6, FR-8, AC-1

## Asked · Q10 · J-2 · 2026-11-08
Question: What happens when two different topics shorten to the same file name?
Options: 1. Fix: check the title (recommended). 2. Fix: ask you. 3. Accept as risk.
Refs: J-2, FR-14, FR-27

## Q10 · J-2 · 2026-11-08
Facet: failure
Answer: 1. Fix: check the title: the file stores the original topic text; if a new run's topic differs, it writes '...-explainer-2.md' and says so. Two topics never merge. [human]
Patched: FR-27, AC-35

## Asked · Q11 · J-20 · 2026-11-08
Question: Should a test prove the 120-word walk-through limit?
Options: 1. Fix: add the failing test (recommended). 2. Accept as risk.
Refs: J-20, FR-6, AC-1

## Q11 · J-20 · 2026-11-08
Facet: verification
Answer: 1. Fix: add the failing test: an explainer with a 121-word walk-through makes the check fail naming that diagram. [human]
Patched: AC-36

Session 3 (2026-11-08): plan stage, architecture choices nothing upstream settled. Asked of the human.

## Asked · Q12 · architecture; contradiction FR-5 vs FR-17 · 2026-11-08
Question: How does the explainer link from quickstart without reopening the approved plan?
Context: The plan jury judges quickstart.md; any edit after approval withdraws the approval and stalls tasks, which breaks "never block".
Options: 1. Gate ignores the one "Read first" line (recommended). 2. Template writes the line up front. 3. Drop the quickstart edit (spec change).
Refs: FR-5, FR-17, RF-9, RF-10, jury.py:182

## Asked · Q13 · architecture · 2026-11-08
Question: Which mechanics run in nio rather than in the skill's instructions?
Options: 1. One nio explain command for hashes, rendering, safe deletes, topic names (recommended). 2. Instructions only. 3. nio prints hashes only.
Refs: FR-9, FR-14, FR-24, FR-26, FR-27, RF-12, RF-13, RF-17

## Asked · Q14 · architecture · 2026-11-08
Question: When should nio flow next suggest @nio:explain?
Options: 1. After plan approval, only while explainer.md is missing (recommended). 2. Always after plan approval. 3. Every later stage while missing.
Refs: FR-18, AC-23, AC-24, RF-8

## Q12 · architecture; contradiction FR-5 vs FR-17 · 2026-11-08
Answer: 1. Gate ignores that one line: the plan gate reads quickstart without the single 'Read first: explainer.md' line, as it already ignores tasks' Fixes sections. Approval holds; a second special case in the gate code. [human]
Patched: architecture.md

## Q13 · architecture · 2026-11-08
Answer: 1. One nio explain command: hashes, pinned rendering, safe deletes of its own old images, topic file names; the skill writes diagrams and prose and calls it. [human]
Patched: architecture.md

## Q14 · architecture · 2026-11-08
Answer: 1. Only while it's missing: after plan approval, one extra line in nio flow next suggests the explainer until explainer.md exists. [human]
Patched: architecture.md

Session 4 (2026-11-08): plan stage, contracts and tests. Calls below the grill's bar, made by the planning agent.

## Call · CT-1, CT-11, Data model · 2026-11-08
Explainer layout: one `## ` section per diagram (`Component map`, `Build order`, `Flow: UJ-n …`, `State: <table>`, `Drill-down: <item>`, a topic's `Overview`); the walk-through is the section's prose; source, images and topic lines written as `(source: …)`, `(images: …)`, `(topic: …)`, the source form matching the onboarding plan's. The spec names these things but not their markdown; one fixed shape is what lets the check find them.
Changes what a user sees: yes, the explainer's headings and three record lines. Data kept: the lines FR-24, FR-26 and FR-27 already ask for, nothing more.
Patched: CT-1, CT-11, Data model

## Call · CT-2 · 2026-11-08
Node IDs are counted by a fixed rule: labels in quotes and brackets dropped, then arrow endpoints and `participant`/`actor`/`state` names. FR-7 defines a node as a distinct node ID but not how to find one; the rule covers the flowchart, sequence and state diagrams the skill draws. A gantt build order counts 0.
Changes what a user sees: no (FR-7's cap is the visible effect). Data kept: none.
Patched: CT-2

## Call · CT-3, CT-4 · 2026-11-08
A failed render with `Parse error` in its output is a broken block; any other failure is the renderer that couldn't be fetched (RF-3 measured both). Under a host-skill format the check still renders any Mermaid block in the file, because after a fallback (FR-21) the config still names the missing skill and only the blocks show what was drawn; a host skill's own blocks aren't Mermaid, so their rendering is skipped, with the note naming the format.
Changes what a user sees: the check's messages and notes, worded in CT-4. Data kept: none.
Patched: CT-3, CT-4

## Call · CT-5 · 2026-11-08
`nio explain finish` also refuses plan mode while the plan gate is open (the skill refuses first, FR-23); names images `<stem>-<section title>.svg`, the drill-down marker left out so an image keeps its name; never counts an image a drill-down section links as a deletion candidate, rendered or not, so FR-26's "never delete a drill-down section's SVG" holds even without Node.
Changes what a user sees: image file names. Data kept: only the images FR-26 already allows; none of a drill-down's is ever deleted.
Patched: CT-5

## Call · CT-6 · 2026-11-08
`nio explain topic` continues any of a day's files for a topic (`-explainer.md`, `-2`, …) whose stored topic text equals the new one, else names the first free one. FR-27 says to continue on an equal stored topic and otherwise take the next free name; checking the numbered files too keeps a repeated clashing topic from opening a third file.
Changes what a user sees: which file a repeated topic continues. Data kept: no change.
Patched: CT-6

## Call · CT-7, CT-8 · 2026-11-08
`nio status` prints FR-16's line, then `  in .nio/specs/<slug>/: re-run @nio:explain`, since several specs may each have an explainer. `nio flow next`'s suggestion appears at the tasks, tasks jury and implementing stages while working, as `suggest: run … for <slug> (no explainer.md yet)`; not while the effort waits on the human, where the talk shape owns the message.
Changes what a user sees: yes, these two lines. Data kept: none.
Patched: CT-7, CT-8

## Call · CT-11, CT-12, CT-13 · 2026-11-08
The skill is one file with three contracts (its steps, its Drill-down section, its Format section), so each user story delivers its own part.
Changes what a user sees: no. Data kept: none.
Patched: CT-11, CT-12, CT-13

## Call · TC-1 to TC-42 · 2026-11-08
Integration tests use a fake `npx` on PATH (an SVG, a parse error, a network failure), so they run offline and fast; the real renderer runs only in the e2e tests (NIO_E2E=1), like the other model-run tests. Two journey misuses get no test: "draws components the plan does not have" (no requirement makes the check refuse an extra component) and "the stale line is ignored for weeks" (FR-17 means nothing should act on it).
Changes what a user sees: no. Data kept: none.
Patched: tests.md

Session 5 (2026-11-08): plan jury round 1 findings that change behaviour or need the human, asked of the human.

## Asked · Q15 · J-6 · 2026-11-08
Question: What protects a drill-down section the agent drops when it rewrites the explainer?
Options: 1. finish refuses if a kept section went missing (recommended). 2. finish restores it from the previous version. 3. Accept as risk (git history only).
Refs: J-6, FR-25, FR-26, CT-5, CT-11

## Asked · Q16 · J-7 · 2026-11-08
Question: Should running only the finishing step be able to clear the stale flag?
Options: 1. finish keeps the old hashes unless a diagram changed (recommended). 2. Accept as risk. 3. Separate --refresh flag.
Refs: J-7, FR-16, FR-24, CT-5, TC-29, QS-4

## Asked · Q17 · J-8 · 2026-11-08
Question: What about a clone still on an older nio, which reads the "Read first" line as an edit to the approved plan?
Options: 1. Accept as risk (recommended). 2. Write the line only when the plan gate code is new enough. 3. Never write the line.
Refs: J-8, CT-9, FR-5

## Q15 · J-6 · 2026-11-08
Facet: data
Answer: 1. Refuse if one went missing: the finishing step compares the drill-down headings with the previous version and refuses, naming the missing ones, before deleting anything. Nothing lost; the agent redoes the rewrite. [human]

## Q16 · J-7 · 2026-11-08
Facet: data
Answer: 1. Only after a diagram changed: the finishing step updates the hashes only if some diagram block changed since the last run; otherwise it keeps them and says the explainer is still stale. [human]

## Q17 · J-8 · 2026-11-08
Facet: failure
Answer: 1. Accept as risk: single user, nio ships with the repo, mixed versions unlikely; if it happens the effort goes back to the plan jury once. [human]

Session 5 (2026-11-08): plan jury round 1 fixes. Calls by the planning agent; J-6, J-7 and J-8 are the human's (Q15 to Q17).

## Call · J-1 · 2026-11-08
`nio flow next` suggests the explainer only when plan.md exists, and the skill's guard also requires plan.md: a lite effort has no plan, so FR-18's "after the plan gate closes" never applies to it.
Patched: CT-8, CT-11

## Call · J-2, J-12 · 2026-11-08
TC-17 to TC-19 run the skill, so they move to US-1's entry, and TC-26 moves to US-4's. TC-10 moves to US-3, which delivers finish. The order is unchanged, and every test can run once its entry is built.
Patched: plan.md build order

## Call · J-4 · 2026-11-08
The status function is `explain.stale`, the name architecture.md uses.
Patched: CT-7, CT-10

## Call · J-5 · 2026-11-08
QS-1 passes only when the component map names every contract, CT-1 to CT-13.
Patched: QS-1

## Call · J-6, J-7 · 2026-11-08
How the human's answers are stored: a `(drill-downs: …)` line and a `(diagrams: <12 hex>)` line in the explainer, so no git is needed. Finish checks the drill-downs before anything else that writes. The diagrams hash covers every section's fenced block except the drill-downs. Without a redraw, finish prints `still stale: …` and keeps the old hashes. TC-29 now redraws before finish, TC-43 and TC-44 test the two refusals, and QS-4 shows finish alone keeping the stale line. QS-4 is now manual, because only a run of the skill redraws.
Patched: CT-5, Data model, TC-29, TC-43, TC-44, QS-4

## Call · J-9 · 2026-11-08
Finish does all its work in memory and writes explainer.md once, through a temporary file and `os.replace`. A listed image that is already gone is skipped silently. `npx` gets a 120 s timeout, which counts as unreachable. TC-45 covers a stopped run followed by a re-run.
Patched: CT-3, CT-5, TC-45

## Call · J-10 · 2026-11-08
Images are named `<stem>--<title slug>.svg`, with `-2`, `-3` on a clash within one run. A slug never starts with a dash, so one file's prefix can't match another's. In topic mode, deletion requires the `<stem>--` prefix. TC-46 covers both clashes.
Patched: CT-5, Data model, TC-46

## Call · J-11 · 2026-11-08
A drill-down section whose linked image exists is left as it is and keeps its image on the images line. TC-10 now asserts that the drill-down image is byte-unchanged and that a listed in-folder `other.svg` without the prefix survives with a warning.
Patched: CT-5, TC-10

## Call · J-13 · 2026-11-08
TC-47 runs finish with no change (no marker), then twice after a change (exactly one marker). It is filed as the UJ-4 misuse, repeated finishes on a stale explainer, because AC-32 is e2e and this is an integration test.
Patched: TC-47

## Call · J-14, J-15 · 2026-11-08
TC-12's walk-through names `CT-3` in prose, so the check must read node labels. TC-42's topic explainer carries a source line that never matches, so only the exclusion of topic explainers keeps `nio status` quiet. Also, from the test-proof notes: TC-5 names the `Calls` block, and TC-19 removes only the folders that hold `npx` from PATH.
Patched: TC-12, TC-42, TC-5, TC-19
