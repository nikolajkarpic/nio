---
slug: 2026-11-15-effort-drilldown-install
retired: []                      # TC IDs removed from this plan; never reused
---
<!-- Tests template: one concrete test per acceptance criterion, at that AC's Level, plus tests for measurable
NFRs and for the misuse each journey names. A test writer must be able to write the test from its entry alone.
Provenance, permanent IDs and `retired` work as in contracts.md. Open questions go in plan.md's Open points. -->
# Tests: Effort drill-down in the NIO pane, and @nio:install installs the Claude Code mods

Python tests go in the existing files, as `test_*` functions run by `selfcheck.main`, with their helpers
(`effort`, `history`, `cli`, `run_main` in tests/test_flow.py; `transcript`, `at` in tests/test_usage.py; `repo` in
tests/test_records.py) (RF-21). Pane tests go in `tools/claude-mods/nio-status-pane/hooks/register.test.tsx`, run by
`claude plugin test tools/claude-mods/nio-status-pane`, with its `setup` mock extended so `process.run` answers
`... flow show <slug> --json` from a per-test map `{cwd + slug: result}` and `session.usage` from a per-test value
(RF-18). "Open the drill-down" below means: `setup`, `start`, mount the Pane, `ui.press({ key: '<slug>' })`, settle
the clock, read every `Text`. [agent]

## Acceptance tests

### TC-1 `flow show` lists each stage change field by field (AC-1; integration) [derived: AC-1]
- File: `tests/test_flow.py:test_show_timeline_lists_stage_changes` (new)
- Covers: CT-1, CT-2, CT-3
- Setup: `effort("tasking")`, then `history(root, S, ...)` with three lines: `{"kind": "pass", "from": "planning", "to": "plan_jury"}` at 2026-11-10T10:00Z, `{"kind": "pass", "from": "plan_jury", "to": "tasking"}` at 11:00Z, `{"kind": "back", "from": "tasking", "to": "planning"}` at 12:00Z, each with `evidence: {"paths": [], "verdict": "", "output": ""}`; `history` writes them with `who` = `orchestrator / test / test`.
- Action: `run_main(root, "flow", "show", S, "--json")`.
- Assert: exit 0; stdout is one line; `json.loads(stdout)["timeline"]` equals exactly the three rows `{"kind": "pass", "from": "planning", "to": "plan_jury", "role": "orchestrator", "host": "test", "model": "test", "at": "2026-11-10T10:00:00Z"}`, then the 11:00 and 12:00 rows in that order, with no `reasons` key.

### TC-2 Selecting a row draws its timeline with no model call (AC-1; integration) [derived: AC-1]
- File: `tools/claude-mods/nio-status-pane/hooks/register.test.tsx:AC-1 drill-down timeline` (new)
- Covers: CT-12, CT-13
- Setup: the existing `STATUS` and `FILES`; `flow show 2026-11-08-e123 --json` in `/w/nio-123` answers exit 0 with a JSON whose `timeline` holds the three rows of TC-1 (slug e123), every other section `[]`, cost with `stages: []` and `"-"` figures; a `model.*` handler that records any call.
- Action: open the drill-down for `2026-11-08-e123`.
- Assert: the process runs include exactly one `/w/nio-123/.venv/bin/nio flow show 2026-11-08-e123 --json` with `cwd` `/w/nio-123`; the texts hold `planning → plan_jury · orchestrator · test · test · 2026-11-10T10:00:00Z`, then the 11:00 and 12:00 rows, in that order; no model call was recorded.

### TC-3 A failed review shows its reasons, or `-` (AC-2; integration) [derived: AC-2]
- File: `tests/test_flow.py:test_show_timeline_failed_review` (new)
- Covers: CT-2, CT-3
- Setup: `effort("implementing")`; history: a `review` line `from`/`to` `implementing` with `evidence.task` `T-1`, `passed` false, `reasons` `["test still fails", "file outside the task"]`; a second failed `review` for `T-2` with `reasons: []`; a passed `review` for `T-3`.
- Action: `run_main(root, "flow", "show", S, "--json")`.
- Assert: `timeline` holds two `review` rows, in order: the first with `reasons == ["test still fails", "file outside the task"]`, the second with `reasons == "-"`; no row for the passed review.

### TC-4 Missing host and model read `-` (AC-3; unit) [derived: AC-3]
- File: `tests/test_flow.py:test_timeline_missing_fields_read_dash` (new)
- Covers: CT-3
- Setup: one line `{"kind": "pass", "from": "grilling", "to": "spec_jury", "who": {"role": "human", "host": "", "model": ""}, "at": "2026-11-10T10:00:00Z"}`, and one with no `who` at all.
- Action: `flow.timeline([line1, line2])`.
- Assert: row 1 has `role == "human"`, `host == "-"`, `model == "-"`; row 2 has `role`, `host` and `model` all `"-"`.

### TC-5 An unreadable history line fails only its sections (AC-4; integration) [derived: AC-4]
- File: `tests/test_flow.py:test_show_bad_history_line_keeps_other_sections` (new)
- Covers: CT-2
- Setup: `effort("implementing")` with one real history line, then append the whole line `not json\n` to `history.jsonl`; a `jury/spec.json` ledger as `with_findings` writes it.
- Action: `run_main(root, "flow", "show", S, "--json")`.
- Assert: exit 0; `timeline == {"error": f"{S}: history.jsonl, line 2"}` and `cost` is an `{"error": ...}` too; `juries` is a list holding the `spec` gate; `tasks` is a list; `memory` is a list.

### TC-6 Back shows the list again (AC-5; integration) [derived: AC-5]
- File: `tools/claude-mods/nio-status-pane/hooks/register.test.tsx:AC-5 back to the list` (new)
- Covers: CT-12
- Setup: as TC-2.
- Action: open the drill-down for `2026-11-08-e123`, then `ui.press({ key: 'back' })`.
- Assert: after the press the texts hold `2026-11-08-e123\nimplementing · working\nnio-123 · jury 2 · task T-18 · jurors correctness` and `2026-11-08-e49`, and no timeline row.

### TC-7 A two-round spec jury lists both rounds with lenses and verdicts (AC-6; integration) [derived: AC-6]
- File: `tests/test_flow.py:test_show_juries_two_rounds` (new)
- Covers: CT-2, CT-4
- Setup: `effort("plan_jury")` and overwrite `jury/spec.json` with `round: 2`, `outcome: "approved"`, jurors `spec-logic` and `spec-scope` (`lens` logic / scope, `round: 2`, `valid: true`, `context: "sufficient"`), and findings J-1 (`severity` major, `validation` confirmed, `status` fixed, `disposition` spec-fix, `first_round: 1`, sources `[{"juror": "spec-logic", "lens": "logic", "round": 1}]`) and J-2 (`severity` minor, `validation` refuted, `status` refuted, `first_round: 1`, sources `[{"juror": "spec-scope", "lens": "scope", "round": 1}]`).
- Action: `run_main(root, "flow", "show", S, "--json")`.
- Assert: the `spec` entry of `juries` has `outcome == "approved"` and two rounds; round 1 lenses `[{"lens": "logic", "verdict": "block"}, {"lens": "scope", "verdict": "approve"}]`; round 2 lenses `[{"lens": "logic", "verdict": "approve"}, {"lens": "scope", "verdict": "approve"}]` (as `jury.votes` gives them).

### TC-8 Confirmed and refuted findings, and the fix task (AC-7; integration) [derived: AC-7]
- File: `tests/test_flow.py:test_show_findings_and_fix_task` (new)
- Covers: CT-4
- Setup: TC-7's ledger, and in the effort's `tasks.md` a fix task `T-9` whose fields hold `- From: J-1 (spec, round 1)`.
- Action: `run_main(root, "flow", "show", S, "--json")`.
- Assert: round 1's `findings` are exactly J-1 with `validation == "confirmed"` and `fix_tasks == ["T-9"]`, and J-2 with `validation == "refuted"` and `fix_tasks == []`; round 2's `findings == []`.

### TC-9 Several gates, each with only its own runs (AC-8; integration) [derived: AC-8]
- File: `tests/test_flow.py:test_show_juries_per_gate` (new)
- Covers: CT-4
- Setup: `effort("tasks_jury")` (real approved spec and plan rounds), then a `jury/tasks.json` ledger with `round: 1`, one juror `tasks-executability` (`round: 1`) and no findings.
- Action: `run_main(root, "flow", "show", S, "--json")`.
- Assert: `[j["gate"] for j in juries] == ["plan", "spec", "tasks"]`; each entry's rounds name only lenses whose jurors are in that gate's ledger (`tasks` round 1 lenses `[{"lens": "executability", "verdict": "approve"}]`).

### TC-10 No jury yet (AC-9; unit) [derived: AC-9]
- File: `tools/claude-mods/nio-status-pane/hooks/register.test.tsx:AC-9 AC-11 empty sections` (new)
- Covers: CT-12
- Setup: `flow show` answers `juries: []`, `tasks: []`, `memory: []`, a timeline of one row.
- Action: open the drill-down.
- Assert: the texts hold `no juries yet` and no line starting `error:`. (The CLI half is TC-38.)

### TC-11 Tasks grouped by epic with status and attempts (AC-10; integration) [derived: AC-10]
- File: `tests/test_flow.py:test_show_tasks_by_epic` (new)
- Covers: CT-2, CT-5
- Setup: `effort("implementing")` (its tasks.md has epics E-1 and E-2); history: `claim`/`red`/`green`/`review` passed/`task_done` for the first task of E-1; `claim` for the second; for the first task of E-2 `claim` then a `review` with `passed` false. Then write the effort's final `state.json` once, with `"claims": {"task": <second of E-1>}` and `"attempts": {<second of E-1>: 2, <first of E-2>: 1}` (values history alone can't give: one claim each).
- Action: `run_main(root, "flow", "show", S, "--json")`.
- Assert: `tasks` has two entries, epics `E-1` then `E-2`; the first task reads `status "done"`, attempts `"-"`; the second `status "claimed"`, `attempts 2`; E-2's first `status "failing"`, `attempts 1`: attempts come from the final `state.json`, not a count of claims.

### TC-12 No tasks yet (AC-11; unit) [derived: AC-11]
- File: `tools/claude-mods/nio-status-pane/hooks/register.test.tsx:AC-9 AC-11 empty sections` (new)
- Covers: CT-12
- Setup: TC-10's pane setup.
- Action: open the drill-down.
- Assert: the texts hold `no tasks yet`. (The CLI half is TC-39.)

### TC-13 Cost so far per stage and per jury, writing no usage.json (AC-12; integration) [derived: AC-12]
- File: `tests/test_usage.py:test_so_far` (new)
- Covers: CT-7
- Setup: `repo()` with `.nio/specs/<SLUG>/`; history lines (as dicts) `pass grilling→spec_jury` at `at(0)`, `pass spec_jury→planning` at `at(10)`, `pass planning→plan_jury` at `at(30)`; events for SLUG in one session: an orchestrator transcript with one request of output 100 at minute 5 and one of 50 at minute 35; a juror agent `j1` (`agent_start` at(2), `agent_stop` at(6), log a transcript whose first line is a `{"type": "user", ...}` prompt naming `.nio/runs/R-261110-aaaa/jury/packs/logic.md`, followed by `transcript`'s rows with one request of output 10); `.nio/runs/R-261110-aaaa/jury/packs/step.json` = `{"gate": "spec", "round": 0, "lenses": ["logic"]}`; a worker agent `w1` at(12)–at(20) with output 20 and no run.
- Action: `usage.so_far(root, SLUG, lines, now=when(at(40)))`.
- Assert: stages in order `spec_jury` (seconds 600, tokens 110, `juries == [{"gate": "spec", "tokens": 10, "seconds": 240}]`), `planning` (seconds 1200, tokens 20, juries `[]`), `plan_jury` (seconds 600, tokens 50: the open stage counted to `now`); `total == {"tokens": 180, "seconds": 2400}`; `.nio/specs/<SLUG>/usage.json` does not exist.

### TC-14 Two visits sum, early events are unattributed, the total adds up (AC-28; integration) [derived: AC-28]
- File: `tests/test_usage.py:test_so_far_visits_and_unattributed` (new)
- Covers: CT-7
- Setup: history `pass tasks_jury→implementing` at(10), `back implementing→tasks_jury` at(20), `pass tasks_jury→implementing` at(30); a worker agent at(1)–at(3) (output 7, before the first line), one at(12)–at(14) (output 5), one at(32)–at(34) (output 8); a juror agent at(22)–at(24) (output 4) whose run's step.json names `tasks`.
- Action: `usage.so_far(root, SLUG, lines, now=when(at(40)))`.
- Assert: `implementing` tokens 13 and seconds 1200 (10 + 10 minutes); `tasks_jury` tokens 4 with `juries == [{"gate": "tasks", "tokens": 4, "seconds": 120}]`; `unattributed == {"tokens": 7, "seconds": 120}`; `total["tokens"] == 13 + 4 + 7 == 24` (the jury's 4 counted once).

### TC-15 The pane's cost figures equal the CLI's (AC-13; integration) [derived: AC-13]
- File: `tools/claude-mods/nio-status-pane/hooks/register.test.tsx:AC-13 cost as the CLI gives it` (new)
- Covers: CT-12
- Setup: `flow show` answers TC-13's cost object (as JSON).
- Action: open the drill-down.
- Assert: the texts hold `spec_jury: 110 tokens · 600s`, an indented `spec: 10 tokens · 240s` under it, `planning: 20 tokens · 1200s`, `plan_jury: 50 tokens · 600s`, `unattributed: 0 tokens · 0s` and `total: 180 tokens · 2400s`.

### TC-16 No usage recorded reads `-` (AC-14; unit) [derived: AC-14]
- File: `tests/test_usage.py:test_so_far_nothing_recorded` (new)
- Covers: CT-7
- Setup: `repo()` with the effort folder, one history line, no events.jsonl.
- Action: `usage.so_far(root, SLUG, lines, now=...)`.
- Assert: `stages == []`, `unattributed == total == {"tokens": "-", "seconds": "-"}`.

### TC-17 Memory lists the records that point at the effort (AC-15; integration) [derived: AC-15]
- File: `tests/test_flow.py:test_show_memory_by_front_matter` (new)
- Covers: CT-6
- Setup: `effort("planning")`; with `records.new` (or written files) three records: a verdict whose `paths` holds `.nio/specs/<S>/spec.md`, a change request whose `against` is S, and a decision whose `paths` holds `src/other.py`; `nio index` built so the first two have standings; a fourth record pointing at the effort written after the index build. `effort("planning")` has already written its own spec-jury verdict (`.nio/memory/project/V-*-spec-gate-for-2026-10-20.md`, title `spec gate for <S>: approved (round 1)`, random ID, `paths` holds `.nio/specs/<S>/jury/spec.md`); the test reads its ID from that file before writing the other records. `fastembed` must not be imported: set `sys.modules["fastembed"] = None` before the call.
- Action: `flow.memory(root, S)`.
- Assert: the IDs are exactly the four records pointing at the effort (the three written above that point at it, plus the fixture's own verdict), sorted; the indexed ones carry the index's standing, the unindexed one `"-"`; each has `kind` and `title` from its front matter; the `src/other.py` decision is absent.

### TC-18 The host's context fill is shown (AC-16; integration) [derived: AC-16]
- File: `tools/claude-mods/nio-status-pane/hooks/register.test.tsx:AC-16 AC-17 context line` (new)
- Covers: CT-12
- Setup: `session.usage` answers `{ context: { percent: 42 } }`.
- Action: open the drill-down.
- Assert: the texts hold `context: 42%`.

### TC-19 No context line when the host gives none (AC-17; unit) [derived: AC-17]
- File: `tools/claude-mods/nio-status-pane/hooks/register.test.tsx:AC-16 AC-17 context line` (new)
- Covers: CT-12
- Setup: `session.usage` throws; a second run where it answers `{ context: {} }`.
- Action: open the drill-down in each.
- Assert: no text starts with `context:`; the timeline, juries, tasks, cost and memory sections are drawn as in TC-2.

### TC-20 Install puts both mods in place (AC-18; e2e) [derived: AC-18]
- File: `tests/test_hooks.py:test_mods_install_e2e` (new)
- Runs: only with `NIO_E2E=1`
- Covers: CT-8, CT-10, CT-11
- Setup: a fresh `repo()`, `CLAUDE_CONFIG_DIR` set to a new temp folder so the real `claude` touches no real settings; `claude` on PATH.
- Action: `nio mods install` (through `run_main`).
- Assert: exit 0; stdout is exactly `background-nio-commands: installed\nnio-status-pane: installed`; `claude plugin list --json` (same env, cwd the repo) lists `background-nio-commands@nio-mods` and `nio-status-pane@nio-mods`; `git status --porcelain` in the repo shows nothing new.

### TC-21 Skip installs neither (AC-19; e2e) [derived: AC-19]
- File: `tests/test_hooks.py:test_mods_install_e2e` (new)
- Runs: only with `NIO_E2E=1`
- Covers: CT-10, CT-11
- Setup: as TC-20, in a second fresh repo and config folder.
- Action: `nio mods install --skip`.
- Assert: stdout is exactly `background-nio-commands: skipped\nnio-status-pane: skipped`; `claude plugin list --json` lists neither id.

### TC-22 A second install leaves them as they are (AC-20; e2e) [derived: AC-20]
- File: `tests/test_hooks.py:test_mods_install_e2e` (new)
- Runs: only with `NIO_E2E=1`
- Covers: CT-10
- Setup: TC-20's repo after its install.
- Action: `nio mods install` again, then `nio mods install --skip`.
- Assert: the first prints `<mod>: already installed` for both, the second `<mod>: already installed (left as is)` for both; `claude plugin list --json` holds exactly one entry per mod id.

### TC-23 One mod failing doesn't stop the other (AC-21; integration) [derived: AC-21]
- File: `tests/test_hooks.py:test_mods_install_one_fails` (new)
- Covers: CT-10, CT-11
- Setup: a fake `claude` script first on PATH that logs its args, prints `[]` for `plugin list --json`, exits 1 with stderr `boom: marketplace unreadable` for `plugin install background-nio-commands ...`, and exits 0 for the other.
- Action: `nio mods install` (through `run_main`).
- Assert: exit 0; stdout is exactly `background-nio-commands: failed: boom: marketplace unreadable\nnio-status-pane: installed`.

### TC-24 The skill offers the mods on Claude Code only (AC-22; unit) [derived: AC-22]
- File: `tests/test_hooks.py:test_install_skill_mods_step` (new)
- Covers: CT-15
- Setup: read `skills/install/SKILL.md`; split its `## Steps` section into numbered steps.
- Action: find the steps whose text holds `mod` (case-insensitive).
- Assert: exactly one step holds it; that step starts with `On Claude Code`; it holds both `nio mods install` and `nio mods install --skip`.

### TC-25 `flow show` prints the five sections and changes no file (AC-23; integration) [derived: AC-23]
- File: `tests/test_flow.py:test_show_json_five_keys_writes_nothing` (new)
- Covers: CT-1, CT-2, CT-3, CT-4, CT-5, CT-6, CT-7
- Setup: `effort("implementing")` committed, with history lines, a `jury/spec.json` ledger, tasks.md, and `.nio/runs/events.jsonl` holding two events for S (`.nio/runs/` and `.nio/cache/` are gitignored); `git status --porcelain` saved.
- Action: `run_main(root, "flow", "show", S, "--json")`.
- Assert: exit 0; `json.loads(stdout)` has the keys `timeline`, `juries`, `tasks`, `cost`, `memory` (plus `slug`, `stage`); no section is a dict with an `error` key (the setup gives each one data); `git status --porcelain` equals the saved one; `.nio/specs/<S>/usage.json` doesn't exist.

### TC-26 An unknown or finished slug gives a JSON error (AC-29; integration) [derived: AC-29]
- File: `tests/test_flow.py:test_show_unknown_or_done_slug` (new)
- Covers: CT-1, CT-2
- Setup: `effort("done")` then `shipped(root, S)` (tests/test_flow.py: writes the history line `{"kind": "override", "from": "implementing", "to": "done", "reason": "shipped by hand"}`, so `flow.where(root, S)["stage"]` is `done`); a second slug `2026-01-01-nothing` with no folder.
- Action: `run_main(root, "flow", "show", "2026-01-01-nothing", "--json")` and `run_main(root, "flow", "show", S, "--json")`.
- Assert: both exit 1 with nothing on stderr; stdout parses as `{"error": "no effort 2026-01-01-nothing"}` and `{"error": f"{S} is done"}`.

### TC-27 The pane shows the error with Back (AC-29; integration) [derived: AC-29]
- File: `tools/claude-mods/nio-status-pane/hooks/register.test.tsx:AC-29 AC-30 drill-down errors` (new)
- Covers: CT-12
- Setup: `flow show` answers exit 1, stdout `{"error": "2026-11-08-e123 is done"}`.
- Action: open the drill-down.
- Assert: the texts hold `2026-11-08-e123 is done`; `ui.findAll({ type: 'Button' })` holds exactly one Button, `back`.

### TC-28 An old nio says to update (AC-30; unit) [derived: AC-30]
- File: `tools/claude-mods/nio-status-pane/hooks/register.test.tsx:AC-29 AC-30 drill-down errors` (new)
- Covers: CT-12
- Setup: `flow show` answers exit 2, stderr `nio flow: error: argument flow_cmd: invalid choice: 'show' (choose from ...)`.
- Action: open the drill-down.
- Assert: the texts hold `this nio has no flow show: update nio`; one Button, `back`.

### TC-29 No venv: the PATH nio, else `nio not found` (AC-24; unit) [derived: AC-24]
- File: `tools/claude-mods/nio-status-pane/hooks/register.test.tsx:AC-24 nio on PATH` (new)
- Also: the existing `AC-11: a worktree with no venv shows an error and runs nothing` test changes to this behaviour (RF-20)
- Covers: CT-13
- Setup: PORCELAIN plus `worktree /w/nio-new` with no `/w/nio-new/.venv/bin/nio`; `process.run` answers `nio flow status` in `/w/nio-new` with `2026-11-15-fresh · planning · manual · working · 2026-11-15 09:00`. A second run: the same, with `process.run` of argv[0] `nio` throwing `ENOENT: nio`.
- Action: `start`, read the Pane.
- Assert: run 1: a process run with argv `nio flow status` and `cwd` `/w/nio-new`, and the row `2026-11-15-fresh`; no argv starts with `uv`. Run 2: the texts hold `nio-new: nio not found`.

### TC-30 The wheel carries the mods (AC-25; integration) [derived: AC-25]
- File: `tests/test_hooks.py:test_wheel_ships_mods` (new)
- Covers: CT-9
- Setup: a temp out dir.
- Action: `uv build --wheel --out-dir <tmp>` in the repo root.
- Assert: the wheel's `zipfile` names include `nio/mods/.claude-plugin/marketplace.json`, `nio/mods/background-nio-commands/.claude-plugin/plugin.json` and `nio/mods/nio-status-pane/.claude-plugin/plugin.json`.

### TC-31 Local scope from the package's mods, and one question in the skill (AC-26; integration) [derived: AC-26]
- File: `tests/test_hooks.py:test_mods_install_local_scope` (new)
- Covers: CT-8, CT-10, CT-15
- Setup: TC-23's fake `claude`, succeeding for both mods.
- Action: `hooks.mods_install(root, claude=<fake>)`; read `skills/install/SKILL.md`.
- Assert: the fake's log holds, for each mod, `plugin install <mod> --marketplace <hooks.mods_dir()> --scope local --json`, run with cwd `root`; `hooks.mods_dir()` is the checkout's `tools/claude-mods` here (an editable install); the skill's mods step holds exactly one question (one line ending `?` whose options are the two commands).

### TC-32 The READMEs describe the mods as optional (AC-27; unit) [derived: AC-27]
- File: `tests/test_hooks.py:test_readmes_call_mods_optional` (new)
- Covers: CT-16, CT-17
- Setup: read `README.md`, `tools/claude-mods/README.md` and both mods' `README.md`; and `.nio/project/architecture.md` and `.nio/project/stack.md`.
- Action: search each text.
- Assert: none of the six holds `not part of the NIO product` or `dev tooling`; each README holds `optional Claude Code part of NIO` and `the skills work the same without`; each project doc holds `optional Claude Code part of NIO` and `D-261115-e6nx`.

### TC-37 A broken effort opens from its error row (AC-4; integration) [derived: AC-4]
- File: `tools/claude-mods/nio-status-pane/hooks/register.test.tsx:AC-4 a broken effort opens` (new)
- Covers: CT-12, CT-14
- Setup: `flow status` in `/w/nio-123` answers `2026-11-08-e123 · broken: history.jsonl, line 2`; `flow show 2026-11-08-e123 --json` there answers exit 0 with `timeline` `{"error": "2026-11-08-e123: history.jsonl, line 2"}`, `cost` an `{"error": ...}` too, `juries` one `spec` gate, `tasks: []`, `memory: []`.
- Action: `start`, mount the Pane, `ui.press({ key: '2026-11-08-e123' })`, settle the clock, read every `Text`.
- Assert: one process run of `flow show 2026-11-08-e123 --json` with `cwd` `/w/nio-123`; the texts hold `error: 2026-11-08-e123: history.jsonl, line 2` and the `spec` gate row, `no tasks yet` and `no memory yet`; a `back` Button.

### TC-38 No jury yet, from the CLI (AC-9; unit) [derived: AC-9]
- File: `tests/test_flow.py:test_juries_none_yet` (new)
- Covers: CT-4
- Setup: `effort("plan_jury")` with its `jury/` folder removed.
- Action: `flow.juries(root, S)`.
- Assert: `== []`.

### TC-39 No tasks yet, from the CLI (AC-11; unit) [derived: AC-11]
- File: `tests/test_flow.py:test_task_rows_none_yet` (new)
- Covers: CT-5
- Setup: `effort("planning")` (no tasks.md).
- Action: `flow.task_rows(root, S, *flow.load(root, S))`.
- Assert: `== []`.

## Quality tests

### TC-33 The drill-down's data in under 5 seconds (NFR-1; integration) [derived: NFR-1]
- File: `tests/test_flow.py:test_show_speed` (new)
- Runs: asserts the time only when `NIO_PERF=1`, as the status-speed limit does (C-261105-6rme)
- Covers: CT-1, CT-2, CT-7
- Setup: `effort("implementing")`; 200 history lines (claims, reds, greens, reviews over 50 tasks, and stage changes); ledgers for spec, plan, tasks and implementation-E-1 to E-6 (10 runs), each with 2 rounds and 5 findings; 2,000 events with 40 agents whose transcripts hold 20 requests each.
- Action: time `run_main(root, "flow", "show", S, "--json")`.
- Assert: under 5.0 seconds of wall time.

### TC-34 Nothing written outside `.nio/cache/` (NFR-2; integration) [derived: NFR-2]
- File: `tests/test_flow.py:test_show_writes_only_caches` (new)
- Covers: CT-2, CT-6, CT-7
- Setup: TC-25's effort, with `.nio/cache/index.db` built; record the path, size and mtime of every file under the repo except `.git/` and `.nio/cache/`.
- Action: `run_main(root, "flow", "show", S, "--json")`.
- Assert: exit 0, and neither `cost` nor `memory` is a dict with an `error` key (so the code that could write ran); then the recorded list is unchanged (no file added, removed or modified).

## Misuse tests

### TC-35 The drill-down offers no action on the effort (UJ-1 misuse; integration) [derived: UJ-1]
- File: `tools/claude-mods/nio-status-pane/hooks/register.test.tsx:UJ-1 the drill-down only reads` (new)
- Covers: CT-12
- Setup: as TC-2.
- Action: open the drill-down.
- Assert: the only Button is `back`; the process runs are only `git worktree list`, `flow status` and the one `flow show`; no `fs.write`.

### TC-36 No Claude Code on the machine (UJ-2 misuse; integration) [derived: UJ-2]
- File: `tests/test_hooks.py:test_mods_install_without_claude` (new)
- Covers: CT-10, CT-11
- Setup: PATH set to a folder without `claude`.
- Action: `nio mods install`, then `nio mods install --skip` (through `run_main`).
- Assert: both exit 0; the first prints `background-nio-commands: failed: claude not found` and `nio-status-pane: failed: claude not found`; the second `<mod>: skipped` for both.
