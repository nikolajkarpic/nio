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

## Inputs and outputs

- **Inputs:** a file you are about to change, or a question.
- **Outputs:** none written. You come away with the record IDs that apply and what they say.

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

   | Standing | What to do |
   | --- | --- |
   | `current`, `approved` | follow it; to go against it, write a change request first (`@nio:remember`) |
   | `drifted` | its code changed a lot since it was confirmed: check it against the code before relying on it, and tell the memory writer whether it still holds |
   | `challenged` | a change request is pending against it: ask the human before relying on it |
   | `conflict` | two records supersede it: stop and ask the human which one holds |
   | `escalated` | the jury passed it to the human: treat it as undecided |
   | `uncommitted` | written in this change but not committed yet: usable, not yet reviewed |
   | `superseded`, `rejected` | do not follow it; follow the record that replaced it |

Stop when the question is answered or after 5 records; if memory has nothing, say so and
carry on.

## When `nio` is missing or fails

`nio query` falls back to plain text and path matching by itself when the index cannot be
built. If `nio` is not installed at all, search the files:

- `grep -rl "<file>" .nio/memory` finds records whose `paths` name the file.
- `grep -rh "^title:" .nio/memory/<area>` lists titles in an area.
- A record with an `outdated_by:` line has been superseded or challenged: open the record
  it names instead.
