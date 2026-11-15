---
name: recall
description: Look up NIO long-term memory in .nio/memory/. Use before editing a file your context pack did not cover, before making a call that an earlier decision may already settle, or when asked why something was done, whether it was done before, or what the jury approved or rejected.
---

# @nio:recall

Memory answers three questions: **why** was X done this way, was it done before and can I
**reuse** it, and what did the **jury** approve or reject. Look it up in three steps: find
IDs, get their links, read at most 5 records. Never load all of `.nio/cache/INDEX.md`; at
1,000 records it is about 25,000 tokens.

Run the CLI as `nio` (inside the NIO repo itself: `uv run nio`).

Flow state: only `nio flow` writes `state.json` and `history.jsonl`; never edit them. Only the human gives `--human` to `nio flow done`, runs `nio flow seen`, or asks for `nio flow abandon`. Never pass `--by human`: only the human grants or revokes auto, or approves a gate.

## Inputs and outputs

- **Inputs:** a file you are about to change, or a question.
- **Outputs:** none written. You come away with the record IDs that apply and what they say.

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

1. **Find IDs.**
   - Decisions on a file: `nio query --path <file>` (repeat `--path` for several files).
   - A question: `nio query "<question in a full sentence>"`. Add `--path` when you know the
     files; records on them rank higher.
   - Each line is `ID type standing similarity title`, followed by its linked records.
     Superseded and rejected records are hidden; add `--all` to see them.
2. **Get links** for the hits that matter: `nio query --graph <ID>`. `←` means that record
   points at this one (a verdict on it, a record superseding it); `→` means this one points
   there (files it touches, what it supersedes).
3. **Read** the records you need, at most 5: `nio get <ID> ...`.
4. **Act on the standing:**

   | Standing | Weight | What to do |
   | --- | --- | --- |
   | `approved` | binding | follow it; to go against it, write a change request first (`@nio:remember`) |
   | `current` | strong | follow it; to go against it, write a change request first (`@nio:remember`) |
   | `drifted` | verify | its code changed a lot since it was confirmed: check it against the code before relying on it, and tell the memory writer whether it still holds |
   | `challenged` | disputed | a change request is pending against it: ask the human before relying on it, saying in plain words what it decided and what is disputed (the record IDs go in `Refs:`) |
   | `conflict` | blocked | two records supersede it: stop and ask the human which one holds, each option saying in plain words what that record decided |
   | `escalated` | undecided | the jury passed it to the human: treat it as undecided |
   | `uncommitted` | tentative | written in this change but not committed yet: usable, not yet reviewed |
   | `superseded`, `rejected` | none | do not follow it; follow the record that replaced it |

Stop when the question is answered or after 5 records; if memory has nothing, say so in one
line ("Nothing needed: memory has nothing on this") and carry on.

## When `nio` is missing or fails

`nio query` falls back to plain text and path matching by itself when the index cannot be
built. If `nio` is not installed at all, search the files:

- `grep -rl "<file>" .nio/memory` finds records whose `paths` name the file.
- `grep -rh "^title:" .nio/memory/<area>` lists titles in an area.
- A record with an `outdated_by:` line has been superseded or challenged: open the record
  it names instead.
