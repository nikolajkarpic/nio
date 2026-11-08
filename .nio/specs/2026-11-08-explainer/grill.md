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
