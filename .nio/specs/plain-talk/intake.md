# Intake: plain-talk

## Source: human message (2026-10-26)

https://github.com/nikolajkarpic/nio/issues/53 lets start working on this now, please lets do brainstormiong session, and we can also use spec skill and grill me skill as well to improve this

## Source: https://github.com/nikolajkarpic/nio/issues/53

Title: Agents talk to the human in plain terms: what's needed first, consequence per option, IDs in a Refs line

## Problem

When a NIO agent talks to the human, the human often can't tell at a glance what's needed from them. Example from the grill-checks jury round (Q7):

> J-7 (major, confirmed, scope): FR-10 and FR-11 check a deferred point's links and format. FR-10: the source OP is retired, and the source item ends with `[deferred: DF-n]`. FR-11: the DF sits in `## Deferred` and follows the `(from <source>[; contradiction])` form. … → Keep both, as an extension (Recommended)

To decide, the human has to open the spec and look up J-7, FR-10, FR-11 and DF. The grill isn't the only place with this problem: no skill has a rule that its messages to the human must make sense on their own.

## Root cause

- `skills/grill/SKILL.md` step 6 lists what a question must **contain**, not that it must be **readable without the spec**. Because "facts naming their source" is required, spec IDs and file:line references end up in the question body. Options describe the action on the spec ("keep as an extension"), not what changes for the human.
- `skills/jury/SKILL.md` passes findings to the grill and to the human with the jury's labels still on them (`J-7 (major, confirmed, scope)`).
- No skill, and nothing in NORTH_STAR or CLAUDE.md, defines how an agent should talk to the human, so every message falls back to the agent's internal vocabulary.

## Decided (grilled 2026-10-25)

1. **It applies to every message to the human**, not just questions: asks, decisions, reports, errors and hand-offs.
2. **Every message has the same shape:**
   - **First line: what's needed from the human, in plain words.** For example "Nothing needed", "Pick one", "Run this command", or "Approve or push back".
   - **About 3 lines of context:** what it is, why it matters, and what it costs. Name each thing by what it does, never by its ID.
   - **Options**, when there are any: each says what happens if it's picked, including what is lost. The recommended option comes first.
   - **A trailing `Refs:` line** with the IDs and sources (`Refs: J-7 · FR-10, FR-11 · jury.py:268`). Logs such as `grill.md` keep everything in full and don't change, because jurors need them.
   - **Self-check before sending:** could the human act on this without opening a file? If not, rewrite it.
3. **Where the rule lives:** the full rule goes in `NORTH_STAR.md` as a principle and in CLAUDE.md's "Rules for writing skills" so new skills follow it. Each skill that talks to the human also gets a short **Talking to the human** block, because skills must be self-contained on any host.
4. **Enforcement is instructions plus the self-check**, with no code to lint messages. If agents still drift, add a lint on `## Asked` entries later.
5. **Bulk review lists show behaviour changes first.** Lists the human is asked to overturn (jury dispositions, grill agent calls, derived items) show, in plain words, only the items that change what the product does (usually 0–5), then one count line: "21 more were wording or test fixes, nothing you'd notice". The full list goes in `Refs:` and the log.
6. **A drift test.** One small `tests/test_*.py` fails if any skill that talks to the human is missing the block, or has a copy that differs from the one in `NORTH_STAR.md`. (It checks the skill text, not messages, so it doesn't conflict with decision 4.)
7. **`grill.md` logs exactly what the human saw:** the shown question, the options and the `Refs:` line, word for word. The entry header (`## Q7 · J-7 · <date>`) keeps the ID for lookups.
8. **The `nio` CLI output doesn't change.** It keeps printing IDs for the logs, jurors and tests. The agent translates for the human and puts the raw output in `Refs:`.

## Change

The block, identical in `NORTH_STAR.md` and every skill that talks to the human:

```markdown
## Talking to the human
Every message to the human (question, report, error or hand-off):
1. **First line: what you need from them**, in plain words: "Nothing needed", "Pick one",
   "Run this command", "Approve or push back".
2. **Then at most 3 lines:** what it is, why it matters, what it costs. Name things by what
   they do, never by an ID or an internal term (FR-n, J-n, DF, lens).
3. **Options** say what happens if picked, including what's lost. The recommended one goes first.
4. **Long lists** (calls, dispositions, findings): group them by what they change for the
   human. Show the few that change behaviour; count the rest.
5. **End with `Refs:`**: the IDs, files and commands, so they can check.
Before sending, ask: could they act on this without opening a file? If not, rewrite it.
```

- `NORTH_STAR.md`: add a principle, "Talking to the human", with the shape above.
- `CLAUDE.md` → Rules for writing skills: every message to the human follows that shape.
- Add a **Talking to the human** block to these skills, and rewrite each point where they talk to the human:
  - `grill`: step 1 (answer or delegate?); step 6 ("facts, each naming its source" becomes plain-language facts with sources in `Refs:`; add the J-7 example below); step 7 (log exactly what was shown); the step 11 finish gate (bulk rule); and the next-stage hand-off
  - `jury`: a missing card, the over-cap choice, a manual lens run, the `human` outcome and the `approved` report (bulk rule), and the step 7 spec-fix (translate the finding; never show its ID, severity or lens)
  - `spec`: the slug/route line and step 7 (show the human)
  - `recall`: `challenged` and `conflict`
  - `remember`: no area fits, and a change request
- Agent cards (`src/nio/agents/*.md`) only talk to the parent agent, never the human, so they're out of scope.

### J-7 after

> **Pick one:** should `nio check spec` also check that each deferred point is written correctly?
> When you defer something, the grill writes a line the jury later reads to raise a finding. If that line is malformed, the jury silently skips it, and the deferred problem is never reviewed. The agent added these checks without being asked. They're already built and tested.
> 1. **Keep both (Recommended):** a malformed deferred line fails the check, so nothing slips past the jury. It costs nothing because it's already built.
> 2. **Keep only the format check:** a point could then be open and deferred at the same time.
> 3. **Drop both:** less to maintain, but a malformed deferred line slips past the jury unnoticed.
>
> *Refs: J-7 · FR-10, FR-11 · jury.py:268*

## Done when

- NORTH_STAR, CLAUDE.md and the five skills are updated.
- The drift test passes, and it's listed among the self-checks in CLAUDE.md.
- In the next grill and jury session, the human can act on every message without opening a file, as judged by the human.


## Source: https://github.com/nikolajkarpic/nio/issues/53 (comments)

> Scope widened from the grill to every NIO message to the human (2026-10-25). Decisions: (1) it covers every message, with what's needed in the first line; (2) the rule goes in NORTH_STAR + CLAUDE.md, plus a short 'Talking to the human' block in each skill that talks to the human; (3) IDs go in a trailing Refs line; (4) enforcement is instructions + a self-check, with no code.

> Deep-dive decisions (2026-10-25): (5) bulk review lists show behaviour changes first, plus a count line, with the full list in Refs; (6) a small test keeps the block identical across NORTH_STAR and the skills; (7) grill.md logs exactly what the human saw; (8) the nio CLI output doesn't change, and the agent translates. The block text is in the issue body.

