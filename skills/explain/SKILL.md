---
name: explain
description: Explain an approved NIO plan, or any topic, as a short Mermaid explainer with a walk-through under each diagram. Use when the human asks to explain a plan, a spec's design or how something works. Needs no tool but nio; only rendering the images needs Node.
---

# @nio:explain

Writes a Mermaid explainer: a few small diagrams, each answering one question, each followed by a short walk-through.
Plan mode explains an approved plan; topic mode explains anything the human names.

Run the CLI as `nio` (inside the NIO repo itself: `uv run nio`).

Flow state: only `nio flow` writes `state.json` and `history.jsonl`; never edit them. Only the human gives `--human` to `nio flow done`, runs `nio flow seen`, or asks for `nio flow abandon`.

## Inputs and outputs

- **Input:** a spec slug (plan mode) or a topic in words (topic mode).
- **Outputs:** plan mode writes `.nio/specs/<slug>/explainer.md`; topic mode writes the file `nio explain topic` names.
  Diagram images (`.svg`) are rendered by `nio explain finish` when Node is installed, and skipped with a note when not.
- `spec.md`, `plan.md` and `contracts.md` are read-only here.

## Talking to the human
Every message to the human (question, report, error or hand-off):
1. **First line: what you need from them**, in plain words: "Nothing needed", "Pick one",
   "Run this command", "Approve or push back". A round of questions gets one such line.
2. **Then about 3 lines:** what it is, why it matters, what it costs. Name things by what
   they do, never by an ID or a NIO term they don't start by name; only stage names (spec,
   grill, jury, plan) stay as they are. A fact names its source beside it in plain words.
3. **Options** say what happens if picked, including what's lost. The recommended one goes first.
4. **Long lists** (calls, dispositions, findings): show every item that changes what a user
   can do or sees, who may do it, what data is kept or changed, or what it costs, however
   many; count the rest in one line.
5. **Commands they must run** go in the body, quoted exactly, ready to copy.
6. **End with `Refs:`** when the message rests on anything: the IDs, files and commands it
   rests on, never raw command output. In a question tool, `Refs:` is the question text's
   last line, and each option's description says what happens.
Before sending, ask: could they act on this without opening a file? If not, rewrite it.

## Plan mode (given a slug)

1. Run `nio check plan <slug> --approved` and look for `.nio/specs/<slug>/plan.md`. On a non-zero exit or no `plan.md`,
   refuse: say the plan jury comes first, and offer topic mode instead.
2. Read `spec.md`, `plan.md` and `contracts.md`.
3. Write `.nio/specs/<slug>/explainer.md`:
   - a `# ` title;
   - `## Component map`: one node per `CT-n`, its label naming the ID;
   - `## Build order`: one node per build-order entry in `plan.md`, in that order;
   - `## Flow: UJ-n <name>` per user journey;
   - `## State: <table name>` per state table in the spec;
   - other diagrams only where they help.
   Each section holds one diagram and, after it, a walk-through (see the rules below).
4. On a re-run, keep the old source, diagrams, images and drill-downs lines and every `## Drill-down: ` section below
   the diagrams, unchanged.
5. Run `nio explain finish <path>`, then `nio check explainer <slug>`. Fix what the check names and run both again.

## Topic mode (given a topic)

Run `nio explain topic "<topic>"`.
- `continue:` shows an existing explainer: show its overview and go to the drill-down.
- `new:` write `# <topic>`, a `(topic: <text as typed>)` line and a `## Overview` section, then run
  `nio explain finish <path>`. When the file name ends `-explainer-<n>.md`, say which file you wrote. Then go to the
  drill-down: end every topic run with its three offers, even when images were not rendered.

Topic mode needs no other skill.

## Drill-down

After an overview (a plan explainer's diagrams, or a topic's `## Overview`), offer exactly three items to zoom into: a
component, a flow and a decision, each named concretely from the file and never one already drilled into in this file.
Label them `component`, `flow` and `decision`, then wait for the human.
- On a pick, append `## Drill-down: <item>` to the same file, with one diagram and its walk-through. Run
  `nio explain finish <path>`, then offer three new items again.
- On `stop`, offer nothing more: the file ends with the last section.

## Mermaid cheat-sheet

- Flowchart: `flowchart LR` (or `TD`), then `a["Label"] --> b["Label"]`; `-->|text|` labels an edge.
- Sequence: `sequenceDiagram`, then `A->>B: message`; `participant A as Name`.
- State: `stateDiagram-v2`, then `[*] --> Idle` and `Idle --> Busy: start`.
- Gantt: `gantt`, `dateFormat YYYY-MM-DD`, then `section Name` and `Task :id, 2026-01-01, 3d`.
- Quote every label that holds spaces or punctuation: `a["Plan (approved)"]`.
- A node ID is plain letters, digits and underscores, starts with a letter, and is not a keyword such as `end`.
  The label goes in brackets and quotes, never the ID.

Credit: Mermaid syntax notes adapted from https://github.com/Agents365-ai/mermaid-skill and https://agent-skills.md/skills/ccheney/robust-skills/mermaid-diagrams

## Diagram rules

- Draw **one question per diagram**. If a diagram needs "and", split it.
- **At most 20 nodes** (node IDs) in one diagram; split or group when it grows.
- **Walk-through of 1 to 120 words** after each diagram, in plain words: what to look at first, and what it means.
- Name things by what they do; put IDs only where a rule above asks for them.

Credit: diagram sizing and one-purpose-per-diagram rules adapted from https://agent-skills.md/skills/ccheney/robust-skills/mermaid-diagrams and https://github.com/Agents365-ai/mermaid-skill

## When to stop

The file is done when `nio explain finish` printed `finished: <path>` (and, in plan mode, `nio check explainer` shows
`0 errors`). Tell the human which file you wrote, then make the drill-down offers; stop when the human says `stop`. A failed render is a note, not an error; do not install Node for it.

## When `nio` is missing or fails

Run it as `uv run nio` inside the NIO repo. If a command fails in a way this skill does not cover, show the human its
message and stop.
