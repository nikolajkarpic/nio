---
slug: 2026-11-08-explainer
route: full
epic: ""                         # "<epic slug>/R-<n>" when this is a slice of an epic
risk: [public-api]               # auth | pii | money | external-input | data-deletion | migration | multi-party | public-api
retired: [OP-1, OP-2, OP-3, OP-4, OP-5, OP-6, OP-7, OP-8, OP-9]                      # IDs removed from this spec; never reused
---
<!-- Spec template. WHAT and WHY only, never HOW. Every item ends with its provenance: [human] (the grill
confirmed it), [research: RF-n] (a finding in research.md) or [agent] (your proposal; the grill must confirm it).
IDs are permanent: number new items after the highest ever used, never renumber, list removed IDs in `retired`.
Remove a section that doesn't apply; never write N/A. `nio check spec 2026-11-08-explainer` checks all of this. -->
# Explain an approved plan, or a topic, with diagrams and a short walk-through

## Summary
A new skill, `@nio:explain`, turns an approved plan into `explainer.md`: diagrams (Mermaid by default, rendered to SVG
images) plus short prose showing what will be built, how, which components and how they talk, the flow per journey,
the state and the build order. Quickstart links to it so a developer or the human approving a plan gets the shape of
the work at a glance before reading the dense contracts and tests. It can also explain a topic or an implementation
interactively, drilling down where the human asks. `nio check explainer` checks it; a changed plan flags it stale but
never blocks. [human]

## Actors and journeys
- **A-1 Developer**: picks up an effort and wants the shape of the work before reading contracts, tests and tasks; skilled, short on time. [human]
- **A-2 Human**: approves plans and asks to have a topic or an implementation explained; drives the drill-down. [human]
- **A-3 Explaining agent**: any host's agent running `@nio:explain`; writes the diagrams and prose, with or without a host diagram skill. [agent]

**UJ-1 Explain an approved plan** (A-3, A-1) [human]
1. The plan jury approves; `nio flow next` suggests `@nio:explain`.
2. The agent writes `explainer.md` with the core diagrams, the conditional ones and a short walk-through, renders each diagram to SVG, and adds the "Read first" line to quickstart.
3. `nio check explainer` passes.
4. A developer opens quickstart, follows the link and reads the explainer first.
- Misuse: the agent draws one huge diagram, or draws components the plan does not have; the developer trusts an explainer the plan has since outgrown.
- Evidence: #123 [research: RF-5].

**UJ-2 Drill down** (A-2, A-3) [human]
1. The agent shows an overview diagram and a short walk-through, then offers three things to zoom into: a component, a flow and a decision.
2. The human picks one; the agent adds a section for it to the same file.
3. Steps 1-2 repeat until the human stops.
- Misuse: the human keeps drilling past the point of use; the agent offers vague or repeated choices.
- Evidence: #123 (Interactive decision).

**UJ-3 Explain a topic** (A-2, A-3) [human]
1. The human asks to explain a topic or an implementation, with or without a spec.
2. The agent writes a topic explainer under `.nio/research/` and runs the drill-down of UJ-2.
- Misuse: a topic explainer is taken for an approved plan's.
- Evidence: #123 (Q1, Q3).

**UJ-4 Notice a stale explainer** (A-1, A-2) [human]
1. The plan changes after the explainer was written.
2. `nio status` prints that `explainer.md` is stale and suggests re-running `@nio:explain`; nothing is blocked.
3. The human or agent re-runs `@nio:explain`; the stale line goes away.
- Misuse: the stale line is ignored for weeks.
- Evidence: #123 (Q7).

## User stories

### US-1 Explain an approved plan (P1) [human]
- **Why this priority:** it is the core value of #123: the shape of the work at a glance, next to the dense plan.
- **Independent test:** on a fixture spec with an approved plan, run `@nio:explain`; `explainer.md` holds the core diagrams and quickstart links to it.

- **AC-1** (FR-1, FR-2, FR-6) Given a spec whose plan the jury approved, when `@nio:explain` runs in plan mode, then `.nio/specs/<slug>/explainer.md` exists holding a component map and a build order diagram, each followed by a walk-through of 1 to 120 words. [human]
  Observable: the file exists; it holds at least two diagram blocks, one titled component map and one titled build order, each followed by prose. Level: e2e.
- **AC-2** (FR-3) Given a spec with two journeys and one state table, when `@nio:explain` runs in plan mode, then the explainer holds one flow diagram per journey and one state diagram. [human]
  Observable: two flow diagrams each naming its UJ-n, and one state diagram naming the state table. Level: e2e.
- **AC-3** (FR-3) Given a spec with no state table, when `@nio:explain` runs in plan mode, then the explainer holds no state diagram and `nio check explainer` still passes. [human]
  Observable: no state diagram block; check exit 0. Level: e2e.
- **AC-4** (FR-5) Given a plan with a quickstart, when `@nio:explain` runs, then the first line of quickstart.md's body is "Read first: explainer.md" linking to the explainer, and a second run leaves exactly one such line. [human]
  Observable: one "Read first: explainer.md" line, at the top, after two runs. Level: integration.
- **AC-5** (FR-7) Given a plan with more components than fit one readable diagram, when `@nio:explain` runs, then no diagram has more than 20 distinct node IDs, and given a fixture explainer with a 21-node diagram, `nio check explainer` fails naming it. [human]
  Observable: distinct node IDs per block at most 20; the fixture check exits 1 naming the diagram. Level: integration.
- **AC-36** (FR-6, FR-8) Given a fixture plan explainer whose build order walk-through has 121 words, when `nio check explainer <slug>` runs, then it fails naming the build order diagram; with the walk-through cut to 120 words it passes. [human]
  Observable: exit 1 naming the diagram, then exit 0. Level: integration.
- **AC-29** (FR-22) Given the shipped `@nio:explain` skill, when it is read, then it holds a Mermaid syntax cheat-sheet, the diagram rules (one question per diagram, the node cap) and a credit line per community skill it borrows from. [human]
  Observable: skills/explain/SKILL.md holds a cheat-sheet section, the rules and at least one credit link. Level: unit.

- **AC-30** (FR-23) Given a spec whose plan gate is still open, when plan mode is asked for it, then no explainer.md is written and the reply says the plan jury comes first and offers topic mode. [agent]
  Observable: no explainer.md in the spec folder; the reply names the plan jury and topic mode. Level: e2e.
- **AC-32** (FR-25) Given a plan explainer with one drill-down section and a changed plan, when `@nio:explain` re-runs, then the diagrams are redrawn and the drill-down section is still in the file, marked as written for an earlier plan. [human]
  Observable: the section's heading and text are present with the marker; the source lines hold the new hashes. Level: e2e.
- **AC-33** (FR-26) Given a previous run that listed `explainer-flow-uj-2.svg`, a kept drill-down's `explainer-drill-1.svg`, `../../README.md` and an unlisted `notes.svg`, and a plan that lost UJ-2, when `@nio:explain` re-runs, then only `explainer-flow-uj-2.svg` is gone and a warning names `../../README.md`. [human]
  Observable: one file deleted; the drill-down SVG, README.md and notes.svg unchanged; the warning line. Level: integration.

### US-2 Check the explainer (P1) [human]
- **Why this priority:** without a check, a broken or incomplete diagram reaches the developer unnoticed.
- **Independent test:** run `nio check explainer <slug>` on fixture explainers: one complete, one missing a contract, one missing build order, one with a broken block.

- **AC-6** (FR-8) Given an explainer whose blocks all render, with both core diagrams and every plan contract ID in the component map's node labels, when `nio check explainer <slug>` runs, then it passes. [human]
  Observable: exit 0. Level: integration.
- **AC-7** (FR-4, FR-8) Given a plan with CT-1, CT-2 and CT-3 and a component map whose node labels name only CT-1 and CT-2, when the check runs, then it fails naming CT-3. [human]
  Observable: exit 1; output names CT-3. Level: integration.
- **AC-8** (FR-8) Given an explainer with no build order diagram, when the check runs, then it fails naming the missing core diagram. [human]
  Observable: exit 1; output names build order. Level: integration.
- **AC-9** (FR-8, FR-10) Given a diagram block with a syntax error, when the check runs, then it fails naming that block as a broken diagram. [human]
  Observable: exit 1; output names the block (its title or position). Level: integration.
- **AC-10** (FR-11) Given no Node on the machine, when the check runs on an otherwise complete explainer, then it skips the render check with a note and still checks the core diagrams and contract IDs. [agent]
  Observable: exit 0; output holds a note that rendering was skipped; removing a contract ID still fails it. Level: integration.
- **AC-11** (FR-1) Given a slug with no explainer.md, when the check runs, then it fails saying the explainer is missing. [agent]
  Observable: exit 1; output names the missing file. Level: integration.

### US-3 Images beside the explainer (P2) [human]
- **Why this priority:** the human wants images, not only diagram source; the text explainer already carries the value without them.
- **Independent test:** on a machine with Node, run `@nio:explain`; one SVG per diagram block sits beside explainer.md.

- **AC-12** (FR-9) Given Node is available, when `@nio:explain` writes an explainer with four diagram blocks, then four SVG files sit next to explainer.md, one per block, and the explainer shows each. [human]
  Observable: four `.svg` files in the spec folder; each is referenced from explainer.md. Level: e2e.
- **AC-13** (FR-10) Given one block fails to render, when `@nio:explain` renders, then that block is flagged as a broken diagram in the explainer and the other blocks still get their SVGs. [human]
  Observable: the explainer marks the block broken; the other SVGs exist. Level: e2e.
- **AC-14** (FR-11) Given no Node on the machine, when `@nio:explain` runs, then the explainer is text only and carries a note saying images were not rendered because Node is missing; with Node but the renderer unreachable, the note says the renderer could not be fetched. [human]
  Observable: no `.svg` written; the explainer holds the note. Level: e2e.

### US-4 Drill down interactively (P2) [human]
- **Why this priority:** the human asked for easy, interactive explaining; the one-shot explainer of US-1 comes first.
- **Independent test:** run `@nio:explain` on a topic, pick one offered item, then stop; the file holds the overview plus one drill-down section.

- **AC-15** (FR-12) Given an overview has been written, when the agent offers what to zoom into, then it offers three items: one component, one flow and one decision. [human]
  Observable: the message lists three items, one of each kind. Level: e2e.
- **AC-16** (FR-13) Given the human picks an item, when the agent answers, then a section for it is appended to the same markdown file and three new items are offered. [human]
  Observable: the file grows by one section named after the item; no new file is created. Level: e2e.
- **AC-17** (FR-13) Given the human says stop, when the agent answers, then nothing more is offered and the file is complete. [human]
  Observable: no offer in the final message; the file ends with the last section. Level: e2e.

### US-5 Explain a topic (P2) [human]
- **Why this priority:** the human wants explain callable alongside research for any topic, not only a plan's output.
- **Independent test:** ask `@nio:explain` about a topic in a repo with no spec; a topic explainer appears under `.nio/research/`.

- **AC-18** (FR-14) Given a topic and no slug, when `@nio:explain` runs, then it writes `.nio/research/<date>-<topic>-explainer.md`, with its SVGs beside it; the topic "../Auth / Tokens!" becomes `auth-tokens`, and the topic "//" is refused. [human]
  Observable: the file exists at that path; any SVGs sit in the same folder. Level: e2e.
- **AC-19** (FR-14) Given no `@nio:research` skill is installed, when the human asks to explain a topic, then topic mode works on its own. [human]
  Observable: the topic explainer is written. Level: e2e.
- **AC-20** (FR-15) Given a topic explainer with no component map, no build order and no contract IDs, when `nio check explainer <its path>` runs, then it raises no core-diagram or contract finding and passes when its blocks render. [agent]
  Observable: exit 0; no core-diagram or contract line in the output. Level: integration.

- **AC-34** (FR-27) Given a topic explainer already exists at today's path for that topic, when `@nio:explain` runs on the same topic, then the same file keeps its earlier sections and gains the new ones; no second file is written. [human]
  Observable: one file; earlier sections unchanged; one new section after a pick. Level: e2e.
- **AC-35** (FR-27) Given today's `auth-tokens-explainer.md` stores the topic "Auth tokens", when `@nio:explain` runs on the topic "auth/tokens", then it writes `auth-tokens-explainer-2.md` and says so, leaving the first file unchanged. [human]
  Observable: two files; the first unchanged; the reply names the new file. Level: e2e.

### US-6 Flag a stale explainer, never block (P2) [human]
- **Why this priority:** an outdated picture misleads; but the explainer is derived, so it must not hold the flow up.
- **Independent test:** write an explainer, change the plan, run `nio status`; then re-run explain and `nio status` again.

- **AC-21** (FR-16) Given explainer.md was written from the plan and the plan changed since, when `nio status` runs, then it prints `stale: explainer.md (spec, plan or contracts changed)` and suggests re-running `@nio:explain`. [human]
  Observable: the stale line and the suggestion in the output; exit status unchanged by it. Level: integration.
- **AC-22** (FR-16) Given the explainer was re-run after the plan change, when `nio status` runs, then no stale line names explainer.md. [human]
  Observable: no line naming explainer.md as stale. Level: integration.
- **AC-23** (FR-17) Given an explainer that is stale or missing, when `nio flow next` or any flow guard runs, then nothing is blocked by it and no jury gate is owed for it. [human]
  Observable: apart from the suggestion of FR-18, `nio flow next` output is the same with and without the explainer; no flow guard refuses for it; no explainer gate exists. Level: integration.

- **AC-31** (FR-16, FR-24) Given an explainer whose source lines match, when only quickstart.md or tests.md changes, then `nio status` prints no stale line for it; when contracts.md changes, it does. [agent]
  Observable: no stale line after the first edit; the stale line after the second; on a fresh copy, the stale line also after editing spec.md, and after deleting contracts.md. Level: integration.

### US-7 Flow suggests explaining once the plan is approved (P2) [human]
- **Why this priority:** the step is only used if the flow points to it.
- **Independent test:** close the plan gate on a fixture effort and run `nio flow next`.

- **AC-24** (FR-18) Given the plan gate has just closed as approved, when `nio flow next` runs, then it suggests `@nio:explain` for that slug. [human]
  Observable: output names `@nio:explain`. Level: integration.
- **AC-25** (FR-18) Given the plan gate is still open, when `nio flow next` runs, then it does not suggest `@nio:explain`. [agent]
  Observable: no `@nio:explain` in the output. Level: integration.

### US-8 Choose the diagram format (P3) [human]
- **Why this priority:** Mermaid by default serves almost everyone; other formats matter only on hosts with a diagram skill.
- **Independent test:** run explain with no config, then with `explain.format` set to a host skill name.

- **AC-26** (FR-19) Given no `explain.format` in `.nio/config.json`, when `@nio:explain` runs, then its diagrams are Mermaid. [human]
  Observable: every diagram block is a Mermaid block. Level: e2e.
- **AC-27** (FR-20) Given `explain.format` names a host skill, when `@nio:explain` runs, then it draws with that skill and `nio check explainer` skips only the render check with a note naming the format; removing a contract ID from the component map section still fails it. [human]
  Observable: check exit 0 with a note naming the format. Level: integration.
- **AC-28** (FR-21) Given `explain.format` names a skill the host does not have, when `@nio:explain` runs, then it draws Mermaid and says it fell back. [human]
  Observable: Mermaid blocks; the explainer or the reply names the missing skill. Level: e2e.

## Functional requirements
- **FR-1** WHEN `@nio:explain` runs for a slug THE SYSTEM SHALL write `.nio/specs/<slug>/explainer.md` from that spec's plan. [human]
- **FR-2** THE SYSTEM SHALL always include a component map and a build order diagram in a plan explainer. [human]
- **FR-3** WHEN the spec has journeys or state tables THE SYSTEM SHALL add a flow diagram per journey and a state diagram per state table, and SHALL add any other diagram only where the agent judges it helps. [human]
- **FR-4** THE SYSTEM SHALL name in each component map node label the plan contract ID (CT-n) it stands for. [human]
- **FR-5** WHEN a plan explainer is written THE SYSTEM SHALL put one "Read first: explainer.md" line, linking to it, at the top of the spec's quickstart.md. [human]
- **FR-6** THE SYSTEM SHALL follow each diagram with a plain-language walk-through of 1 to 120 words, and `nio check explainer` SHALL fail naming a diagram whose walk-through is missing or longer. [human]
- **FR-7** THE SYSTEM SHALL keep each diagram to one question and at most 20 nodes, a node being a distinct node ID in the diagram block; `nio check explainer` SHALL fail naming any diagram over 20. [human]
- **FR-8** WHEN `nio check explainer <slug>` (or a topic explainer's path, FR-15) runs THE SYSTEM SHALL fail, naming each problem, if a diagram block does not render, a core diagram is missing, a plan contract ID is absent from the component map's node labels (under a host skill, from its section text, FR-20), a diagram is over the node cap (FR-7) or a walk-through is missing or too long (FR-6). [human]
- **FR-9** WHILE Node is available THE SYSTEM SHALL render each Mermaid block to an SVG committed next to the explainer and show it in the explainer, using one exact mermaid-cli version that `nio` names. [human]
- **FR-10** IF a diagram block fails to render THEN THE SYSTEM SHALL flag it in the explainer as a broken diagram. [human]
- **FR-11** IF Node is not available, or the pinned renderer cannot be fetched, THEN THE SYSTEM SHALL write the explainer as text only with a note naming which of the two happened, and `nio check explainer` SHALL skip its render check with that note; only a diagram that fails to render fails the check. [human]
- **FR-12** WHEN an overview has been shown THE SYSTEM SHALL offer three items to zoom into: a component, a flow and a decision. [human]
- **FR-13** WHEN the human picks an offered item THE SYSTEM SHALL append a section for it to the same markdown file and offer three again, until the human stops. [human]
- **FR-14** WHEN `@nio:explain` is asked about a topic rather than a slug THE SYSTEM SHALL write `.nio/research/<date>-<topic>-explainer.md`, with its SVGs beside it, where `<topic>` is the topic lowercased, every run of characters other than a-z and 0-9 turned into one dash, trimmed of dashes and cut to 40 characters; an empty result SHALL be refused. [human]
- **FR-15** THE SYSTEM SHALL apply the core-diagram and contract-ID checks to plan explainers only; `nio check explainer` given a topic explainer's path runs the render check alone. [agent]
- **FR-16** WHEN a source recorded in the explainer (FR-24) changed or is gone since it was written THE SYSTEM SHALL print `stale: explainer.md (spec, plan or contracts changed)` in `nio status` and suggest re-running `@nio:explain`. [human]
- **FR-17** THE SYSTEM SHALL neither jury the explainer nor gate the flow on it, stale or missing. [human]
- **FR-18** WHEN the plan gate closes as approved THE SYSTEM SHALL suggest `@nio:explain` in `nio flow next`. [human]
- **FR-19** THE SYSTEM SHALL draw in Mermaid unless `explain.format` in `.nio/config.json` names another format. [human]
- **FR-20** IF `explain.format` names a host skill THEN THE SYSTEM SHALL draw with that skill while explainer.md keeps the core diagram section headings and names every plan contract ID in the component map section's text; rendering alone SHALL be skipped with a note, and the core-diagram, contract-ID, node-cap and walk-through checks still run. [human]
- **FR-21** IF `explain.format` names a skill the host does not have THEN THE SYSTEM SHALL draw Mermaid and say so. [human]
- **FR-22** THE `@nio:explain` skill SHALL carry its own short Mermaid syntax cheat-sheet and diagram rules, crediting the community skills it borrows them from. [human]
- **FR-23** IF plan mode is asked for a slug whose plan gate has not closed as approved THEN THE SYSTEM SHALL refuse, saying the plan jury comes first, and offer topic mode instead. [agent]
- **FR-24** WHEN a plan explainer is written THE SYSTEM SHALL record in it one source line per input, spec.md, plan.md and contracts.md, as `path@<first 12 hex of its SHA-256>`. [agent]
- **FR-25** WHEN a plan explainer is re-run THE SYSTEM SHALL redraw its diagrams and keep every drill-down section below them, marking each as written for an earlier plan only when a source's hash differs from the one recorded (FR-24), and never twice. [human]
- **FR-26** WHEN a plan explainer is re-run THE SYSTEM SHALL, before rendering the new set, delete only SVGs that the previous run listed as its own, that sit in the explainer's own folder, whose names carry the `explainer-` prefix and that it no longer draws; it SHALL never delete a drill-down section's SVG, and SHALL ignore any other listed path with a warning. [human]
- **FR-27** WHEN a topic explainer already exists at its path THE SYSTEM SHALL continue that file (show its overview and offer new items to zoom into, appending sections) only if the topic text stored in it equals the new topic; otherwise it SHALL write the next free `-explainer-<n>.md` name, from 2, and say so. Every topic explainer SHALL store its topic text as typed. [human]

## Rules
### Decision table: what the explainer holds
| Mode (plan, topic) | Spec has journeys (yes, no) | Spec has state tables (yes, no) | → diagrams | Src |
| --- | --- | --- | --- | --- |
| plan | no | no | component map, build order, agent extras | [human] |
| plan | yes | no | component map, build order, a flow per journey, agent extras | [human] |
| plan | no | yes | component map, build order, a state diagram per table, agent extras | [human] |
| plan | yes | yes | component map, build order, a flow per journey, a state diagram per table, agent extras | [human] |
| topic | - | - | an overview diagram, then one per drill-down section | [human] |

### Decision table: images and checks
| explain.format (mermaid, host skill, missing skill) | Node (yes, no) | Block renders (yes, no) | → outcome | Src |
| --- | --- | --- | --- | --- |
| mermaid | yes | yes | SVG beside the explainer; check passes that block | [human] |
| mermaid | yes | no | block flagged broken; check fails naming it | [human] |
| mermaid | no | - | text only with a note; check skips render with a note | [human] |
| host skill | - | - | drawn by the host skill; render skipped with a note; core-diagram, contract, node-cap and walk-through checks still run | [human] |
| missing skill | - | - | falls back to the mermaid rows, saying so | [human] |

## Key entities
- **Plan explainer**: `.nio/specs/<slug>/explainer.md`; diagrams and walk-through of an approved plan, plus drill-down sections. [human]
- **Topic explainer**: `.nio/research/<date>-<topic>-explainer.md`; an overview and drill-down sections on a topic. [agent]
- **Diagram block**: one diagram in the explainer, answering one question. [human]
- **Rendered image**: the SVG of one diagram block, committed beside its explainer. [human]
- **explain.format**: the config key choosing the diagram format; default `mermaid`. [agent]

## Non-functional requirements
- **NFR-1** THE SYSTEM SHALL keep every diagram at or under 20 distinct node IDs. [human]
- **NFR-2** THE SYSTEM SHALL let any host's agent write a Mermaid explainer with no tool installed; only rendering needs Node. [human]

## Success criteria
- **SC-1** On this repo, an explainer for an approved plan passes `nio check explainer` and its component map names every contract of the plan and its build order diagram names every build-order entry of plan.md, in the same order. [agent]

## Non-goals
- Jurying the explainer or gating the flow on it. [human]
- Regenerating the explainer on its own when the plan changes; it is only flagged stale. [human]
- Vendoring or depending on a community Mermaid skill; NIO writes its own minimal one. [human]
- Building `@nio:research`. The wish to pair explain with research is served by topic mode, which any stage or research step can call on a topic (FR-14); a research skill that calls it is a separate issue. [human]
- PNG images or other render formats than SVG. [agent]
- Flagging topic explainers stale. [agent]

## Glossary
- **Explainer**: the markdown file `@nio:explain` writes, plan or topic. Never "diagram doc".
- **Plan mode**: explaining a spec's approved plan, written into its spec folder.
- **Topic mode**: explaining a topic or an implementation, written under `.nio/research/`.
- **Core diagrams**: the component map and the build order, always present in a plan explainer.
- **Drill-down**: the offer of three items to zoom into, and the section added for the one picked.

## Risks and evidence against
- Rendering through `npx` fetches and runs a third-party package, needs Node, and may be slow inside a check that other checks keep fast: about 3 s per block once cached, and the cache takes 382 MB plus a headless Chrome. [research: RF-3, RF-4]
- An explainer that drifts from the plan misleads more than none; staleness is only flagged. [agent]

## Decisions
- Spec jury round 2, the human (Q10-Q11): a topic slug clash with a different stored topic writes `-explainer-<n>.md`; a test proves the 120-word limit.
- Spec jury round 1, the human (Q4-Q9): re-runs delete only own-prefixed images in the explainer's folder, never drill-down images; a host skill skips rendering only; the check enforces 20 nodes and 120-word walk-throughs; mermaid-cli pinned and failures named; topics slugged to a-z0-9 dashes, 40 chars.
- Grill delegated to an agent by the human, 2026-11-08; deletion and overwrite points asked to the human (Q1-Q3).
- Re-run keeps drill-down sections, marking each as written for an earlier plan only when a source hash changed, once; deletes only its own orphaned SVGs; a repeated topic continues its file: the human, Q1-Q3.
- Plan explainer staleness: hashes of spec.md, plan.md, contracts.md recorded in the explainer; quickstart.md (which explain itself edits) and tests.md are not sources: agent call.
- `nio check explainer` ships in the `nio` Python package, installed with uv: D-261024-adue (memory, 2026-10-24).

## Open points
