---
slug: 2026-11-15-effort-drilldown-install
retired: []                      # QS IDs removed from this plan; never reused
---
<!-- Quickstart template: one runnable scenario per journey in the spec, written as the human's demo script and
the evaluator's evidence. No implementation code. An `auto` scenario is run by the evaluator, which compares each
step's output with Expected: the exact output, or lines starting `contains:` that must each appear. A `manual`
scenario (UI, hardware, external accounts) goes to the human as a checklist. Provenance, permanent IDs and `retired`
work as in contracts.md. Open questions go in plan.md's Open points. -->
# Quickstart: Effort drill-down in the NIO pane, and @nio:install installs the Claude Code mods

## Prerequisites
- `uv sync` in the NIO checkout, so `.venv/bin/nio` exists: `uv run nio --help`.
- Claude Code with mods (plugins with hooks modules): `claude plugin --help` lists `test` and `install`.

## Scenarios

### QS-1 Inspect how an effort ran (UJ-1; manual) [derived: UJ-1]
- Needs: this repo, with this effort (`2026-11-15-effort-drilldown-install`) active; the `nio-status-pane` mod installed (QS-2) or loaded with `claude --plugin-dir tools/claude-mods/nio-status-pane`.

1. `uv run nio flow show 2026-11-15-effort-drilldown-install --json`
   Expected:
   ```
   contains: "timeline": [
   contains: "juries": [
   contains: "gate": "spec"
   contains: "cost": {
   contains: "memory": [
   ```
2. In Claude Code, open the `NIO efforts` pane (`/nio` places it) and press the row `2026-11-15-effort-drilldown-install`.
   Expected: the drill-down shows, in order, its timeline (the `spec_jury → arch_grilling` and `arch_grilling → planning` changes), its juries (`spec`, two rounds, with lenses and verdicts and the findings J-1 to J-19), `no tasks yet` until the tasks stage, its cost per stage, its memory (V-261115-6snr, V-261115-rida), and a `context: <n>%` line; no model turn is spent.
3. Press `Back`.
   Expected: the list of active efforts is shown again.
- Pass when: step 1's JSON holds the five sections; steps 2 and 3 show what they expect, the cost figures in step 2 equal those in step 1's `cost`, and the session's transcript gains no turn.

### QS-2 Install NIO with the mods (UJ-2; manual) [derived: UJ-2]
- Needs: a scratch git repo with `nio` installed (`uv tool install <path to this checkout>`), opened in Claude Code; neither mod installed there (`claude plugin list --json` has no `@nio-mods` entry).

1. In Claude Code in the scratch repo, run `@nio:install` and answer the mods question with the recommended option.
   Expected: the closing message holds `background-nio-commands: installed` and `nio-status-pane: installed`.
2. `claude plugin list --json`
   Expected:
   ```
   contains: "id": "background-nio-commands@nio-mods"
   contains: "id": "nio-status-pane@nio-mods"
   ```
3. `git status --porcelain`
   Expected: nothing from the mods install (no settings file to commit).
4. Run `@nio:install` again and pick the recommended option.
   Expected: the closing message says `already installed` for both mods.
- Pass when: every step matched, and after a restart of Claude Code in the scratch repo the `NIO efforts` pane opens.
