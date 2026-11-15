---
name: jury
description: Take a settled NIO spec, its plan, its tasks, or a finished effort's whole diff (the pr gate) to a verdict. Independent lens subagents judge it, the refuter validates their findings, and `nio jury` composes the outcome. Use after @nio:grill or @nio:plan finishes, when the human asks to run the jury, judge or approve a spec or a plan, or to continue a jury after fixes.
---

# @nio:jury

Takes a spec that passes the spec gate (the step checks it) to a verdict: approved, rejected (fix and re-run) or the
human's call. The lenses are independent agents that judge the spec in a fresh context. You pick them, build their
packs, save what they return, and drive `nio jury`, which grounds, merges, validates and composes. You never judge the
spec yourself. The steps below are the spec gate's; the plan gate runs the same steps with the differences in
"At the plan gate". The tasks gate comes with its stage.

Run the CLI as `nio` (inside the NIO repo itself: `uv run nio`).

Flow state: only `nio flow` writes `state.json` and `history.jsonl`; never edit them. Only the human gives `--human` to `nio flow done`, runs `nio flow seen`, or asks for `nio flow abandon`. Never pass `--by human`: only the human grants or revokes auto, or approves a gate.

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

## Drivers and waiting

An effort runs one unit of work at a time: one gate (spec, plan, tasks or pr), or one epic with its tasks; the
pr gate, on the whole effort diff, is always its own unit, so its driver built none of the effort. Each unit runs in a **driver**, a fresh agent that runs that one unit and then ends. The main
session, the one the human talks to, only routes.

**The main session** does only this:
1. Run `nio flow next <slug>` to see the next unit.
2. Start a fresh driver for it whose first input is what `nio flow brief <slug>` prints, and nothing else: no note
   from an earlier driver, nothing from an earlier unit. One epic may take several drivers one after another; a unit
   resumed after a hand-back gets a new one.
3. Start a driver only once the previous one for this effort has ended; never two at once. A driver that ended
   without a summary counts as ended: go on from `nio flow brief <slug>` alone.
4. Relay the driver's summary: what needs the human goes to them from the summary alone, in the shape above. When
   it holds nothing for the human (a gate approved, an epic done), start the next unit's fresh driver from
   `nio flow brief <slug>`.
5. When the human answers, record their ruling yourself with the command the summary names (`nio jury rule`,
   `nio jury dispose ... --by human`, `nio flow unblock ... --human` and the like), their words as the note: that
   counts as routing. Then start a fresh driver from `nio flow brief <slug>`.
Read nothing else yourself: what lies past the brief and the summaries is the driver's.

Under auto (the effort's auto flag, granted only by the human), the main session starts the next driver without asking
the human, and stops only when `nio flow next <slug>` waits for the human, is suspended, or reaches the pr gate's
approval; on a stop it tells the human the reason and the command `nio flow next` prints. Each driver first takes the
driver claim with `nio flow drive <slug> --by`, and refreshes it with `--token` while it works.

On a host without subagents, the main session runs the unit itself from `nio flow brief <slug>`, following the
driver's rules below, and goes on without stopping for the human. Optional, on Claude Code: run each driver as a
subagent (general-purpose) in the background.

**The driver** runs every step under Steps below, and only for its unit:
- Start from the brief. If it shows `running: <command>, started <time>`, that command is still running from an
  earlier driver: wait on that run (below), never start it again. If it shows `running on <host>, can't check:
  <command>, ...`, the run is on another machine: end with the summary asking the human whether that run is still
  alive, and start the command again only once they say it is gone.
- Where a step says to show or ask the human (a human-only disposition, a ruling at the round cap, a blocked task, a
  change request, a refusal it can't settle), end there with the summary naming that item and the command to
  continue. Never make the human's decision yourself.
- End once the unit is closed or handed back; never go on into the next unit.
- Your last message is the summary, at most 15 lines, in three parts: `closed:` what closed, `open:` what is open
  (each item for the human), `next:` the command to run next.

**Waiting for long work.** A long command is one that can outlast the host's foreground limit: `nio flow finish`,
`nio jury evidence`, a suite run, and any subagent (a juror, an implementation agent, a driver). The main session and the driver
wait for it like this:
- **The host sends completion notices:** start it in the background, then act on its notice when it arrives. Nothing
  in between: no sleep, no loop, no status check.
- **No notices, or it is not known whether it has them, but a blocking wait with a timeout:** wait blocking, with a
  10-minute timeout. If the wait times out, check once whether the command finished; if not, wait again. At most
  three waits: after the third that times out, end with the summary naming the command as still running and how to
  continue. Never check at an interval.
- **Neither:** don't run the long command; end with the summary naming it as open and how to continue, for the main
  session to take to the human.
`nio flow finish` and `nio jury evidence` record themselves as running while they run, so the next brief shows them.

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
   - **run `nio-refuter`** on the batch pack the step names (`packs/refuter-<n>.md`, one per batch), writing the output path the step printed;
   - **re-run a lens** on its pack with the INVALID lines added, once. A second failure goes to the human: say in
     plain words which review failed and why, with the error in `Refs:`;
   - **escalate a lens** with a confirmed blocker: run it twice more as independent jurors on copies of its pack, written as
     `packs/<lens>-2.md` and `packs/<lens>-3.md`, each ending with the `## Your output` line naming
     `<gate>-<lens>-2.md` / `<gate>-<lens>-3.md` (the files the step printed). Before starting the two jurors, check
     that neither copy names `<gate>-<lens>.md`, the first review's file. After the first review the copies are
     of the blocker's pack, `nio jury fixcheck <slug> spec --lens <lens> --blocker J-<n>` plus the lens output format
     (the step never writes these). Two of three decide. Majors and refuted blockers never escalate. Don't edit the
     artefact until the escalation is collected. Escalation jurors join the round they were asked in, and count for
     their blocker in every later round, so the step never asks for them twice;
   - **dispose of findings** (step 4), then edit the artefact and call the step again;
   - **show the human** the listed findings and wait;
   - **show the human the capped batch** (see "At the round cap") and record their rulings.
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

## At the round cap

Every gate stops after `jury.max_rounds` rounds (in `.nio/config.json`, default 2; anything but a whole number of at
least 1 stops the step with an error). The pr gate counts its own rounds; an old implementation gate counts per epic. Below the cap nothing changes: only a
confirmed blocker starts another round. When a round at or over the cap ends with findings open, the step decides:
- **two or more confirmed blockers, the first time:** one automatic round, on those blockers' lenses only. The outcome
  is `rejected`: dispose and fix as usual, then call the step again; it starts that round by itself. Never a second one;
- **minors:** closed as accepted risk by the system ("minor, skipped at the round cap"); the gate summary
  (`closed by the system:`) lists them. If only minors were open, the gate closes with no batch;
- **majors and any blocker otherwise:** the step prints `capped:` and the batch, and starts no round. Never rule on it
  yourself, and never call the step again hoping for another round: show the human every finding of the batch in one
  message, each with three options: accept as risk; fix (no juror checks the fix); one more round (the reviewers that
  raised it check the fix once). Record each answer, one call per ruling, with their words as the note:
  `nio jury rule <slug> <gate> J-a,J-b accept|fix|again --note "<their words>"`. It is refused while a round runs or
  before the cap. For `fix` and `again`, the driver makes the fix, never the main session: it edits the spec, plan or
  tasks (at the pr gate the ruling appends the fix task; run it through the implement stage: the gate
  waits until it is done). Until the artefact differs from the version the capped round judged, the step prints
  `waiting: edit the <gate> for J-a (ruled fix by the human)` and `nio flow brief` lists the owed fixes, and the gate
  doesn't close. Then call the step again: while a finding of
  the batch is unruled it prints the batch again; once all are ruled, `again` starts one round on those findings'
  lenses, after which the step prints a new batch if anything is still open (the human may ask again), and otherwise
  the gate closes on the human's rulings with no re-check. Tell the human, then run the `next:` line.

## Under auto

With the effort's auto flag on, the flow approves every gate but the pr gate itself: `nio flow done <stage> <slug>`
commits the approval of a spec, plan or tasks gate whose jury approved, naming the grant. Rulings the human gives
today the driver gives, with `--by "<role> / <host> / <model>"` and never `--by human`: a ruling on the capped batch
(`nio jury rule ... --by`), and minors are accepted as the gate's risk. The pr gate is the human's alone.

A `rejected` round goes to one fresh fix agent (optional, on a host with subagents: a general-purpose one), given
every confirmed blocker and major ID of the round in one batch. For each it edits the gate's files and disposes it
with `--by auto`. It disposes a finding `held --by auto` instead of editing when the fix would change a line tagged
`[human]`, cut scope (remove an item or add a non-goal) or change `risk:`; a held finding, or such an edit found by the
round check, sends the gate to the human. Then the next round starts. At the pr gate the confirmed findings become the
closing `PR fixes` epic, and its one implementation agent (@nio:implement) is that round's fix agent.

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
--approved` is what the implement stage reads. Fix tasks appended under `#### Fixes` later, and fix tasks retired with
`nio task retire <slug> T-n --reason "<why>" --by <human|agent>`, don't withdraw it; the retired task's finding closes as accepted risk.

## At the pr gate

An epic closes when its tasks are done: the task closing it re-runs its tasks' own tests, with no jury. Once every task
is done, the effort is at the `pr` gate, the one implementation jury of the effort, on the whole effort diff
(`main...HEAD`, where main is the remote's default branch: commits made outside the flow included). It is its own unit:
run it only in a fresh driver started from `nio flow brief <slug>` alone, never in the driver that built the tasks. In
order:
1. Run `nio jury next <slug> pr`. It pushes `nio/<slug>` and opens its pull request (or reuses the open one), then says
   to run `nio jury evidence <slug> pr --run <run>`, which runs the whole test suite once, the checks, attacks and
   journeys in a throwaway copy. A failing suite is an ordinary finding, with a fix task like any other. Correctness,
   conformance, adversary, consistency and integration always run, plus the lenses the spec's risk flags add; the cap
   is `jury.max_runs`, 7 by default here.
2. Run `nio jury next <slug> pr --run <run>`: it writes each lens its pack. Over `jury.split_lines` changed lines outside `.nio/` (2,500
   by default; exactly 2,500 is not over), every lens but integration gets one pack per epic (`<lens>~E1`, ...) plus
   one, `<lens>~rest`, for the commits outside any epic (out-of-flow ones and the `PR fixes` epic), all run in
   parallel; integration gets the whole change at summary level: the stat of every changed file, then the full diff
   of the files two or more parts touch. Loop as in step 2 above until it prints an outcome.
3. Each recorded outcome edits the pull request's one verdict comment (posted the first time), whose first word is
   `APPROVED` or `REQUEST_CHANGES`, then the head commit judged, the verdict and the findings: fixed, open, ruled by
   the human, closed by the system. Show the human that outcome in one message. A push, pull request or comment that
   fails stops the step with a message naming it; tell the human, the gate stays open. A verdict comment that failed
   waits: the gate can't be approved until it is posted, and the next `nio jury next <slug> pr` posts it again.
4. **rejected:** the confirmed findings' fix tasks go into the closing `PR fixes` epic, made on the first one. End the
   unit: they are built through @nio:implement, and once they are done the next `nio jury next <slug> pr` (a fresh
   driver again) pushes, which updates the pull request, and runs the gate's fix check. The round cap applies as above.
5. **approved,** or closed by the human's rulings: stop. Only the human approves the gate, at a terminal, with
   `nio flow approve <slug>` (it types the slug back); `nio flow done pr` refuses everyone, whatever the auto flag.
   It refuses while a finding is unruled, or once a commit lands after the head the verdict judged (stale: run the
   step again). Merging the pull request records nothing; nio never merges.

An epic already in its old `implementation-E-n` jury when the pr gate came in finishes that jury first, findings
kept: run `nio jury next <slug> implementation-E-n` as before, then the `nio flow done implementation-E-n <slug> --by
"<role / host / model>"` command it prints. Its fix tasks go under that epic's `#### Fixes`.

## When to stop

Stop when the outcome is `approved` and the human has been told, or when the outcome is `human` and the decision is
theirs. The step records every ruling, once per round. End with the next step: run `nio flow next <slug>` and show the human its `next:` line, or the command it prints when the effort waits. If it prints neither (a lite or bug-fix spec, or no `nio`), say the next stage is the plan after the spec gate, the tasks after the plan gate, the implement stage after the tasks gate.

Only the human can close a gate the jury hasn't approved, for example when re-review rounds keep finding new edge
cases (the one use of `nio jury check`): `nio jury check <slug> spec --record --human "<their reason>"` records outcome `human` with that reason. Offer it as an option saying what it costs (the record shows the gate closed by the human, not approved by the jury).
Never use it on your own judgement, and accept the open findings as risk (`--by human`) first.
