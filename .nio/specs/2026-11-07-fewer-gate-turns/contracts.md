---
slug: 2026-11-07-fewer-gate-turns
retired: []                      # CT IDs removed from this plan; never reused
---
# Contracts: drive a jury gate in fewer orchestrator calls

## Contracts

### CT-1 The gate step command (FR-1, FR-2, FR-3, FR-4, FR-5, FR-6, FR-13, FR-14) [agent]
- Binding: `src/nio/jury.py:step` (new)
- Like: `src/nio/jury.py:collect`
- Kind: cli
- Shape: it calls `collect` and `check` in turn; its `nio jury next` branch in `src/nio/cli.py:main` prints its lines as `collect`'s branch does. `nio jury next <slug> <gate> [--run <run>] [--add <lens:reason> ...] [--pick <lens,lens>]`; `step(root, slug, gate, run="", add=(), pick=None) -> lines`. `--add` and `--pick` go to `plan` as `nio jury plan` takes them. Exit 0, or 1 with `error: <reason>` on a refusal.
- Accepts: a gate `jury.gate_arg` accepts; `--run` an existing run folder.
- Returns: lines, the last one always `next: <action>`, by the first case that holds:
  1. `plan` fails (gate check, missing card) → its lines, then `next: <what plan says>`; nothing written.
  2. Packs to write (no `--run`; or a `--run` whose `jury/` holds no `<gate>-*.md` output): `agents.sync(root)` renders the agents (its errors refuse the step, `error: <card>: <error>`), then CT-2 writes the round's packs, unless the run already has them (FR-13); prints `run: <run>`, one line per juror `run <lens>: card nio-<lens>, pack <path>, output <path>`, then `next: run each juror above in parallel, then nio jury next <slug> <gate> --run <run>`. At an implementation gate whose run has no `results.json`: only `next: nio jury evidence <slug> E-n --run <run>, then nio jury next <slug> <gate> --run <run>`, no pack written.
  3. Outputs in the run: refuse when a `<gate>-<lens>.md` names a lens not planned (the name with a `-<n>` suffix dropped; `refuter` aside) (FR-14); else `collect(root, slug, gate, run, planned, tier)`, printing its one-line results (every line before `## Refuter batch`), CT-4's mismatch lines included. Then:
     - a refuter batch printed → CT-2 writes its pack; `next: run nio-refuter on .nio/runs/<run>/jury/packs/refuter.md (output .nio/runs/<run>/jury/<gate>-refuter.md), then nio jury next <slug> <gate> --run <run>` (FR-2);
     - a lens with a confirmed open blocker and fewer than 3 of its jurors (`led["jurors"]` entries of that lens whose `round` is the current round) → `next: escalate <lens>: run 2 more jurors on copies of its pack whose ## Your output line names <gate>-<lens>-2.md and <gate>-<lens>-3.md (in the first review the copies are of packs/<lens>.md; after it, of nio jury fixcheck <slug> <gate> --lens <lens> --blocker J-n plus the lens output format), then nio jury next ...`; no outcome composed. The orchestrator writes those two copies (escalation stays the skill's, spec Non-goals);
     - otherwise `check(root, slug, gate, record=True)` and all its lines (FR-3), then by outcome:
       - `rerun` naming an unusable output (`: invalid`, `: needs-more`, `: no output`) → per lens `next: re-run <lens> on .nio/runs/<run>/jury/packs/<lens>.md, adding the INVALID lines above to it (output <path>), then nio jury next ...`, same run (FR-6);
       - any other `rerun` → CT-2 in a new run, as case 2, with the fix-check packs of the lenses `changed()` names (FR-4);
       - `rejected` → `next: dispose of each open finding in one nio jury dispose <slug> <gate> J-a,J-b <disposition> --by <by> --note <note> call per disposition, fix the artefact, then nio jury next <slug> <gate> --run <run>`; at an implementation gate `next: nio flow next <slug>` (the fix tasks were appended);
       - `human` → `next: show the human the listed findings and wait for their ruling`;
       - `approved` → `next: tell the human the outcome, then nio flow next <slug>`; at an implementation gate `next: nio flow done <gate> <slug> --by "<role> / <host> / <model>"`.
- Fails: a `--run` with no folder → `error: no run <run> under .nio/runs/`; an unplanned lens file → `error: <file>: <lens> is not planned for <gate> (planned: <lenses>); rename or remove it`, nothing collected.
- Rules: "print only collect's one-line results, the lens-name mismatch lines, `nio jury check`'s lines when it composed an outcome, and a `next:` action with the paths it needs; the refuter batch goes to its file" (FR-5). "write no pack, start no run and record no verdict again, and SHALL print the same next action with the run it started" (FR-13): `check` already records once per round and outcome; case 2 reuses a run's packs.

### CT-2 Pack files the step writes (FR-2, FR-4, FR-12, FR-13, NFR-2) [agent]
- Binding: `src/nio/jury.py:packs` (new)
- Like: `src/nio/jury.py:fixcheck`
- Kind: function
- Shape: a fix-check pack holds `fixcheck`'s lines unchanged; `evidence.pack` is the implementation gate's. `packs(root, slug, gate, run, lenses, fix=False) -> lines` writes `.nio/runs/<run>/jury/packs/<lens>.md` per lens and `packs/step.json` = `{"gate", "round", "version", "lenses"}` (the ledger's round and `version_now` when written), and returns the `run <lens>: ...` lines. `refuter_pack(root, slug, gate, run, batch)` writes `packs/refuter.md`.
- Returns: each lens pack is what the skill gives that lens today, then the lens output format (`templates/lens-output.md`), then `## Your output` with one line: `Write your whole output, front matter first, to .nio/runs/<run>/jury/<gate>-<lens>.md and to no other file. Set lens: <lens>, gate: <gate>, subject: <slug>, by: "juror / <your host> / <your model>".` What the skill gives today:
  - spec, plan or tasks gate, first review: `# Pack: <lens>, <gate> gate of <slug>`, the files to read (`sources()`, one path per line; quotes may come only from them), and the `nio check <gate> <slug>` output as the CLI prints it; for `scope` also the path of `intake.md` and the human's grill answers (`answers()`); for `consistency` also the memory pack `pack.build` makes from the spec's `## Summary`, saved with `pack.save` under the run and logged with `query.log`, as `nio pack --run` does.
  - spec, plan or tasks gate, fix check (`fix=True`): the lines `fixcheck(root, slug, gate, lens)` returns.
  - implementation gate: `evidence.pack(root, slug, gate, lens, run)`, which is itself a first review or a fix check; its sentence "You have no way to write files or run commands." becomes "You may write only your output file, named at the end; you can't run commands."
  - refuter: the batch, the files to read (`sources()`), the ledger path `.nio/specs/<slug>/jury/<gate>.md`, at the spec gate the grill answers (`answers()`), and the `## Your output` line for `<gate>-refuter.md`.
- Rules: "the content the skill gives it today plus its output path" (FR-12); "the same pack content as before, apart from the line naming where it writes its output" (NFR-2). A lens pack or `step.json` that exists is never rewritten; `packs/refuter.md` is rewritten for each new batch. A step without `--run` (a first review or a re-review alike) reuses a run whose `step.json` holds the same gate, round and version and which has no `<gate>-*.md` output yet, instead of starting one.

### CT-3 Dispose several findings in one call (FR-7, FR-8) [agent]
- Binding: `src/nio/jury.py:dispose` (existing)
- Kind: function
- Shape: `nio jury dispose <slug> <gate> <J-n[,J-m...]> <disposition> --by <by> --note <note> [--note <note> ...] [--change C-ID]`; `dispose(root, slug, gate, fid, disposition, by, note, change="", routed=False)`, `fid` one ID or comma-separated IDs, `note` a string or a list.
- Returns: the CLI prints one `J-n: <disposition> by <by>` line per ID.
- Fails: an empty or repeated ID → `error: IDs must be distinct and non-empty: <ids>`; a note count neither 1 nor the ID count → `error: <n> notes for <m> findings; give one note, or one per finding in order`; any refusal today's dispose raises for a finding → `error:` then `J-n: <reason>` per refused ID. The ledger is not written in any of these.
- Rules: every check runs on one loaded ledger before one `save` (FR-8); one ID with one note behaves as today. `tasks.append_fix` keeps calling it with one ID.

### CT-4 The file name gives the lens (FR-10) [agent]
- Binding: `src/nio/jury.py:merge` (existing)
- Kind: function
- Shape: in `merge` (with `src/nio/templates/lens-output.md`), `lens = re.sub(r"-\d+$", "", path.stem[len(gate) + 1:])` replaces `meta.get("lens", ...)`; when the front matter's `lens` differs it adds `lens    <file name>: front matter says <its lens>; filed under <lens>` to its lines. The template's first line becomes `lens: <your card's name>`, with its comment.
- Rules: "file each lens output's findings under the lens its file name gives, print one line when the front matter names another lens, and show `lens: <your card's name>` in the lens output format" (FR-10). An escalation juror's `<gate>-<lens>-2.md` counts as `<lens>`. `parse_lens` still requires a `lens` value.

### CT-5 Jurors write their own output file (FR-9) [agent]
- Binding: `src/nio/agents.py:TOOLS` (existing)
- Kind: file
- Shape: `TOOLS` gains `"write": ["Write"]`; each juror card in `src/nio/agents/` (adversary, architecture-fit, conformance, consistency, correctness, executability, logic, refuter, risk-rollback, scope, security, test-proof, testability): `tools:` becomes `[read, write]`, and its `## Output format` section starts with: "Write your whole output to the file your pack names, and to no other file; never edit the files you judge." The refuter card's "Write `.nio/runs/<run>/jury/<gate>-refuter.md`" names "the file your pack names (`.nio/runs/<run>/jury/<gate>-refuter.md`)".
- Rules: "through a write tool its card limits to that path by instruction" (FR-9). Codex gets no tool list, only the shell withheld, so the card's sentence is the limit there, as `read` is today (research RF-3).

### CT-6 The jury skill drives a gate with the step (FR-11, NFR-1) [agent]
- Binding: `skills/jury/SKILL.md` (existing)
- Kind: file
- Shape: steps 2–5 and 8 become one loop: plan and add your own triggers (`nio jury plan`, `nio pack`, `--add`); the step renders the agents and checks the gate itself, so the skill drops its `nio run`, `nio agents sync`, `nio jury template`, `nio check <gate> --gate`, `nio jury collect`, `nio jury check` and `nio jury changed` calls. Run `nio jury next <slug> <gate> [--add ...]` and after it `nio jury next <slug> <gate> --run <run>`, each time doing what its `next:` line says: run each juror it lists in parallel on its pack (the juror writes its own output; without subagents, the manual-session note stays), run the refuter on its pack, escalate, re-run a lens with its errors, or dispose several findings in one `nio jury dispose` call. Step 6's outcome table, step 7's disposition table and their rules stay. The implementation gate section keeps `nio jury evidence` and replaces its pack, collect and check calls with `next`. One optional note: a host may run the whole loop in a fresh, cheaper subagent that returns the outcome and the list for the human.
- Rules: "drive each gate step with the step command and dispose several findings per call, in place of separate collect, check, changed and fix-check calls" (FR-11). The "Talking to the human" block stays word for word (`tests/test_talk.py`).
