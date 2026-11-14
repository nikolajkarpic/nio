# Intake

we also need an explainer skill/workflow/agent etc which can use any of the standardized skill sets to generate graps and explanations of what will be implemented, how it will be done, what, what achiteture etc. this would be apended into specification quickstart for developer, we need to investigate some of the skills for generating ilustrations/graphs etcs

## Human's own answers during the issue grill (verbatim)

- On shape: "i like the own skill like number 1 option, but i would also like it to be callable in pair wiht nio:research where we can explain a topic or impleemntation easily and interactivly "
- On format: "i like it being configurable and being mermaid by defaulet, but also we need images and easy ways to explain something "
- Picked recommended options for: interactive = explain then drill down; when = after plan jury approves; where = explainer.md linked from quickstart; images = render Mermaid to SVG; diagrams = core set + agent extras; checking = nio check explainer; staleness = flag stale, never block; adopt = write own, borrow ideas.

## Source: https://github.com/nikolajkarpic/nio/issues/123

## What

An **explainer** step that turns an approved plan into a developer-facing picture of what will be built: what changes, how, which components and how they talk, the flow per journey, the state, the build order. Diagrams plus short prose, appended to the spec's quickstart (or linked from it) so a developer can get the shape of the work before reading contracts and tasks.

## Why

`plan.md`, `contracts.md` and `tests.md` are precise but dense. A human approving a plan, or a dev picking up an effort, needs the shape at a glance. This serves "I can read why every autonomous decision was allowed" and the "actionable at a glance" rule.

## Research (2026-11-08)

**Format.** Mermaid is the lowest common denominator: plain text inside markdown, renders natively on GitHub, diffable, needs no tool for any agent to *write* it. Fits "agent-agnostic" and "files and git are the state". D2, PlantUML, Graphviz and Excalidraw all need a binary or an app to render; none are installed here (`mmdc`, `dot`, `d2`, `plantuml` all missing; `npx` exists, so `npx @mermaid-js/mermaid-cli` could validate/render on demand).

**Skills already on this machine (all host-specific, so optional helpers only):**
- `artifact-diagramming` / `dataviz` (Claude Code): inline SVG / HTML pages, published as private claude.ai pages.
- `figma:figma-generate-diagram` (Figma MCP): Mermaid -> FigJam board.
- `graphify`, `codegraph`, `claude-mem:pathfinder`: maps of the *existing* code (inputs for "where it lands", not for drawing the plan).

**Community skills** (same shape: a SKILL.md plus `references/` per diagram type): [Agents365-ai/mermaid-skill](https://github.com/Agents365-ai/mermaid-skill), [athola architecture-diagram](https://skillselion.com/skills/athola/claude-night-market/architecture-diagram) (caps at 15-20 nodes), [oimiragieo diagram-generator](https://skills.sh/oimiragieo/agent-studio/diagram-generator), [ccheney mermaid-diagrams](https://agent-skills.md/skills/ccheney/robust-skills/mermaid-diagrams), [arisng mermaid-creator](https://agent-skills.md/skills/arisng/github-copilot-fc/mermaid-creator), [diagram-generation](https://claudskills.com/skills/diagram-generation/) (Mermaid/PlantUML/D2/Graphviz/C4), several Excalidraw generators ([awesome-copilot](https://www.vibeindex.ai/skills/github/awesome-copilot/excalidraw-diagram-generator), [ooiyeefei](https://agent-skills.md/skills/ooiyeefei/ccc/excalidraw)). Not read in full yet. Common lesson: cap node count, one diagram per question, references per diagram type.

## Open questions: brainstorm all of these before implementing

1. **Shape:** a new skill (`@nio:explain`), a step at the end of `@nio:plan`, or an agent card the plan skill calls?
2. **When:** after the plan is drafted (jurors and the human see it), or after the plan jury approves (no churn)?
3. **Where:** a section appended to `quickstart.md`, or its own `explainer.md` linked from quickstart?
4. **Format:** Mermaid only; Mermaid by default with "use the host's diagram skill if one exists"; or pluggable via extensions config?
5. **Which diagrams:** a fixed set (components/contracts, a sequence per journey, state from the spec's state tables, build order) or the agent picks what helps?
6. **Checking:** none, a `nio check` lint (fenced blocks parse, every node maps to a contract/component ID), or a real render via `npx mermaid-cli`?
7. **Staleness and review:** is it derived (regenerated when the plan changes, not juried) or a juried artifact? Does `nio flow` gate on it?
8. **Rendered images:** text only, or also commit SVG/PNG?
9. **Adopt or write:** vendor/recommend a community Mermaid skill, or write a minimal NIO one?


### Decisions (issue comments)
> **Q1 Shape, decided 2026-11-08:** its own skill, `@nio:explain`. Also callable alongside research to explain a topic or an implementation, interactively (not only a plan's output).
> **Interactive, decided 2026-11-08:** explain, then drill down. Overview diagram + short walk-through, then offer 3 things to zoom into (component, flow, decision); human picks, a section is added, repeat until they stop. Saved as one markdown file. Note: no @nio:research skill exists yet; topic mode stands on its own.
> **Q2 When, decided 2026-11-08:** after the plan jury approves. `nio flow next` suggests @nio:explain once the plan gate closes.
> **Q3 Where, decided 2026-11-08:** `.nio/specs/<slug>/explainer.md`, with a 'Read first: explainer.md' line at the top of quickstart.md. Topic mode writes under `.nio/research/` (to confirm with Q-format).
> **Q4 Format, decided 2026-11-08:** configurable, Mermaid by default. Also wants images and easy ways to explain (not just diagram source). How images are made: see Q8.
> **Q8 Images, decided 2026-11-08:** render each Mermaid block to SVG with `npx @mermaid-js/mermaid-cli`, committed next to explainer.md. Render failure flags a broken diagram. No Node: text only, with a note.
> **Q5 Diagrams, decided 2026-11-08:** core set + agent extras. Always a component map and the build order; a flow per journey and a state diagram when the spec has them; anything else the agent judges helpful.
> **Q6 Checking, decided 2026-11-08:** `nio check explainer <slug>`: every block renders, the two core diagrams exist, every contract ID in the plan appears in the component map's node labels.
> **Q7 Staleness, decided 2026-11-08:** flag stale, never block. `nio status` prints 'stale: explainer.md (plan changed)' like onboarding docs and suggests re-running @nio:explain. Not juried, no flow gate.
> **Q9 Adopt, decided 2026-11-08:** write our own minimal @nio:explain; borrow rules from community Mermaid skills (<=15-20 nodes per diagram, one question per diagram, short syntax cheat-sheet) with credit.
> 
> **[agent] defaults, below the grill bar (push back if wrong):**
> - Config: `explain.format` in `.nio/config.json`, default `mermaid`. Any other value names a host skill to draw with; render and `nio check explainer` then skip with a note.
> - Topic mode writes `.nio/research/<date>-<topic>-explainer.md` (+ SVGs beside it); the component-map/contract check applies to plan mode only.
> 
> All open questions settled. Next: `@nio:spec` from this issue.
