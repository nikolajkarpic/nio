---
name: implement
description: Build an effort's approved tasks one at a time, each by a fresh worker from its own pack, with the CLI proving every test failed before the code and passes after it. Use when `nio flow next` names @nio:implement, or when the human asks to implement or continue implementing an approved task list.
---

# @nio:implement

Takes an effort at implementing, whose `tasks.md` the human approved, through its epics: one task at a time, each in a
fresh worker that sees only that task's pack. You orchestrate and report; `nio flow` decides. It runs the test itself
to accept red (the test fails, for the right reason, before the code) and green (it passes after), then reviews and
commits the task on the effort branch `nio/<slug>`. A worker's handoff never counts as proof.

Run the CLI as `nio` (inside the NIO repo itself: `uv run nio`). Below, `--by` is `--by "orchestrator / <host> / <model>"`.

Flow state: only `nio flow` writes `state.json` and `history.jsonl`; never edit them. Only the human gives `--human` to `nio flow done`, runs `nio flow seen`, or asks for `nio flow abandon`.

A worker runs no `nio flow` command, except in single mode `nio flow red` and `nio flow green` on its own task.

## Inputs and outputs

- **Input:** the slug of an effort at implementing (`nio flow next` names this skill), with a `nio: approve tasks`
  commit and `tests.suite` set in `.nio/config.json` (the command that runs the whole test suite, which runs at the baseline and for the task closing each epic; other tasks run only their own test). For a slow suite, set `tests.epic` to a faster command: it replaces the suite at each epic's end, and the full suite then runs only when the last epic closes.
- **Outputs:** one `T-n: <title>` commit per done task on `nio/<slug>`, never merged; the task lines `nio flow` keeps;
  a change request for each spec problem a worker finds; the epic reports and notices passed on to the human.

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

An effort runs one unit of work at a time: one gate (spec, plan or tasks), or one epic with its tasks and its
implementation jury. Each unit runs in a **driver**, a fresh agent that runs that one unit and then ends. The main
session, the one the human talks to, only routes.

**The main session** does only this:
1. Run `nio flow next <slug>` to see the next unit.
2. Start a fresh driver for it whose first input is what `nio flow brief <slug>` prints, and nothing else: no note
   from an earlier driver, nothing from an earlier unit. One epic may take several drivers one after another; a unit
   resumed after a hand-back gets a new one.
3. Start a driver only once the previous one for this effort has ended; never two at once. A driver that ended
   without a summary counts as ended: go on from `nio flow brief <slug>` alone.
4. Relay the driver's summary: what needs the human goes to them from the summary alone, in the shape above. Then
   start the next driver.
Read nothing else yourself: what lies past the brief and the summaries is the driver's.

On a host without subagents, the main session runs the unit itself from `nio flow brief <slug>`, following the
driver's rules below, and goes on without stopping for the human. Optional, on Claude Code: run each driver as a
subagent (general-purpose) in the background.

**The driver** runs every step under Steps below, and only for its unit:
- Start from the brief. If it shows `running: <command>, started <time>`, that command is still running from an
  earlier driver: wait on that run (below), never start it again.
- Where a step says to show or ask the human (a human-only disposition, a ruling at the round cap, a blocked task, a
  change request, a refusal it can't settle), end there with the summary naming that item and the command to
  continue. Never make the human's decision yourself.
- End once the unit is closed or handed back; never go on into the next unit.
- Your last message is the summary, at most 15 lines, in three parts: `closed:` what closed, `open:` what is open
  (each item for the human), `next:` the command to run next.

**Waiting for long work.** A long command is one that can outlast the host's foreground limit: `nio flow green`,
`nio jury evidence`, a suite run, and any subagent (a juror, a worker, a driver). The main session and the driver
wait for it like this:
- **The host sends completion notices:** start it in the background, then act on its notice when it arrives. Nothing
  in between: no sleep, no loop, no status check.
- **No notices, or it is not known whether it has them, but a blocking wait with a timeout:** wait blocking, with a
  10-minute timeout. If the wait times out, check once whether the command finished; if not, wait again. At most
  three waits: after the third that times out, end with the summary naming the command as still running and how to
  continue. Never check at an interval.
- **Neither:** don't run the long command; end with the summary naming it as open and how to continue, for the main
  session to take to the human.
`nio flow green` and `nio jury evidence` record themselves as running while they run, so the next brief shows them.

## Steps

1. **Claim.** Run `nio flow claim <slug> --by`. It prints `task:`, `mode:`, `card:` (`nio-worker-<tier>`), `effort:`
   and `pack:`. The first claim also switches to `nio/<slug>` and records the suite's baseline. If it refuses
   (uncommitted changes, a task already claimed, no ready task, the wrong branch), or prints a waiting message, stop and
   tell the human in the shape above, except that while a wave is open, `is claimed` means wait for the other wave
   workers, not stop; claim again only once every wave task is done or blocked.
2. **Start the worker** as a fresh subagent of the named card, on the pack's path, with the mode, and the effort where
   the host takes one per call. For a wave, start one worker per claimed task at the same time, each with
   the task's worktree as its working directory. Report each red and green by its own ID. By mode:
   - **split:** a test-phase worker writes the test and hands off `status: red-ready` with its command. Report it:
     `nio flow red <slug> T-n --run "<command>" --by`. Give the code-phase worker the `output:` lines `nio flow red` printed, with the pack. Then a fresh code-phase worker, given the same pack, writes the
     code and hands off `status: done`. Report it: `nio flow green <slug> T-n --by`.
   - **single:** one worker writes the test, runs `nio flow red` itself, writes the code and runs `nio flow green`
     itself. When it hands off `done`, check with `nio flow next <slug>` that the task is done, not its word.
   - **direct:** one worker writes the code and hands off `status: done` with a command. Report it:
     `nio flow green <slug> T-n --run "<command>" --by`.
3. **On a refusal** of red or green, or a failed review, start a fresh worker for that phase, giving it the refusal's
   text. Each one uses an attempt; at the third the CLI blocks the task and the effort waits for the human. A `try again`
   from `nio flow` is retried after a few seconds, not counted as a refusal. A `nio flow green` started in the
   background that refuses (exits non-zero) comes here too, on its completion notice, with the text it printed, exactly.
4. **On a `blocked` handoff** (a spec problem), save it to a file and run
   `nio flow block <slug> T-n --handoff <file> --by`. It files the change request and the effort waits for the human.
   Never edit the spec, plan or tasks yourself. On a bug fix, when the handoff names a new dependency, a change to an interface used outside the bug's folder or to stored data, or a fix task whose non-test files sit in a second folder, also offer the full flow (`@nio:spec`, "Escalating a bug fix") alongside the change request.
5. **Pass everything on.** After green, the CLI prints the review, `done: T-n <commit>`, and when an epic ends its
   report and a `notify:` line; when the last epic ends, `merge: nio/<slug>`. Tell the human each `notify:` and every
   `waiting_for_human` in the shape above, with the command that clears it. Never merge the branch: the human does.
6. **Next task.** Go back to step 1 until the claim refuses, the effort waits for the human, or it is done.

## When to stop

Stop when `nio flow next <slug>` says `done` (tell the human to merge `nio/<slug>`), when it says `waiting_for_human`,
or when a claim is refused, and show the human what it prints.

## When `nio` is missing or fails

Don't build anything by hand: red, green and the review exist so that no agent's word decides them. Tell the human, in
the shape above, what failed, and stop.
