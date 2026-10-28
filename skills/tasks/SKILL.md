---
name: tasks
description: Break an approved NIO spec (and, for a full spec, its approved plan) into epics and tasks in tasks.md, rated by model tier and effort, and show the human the estimate. Use after the plan jury approves (or, for a bug fix, after the spec jury does), when the human asks to break a spec into tasks or to continue the tasks stage.
---

# @nio:tasks

Takes an approved spec to a `tasks.md` that passes `nio check tasks <slug>`, then to the tasks jury and the human's
approval of the estimate. A full spec's tasks follow its approved plan; a bug fix's come from the spec and the code.
Nothing here makes a design choice.

Run the CLI as `nio` (inside the NIO repo itself: `uv run nio`).

Flow state: only `nio flow` writes `state.json` and `history.jsonl`; never edit them. Only the human gives `--human` to `nio flow done`, runs `nio flow seen`, or asks for `nio flow abandon`.

## Inputs and outputs

- **Input:** the slug of a spec whose spec jury approved it, or which the human closed with a reason; on a full spec,
  its plan approved too (`nio check plan <slug> --approved` exits 0).
- **Outputs:** `.nio/specs/<slug>/tasks.md`, passing `nio check tasks <slug>`; the tasks jury's ledger; one
  `nio: approve tasks` commit once the human approves the estimate.

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

1. **Check the inputs.** Run `nio new tasks <slug>`. It refuses, and you stop and tell the human why, when the spec
   isn't approved (or was handed to the human but not closed), when a full spec's plan isn't approved, or when the
   spec is an epic (run the tasks stage on each slice's spec). If `tasks.md` already exists, this is a resume: run
   `nio check tasks <slug>` and carry on from what it lists. Never overwrite `tasks.md`.
2. **Draft.** Run the `nio-tasks-drafter` subagent with the slug, the paths of the spec and plan files, and the exact
   CLI command. If it stops on a design choice nothing settles, stop too: on a full spec, tell the human the plan or
   the spec needs a change request (`@nio:remember`); on a bug fix, that the spec must be re-routed to a full spec
   with a plan.
3. **Rate.** Run the `nio-evaluator` subagent on `tasks.md`. It sets every `Tier:` (with a reason) and `Effort:`.
4. **Verify, don't trust the reports.** Run `nio check tasks <slug>` yourself and fix every error (send structural
   ones back to the drafter once). It prints the estimate.
5. **Jury.** Run the tasks jury with `@nio:jury` at the `tasks` gate (`nio jury plan <slug> tasks` refuses until the
   check passes; its core lens is executability).
6. **Show the human the estimate**, in the shape above: per epic, the task count, how many tasks run on each model tier
   and effort, and which run in parallel; no token or money figure. Ask them to approve or push back.
7. **Record the approval.** Only when the human approves and the tasks jury approved (or the human closed it), commit
   `tasks.md` and the tasks verdict record together as one `nio: approve tasks` commit. `nio check tasks <slug>
   --approved` is what the implement stage reads.

## Tasks added later

After approval, never edit or renumber a planned task. New work (an implementation-jury finding, a "justify or remove"
task, or a change request) goes under its epic's `#### Fixes` heading, with the next free `T-n` (one above the highest
ID ever used, live or retired), a `From:` line naming its source (`J-n (implementation-E-n, round n)` or the change
record's ID) and the seven lines. A task made pointless is removed and its ID listed in `retired:`.

## When to stop

Stop after step 7, or when step 1 or 2 stops. Don't start the implement stage.

## When `nio` is missing or fails

Without `nio`, copy the template from the NIO package (`src/nio/templates/tasks.md`) to `.nio/specs/<slug>/tasks.md`
and fill it in by hand following the drafter's card. Tell the human, in the shape above, that the automatic checks
didn't run.
