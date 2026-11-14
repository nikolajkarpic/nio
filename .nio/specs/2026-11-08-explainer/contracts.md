---
slug: 2026-11-08-explainer
retired: []                      # CT IDs removed from this plan; never reused
---
# Contracts: explainer

## Contracts

### CT-1 The explainer's sections (FR-2, FR-3, FR-6, FR-24) [agent]
- Binding: `src/nio/explain.py:sections` (new)
- Like: `src/nio/spec.py:sections`
- Kind: function
- Shape: `sections(text) -> list[dict]`, one per `## ` heading in order: `{"title": str, "fence": str | None, "block": str | None, "walk": str, "drill": bool}`. `fence` is the language of the section's first fenced block (`mermaid` for a Mermaid block), `block` its source. A diagram section is one with a fenced block or a line starting `![`. `walk` is the section's text without fenced blocks, `![` lines, lines starting `> ` and the record lines of the Data model, with surrounding blank lines removed. `drill` is true when the title starts `Drill-down: `.
- Accepts: the text of an explainer, plan or topic; text before the first `## ` heading belongs to no section.
- Returns: the list; `[]` for a file with no `## ` heading.
- Rules: the core diagrams are the sections titled `Component map` and `Build order`, compared case-insensitively (FR-2, FR-20: "explainer.md keeps the core diagram section headings").

### CT-2 Node IDs in a diagram block (FR-7, NFR-1) [agent]
- Binding: `src/nio/explain.py:nodes` (new)
- Like: `src/nio/spec.py:defined`
- Kind: function
- Shape: `nodes(block) -> set[str]`
- Accepts: a diagram block's source, Mermaid or another fenced language.
- Returns: the distinct node IDs. Each `"…"`, `[…]`, `(…)`, `{…}` and `|…|`, delimiters included, is dropped first, then the first line (the diagram type) and lines starting `%%`, `classDef`, `class `, `style `, `linkStyle`, `click `, `subgraph` or `end` are skipped. An ID is a token `[A-Za-z_][\w]*` that is an endpoint of an arrow (`-->`, `---`, `-.->`, `==>`, `->>`, `-->>`, `->`), or follows `participant `, `actor ` or `state `, or stands alone on a line.
- Rules: "a node being a distinct node ID in the diagram block" (FR-7); "at most 20 nodes" (FR-7).

### CT-3 Render one block (FR-9, FR-10, FR-11) [agent]
- Binding: `src/nio/explain.py:render` (new)
- Like: `src/nio/jury.py:blob`
- Kind: function
- Shape: `MERMAID = "@mermaid-js/mermaid-cli@11.4.2"`; `render(block, out) -> str`, running `npx -y MERMAID -i <temp .mmd> -o <out>` with `subprocess.run(..., timeout=TIMEOUT)`, `TIMEOUT = 120` seconds.
- Accepts: a Mermaid block's source and the SVG path to write.
- Returns: `"ok"` when the run exits 0 and `out` exists; `"broken: <first stderr line holding Parse error>"` when it exits non-zero with `Parse error` in its output; `"no node"` when `shutil.which("npx")` is None; `"unreachable"` for any other failure, `FileNotFoundError` and `subprocess.TimeoutExpired` included.
- Rules: "using one exact mermaid-cli version that `nio` names" (FR-9); "naming which of the two happened" (FR-11). [research: RF-3]

### CT-4 `nio check explainer` (FR-1, FR-6, FR-7, FR-8, FR-11, FR-15, FR-20, NFR-1) [agent]
- Binding: `src/nio/explain.py:check` (new)
- Like: `src/nio/plan.py:check`
- Kind: cli
- Shape: `nio check explainer <slug | path>`; `check(root, target, gate=False, base="HEAD") -> (errors, notes)`, called from the dispatch map in `cli.py` beside `spec`, `plan` and `tasks`; `--gate` and `--base` change nothing. Prints `ERROR <e>` per error, then the notes, then `<n> errors`; exit 1 when there is an error, else 0, as the other checks do.
- Accepts: a slug (plan mode: `.nio/specs/<slug>/explainer.md`) or a path to a `.md` file (relative to the repo root or absolute; a path resolving to `.nio/specs/<slug>/explainer.md` is plan mode, any other is topic mode).
- Returns, in plan mode, one error each for:
  - `explainer missing: .nio/specs/<slug>/explainer.md` (the only error then);
  - `missing core diagram: component map` and `missing core diagram: build order`, for a core section that is absent or has no diagram;
  - `component map misses CT-n`, for each `### CT-n` in contracts.md (`implement.defs`) not named in the component map's node labels (the bracketed and quoted text CT-2 drops), or, when `explain.format` isn't `mermaid`, anywhere in that section's text;
  - `too many nodes: <title> (<n> > 20)`, for each diagram section whose fenced block has more than 20 node IDs (CT-2);
  - `walk-through missing: <title>` when `walk` is empty, and `walk-through too long: <title> (<n> words)` when it has more than 120 words split on whitespace;
  - `broken diagram: <title>`, for each Mermaid block CT-3 reports `broken`.
  In topic mode only the `explainer missing` and `broken diagram` errors apply.
- Notes: `render skipped: Node is not installed` (CT-3 `no node`) or `render skipped: the renderer could not be fetched` (`unreachable`), after which no further block is rendered; `render skipped: diagrams drawn with <format>` when `explain.format` is set and isn't `mermaid` (Mermaid blocks in the file are still rendered, for the fallback of FR-21).
- Fails: an unknown slug with no spec folder → `error: no effort <slug> under .nio/specs/`, exit 1.
- Rules: "the core-diagram and contract-ID checks to plan explainers only; `nio check explainer` given a topic explainer's path runs the render check alone" (FR-15); "only a diagram that fails to render fails the check" (FR-11).

### CT-5 `nio explain finish` (FR-5, FR-9, FR-10, FR-11, FR-23, FR-24, FR-25, FR-26) [human]
- Binding: `src/nio/explain.py:finish` (new)
- Like: `src/nio/plan.py:new`
- Kind: cli
- Shape: `nio explain finish <path>`; `finish(root, path) -> list[str]`, the lines it prints. Run by the skill after it writes or rewrites the explainer's text.
- Accepts: the path of an explainer the skill has just written. Plan mode as in CT-4.
- Returns, doing in this order, all in memory until step 8:
  1. plan mode only: refuses unless plan.md exists and `plan.approved(root, slug)` is ok (`error: the plan jury comes first (<why>); explain a topic instead`);
  2. refuses when a heading the drill-downs line records has no `## Drill-down: ` section now, the marker ignored (`error: drill-down sections missing: <heading>, <heading>; restore them before finishing`) (the human, Q15);
  3. plan mode only: if any recorded source hash differs from the file's hash now, appends ` (written for an earlier plan)` to each `## Drill-down: ` heading that doesn't end with it;
  4. plan mode only: computes the diagrams hash, the first 12 hex of `flow.sha` over the fenced blocks of every section but the drill-downs, joined in order. When the file has no source lines, or the diagrams hash differs from the recorded one, writes one source line per spec.md, plan.md and contracts.md (`implement.digest(root, path)[:12]`, which is `flow.sha` of the bytes) and the diagrams line; otherwise keeps both and, when a source hash differs, prints `still stale: no diagram changed since the last finish; redraw the diagrams to clear the stale line` (the human, Q16);
  5. for each path the old images line lists: a path outside the explainer's folder, or whose name doesn't start with the image prefix (`explainer-` in plan mode, `<stem>--` in topic mode), prints `warning: ignored <path>: not this explainer's own image`; a file already gone is skipped silently; one that is a name step 6 will use, or that a `## Drill-down: ` section links, is kept; any other is deleted, printing `deleted: <name>`;
  6. removes the image links and `> ` notes an earlier finish wrote, except in a `## Drill-down: ` section whose image link names an existing file, which is left as it is. Renders each other Mermaid section's block (CT-3) to `<stem>--<title slug>.svg` beside the explainer (the title without the marker, named by CT-6's rule without the 40-character cut), with `-2`, `-3` added before `.svg` when an earlier section of this run took that name; adds `![<title>](<file>)` under the block when `ok`, or `> Broken diagram: <reason>` when `broken`; on `no node` or `unreachable` renders nothing more and writes `> Images not rendered: Node is not installed.` or `> Images not rendered: the renderer could not be fetched.` under the title;
  7. sets the images line to the SVGs it rendered plus the existing ones drill-down sections link, and the drill-downs line to every `## Drill-down: ` heading, the marker left out;
  8. writes explainer.md once, through a temporary file and `os.replace`; in plan mode, then makes `Read first: [explainer.md](explainer.md)` the first line of quickstart.md's body, once, when quickstart.md exists, the same way.
  It prints `finished: <path>` last. On a refusal it prints `error: …`, exits 1, and writes and deletes nothing. A run stopped before step 8 leaves explainer.md as it was, and a new run over it carries on from that.
- Rules: "delete only SVGs that the previous run listed as its own, that sit in the explainer's own folder, whose names carry the `explainer-` prefix and that it no longer draws; it SHALL never delete a drill-down section's SVG, and SHALL ignore any other listed path with a warning" (FR-26); "marking each as written for an earlier plan only when a source's hash differs from the one recorded (FR-24), and never twice" (FR-25); "one "Read first: explainer.md" line, linking to it, at the top of the spec's quickstart.md" (FR-5).

### CT-6 `nio explain topic` (FR-14, FR-27) [human]
- Binding: `src/nio/explain.py:topic` (new)
- Like: `src/nio/records.py:slug`
- Kind: cli
- Shape: `nio explain topic "<text>"`; `topic(root, text, today=None) -> str`, printed as `continue: <path>` or `new: <path>`.
- Accepts: the topic as typed. The name is `re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:40]`.
- Returns: for `.nio/research/<YYYY-MM-DD>-<name>-explainer.md`, then `-explainer-2.md`, `-3` and on: the first that doesn't exist (`new:`), unless an earlier one stores this exact topic text (`continue:` with that path).
- Fails: an empty name → `error: the topic "<text>" gives an empty file name`, exit 1.
- Rules: "every run of characters other than a-z and 0-9 turned into one dash, trimmed of dashes and cut to 40 characters; an empty result SHALL be refused" (FR-14); "only if the topic text stored in it equals the new topic" (FR-27).

### CT-7 Stale explainers in `nio status` (FR-16, FR-17) [agent]
- Binding: `src/nio/explain.py:stale` (new)
- Like: `src/nio/query.py:status`
- Kind: function
- Shape: `stale(root) -> list[str]`; `cli.py` prints them after `query.status(root)`, also when there is no index.
- Returns: for each `.nio/specs/*/explainer.md`, in folder order, whose source lines hold a path that is gone or whose hash now differs: `stale: explainer.md (spec, plan or contracts changed)` then `  in .nio/specs/<slug>/: re-run @nio:explain`. An explainer with no source lines, and every file under `.nio/research/`, gives nothing.
- Rules: "print `stale: explainer.md (spec, plan or contracts changed)` in `nio status` and suggest re-running `@nio:explain`" (FR-16); `nio status` keeps exit 0.

### CT-8 `nio flow next` suggests the explainer (FR-17, FR-18) [human]
- Binding: `src/nio/flow.py:next_step` (existing)
- Kind: function
- Shape: in the `working` branch, when the stage is `tasking`, `tasks_jury` or `implementing` and `.nio/specs/<slug>/plan.md` exists and `.nio/specs/<slug>/explainer.md` doesn't, one more line after `exit:`: `suggest: run {typed("@nio:explain")} for <slug> (no explainer.md yet)`.
- Rules: "suggest `@nio:explain` in `nio flow next`" (FR-18) only after "the plan gate closes as approved"; "neither jury the explainer nor gate the flow on it, stale or missing" (FR-17): `SKILL`, `EXIT`, the guards and the gates are unchanged.

### CT-9 The plan gate ignores the "Read first" line (FR-5, FR-17) [human]
- Binding: `src/nio/jury.py:planned` (existing)
- Kind: function
- Shape: `planned("quickstart.md", text)` returns `text` without the first line that is exactly `Read first: [explainer.md](explainer.md)` (and the blank line after it); `artefact` reads every gate's files through `planned`, not only the tasks gate's; `flow.judged_blob` and `flow.scan` compare quickstart.md through `planned` as they do tasks.md.
- Rules: a quickstart.md without that line reads exactly as before, so a version judged before this change still compares equal (the human, Q12).

### CT-10 CLI wiring (FR-5, FR-8, FR-14, FR-16) [derived: FR-8]
- Binding: `src/nio/cli.py:main` (existing)
- Kind: cli
- Shape: `check`'s `what` choices gain `explainer`, dispatched to `explain.check`; `--approved` with `explainer` is refused as it is with `spec`. A new `explain` group with `finish <path>` and `topic <text>`, each printing its lines and turning a `ValueError` into `error: <message>` and exit 1. `status` prints `explain.stale(root)` after the index lines.

### CT-11 The `@nio:explain` skill (FR-1, FR-2, FR-3, FR-4, FR-6, FR-7, FR-14, FR-22, FR-23, FR-25, FR-27, NFR-2) [agent]
- Binding: `skills/explain/SKILL.md` (new)
- Like: `skills/plan/SKILL.md`
- Kind: file
- Shape: front matter `name: explain` and a description; the "Talking to the human" block word for word; inputs and outputs; when to stop; the sections of CT-12 and CT-13. Steps:
  - plan mode, given a slug: run `nio check plan <slug> --approved` and look for `.nio/specs/<slug>/plan.md`; on a non-zero exit or no plan.md refuse, saying the plan jury comes first, and offer topic mode (FR-23). Read spec.md, plan.md and contracts.md. Write `.nio/specs/<slug>/explainer.md`: a `# ` title; `## Component map` (one node per `CT-n`, its label naming the ID); `## Build order` (one node per plan.md build-order entry, in that order); `## Flow: UJ-n <name>` per journey; `## State: <table name>` per spec state table; other diagrams only where they help; each section one diagram and 1 to 120 words of walk-through after it, at most 20 node IDs. On a re-run keep the old source, diagrams, images and drill-downs lines and every `## Drill-down: ` section below the diagrams, unchanged (FR-25). Then run `nio explain finish <path>` and `nio check explainer <slug>`, and fix what the check names.
  - topic mode, given a topic: run `nio explain topic "<topic>"`; on `continue:` show the file's overview and go to the drill-down; on `new:` write `# <topic>`, a `(topic: <text as typed>)` line and a `## Overview` section, run `nio explain finish <path>`, and say which file it wrote when its name ends `-explainer-<n>.md` (FR-27). It needs no other skill.
  - a "Mermaid cheat-sheet" section (flowchart, sequence, state and gantt syntax, quoting labels, the node-ID rule of CT-2) and a "Diagram rules" section (one question per diagram, at most 20 nodes, a walk-through of 1 to 120 words), each ending with a `Credit:` line linking the community skill it borrows from (FR-22).
  The README's skill table gains a row for it.
- Rules: "let any host's agent write a Mermaid explainer with no tool installed; only rendering needs Node" (NFR-2): every step but `finish`'s rendering works without Node.

### CT-12 The skill's drill-down (FR-12, FR-13) [agent]
- Binding: `skills/explain/SKILL.md:Drill-down` (new)
- Like: `skills/grill/SKILL.md`
- Kind: file
- Shape: a `## Drill-down` section of the skill: after an overview (a plan explainer's diagrams or a topic's `## Overview`), offer exactly three items, one component, one flow and one decision, each named concretely from the file, never one already drilled into in this file; on a pick append `## Drill-down: <item>` with one diagram and its walk-through to the same file, run `nio explain finish <path>`, and offer three again; on stop offer nothing more.
- Rules: "offer three items to zoom into: a component, a flow and a decision" (FR-12); "append a section for it to the same markdown file and offer three again, until the human stops" (FR-13).

### CT-13 The skill's diagram format (FR-19, FR-20, FR-21) [agent]
- Binding: `skills/explain/SKILL.md:Format` (new)
- Like: `skills/install/SKILL.md`
- Kind: file
- Shape: a `## Format` section of the skill: read `explain.format` from `.nio/config.json` and its local and global layers, default `mermaid`. A host skill by that name draws instead, the explainer keeping the section headings of CT-11 and naming every `CT-n` in the component map section's text, and `nio explain finish` still runs (it renders nothing then). When the host has no skill by that name, draw Mermaid and say so in the reply.
- Rules: "draw in Mermaid unless `explain.format` in `.nio/config.json` names another format" (FR-19); "draw Mermaid and say so" (FR-21).

## Data model
- **Plan explainer** (spec Key entity) in `src/nio/explain.py:SOURCE` (new) [agent]
  - source lines: one per input, `(source: .nio/specs/<slug>/<file>@<12 hex>)`, after the `# ` title. "record in it one source line per input, spec.md, plan.md and contracts.md, as `path@<first 12 hex of its SHA-256>`" (FR-24)
  - drill-down marker: ` (written for an earlier plan)` at the end of a `## Drill-down: ` heading, at most once (FR-25)
  - the diagrams line: `(diagrams: <12 hex>)`, the hash of the diagram blocks when the source lines were last written (the human, Q16)
  - the drill-downs line: `(drill-downs: <heading>; <heading>)`, the drill-down headings after the last finish, marker left out (the human, Q15)
- **Rendered image** (spec Key entity) in `src/nio/explain.py:IMAGES` (new) [agent]
  - the images line: `(images: <name>.svg, <name>.svg)`, the SVGs the last finish rendered and the drill-down images it kept, names relative to the explainer's folder; files `<stem>--<title slug>.svg` (`-2`, `-3` on a clash within one run) beside the explainer; the previous images line is how a re-run knows its own. "delete only SVGs that the previous run listed as its own" (FR-26)
- **Topic explainer** (spec Key entity) in `src/nio/explain.py:TOPIC` (new) [agent]
  - the topic line: `(topic: <text as typed>)`, after the `# ` title. "Every topic explainer SHALL store its topic text as typed" (FR-27)
- **explain.format** (spec Key entity) in `src/nio/explain.py:fmt` (new) [agent]
  - `records.config(root).get("explain", {}).get("format", "mermaid")`, a string. "draw in Mermaid unless `explain.format` in `.nio/config.json` names another format" (FR-19)
