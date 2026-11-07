---
name: jury
description: Take a settled NIO spec, or its plan, to a verdict. Independent lens subagents judge it, the refuter validates their findings, and `nio jury` composes the outcome. Use after @nio:grill or @nio:plan finishes, when the human asks to run the jury, judge or approve a spec or a plan, or to continue a jury after fixes.
---

# @nio:jury

Takes a spec that passes the spec gate (the step checks it) to a verdict: approved, rejected (fix and re-run) or the
human's call. The lenses are independent agents that judge the spec in a fresh context. You pick them, build their
packs, save what they return, and drive `nio jury`, which grounds, merges, validates and composes. You never judge the
spec yourself. The steps below are the spec gate's; the plan gate runs the same steps with the differences in
"At the plan gate". The tasks gate comes with its stage.

Run the CLI as `nio` (inside the NIO repo itself: `uv run nio`).

Flow state: only `nio flow` writes `state.json` and `history.jsonl`; never edit them. Only the human gives `--human` to `nio flow done`, runs `nio flow seen`, or asks for `nio flow abandon`.

## Inputs and outputs

- **Input:** the slug of a spec the grill finished, or of a spec whose plan passes `nio check plan <slug> --gate`.
- **Outputs:**
  - lens outputs in `.nio/runs/<run>/jury/`;
  - the findings ledger `.nio/specs/<slug>/jury/spec.md` (and its `.json`);
  - fixes to `spec.md` within your authority;
  - a verdict record in memory for each ruling.

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

## Steps

1. **Plan.** Run `nio jury plan <slug> spec`. It checks the gate, lists the lenses with the reason each runs, sets
   the tier from the risk flags, counts runs against the cap and names missing cards.
   - If the gate fails, run no lens: tell the human the spec still has unsettled points and the grill comes next.
   - If a card is missing, run no lens: tell the human which reviewer is missing and that it needs a card at
     `.nio/agents/<lens>.md`.
   - Add your own triggers, then plan again with `--add "<lens>:<reason>"`:
     - **consistency**, when `nio pack "<the spec's summary>"` lists any `approved` or `current` decision (the reason
       names their IDs);
     - **scope**, when the spec names a new dependency, or an FR that neither `intake.md` nor the human's grill
       answers (`nio jury answers <slug>`) ask for (the reason names them).
   - If the plan is over the cap, show the human the planned reviews, each by what it checks, and let them
     choose, each option saying what it costs: run all, drop the reviews with the lowest hit rate, or pick. Never skip a lens silently.
     Pass their choice as `--pick <lens,lens>` to the step below.
2. **Drive the step.** Run `nio jury next <slug> spec [--add "<lens>:<reason>" ...] [--pick <lens,lens>]`, and after it
   `nio jury next <slug> spec --run <run>` with the run it printed, repeating the same `--add` each time. Each call
   prints its results and ends in a `next:` line; do what that line says, then call again, until it says to tell the
   human or to show them a list. You never judge the spec yourself. The step renders the agents, writes the packs and
   composes the outcome. A `next:` line asks for one of:
   - **run the jurors it lists**, each as its own subagent (`nio-<lens>`), in parallel, on its pack. A juror writes its
     own output file; if the host's agents can't write files, save the juror's reply verbatim to the output path the
     step printed. Never put `grill.md`, `research.md`, this conversation or another juror's output in a pack.
     - **Without subagents**, never play a lens in your own session. Ask the human to run the pack
       `.nio/runs/<run>/jury/packs/<lens>.md` in a fresh session (or with the host's CLI, such as `claude -p`), showing
       the exact command to copy, with `by: juror / manual session / <model>` so the verdict records the manual run.
   - **run `nio-refuter`** on `packs/refuter.md`, writing the output path the step printed;
   - **re-run a lens** on its pack with the INVALID lines added, once. A second failure goes to the human: say in
     plain words which review failed and why, with the error in `Refs:`;
   - **escalate a lens** with a confirmed blocker: run it twice more as independent jurors on copies of its pack, written as
     `packs/<lens>-2.md` and `packs/<lens>-3.md`, each ending with the `## Your output` line naming
     `<gate>-<lens>-2.md` / `<gate>-<lens>-3.md` (the files the step printed). Before starting the two jurors, check
     that neither copy names `<gate>-<lens>.md`, the first review's file. After the first review the copies are
     of the blocker's pack, `nio jury fixcheck <slug> spec --lens <lens> --blocker J-<n>` plus the lens output format
     (the step never writes these). Two of three decide. Majors and refuted blockers never escalate. Don't edit the
     artefact until the escalation is collected;
   - **dispose of findings** (step 4), then edit the artefact and call the step again;
   - **show the human** the listed findings and wait.
3. **Decide.** When the step prints `outcome:`, act on it:

   | Outcome | What you do |
   | --- | --- |
   | `rerun` | the step wrote the fix-check packs of the lenses to re-check (a new run, or the one final fix check): run those jurors as its `next:` line says; each gets its fix-check pack and answers fixed or not fixed for each finding in it, and raises only blockers (a new major or minor becomes a note) |
   | `human` with one list | after the first review there's no confirmed blocker, so no new round: show every listed finding in one message, each with two options, fix or accept as risk, in plain words (their IDs in `Refs:`); record each answer with `nio jury dispose` (a fix as you would in step 4), then call the step again |
   | `human`, the final fix check flagged | show every flagged finding in one message, each with fix, accept as risk, or overrule (it is already fixed: the human says why, recorded with `overruled --by human`), saying a confirmed blocker may be among them and that no further check follows; record each with `nio jury dispose`, then call the step again: the jury then ends |
   | `human`, other reasons | show each reason with its findings in plain words (their IDs in `Refs:`), and wait for the human |
   | `rejected` | dispose of each open finding (step 4), fix the artefact, then call the step again |
   | `approved` | tell the human the outcome and give the next step (see When to stop); show the dispositions you made as a long list (see the block above), with the verdict record and their IDs in `Refs:` |

   Show refuted findings too, in plain words with the refuter's reason; never hide them. Show the notes the step lists
   (findings below blocker raised after the first review) as one line each; they need no ruling. After the first review
   only a confirmed blocker starts another round; everything else comes to the human as one list. Once they settle it
   with a fix, the step asks for the one final fix check; what it flags goes to the human, and once they settle that
   the jury ends. A finding that has failed two rounds goes to the human, described in plain words.
4. **Dispose** of each open finding, within your authority, several per call with comma-separated IDs and one note
   per finding in order, or one note for all: `nio jury dispose <slug> spec J-a,J-b <disposition> --by <by> --note "<note>"`.

   | Disposition | Who | How |
   | --- | --- | --- |
   | `spec-fix` that changes no behaviour (wording, an ID, a missing Observable from existing text) | you | fix the spec, then `nio jury dispose <slug> spec J-a,J-b spec-fix --by agent --note "<what changed>"` |
   | `spec-fix` that changes behaviour | the human, through @nio:grill | grill it with the finding's fix as the recommended option, described in plain words, never by its ID, severity or reviewer, then `--by grill` |
   | `open-question` | you | add it to the spec as an `OP-n`, run @nio:grill on it before any lens re-runs, then `--by agent` |
   | `accepted-risk`, `out-of-scope` | the human only | ask in the shape above, saying what accepting it costs; then `--by human`, with their words as the note |

   You judge whether a fix changes behaviour. The step lists every disposition you made; show them to the
   human as a long list (see the block above). A
   finding that came from a point the grill deferred is the human's, or a grill session's, never yours. A grill
   session settles one by removing its DF line from `## Deferred` (DF-n moves to `retired:`) before `--by grill`, which only a session the human answered may record;
   `nio jury dispose` refuses the spec-fix while the line is still there.
   The same applies when a change request edits a gate that was approved or closed: every lens that judged it
   re-checks the change, which the step arranges as a fix check.
5. **Optional: a gate driver.** A host may run steps 2 to 4 in a fresh, cheaper subagent that returns the outcome and
   the list for the human, so the main context doesn't grow. Dispositions that need the human stay with you.

## At the plan gate

Run the steps above with `plan` in place of `spec` (`nio jury plan <slug> plan`, then `nio jury next <slug> plan`, the ledger `jury/plan.md`), with these differences:
- **Packs.** The step writes them: the plan files, and the only ones a quote may come from. The plan gate has no scope or
  consistency lens of the skill's own.
- **Fixes in the plan.** A finding whose cause is in the plan is a `plan-fix`: fix the plan files, and dispose it as you
  would a `spec-fix` (you for a fix that changes no behaviour, the human otherwise).
- **Findings rooted in the spec.** When a finding's cause is in the approved spec (the spec leaves a limit unstated, two
  FRs contradict, an AC can't be met as written), never fill the gap in the plan. Propose it to the human as rooted in
  the spec, with a draft change request (`@nio:remember`, `against` the spec). Only once they confirm, dispose it:
  `nio jury dispose <slug> plan J-n spec-change --by human --note "<why>" --change C-<id>`. A second spec-rooted finding
  joins the same open change request. The plan jury is then paused (`nio jury next <slug> plan` prints
  `state: waiting-on-spec`) until the spec jury re-approves the changed spec, or the human rejects the change request,
  which hands the finding back to them.
- **With the human.** While the step prints `state: with-human`, it refuses a new round: show
  the human the list and wait for their ruling.
- **Approval.** When the outcome is `approved`, or the human closed the gate with a reason, and the human asks, commit
  the four plan files and the plan verdict record as one `nio: approve plan` commit. `nio check plan <slug> --approved`
  is what the tasks stage reads; a later spec change withdraws the approval until the plan jury re-checks what changed.

## At the tasks gate

Run the steps with `tasks` in place of `spec`. `nio jury plan <slug> tasks` refuses until `nio check tasks <slug>`
passes, and plans executability alone. Each pack holds `tasks.md`, the spec and, on a full spec, the plan's files, plus
the `nio check tasks` output with its estimate. A finding is fixed in `tasks.md` (`plan-fix` doesn't apply here: dispose
it as a `spec-fix` on the tasks, as you would at the spec gate). When the outcome is `approved` and the human approves
the estimate, commit `tasks.md` and the tasks verdict record as one `nio: approve tasks` commit; `nio check tasks <slug>
--approved` is what the implement stage reads. Fix tasks appended under `#### Fixes` later don't withdraw it.

## At the implementation gate

Run this for one epic (`implementation-E-n`) once every task of it is done. The lenses judge the epic's diff and its
test results, not the spec text alone. In order:
1. Run `nio jury next <slug> implementation-E-n`. It starts the run and says to run
   `nio jury evidence <slug> E-n --run <run>`, which runs the epic's tests, checks, attacks and journeys in a throwaway
   copy and writes the run's `results.json`. Over the cap, show the human the planned runs and let them pick, then call
   again with `--pick <lens,lens>`. Conformance and correctness always run.
2. Run `nio jury next <slug> implementation-E-n --run <run>`: it writes each lens its pack. Then loop as in step 2
   above until it prints an outcome, running the refuter when it says so.
3. When the outcome is `approved` or the human closed the gate, run the `nio flow done implementation-E-n <slug> --by
   "<role / host / model>"` command the step prints.

Other outcomes:
- **rejected:** the epic goes back to the implement stage. Its fix tasks are appended under `#### Fixes`; run
  `nio flow next <slug>` and show the human its `next:` line.
- **waiting on a change request:** the epic waits. Show the human each change request and wait for their ruling on
  each one before you call the step again.
- **a noted major:** a major the jury raised after the first review is a note, not a blocker. Show it to the human, who
  decides whether it goes to a fix. Never fix it yourself.

## When to stop

Stop when the outcome is `approved` and the human has been told, or when the outcome is `human` and the decision is
theirs. The step records every ruling, once per round. End with the next step: run `nio flow next <slug>` and show the human its `next:` line, or the command it prints when the effort waits. If it prints neither (a lite or bug-fix spec, or no `nio`), say the next stage is the plan after the spec gate, the tasks after the plan gate, the implement stage after the tasks gate.

Only the human can close a gate the jury hasn't approved, for example when re-review rounds keep finding new edge
cases (the one use of `nio jury check`): `nio jury check <slug> spec --record --human "<their reason>"` records outcome `human` with that reason. Offer it as an option saying what it costs (the record shows the gate closed by the human, not approved by the jury).
Never use it on your own judgement, and accept the open findings as risk (`--by human`) first.
