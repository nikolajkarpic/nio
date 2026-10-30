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
  commit and `tests.suite` set in `.nio/config.json` (the command that runs the whole test suite).
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

## Steps

1. **Claim.** Run `nio flow claim <slug> --by`. It prints `task:`, `mode:`, `card:` (`nio-worker-<tier>`), `effort:`
   and `pack:`. The first claim also switches to `nio/<slug>` and records the suite's baseline. If it refuses
   (uncommitted changes, a task already claimed, no ready task, the wrong branch), or prints a waiting message, stop and
   tell the human in the shape above.
2. **Start the worker** as a fresh subagent of the named card, on the pack's path, with the mode, and the effort where
   the host takes one per call. By mode:
   - **split:** a test-phase worker writes the test and hands off `status: red-ready` with its command. Report it:
     `nio flow red <slug> T-n --run "<command>" --by`. Then a fresh code-phase worker, given the same pack, writes the
     code and hands off `status: done`. Report it: `nio flow green <slug> T-n --by`.
   - **single:** one worker writes the test, runs `nio flow red` itself, writes the code and runs `nio flow green`
     itself. When it hands off `done`, check with `nio flow next <slug>` that the task is done, not its word.
   - **direct:** one worker writes the code and hands off `status: done` with a command. Report it:
     `nio flow green <slug> T-n --run "<command>" --by`.
3. **On a refusal** of red or green, or a failed review, start a fresh worker for that phase, giving it the refusal's
   text. Each one uses an attempt; at the third the CLI blocks the task and the effort waits for the human.
4. **On a `blocked` handoff** (a spec problem), save it to a file and run
   `nio flow block <slug> T-n --handoff <file> --by`. It files the change request and the effort waits for the human.
   Never edit the spec, plan or tasks yourself.
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
