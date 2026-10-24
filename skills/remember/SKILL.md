---
name: remember
description: Write NIO long-term memory records in .nio/memory/. Use to record a decision, lesson or change request by hand, to write a jury verdict, to add a memory candidate at the end of a task, or to promote a run's candidates into records.
---

# @nio:remember

Memory answers three questions for the next agent: **why** was X done this way, can I
**reuse** something done before, and what did the **jury** approve or reject. Write a record
only when it answers one of them. The full rules are in `MEMORY_NORTH_STAR.md` in the NIO repo.

Run the CLI as `nio` (inside the NIO repo itself: `uv run nio`).

## Pick a mode

| Mode | When | Who |
| --- | --- | --- |
| Record | the human asks to remember something, or you are the memory writer | writer |
| Verdict | a jury has ruled (`jury.verdict`) | writer |
| Candidate | you finished a task (`task.done`) and made calls the task did not dictate | any agent |
| Promote | an epic, an approved stage or a run ended (`epic.done`, `stage.approved`, `run.end`) | writer |

The writer is the role in `memory.writer` in `.nio/config.json`. If none is set, the agent
the human invoked is the writer. If you are not the memory writer, you may only add candidates.

Candidate and Promote need a run. Inside a pipeline run, use its ID. By hand, start one
with `nio run`, which prints the ID and creates `.nio/runs/<run>/promote.md`; or skip
candidates and use Record mode.

## Inputs

- `.nio/config.json`: `memory.areas`, the folders records may go in.
- `.nio/memory/<area>/*.md`: existing records.
- `.nio/runs/<run>/promote.md`: candidates, in Candidate and Promote modes.

## Outputs

- New files in `.nio/memory/<area>/`, passing `nio check`.
- In Candidate mode, new entries appended to `.nio/runs/<run>/promote.md`.

## Rules for every record

1. **Never edit a committed record's meaning.** To change one, write a new record that lists
   the old ID in `supersedes`, and add the new ID to the old record's `outdated_by` list in
   the same change. Only a file you created in this session may still be edited otherwise.
   The exceptions are `outdated_by` (only ever add to it) and `paths` (repoint them when code
   moved in a way git cannot follow; renames are followed for you). `nio check` rejects any
   other edit.
2. **Pick one area** from `memory.areas`: the part of the project the record is mostly
   about. Put other areas in `tags`. If no area fits, stop and ask the human to add one;
   never create a folder yourself.
3. **Verdicts go in their subject's area.** Verdicts on a whole stage (spec, plan, tasks)
   go in `project`.
4. **Write for a new agent.** Someone with no context must understand what was decided and
   why from this file alone. Name the constraint that forced the choice. A Why that only
   restates the Decision fails.
5. **Keep it short:** a body under 40 lines; frontmatter values flat strings or lists of
   strings, quoted when YAML could misread them.
6. **Fill `paths`** with the files or globs the record is about, so lookups by file find it.

## Record

1. **Check it is worth keeping.** It must answer why, reuse or jury. Skip anything the code
   already says plainly, restates the task, or only matters to this session.
2. **Look for an existing record.** Search by the files involved
   (`grep -rl "<file>" .nio/memory`) and scan the titles in the record's area
   (`grep -rh "^title:" .nio/memory/<area>`). Grepping the bodies for common words matches
   almost everything; prefer `nio query` once it exists.
   - Same question, same answer: stop, it is already recorded.
   - Same question, new answer: write a new record that supersedes the old one.
3. **Create the file:**
   `nio new <decision|lesson|change> --area <area> --title "<title>" [--by "<role / host / model>"] [--run <run>]`
   It prints the path. Leave `--by` out when the human made the decision.
4. **Fill it in.** Replace every `TODO`. Set `answers` to the question the record answers
   (`why`, `reuse` or `jury`). For a decision or lesson set `status`: `human` if the human
   decided it, `proposed` otherwise. Never store the jury's ruling in `status`; a verdict
   record carries it. Fill `paths`, `tags`, `supersedes`, and `serves` or `task` when known.
   For a change request, set `against` to the spec, plan or record that is wrong; if it is a
   record, add the change request's ID to that record's `outdated_by`. Then stop the work it
   blocks and tell the human: a change request is never fixed silently.
5. **Run `nio check`** and fix every error in your file. Warnings on older records are not
   yours to fix.

## Verdict

Every jury ruling is recorded, with no admission rule and no promotion.

1. `nio new verdict --area <subject's area> --title "<subject title>" --by "<writer role / host / model>" --run <run>`
2. Set `subject` to the judged record or task ID, `outcome` (`approved`, `rejected` or
   `human` when the jury split and the human ruled) and `tier` (`low`, `medium`, `high`).
   The template leaves both empty, so `nio check` fails until you choose.
3. Body: the ruling, one row per juror (lens, host, model, vote), the reasons, and what was
   rejected. Raw juror output stays in `.nio/runs/<run>/jury/`; summarise it, never paste it.
4. Run `nio check`.

## Candidate

At the end of a task, append at most 5 entries to `.nio/runs/<run>/promote.md`, one per
call you made that the task did not dictate (`decision`) or reusable fix you found
(`lesson`). Use this shape:

```markdown
## <decision | lesson>: <title>
- area: <area>
- answers: <why | reuse | jury>
- paths: <files or globs>
- task: <task ID>
- by: <role / host / model>

<2 to 5 lines: what you decided, why, and what you rejected.>
```

Write nothing if you made no such call. Never write to `.nio/memory/` in this mode.

## Promote

1. Read `.nio/runs/<run>/promote.md`. Skip entries already marked `promoted` or `dropped`.
2. For each entry, apply the Record steps 1 and 2. Merge entries that say the same thing.
3. Write the survivors with the Record steps 3 to 5, passing `--run <run>`.
4. Under each entry, add one line: `- promoted: <ID>` or `- dropped: <reason>`.
5. Run `nio check`; nothing may be left failing.
6. Once `nio index` exists, run it so lookups see the new records.
7. Once the spot-check juror exists, send it every record that supersedes a decision a
   verdict approved (`memory.promote.jury`). A fail goes back to step 4 of Record.

## Stop when

- `nio check` reports no errors in the files you wrote, and
- you have told the human the IDs and paths you wrote, plus anything you dropped or
  could not place in an area.

Do not commit. The human, or the pipeline step that called you, commits memory with the work
it explains.
