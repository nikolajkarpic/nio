---
name: remember
description: Write NIO long-term memory records in .nio/memory/. Use to record a decision, lesson or change request by hand, to write a jury verdict, to add a memory candidate at the end of a task, or to promote a run's candidates into records.
---

# @nio:remember

Memory answers three questions for the next agent: **why** was X done this way, can I
**reuse** something done before, and what did the **jury** approve or reject. Write a record
only when it answers one of them. The full rules are in `MEMORY_NORTH_STAR.md` in the NIO repo.

Run the CLI as `nio` (inside the NIO repo itself: `uv run nio`).

Flow state: only `nio flow` writes `state.json` and `history.jsonl`; never edit them. Only the human gives `--human` to `nio flow done`, runs `nio flow seen`, or asks for `nio flow abandon`.

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

## Rules for every record

1. **Never edit a committed record's meaning.** To change one, write a new record that lists
   the old ID in `supersedes`, and add the new ID to the old record's `outdated_by` list in
   the same change. Only a file you created in this session may still be edited otherwise.
   The exceptions are `outdated_by` (only ever add to it) and `paths` (repoint them when code
   moved in a way git cannot follow; renames are followed for you). `nio check` rejects any
   other edit.
2. **Pick one area** from `memory.areas`: the part of the project the record is mostly
   about. Put other areas in `tags`. If no area fits, stop and ask the human, in the shape above, where the record should be
   filed or whether to add a new place, each option saying what that place holds; never create a folder yourself.
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
2. **Look for an existing record.** Run
   `nio query "<title>. Decision: <one sentence>. Why: <one sentence>" --path <file> ...`
   with the candidate's own title, decision and reason, and every file it touches. Pass whole
   sentences: a short question scores lower and never gets the duplicate mark. Read every hit
   marked `≈` (a likely duplicate) and any hit that shares your files.
   If `nio` is not installed, search by the files involved (`grep -rl "<file>" .nio/memory`)
   and scan the titles in the record's area (`grep -rh "^title:" .nio/memory/<area>`).
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
   record, add the change request's ID to that record's `outdated_by`. Then stop the work it blocks and tell the human in plain words what is
   wrong and what it blocks, with the record IDs in `Refs:`: a change request is never fixed silently.
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
- you have told the human, in the shape above, what you recorded and anything you dropped or could not place, in
  plain words, with the IDs and paths in `Refs:`.

Do not commit. The human, or the pipeline step that called you, commits memory with the work
it explains.
