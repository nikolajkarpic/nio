---
name: jury
description: Take a settled NIO spec to a verdict. Independent lens subagents judge it, the refuter validates their findings, and `nio jury` composes the outcome. Use after @nio:grill finishes, when the human asks to run the jury, judge or approve a spec, or to continue a jury after fixes.
---

# @nio:jury

Takes a spec that passes `nio check spec <slug> --gate` to a verdict: approved, rejected (fix and re-run) or the
human's call. The lenses are independent agents that judge the spec in a fresh context. You pick them, build their
packs, save what they return, and drive `nio jury`, which grounds, merges, validates and composes. You never judge the
spec yourself. The spec gate is the only gate so far; the plan and tasks gates come with their stages.

Run the CLI as `nio` (inside the NIO repo itself: `uv run nio`).

## Inputs and outputs

- **Input:** the slug of a spec the grill finished.
- **Outputs:**
  - lens outputs in `.nio/runs/<run>/jury/`;
  - the findings ledger `.nio/specs/<slug>/jury/spec.md` (and its `.json`);
  - fixes to `spec.md` within your authority;
  - a verdict record in memory for each ruling.

## Steps

1. **Plan.** Run `nio jury plan <slug> spec`. It checks the gate, lists the lenses with the reason each runs, sets
   the tier from the risk flags, counts runs against the cap and names missing cards.
   - If the gate fails, run no lens: send the human back to @nio:grill.
   - If a card is missing, run no lens: tell the human which card is missing.
   - Add your own triggers, then plan again with `--add "<lens>:<reason>"`:
     - **consistency**, when `nio pack "<the spec's summary>"` lists any `approved` or `current` decision (the reason
       names their IDs);
     - **scope**, when the spec names a new dependency, or an FR that neither `intake.md` nor the human's grill
       answers (`nio jury answers <slug>`) ask for (the reason names them).
   - If the plan is over the cap, show the human the planned runs and let them choose: run all, drop the lenses with
     the lowest hit rate, or pick. Never skip a lens silently.
2. **Run the lenses.** Start a run with `nio run`, and run `nio agents sync` so every `nio-<lens>` agent exists. Run
   each planned lens as its own subagent, in parallel, with a fresh pack holding only:
   - the gate (`spec`) and the slug;
   - the path of `spec.md`;
   - the output of `nio check spec <slug>`;
   - the lens output format (`nio jury template`), with `by:` set to the juror's role, host and model;
   - for **scope** only, `intake.md` and the human's grill answers (`nio jury answers <slug>`);
   - for **consistency** only, the memory pack from step 1.

   Never put `grill.md` itself (scope gets only the extracted answers), `research.md`, this conversation or another
   juror's output in a pack: the author's reasoning sways a juror. Lens agents are read-only, so save each one's answer
   verbatim to `.nio/runs/<run>/jury/spec-<lens>.md`.
   - **Without subagents**, never play a lens in your own session. Write each pack to
     `.nio/runs/<run>/jury/packs/<lens>.md` and ask the human to run it in a fresh session (or with the host's CLI,
     such as `claude -p`), with `by: juror / manual session / <model>` so the verdict records the manual run.
3. **Collect.** Run `nio jury collect <slug> spec --run <run> --tier <tier>`, with one `--expect <lens>` per planned
   lens. A lens output that is missing, invalid or `needs-more` is re-run once under the same file name, with collect's
   error messages added to its pack. A second failure goes to the human.
4. **Validate.** If collect prints a refuter batch, run `nio-refuter` once on the whole batch, with the path of
   `spec.md`, the ledger `.nio/specs/<slug>/jury/spec.md` (so it can mark a duplicate of a finding outside the batch)
   and the human's grill answers (for findings about what was or wasn't asked for). Save its answer to
   `.nio/runs/<run>/jury/spec-refuter.md` and collect again.
5. **Escalate.** For each lens with a blocker the refuter **confirmed**, run that lens twice more as independent
   jurors, `spec-<lens>-2.md` and `spec-<lens>-3.md`, each with a fresh pack, then collect. Two of three decide. Majors
   and refuted blockers never escalate. Every juror counts toward the cap.
6. **Decide.** Run `nio jury check <slug> spec --record` and act on the outcome:

   | Outcome | What you do |
   | --- | --- |
   | `rerun` | re-run each lens it names, once, then collect; when it says the spec changed, re-review (step 8) |
   | `pending` | run the refuter (step 4) |
   | `human` | show each reason with its findings, and wait for the human |
   | `rejected` | dispose of each open finding (step 7), then re-review (step 8) |
   | `approved` | tell the human: the verdict record, every disposition you made, and the next stage (the plan) |

   Show refuted findings too, with the refuter's reason; never hide them.
7. **Dispose** of each open finding, within your authority:

   | Disposition | Who | How |
   | --- | --- | --- |
   | `spec-fix` that changes no behaviour (wording, an ID, a missing Observable from existing text) | you | fix the spec, then `nio jury dispose <slug> spec J-n spec-fix --by agent --note "<what changed>"` |
   | `spec-fix` that changes behaviour | the human, through @nio:grill | grill it with the finding's fix as the recommended option, then `--by grill` |
   | `open-question` | you | add it to the spec as an `OP-n`, run @nio:grill on it before any lens re-runs, then `--by agent` |
   | `accepted-risk`, `out-of-scope` | the human only | `--by human`, with their words as the note |

   You judge whether a fix changes behaviour. `nio jury check` lists every disposition you made for the human. A
   finding that came from a point the grill deferred is the human's, or a grill session's, never yours. A grill
   session settles one by removing its DF line from `## Deferred` (DF-n moves to `retired:`) before `--by grill`;
   `nio jury dispose` refuses the spec-fix while the line is still there.
8. **Re-review.** After the fixes, `nio check spec <slug> --gate` must pass again. Run `nio jury changed <slug> spec`:
   it lists the IDs the fixes changed and the lenses to re-run (every lens that blocked, plus any lens whose findings
   cite a changed ID). Start a new run, re-run only those lenses with packs that name the changed IDs and the findings
   the human accepted as risk (so they aren't raised again), and continue from step 3. A finding that has failed two
   rounds goes to the human, not to another re-run (`nio jury check` says so).

## When to stop

Stop when the outcome is `approved` and the human has been told, or when the outcome is `human` and the decision is
theirs. Every ruling is recorded by `--record`, once per round.

Only the human can close a gate the jury hasn't approved, for example when re-review rounds keep finding new edge
cases: `nio jury check <slug> spec --record --human "<their reason>"` records outcome `human` with that reason. Never
use it on your own judgement, and accept the open findings as risk (`--by human`) first.
