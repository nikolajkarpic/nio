---
name: grill
description: Settle a NIO spec draft with the human, one question at a time, until nothing in it is assumed. Use after @nio:spec has drafted .nio/specs/<slug>/spec.md, when the human asks to grill, settle or finish a spec, or to continue a grill from an earlier session. The human can delegate the session to an agent.
---

# @nio:grill

Takes a draft spec to the point where `nio check spec <slug> --gate` passes: no `[default]` and no open point left.
You look facts up yourself and ask the human only for decisions, one at a time, in a fixed format. You write in what
follows from their answers, decide the small calls yourself where the human will see them, and stop when the spec is
settled and they confirm.

Run the CLI as `nio` (inside the NIO repo itself: `uv run nio`).

## Inputs and outputs

- **Input:** the slug of a spec that passes `nio check spec <slug>`. Whether the human is answering, or has delegated
  the session to an agent.
- **Outputs**, all under `.nio/specs/<slug>/`:
  - `spec.md`, patched after every answer;
  - `grill.md`, an append-only log with one entry per question or call;
  - `research.md`, with an `RF-n` entry for each fact you looked up;
  - memory decision records (`@nio:remember`) for the weighty decisions only.

## The spec is the state

What is still open is whatever `nio check spec <slug> --gate` lists: every `[default]` item and every open point
`OP-n`. Re-run it whenever you need the current picture; never keep a separate list. To resume an earlier session, run
it and read `grill.md`: an `Asked` entry with no answer after it is the question to ask first.

## Provenance you write

| Tag | When |
| --- | --- |
| `[human]` | the human chose it (an option, "yes", or their own words) |
| `[agent]` | an agent decided it: below the bar (step 4), or the session is delegated |
| `[research: RF-n]` | a fact you looked up, recorded as `RF-n` in research.md |
| `[derived: AC-3, RF-2]` | it follows from those items or findings, each answered, researched or an agent call; never from a proposal, a deferred point or another derived item |
| `[deferred: DF-n]` | the session ended before it was settled (step 10) |

## Steps

1. **Start.** Run `nio check spec <slug>`; if it fails, fix the structure first or send the spec back to @nio:spec.
   Run it again with `--gate` to get what's open. Ask the human whether they'll answer or delegate the session.
2. **Facts first.** For each `OP-n (fact; …)`, and any item the code, memory (`nio query`) or docs can settle, look it
   up. Use a subagent for anything broad, and don't wait: only questions that depend on that fact hold. Record what you
   found in research.md as `- **RF-n** <finding>. Source: <file:line or URL>: "<excerpt of at most 25 words>"`, patch
   the item with `[research: RF-n]`, and move the OP's ID to `retired:`. When a lookup finds nothing, never guess: show
   the human what you searched and found, and let them decide it now (`[human]`) or defer it (step 10). When sources
   disagree, raise it as a contradiction (step 9).
3. **Order what's left.** Contradictions come first, always. Then, for each goal the spec states, its core facets:
   meaning, actors and permissions, effect on data and state, failure and conflict, the change from today, and
   verification. Then everything else, most impact first. A question whose answer depends on another open question
   waits until that one is answered.
4. **The bar.** A goal's core facet is covered once `grill.md` logs a question or a fact lookup for that goal tagged
   with the facet (`Facet: data`); a below-the-bar call never counts. Once all six are covered, ask a point only if one
   of its alternatives changes (1) what a user can do, (2) what a user sees, (3) who may do it, (4) what data is kept or
   changed, or (5) what it costs. Any yes means ask. Below the bar, take the recommended answer yourself, tag it
   `[agent]`, and log the call with its five no's. Permissions, irreversible operations, money, deletion and breaking
   changes are never below the bar.
5. **Settle what follows.** When an answer makes another point certain, write that point in as `[derived: <sources>]`
   instead of asking it. Never derive permissions, irreversible operations, money, deletion or new states.
6. **Ask one question** (or a round, see below):
   Before showing it, append `## Asked · Q7 · <ID> · <date>` with the question and its options to `grill.md`.
   - the question in full, ending in `?`;
   - one line on why it matters;
   - the verified facts it rests on, each naming its source (an `RF-n`, a file:line or a spec ID);
   - 3 options, or 1–2 when no real alternative exists (never filler), exactly one marked **Recommended** with its
     reason, worded so that "yes" accepts it;
   - room for a free-form answer. If the host has a question tool, use it; plain text works anywhere.

   **Rounds mode.** If `grill.mode` is `rounds` in the config (`~/.nio/config.json`, `.nio/config.json` or
   `.nio/config.local.json`, later files win), or the human asks for rounds, ask the whole frontier at once: every
   question whose prerequisites are settled, numbered, each in the format above, so the human can answer by number
   ("1 yes, 2 the second, 3 …"). Never put two questions in one round when one's answer could change the other. Record
   each answer separately (step 7), then work out the next round from scratch.
7. **Record the answer before the next question:**
   - patch every spec item it settles and tag it `[human]` (`[agent]` when delegated);
   - move a resolved `OP-n` to `retired:`;
   - append to grill.md:
     ```
     ## Q7 · OP-5 · 2026-10-25
     Question: <the question>
     Options: 1. <…> (recommended) 2. <…> 3. <…>
     Answer: 1. <the chosen option's full text, description included> [human]
     Patched: FR-15, AC-13; retired OP-5
     ```
     The answer line carries the chosen option's whole text, not just its number: the scope lens judges what was asked
     for from these lines alone. Log below-the-bar calls and derived items the same way, as `## Call · FR-24` and
     `## Derived · AC-21`;
   - add a line to `## Decisions`. For a weighty decision (costly to reverse, surprising, or a real trade-off), also
     write a decision record with `@nio:remember`, citing the spec IDs it serves, and put its D- ID on that line;
   - run `nio check spec <slug>`. It must still pass.

   If a free-form answer can't be written as a testable item, ask one follow-up on the same point, with options built
   from their words. If it's still vague, record it as an open decision point instead of guessing.
8. **Words.** When a term settles, write it into the spec's `## Glossary` straight away: `- **Term**: what it is, in
   one or two sentences. Never "<synonym>", "<synonym>".` The glossary holds vocabulary only, never decisions or
   implementation detail. When the human uses a word the glossary defines differently, or two words for one thing,
   stop and ask which they mean. `nio check spec` rejects a banned synonym anywhere else in the spec, except in
   `## Decisions`, which may record a rename.
9. **Contradictions.** When an answer contradicts an earlier answer, the spec or the code, don't overwrite anything.
   Show both sides, with the code's file:line when it's the code, and make resolving it the next question. Hold every
   question that depends on it.
10. **Every 15 questions**, pause and offer: continue, delegate the rest to an agent, or end early. At the first pause,
    if more than 15 points are still open, also suggest splitting the spec into an epic with slices.
    - **Ending early** never assumes an answer. Each unsettled open point moves to `## Deferred` as
      `- **DF-n** (from OP-n) <what is unsettled>. Deferred: <why>`, with the OP moved to `retired:`. Each unsettled
      `[default]` item gets `(from <its ID>)`, or `(from <its section>)` when it has no ID (a table row, a
      non-goal), and its own tag becomes `[deferred: DF-n]`.
    - An open contradiction is deferred as `(from <ID>; contradiction)`, quoting both sides. The jury treats it as a
      blocker.
11. **Finish gate.** When `nio check spec <slug> --gate` passes:
    - **Fidelity.** Re-read every item this session patched against its answer in `grill.md`. Numbers, negatives
      ("never", "only", "not") and orderings must say exactly what was answered; precise answers soften into vaguer
      prose easily. Fix any that drifted, and log the fix.
    - **Passivity.** Count the recommendations the human accepted as-is (their answers only; skip this in a
      delegated session). If they accepted every one of more than three, say so, and ask which decision they would
      push back on before finishing.
    - Show the notes of `--gate`: the agent calls, the derived items and any deferred points, so they can overturn any
      of them. Then ask: finish, explore further, or stop with concerns. The grill is done only when they choose
      finish. Explore further goes back to asking; stop with concerns is an early end that defers the concerns
      (step 10).

## Delegated sessions

When the human delegates, the agent answers each question the way it would recommend, tags the answer `[agent]`, and
logs its reason. It still stops at permissions, irreversible operations, money, deletion and breaking changes: those
wait for the human. It confirms the finish gate itself, and the notes show the human every `[agent]` answer. It may settle a deferred
point, but never closes its jury finding: `--by grill` means the human answered.

## When to stop

Stop when the human (or the delegated agent) chooses finish at the finish gate, or the session ends early with every
unsettled point deferred. Then tell the human the next stage: the spec jury.
