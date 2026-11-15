---
name: implement
description: Build an effort's approved tasks one epic at a time, one agent per epic from one pack, with the CLI running the epic's tests itself and closing it only when they pass. Use when `nio flow next` names @nio:implement, or when the human asks to implement or continue implementing an approved task list.
---

# @nio:implement

Takes an effort at implementing, whose `tasks.md` the human approved, through its epics: one agent per epic, a fresh
one that sees only that epic's pack and writes its tasks' tests and code. You orchestrate and report; `nio flow`
decides. When the agent hands the epic back, `nio flow finish` runs the tests its tasks name itself and closes the epic
only if they pass, with one commit on the effort branch `nio/<slug>`. An agent's hand-off never counts as proof.

Run the CLI as `nio` (inside the NIO repo itself: `uv run nio`). Below, `--by` is `--by "orchestrator / <host> / <model>"`.

Flow state: only `nio flow` writes `state.json` and `history.jsonl`; never edit them. Only the human gives `--human` to `nio flow done`, runs `nio flow seen`, or asks for `nio flow abandon`. Never pass `--by human`: only the human grants or revokes auto, or approves a gate.

An implementation agent runs no `nio flow` command.

## Inputs and outputs

- **Input:** the slug of an effort at implementing (`nio flow next` names this skill), with a `nio: approve tasks`
  commit and `tests.suite` set in `.nio/config.json` (the command that runs the whole test suite: it runs at the baseline and once at the pr gate; each epic runs only the tests its tasks name, once, when it is handed back).
- **Outputs:** one `E-n: <heading>` commit per closed epic on `nio/<slug>`, never merged; the epic lines `nio flow`
  keeps; a change request for each spec problem an agent finds; the notices passed on to the human.

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
3. Start a driver only once the previous one for this unit has ended: one driver per claimed epic may run at once,
   each with its own epic, and none beside a gate's. A driver that ended
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
- Where a step says to show or ask the human (a human-only disposition, a ruling at the round cap, a blocked task or
  epic, a change request, a refusal it can't settle), end there with the summary naming that item and the command to
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

1. **Claim.** Run `nio flow claim <slug> --by`. It prints `epic:`, `tasks:`, `card:` (`nio-worker-<tier>`), `effort:`,
   `pack:` and `then:`, the command that hands the epic back. The first claim also switches to `nio/<slug>` and records
   the suite's baseline. If it refuses (uncommitted changes, an epic already claimed, no epic ready, a blocked epic, the
   wrong branch), or prints a waiting message, stop and tell the human in the shape above. An epic whose tasks were all
   done before (`every task done: run its tests`) has nothing to build: run its `then:` command at once.
2. **Start one agent per claimed epic**: a fresh subagent of the named card, on the pack's path, with the effort where
   the host takes one per call. A second epic claimed while one runs prints `worktree:`; its agent gets that worktree
   as its working directory. The agent writes every task's tests and code, in task order, and hands back
   `status: done` with `command:`, the one command that runs the epic's tests.
3. **Hand the epic back.** On `done`, run the `then:` line: `nio flow finish <slug> E-n --by` (when the line asks for
   `--run`, pass the agent's `command:`). It runs the epic's tests once itself; a pass closes the epic with one commit.
   A failed run (a failing test, a test file that doesn't import, no test run, or past 30 minutes) keeps the epic open:
   claim it again and start a fresh agent; the new pack holds the failing tests and the run's last lines. The third
   failed run blocks the epic for the human. A `try again` from `nio flow` is retried after a few seconds, not counted
   as a failed run. A `nio flow finish` started in the background that fails (exits non-zero) comes here too, on its
   completion notice, with the text it printed, exactly.
4. **On a `blocked` handoff** (a spec problem), save it to a file and run
   `nio flow block <slug> T-n --handoff <file> --by`, naming the task it is about. It files the change request and the
   effort waits for the human; the epic keeps its claim. Once the human unblocks the task, a fresh driver's
   `nio flow brief <slug>` prints the epic's `pack:` and `then:` again, and a fresh agent resumes it.
   Never edit the spec, plan or tasks yourself. On a bug fix, when the handoff names a new dependency, a change to an interface used outside the bug's folder or to stored data, or a fix task whose non-test files sit in a second folder, also offer the full flow (`@nio:spec`, "Escalating a bug fix") alongside the change request.
5. **Pass everything on.** `nio flow finish` prints `closed: E-n <commit>`: the epic closed on its own tests, with no
   jury. When the last epic closes, it says the pr gate is next and prints a `notify:` line: end your unit there; the pr
   gate runs in a fresh driver (@nio:jury), and its jury judges the whole effort diff. Tell the human each `notify:`
   and every `waiting_for_human` in the shape above, with the command that clears it. Never merge the branch: the human
   does. The pr gate's fix tasks, in the closing `PR fixes` epic, are built like any other epic.
6. **Next epic.** Go back to step 1 until the claim refuses, the effort waits for the human, or it is done.

## When to stop

Stop when `nio flow next <slug>` names the pr gate (every epic is closed: the next unit is @nio:jury's), when it says
`waiting_for_human`, or when a claim is refused, and show the human what it prints.

## When `nio` is missing or fails

Don't close an epic by hand: `nio flow finish` runs its tests so that no agent's word decides them. Tell the human, in
the shape above, what failed, and stop.
