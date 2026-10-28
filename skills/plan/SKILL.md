---
name: plan
description: Turn an approved NIO spec into its plan, contracts, tests and quickstart, derived from the spec, the architecture (when there is one) and the code. Use after the spec jury approves, when the human asks to plan a spec or to continue a plan. Asks the human only about decisions nothing upstream settled.
---

# @nio:plan

Takes an approved spec to a plan that passes `nio check plan <slug> --gate`. Every requirement maps to a contract,
every acceptance criterion to a test, and every journey to a quickstart scenario. The plan is **derived**: from the
spec, from `architecture.md` when it exists, and from the code as it is. It never invents a design. When it needs
one, it stops and sends the human to the architecture stage.

Run the CLI as `nio` (inside the NIO repo itself: `uv run nio`).

Flow state: only `nio flow` writes `state.json` and `history.jsonl`; never edit them. Only the human gives `--human` to `nio flow done`, runs `nio flow seen`, or asks for `nio flow abandon`.

## Inputs and outputs

- **Input:** the slug of a spec the jury approved.
- **Outputs**, all under `.nio/specs/<slug>/`:
  - `contracts.md`, `tests.md`, `quickstart.md` and `plan.md`, passing `nio check plan <slug> --gate`;
  - `research.md`, with an `RF-n` entry appended for each fact you looked up;
  - `grill.md`, with your questions and the human's answers appended, in the grill's format;
  - memory decision records (`@nio:remember`) for the weighty decisions only.
- `spec.md` and `architecture.md` are read-only here.

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

## When the plan stops for architecture

Stop and send the human to the architecture stage (`@nio:architecture`) when the plan needs any of these and
`architecture.md` doesn't already settle it:
1. a new dependency;
2. a new module or package;
3. new stored data or a schema change;
4. a change to an interface used outside this feature;
5. two or more approaches with real trade-offs that the code and research don't settle.

Anything else follows the existing code's structure. Never pick one of these yourself and never edit
`architecture.md`. If the approved architecture itself is what blocks the plan, say so: changing it takes a change
request (`@nio:remember`) and the human's approval, and that re-opens the architecture stage. `nio check plan`
catches the mechanical cases (a new folder, or a new data model entry, with `architecture: none`).

## Steps

1. **Check the inputs.** Run `nio jury check <slug> spec`. Unless it says `outcome: approved`, or `outcome: human` with
   "the human closed the gate", stop: tell the human the spec isn't approved yet and the spec jury comes first. If `architecture.md` exists, read it. Its
   decisions are settled.
2. **Create or resume.** If the plan files don't exist, run `nio new plan <slug>`, and set `architecture:` in
   `plan.md` to `approved` when `architecture.md` exists, else `none`. If they exist, this is a resume: run
   `nio check plan <slug>` and carry on from what it lists. Never overwrite a plan file.
3. **Memory and facts.** Start a run with `nio run`, then `nio pack "<the spec's summary in one sentence>" --run <run>`
   and follow it. Look up in the code what the plan needs: where each requirement lands, what already exists to reuse,
   the test runner, the test layout and how the project is run. Use a subagent for anything broad. Append each fact
   to `research.md` as `- **RF-n** <finding>. Source: <file:line or URL>: "<excerpt of at most 25 words>"`, numbered
   after the highest RF there. When the project has a Technical Context file, read it first and look up only what it
   doesn't say.
4. **Stop check.** Walk the requirements against the stop list above. On a hit, stop before writing contracts, and
   tell the human what needs designing and why, with the option to run the architecture stage. If they prefer, the
   other option is to change the spec so the need goes away, which sends it back through the spec jury.
5. **Contracts** (`contracts.md`). One `CT-n` per interface the requirements need, citing the FRs (and NFRs) it serves.
   Bind each to `file:symbol`, `existing` only when the code has it. Point at the project's own schema files (OpenAPI,
   JSON Schema) instead of restating them, and never invent a schema format the project doesn't use. Quote spec
   constraints word for word, and refer to the spec's state tables and Key entities by name, without restating them.
6. **Tests** (`tests.md`):
   - one `TC-n` per AC, at the AC's Level, with the AC's Observable turned into an exact assertion;
   - one per NFR a test can measure;
   - one per journey misuse the system must handle.

   A test writer must be able to write each test from its entry alone.
7. **Quickstart** (`quickstart.md`). One `QS-n` per journey: commands and their exact expected output (or
   `contains:` lines). Mark a scenario `manual` only when it needs a person (UI, hardware, external accounts).
8. **Plan** (`plan.md`):
   - **Build order:** a `Foundation` entry when shared setup is needed, then one entry per user story, in the order
     they can be built.
   - **Coverage:** one row per FR, AC and NFR. An NFR no test can measure and no contract serves says `none` in
     both cells; name it to the human in step 11.
   - **Complexity tracking:** only when the plan breaks a project principle or adds something no requirement needs.
9. **Open points.** Write each question you can't settle as an `OP-n` in `plan.md`.
   - **Facts:** look them up (step 3) and retire them.
   - **Decisions:** ask only those nothing upstream settled, one at a time, in the grill's format (`@nio:grill`
     step 6), logged in `grill.md` the same way.
   - **Contradictions:** when the plan contradicts a spec answer or the code, show both sides and ask. Never
     resolve one silently.
   - **Below the grill's bar:** decide it yourself, tag it `[agent]`, and log the call.

   Record each answer: patch the items it settles, move the OP to `retired:`, add a line to `## Decisions`, and write
   a decision record (`@nio:remember`) for a weighty one.
10. **Verify, don't trust yourself:** run `nio check plan <slug> --gate` and fix every error. Then re-read each
    contract and test against the spec item it cites. Numbers, negatives ("never", "only", "not") and orderings must
    say exactly what the spec says.
11. **Show the human**, in the shape above:
    - the build order in plain words;
    - each manual scenario they will have to walk;
    - each quality requirement the plan leaves without a contract or a test;
    - every proposal (`[default]`) that changes what a user can do or sees, or what data is kept, then a count of the
      rest. `nio check plan` lists them.

    Then say the next stage is the plan jury.

## When to stop

Stop after step 11, or when the plan stops for architecture (step 4). Don't start the plan jury and don't break the
plan into tasks.

## When `nio` is missing or fails

Without `nio`, copy the four templates from the NIO package (`src/nio/templates/plan.md`, `contracts.md`,
`tests.md`, `quickstart.md`) into `.nio/specs/<slug>/` and fill them in by hand. Tell the human, in the shape above,
that the automatic checks didn't run.
