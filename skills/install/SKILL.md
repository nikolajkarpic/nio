---
name: install
description: Set NIO up in a repo: install its git hooks, render its agents, and let the human choose whether stage commands run without permission prompts. Use when the human asks to install or set up NIO in a project.
---

# @nio:install

Sets NIO up in the current repo. Run the CLI as `nio` (inside the NIO repo itself: `uv run nio`).

Flow state: only `nio flow` writes `state.json` and `history.jsonl`; never edit them. Only the human gives `--human` to `nio flow done`, runs `nio flow seen`, or asks for `nio flow abandon`.

### Talking to the human
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

## Inputs and outputs

- **Input:** the repo, and the human's answer to one question.
- **Outputs:** git hooks, agent files under `.claude/agents` or `.codex/agents`, and on Claude Code the chosen
  settings file.

## Steps

1. Run `nio hooks`, then `nio agents sync`.
2. On Claude Code, ask once, per repo, in the shape above, and run what they pick. Elsewhere skip this and say prompts stay.
   - **Just me (recommended):** `nio allow --personal`. Applies to this clone only and changes nothing to commit;
     teammates keep their prompts.
   - **Everyone on the repo:** `nio allow --shared`. Everyone who pulls it gets fewer prompts without choosing to, and
     the settings file must be committed.
   - **Keep every prompt:** runs nothing. Stages stop for each command.

   Either way approvals, overrides and other human decisions still prompt, and so do `nio flow red` and `green`,
   because they run any command they are given.

## When to stop

Stop after step 2. Don't commit. Tell the human what was set up, and that `/nio:spec` on Claude Code, or the spec
skill elsewhere, starts the first effort.
