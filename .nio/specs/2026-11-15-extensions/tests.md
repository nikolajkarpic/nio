---
slug: 2026-11-15-extensions
retired: []                      # TC IDs removed from this plan; never reused
---
# Tests: Extensions

Shared setup, named below. Every test is a self-check (`tests/selfcheck.py`) in a fresh temp git repo.
- `S`, `effort(stage)` and `BY = "driver / test / test"`: `tests/test_flow.py`'s effort fixture at `stage`; `gate_approved(root, gate)`
  writes that gate's ledger approved for its current round, as `tests/test_flow.py`'s plan gate tests do; `pass_plan(root)` is
  `nio flow done plan_jury S --commit --by human` on an effort at `plan_jury` with its ledger approved.
- `src(tmp, name, steps=[], cards=[], hooks=[], **extra)`: writes a source folder `<tmp>/src/<name>/` holding `manifest.json`
  `{"name": name, "version": "1.0.0", "steps": steps, "cards": cards, "hooks": hooks, **extra}`, `skills/<step>/SKILL.md` for each
  step and a valid `agents/<card>.md` for each card (front matter `name`, `description`, `tier: strong`, `effort: med`; sections
  Job, Inputs, Output format, Stop when). `step(name, after="plan_jury", check="true", **kw)` is
  `{"name": name, "after": after, "skill": f"skills/{name}/SKILL.md", "check": check, **kw}`.
- `nio(root, *args)`: runs the CLI in `root`, returning (exit code, output). `snap(root)`: `{path: bytes}` of every file under
  `.nio/extensions` (empty when absent). `flowfiles(root)`: the bytes of S's `state.json` and `history.jsonl`.
- `npx_stub(tmp, report, out="", code=1)`: puts an `npx` first on `PATH` that writes the JSON `report` to
  `$PLAYWRIGHT_JSON_OUTPUT_NAME`, prints `out`, logs its argv to `<tmp>/npx.log` and exits `code`. `report` follows Playwright's
  JSON reporter (RF-22): `suites[].specs[].tests[].results[]` with `status`, `errors[].message` and `attachments[]`, plus a
  top-level `errors`. `e2e_spec(root, acs)`: S's spec.md with the given ACs at `Level: e2e`, and tests.md with one TC per such AC
  whose `File:` is `e2e/<ac>.spec.ts:<ac> shows the page`, each file written with a test titled `<AC-ID> <ac> shows the page`.
- Tests run with `NIO_E2E=1` only live in `tests/test_extensions_e2e.py`: they need Node, `npx playwright` with Chromium, and
  (TC-29) a real model; their fixture is `tests/fixtures/e2e-app/`, a static page served by `python3 -m http.server`, named in
  its `playwright.config.ts` `webServer`.

The spec's journey misuses are each an AC, so their tests are the AC tests: UJ-1's untrusted commands TC-39 and hand edit
TC-21, TC-41; UJ-2's false done TC-16 and auto gate TC-19; UJ-3's misplaced step TC-17 and host-only skill TC-38; UJ-4's app
not started TC-31 and tests passing early TC-30.

TC-13 runs as an integration test, as AC-13 asks; its heading says `e2e` only because today's `nio check plan` takes an
AC's first `Level:`, which in AC-13 is the trigger rule's text. CT-17 makes every reader take the AC's own `Level:`.

## Acceptance tests

### TC-1 Add from a folder copies and records it (AC-1; integration) [agent]
- File: `tests/test_extensions.py:test_add_from_folder` (new)
- Covers: CT-1
- Setup: `src(tmp, "x", steps=[step("tests")])`; no `.nio/extensions` in the repo.
- Action: `nio(root, "extensions", "add", "<tmp>/src/x")`.
- Assert: exit 0; every file of the source exists byte-equal under `.nio/extensions/x/`; `record.json["x"]` has `source` the path given, `version` `1.0.0` and `hash` the sha256 the Data model defines over those files.

### TC-2 Add from a git URL records the fetched revision (AC-2; integration) [agent]
- File: `tests/test_extensions.py:test_add_from_git_url` (new)
- Covers: CT-1
- Setup: `src(tmp, "x", ...)` committed into a git repo at `<tmp>/repo`; `url = "file://<tmp>/repo"`; `rev` its HEAD.
- Action: `nio(root, "extensions", "add", url)`.
- Assert: exit 0; `.nio/extensions/x/manifest.json` exists and `.nio/extensions/x/.git` doesn't; `record.json["x"]` is `{"source": url, "version": rev, ...}`.

### TC-3 Add a shipped extension by name (AC-3; integration) [agent]
- File: `tests/test_extensions.py:test_add_shipped_e2e` (new)
- Covers: CT-1, CT-14
- Setup: `HOME` set to an empty temp folder (no `~/.nio/extensions`).
- Action: `nio(root, "extensions", "add", "e2e")`.
- Assert: exit 0; `.nio/extensions/e2e/` equals `src/nio/shipped/e2e/` file by file; `record.json["e2e"]` has `source: "shipped"` and `version` equal to `importlib.metadata.version("nio")`; with `~/.nio/extensions/e2e/` holding a manifest of version `9.9.9`, the same add records source `~/.nio/extensions/e2e` and version `9.9.9`.

### TC-4 Adding again replaces the copy (AC-4; integration) [agent]
- File: `tests/test_extensions.py:test_add_again_replaces` (new)
- Covers: CT-1
- Setup: `x` added at version `1.0.0` with a file `old.txt`; a new source `x` at version `2.0.0` without `old.txt`.
- Action: add the new source.
- Assert: exit 0; `.nio/extensions` holds one folder `x`, without `old.txt`; `record.json["x"]["version"] == "2.0.0"` and `hash` matches the new files.

### TC-5 A missing or malformed field refuses the add (AC-5; unit) [agent]
- File: `tests/test_extensions.py:test_manifest_missing_or_bad_field` (new)
- Covers: CT-1, CT-2
- Setup: five sources: no `manifest.json`; `manifest.json` = `{`; no `version`; `steps[0].after` = `3`; `steps[0]` with an unknown key `colour`.
- Action: add each.
- Assert: each exits 1 with, in order, `manifest.json is missing`, `manifest.json is not JSON`, `missing field version`, `steps[0].after must be`, `unknown field steps[0].colour`; `snap(root)` is the same before and after every add.

### TC-6 List shows each extension's five facts (AC-6; integration) [agent]
- File: `tests/test_extensions.py:test_list_shows_each` (new)
- Covers: CT-3
- Setup: `a` (step `one` after `plan_jury`, card `a-card`, hook `step-passed: true`) and `b` (no step, card or hook) added from folders.
- Action: `nio(root, "extensions", "list")`.
- Assert: exit 0; output is exactly `a · 1.0.0 · <a's path>`, `  steps: a.one (after plan_jury)`, `  cards: a-card`, `  hooks: step-passed: true`, `b · 1.0.0 · <b's path>`, `  steps: none`, `  cards: none`, `  hooks: none`.

### TC-7 Remove deletes it and its step leaves the flow (AC-7; integration) [agent]
- File: `tests/test_extensions.py:test_remove_drops_the_step` (new)
- Covers: CT-4, CT-6
- Setup: `effort("plan_jury")` with its ledger approved; `x` added with `step("tests")`.
- Action: `nio(root, "extensions", "remove", "x")`, then `pass_plan(root)`.
- Assert: remove exits 0; `.nio/extensions/x` is gone and `record.json` has no `x`; `"x.tests" not in flow.table(root)[0]`; the pass moves S `plan_jury → tasking` and `nio flow status` names no `x.` stage.

### TC-8 A shipped extension stays off until added (AC-8; integration) [agent]
- File: `tests/test_extensions.py:test_shipped_off_until_added` (new)
- Covers: CT-5, CT-6
- Setup: `effort("plan_jury")` with its ledger approved, spec with an AC at `Level: e2e`; nothing added.
- Action: `pass_plan(root)`; `nio(root, "flow", "status")`.
- Assert: `flow.table(root)[0] is flow.STAGES`; S's stage is `tasking`; the status row and history name no `e2e.` stage.

### TC-9 The step is next after its gate (AC-9; integration) [agent]
- File: `tests/test_extensions.py:test_step_runs_after_its_gate` (new)
- Covers: CT-6
- Setup: `effort("plan_jury")` with its ledger approved; `x` added with `step("tests")` (no trigger).
- Action: `pass_plan(root)`; `nio(root, "flow", "next", S)`.
- Assert: the newest `pass` line goes `plan_jury → x.tests`; next prints `state: x.tests (working)`, `skill: .nio/extensions/x/skills/tests/SKILL.md` and `done: nio flow done x.tests S`; it doesn't print `tasking`.

### TC-10 Two steps after one stage run in extension-name order (AC-10; integration) [agent]
- File: `tests/test_extensions.py:test_two_steps_run_in_name_order` (new)
- Covers: CT-6
- Setup: `beta` (`step("two")`) added before `alpha` (`step("one")`), both after `plan_jury`; plan ledger approved.
- Action: `pass_plan(root)`; `nio flow done alpha.one S --by BY`; `nio flow done beta.two S --by BY`.
- Assert: the history's `pass` lines go `plan_jury → alpha.one`, `alpha.one → beta.two`, `beta.two → tasking`, in that order; done on `beta.two` before `alpha.one` passes exits 1 (`S is at alpha.one`).

### TC-11 A step after an unknown step is refused (AC-11; unit) [agent]
- File: `tests/test_extensions.py:test_after_unknown_step_refused` (new)
- Covers: CT-2
- Setup: source with `step("tests", after="planing")`.
- Action: add it.
- Assert: exit 1; output holds `step tests follows planing, which is neither a built-in step nor a step of an added extension`; `snap(root)` unchanged.

### TC-12 A trigger that doesn't apply is skipped on the record (AC-12; integration) [agent]
- File: `tests/test_extensions.py:test_trigger_not_applying_skips` (new)
- Covers: CT-7
- Setup: `x` with `step("tests", trigger={"plan_path": "nowhere/"})`; S's plan binds no file under `nowhere/`; plan ledger approved.
- Action: `pass_plan(root)`.
- Assert: history ends with `pass plan_jury → x.tests` and `skip x.tests → tasking` whose `reason` is `skipped: the plan touches no file under nowhere/`; `nio flow next S` prints `state: tasking`.

### TC-13 The spec-level trigger reads the spec's ACs (AC-13; e2e) [agent]
- File: `tests/test_extensions.py:test_spec_level_trigger` (new)
- Covers: CT-7
- Setup: two efforts at `plan_jury`, plan ledgers approved: `S1` whose spec has no `Level: e2e` AC, `S2` with one; `x` with `step("tests", trigger={"spec_level": "e2e"})`.
- Action: `nio flow done plan_jury <slug> --commit --by human` on each.
- Assert: S1's spec also holds an AC whose Given names `Level: e2e` while its own `Level:` is `integration`, and still S1's history has `skip x.tests → tasking` with reason `skipped: the spec has no AC at Level: e2e`; S2's newest line is `pass plan_jury → x.tests` and `nio flow next S2` prints `state: x.tests (working)`.

### TC-14 The plan-path trigger reads the plan's files (AC-14; integration) [agent]
- File: `tests/test_extensions.py:test_plan_path_trigger` (new)
- Covers: CT-7
- Setup: as TC-13 with `trigger={"plan_path": "web/"}` and three efforts: S1's contracts.md binds `src/web/x.py` and nothing starts with `web/`; S2's only `web/` path is tests.md's `- File: \`web/app.spec.ts:loads\` (new)`; S3's only `web/` path is contracts.md's `- Binding: \`web/app.tsx:App\` (new)`.
- Action: as TC-13, on each.
- Assert: S1 has `skip x.tests → tasking` with `skipped: the plan touches no file under web/`; S2 and S3 are at `x.tests`.

### TC-15 A check exiting 0 passes the step (AC-15; integration) [agent]
- File: `tests/test_extensions.py:test_check_zero_passes` (new)
- Covers: CT-8
- Setup: S at `x.tests` (TC-9's setup), check `test "$NIO_SLUG" = S && test -d "$NIO_EXTENSION_DIR"`.
- Action: `nio flow done x.tests S --by BY`.
- Assert: exit 0; the newest line is `pass x.tests → tasking` by `BY`; `nio flow next S` prints `state: tasking`.

### TC-16 A failing check keeps the step and records code and tail (AC-16; integration) [agent]
- File: `tests/test_extensions.py:test_check_failing_records_tail` (new)
- Covers: CT-8
- Setup: S at `x.tests`, check `for i in $(seq 1 80); do echo line-$i; done; exit 3`; auto off.
- Action: `nio flow done x.tests S --by BY`.
- Assert: exit 1, output holds `check failed: exit 3` and `line-80`; S's stage is still `x.tests`; the newest line is `fail x.tests → x.tests` with `evidence.code == 3`, `timed_out` false and `tail` exactly `line-31` … `line-80` (50 lines).

### TC-17 A step whose inputs don't exist yet fails at its check (AC-17; integration) [agent]
- File: `tests/test_extensions.py:test_misplaced_step_fails_at_check` (new)
- Covers: CT-2, CT-8
- Setup: `x` with `step("tests", after="spec_jury", check='test -f .nio/specs/$NIO_SLUG/tasks.md')`; S at `spec_jury` with its spec ledger approved.
- Action: add `x`; `nio flow done spec_jury S --commit --by human`; `nio flow done x.tests S --by BY`.
- Assert: the add exits 0; the gate pass goes `spec_jury → x.tests`; the done exits 1 with `check failed: exit 1`; S stays at `x.tests`.

### TC-18 Status and the timeline show the step at its spot (AC-18; integration) [agent]
- File: `tests/test_extensions.py:test_status_shows_the_step` (new)
- Covers: CT-6
- Setup: TC-9's setup.
- Action: `nio flow status` while S is at `x.tests`; then `nio flow done x.tests S --by BY` and `nio flow show S`.
- Assert: the status row is `S · x.tests · manual · working · …`; the shown timeline's rows hold, in order, `plan_jury → x.tests` then `x.tests → tasking`, nothing between them; a second effort whose `x.tests` was skipped shows `skip` from `x.tests` at the same spot.

### TC-19 Under auto an extension gate goes as a built-in gate does (AC-19; integration) [agent]
- File: `tests/test_extensions.py:test_auto_extension_gate` (new)
- Covers: CT-6, CT-9
- Setup: auto granted on S (`tests/test_flow.py`'s `auto_on`); `x` with `step("tests", output="x.md", gate={"lenses": ["x-lens"]})` and card `x-lens`; S at `x.tests.jury` (the step's check passed), `x.md` present.
- Action: case one: `gate_approved(root, "x.tests")`, then `nio flow done x.tests.jury S --by BY`. Case two (fresh repo): the ledger's outcome `human` with one finding open, then the same done, then `nio flow next S`.
- Assert: case one exits 0, its `pass x.tests.jury → tasking` line has `who.role == "driver"` and `evidence.auto.grant` equal to the grant's line number, and a `nio: approve x.tests` commit exists. Case two exits 1 and writes no `pass` line from `x.tests.jury`; `nio flow next` prints the same lines a built-in `plan_jury` prints with its ledger in that state, with `plan_jury` replaced by `x.tests.jury`.

### TC-20 Removing, reordering, skipping or replacing a built-in step is refused (AC-20; unit) [agent]
- File: `tests/test_extensions.py:test_add_only_rule` (new)
- Covers: CT-2
- Setup: four sources: top-level `"remove": ["plan_jury"]`; a step with `"before": "tasking"`; top-level `"skip": ["tasks_jury"]`; a step named `planning`.
- Action: add each.
- Assert: each exits 1, `snap(root)` unchanged, the outputs holding `remove would change built-in plan_jury`, `before would change built-in tasking`, `skip would change built-in tasks_jury` and `step planning would replace built-in planning`.

### TC-21 A hand edit that skips a gate stops every effort (AC-21; integration) [agent]
- File: `tests/test_extensions.py:test_hand_edit_skipping_gate_stops_flow` (new)
- Covers: CT-18
- Setup: S at `planning`; `x` added; then its `manifest.json` gains `"skip": ["plan_jury"]` and `record.json["x"]["hash"]` is set by hand to the new files' hash.
- Action: `nio(root, "flow", "next", S, "--by", BY)` and `nio(root, "flow", "done", "planning", S, "--by", BY)`.
- Assert: both exit non-zero with `extension x breaks the add-only rule: skip would change built-in plan_jury`; `flowfiles(root)` byte-equal before and after.

### TC-22 A card named like a shipped card is refused (AC-22; unit) [agent]
- File: `tests/test_extensions.py:test_card_named_like_shipped_refused` (new)
- Covers: CT-2
- Setup: source with card `worker`.
- Action: add it.
- Assert: exit 1 with `card worker has the name of a shipped card`; `snap(root)` unchanged.

### TC-23 An extension gate runs its jury and waits for approval (AC-23; integration) [agent]
- File: `tests/test_extensions.py:test_extension_gate_runs_its_jury` (new)
- Covers: CT-9
- Setup: TC-19's extension, auto off; S at `x.tests`, `x.md` written.
- Action: with a second extension `y` hooking `step-passed` with `echo $NIO_STAGE >> passed.log`: `nio flow done x.tests S --by BY`; `nio jury plan S x.tests`; `nio flow done x.tests.jury S --commit --by human` before and after `gate_approved(root, "x.tests")`.
- Assert: the first done moves S to `x.tests.jury`; jury plan exits 0 listing lens `x-lens` (core) and no other lens; the done before approval exits non-zero and S stays at `x.tests.jury`; after approval it exits 0, `jury/x.tests.json` exists, a `nio: approve x.tests` commit exists and S is at `tasking`, with no `tasks` ledger needed; `passed.log` is exactly `x.tests.jury\n` (nothing when the step moved to judging).

### TC-24 A rejected extension gate goes back to its step (AC-24; integration) [agent]
- File: `tests/test_extensions.py:test_extension_gate_rejected_goes_back` (new)
- Covers: CT-6, CT-9
- Setup: TC-23 at `x.tests.jury`; its ledger records round 1 outcome `rejected` judging the current `x.md`.
- Action: `nio flow next S`.
- Assert: prints `state: x.tests (working: the x.tests jury rejected round 1)`.

### TC-25 Extension cards render per host (AC-25; integration) [agent]
- File: `tests/test_extensions.py:test_agents_sync_renders_extension_cards` (new)
- Covers: CT-10
- Setup: `.nio/config.json` `{"agents": {"hosts": ["claude", "codex"]}}`; `x` added with card `x-card`.
- Action: `nio(root, "agents", "sync")`.
- Assert: exit 0; `.claude/agents/nio-x-card.md` and `.codex/agents/nio-x-card.toml` exist, each holding the card's Job text.

### TC-26 A gate-approved hook runs once and its code is recorded (AC-26; integration) [agent]
- File: `tests/test_extensions.py:test_gate_approved_hook_runs_once` (new)
- Covers: CT-11
- Setup: `effort("plan_jury")`, ledger approved; `x` with hook `{"event": "gate-approved", "command": "echo $NIO_EVENT $NIO_STAGE $(git log -1 --format=%s) >> hook.log"}`.
- Action: `pass_plan(root)`; then, on a copy where git refuses the approval commit (a failing `pre-commit` hook), the same.
- Assert: `hook.log` is exactly `gate-approved plan_jury nio: approve plan\n` (the hook ran after the commit); on the copy no `hook.log` exists; history holds one `hook` line with `evidence.extension == "x"`, `event == "gate-approved"`, `code == 0`.

### TC-27 Hooks on one event run in extension-name order (AC-27; integration) [agent]
- File: `tests/test_extensions.py:test_hooks_run_in_name_order` (new)
- Covers: CT-11
- Setup: `b` then `a` added, each with hook `{"event": "step-passed", "command": "echo <name> >> order.log"}`; S at `planning` with a passing plan.
- Action: `nio flow done planning S --by BY`.
- Assert: `order.log` is `a\nb\n`; the two `hook` lines are `a` then `b`.

### TC-28 A hook on an unknown event is refused (AC-28; unit) [agent]
- File: `tests/test_extensions.py:test_unknown_event_refused` (new)
- Covers: CT-2
- Setup: source with hook event `after-task-green`.
- Action: add it.
- Assert: exit 1 with `hook on after-task-green: NIO fires only step-passed, step-skipped, gate-approved, gate-rejected, epic-closed, waiting-on-human, effort-done`; `snap(root)` unchanged.

### TC-29 The e2e tester writes one test per e2e AC (AC-29; e2e) [agent]
- File: `tests/test_extensions_e2e.py:test_tester_writes_one_test_per_e2e_ac` (new)
- Covers: CT-14, CT-16
- Setup: `NIO_E2E=1`; a copy of `tests/fixtures/e2e-app/` with an effort whose spec has two ACs at `Level: e2e` (the page shows a title; a button shows a message) and tests.md TCs for them, the plan gate approved; `nio extensions add e2e`.
- Action: `pass_plan`, then run the step's skill with a real model (the `nio-e2e-tester` card on its inputs).
- Assert: each TC's `File:` exists and holds exactly one test whose title holds its AC ID; `e2e.md` lists both; the fixture config's own `timeout: 12345` and `outputDir: 'pw-out'` are unchanged and `.gitignore` lists `pw-out`; `nio flow done e2e.tests` exits 0.

### TC-30 The e2e check passes only on tests failing for the missing feature (AC-30; integration) [agent]
- File: `tests/test_extensions.py:test_e2e_check_wants_assertion_failures` (new)
- Covers: CT-15
- Setup: `e2e_spec(root, ["AC-1", "AC-2"])`; `NIO_SLUG=S`.
- Action: run `python3 src/nio/shipped/e2e/check.py` three times: (a) `npx_stub` with both tests `failed`, messages `Error: expect(locator).toBeVisible() failed`; (b) as (a) with AC-2's test file removed; (c) as (a) with AC-1's test `passed`.
- Assert: (a) exit 0 printing `e2e: 2 tests fail on their assertions, as they should before implementation`; (b) exit 1 with `AC-2 has no e2e test`; (c) exit 1 with `AC-1 AC-1 shows the page: passes before any code is written`.

### TC-31 An app that doesn't start is a setup error (AC-31; integration) [agent]
- File: `tests/test_extensions.py:test_e2e_check_app_not_started` (new)
- Covers: CT-15
- Setup: as TC-30 (a), but the stub prints `Error: Process from config.webServer was not able to start. Exit code: 1` and the report has no test results.
- Action: run the check.
- Assert: exit 1; output holds `setup error: the app didn't start` and that line; it holds no `fail on their assertions` count.

### TC-32 Tasks covering an e2e AC name its test, and the epic runs it (AC-32; integration) [agent]
- File: `tests/test_extensions.py:test_tasks_name_the_e2e_test` (new)
- Covers: CT-12, CT-13
- Setup: `tests/test_tasks.py`'s `repo()` whose spec has AC-1 and AC-2 at `Level: e2e` and AC-3 at `unit`; TC-1 aimed at AC-1 with `File: \`e2e/a.spec.ts:AC-1 loads\``, TC-2 aimed at AC-2 with `File: \`e2e/b.spec.ts:AC-2 shows (x)\``, TC-3 aimed at AC-3 with `File: \`tests/test_app.py:test_three\``; `tests.suite` `python -m pytest`; a `playwright.config.ts` at the root; T-1 serves AC-1 and AC-2, T-2 serves AC-3, both in E-1.
- Action: `tasks.check` with T-1's `Test: TC-3`, then with `Test: TC-1, TC-2`; `implement.epic_tests(root, S, [T-1, T-2])`.
- Assert: the first check has the errors `T-1 serves AC-1 (Level: e2e) but its Test: cites no TC aimed at it` and the same for AC-2; the second has none; the epic command is exactly `npx playwright test e2e/a.spec.ts e2e/b.spec.ts -g 'AC\-1\ loads|AC\-2\ shows\ \(x\)' && python -m pytest tests/test_app.py::test_three`.

### TC-33 A failing e2e test keeps its epic open (AC-33; integration) [agent]
- File: `tests/test_extensions.py:test_failing_e2e_keeps_epic_open` (new)
- Covers: CT-13
- Setup: `tests/test_implement.py`'s `impl()` whose E-1's task cites TC-1 of TC-32's setup; E-1 claimed; `npx_stub` exiting 1 with output `1 failed`.
- Action: `nio flow finish S E-1 --by BY`.
- Assert: exit non-zero; the `epic_test` line has `passed: false` and `command` holding `npx playwright test e2e/a.spec.ts -g`; no `task_done` line; `npx.log` holds that command's argv.

### TC-34 The app is started and stopped around a run (AC-34; integration) [agent]
- File: `tests/test_extensions_e2e.py:test_app_started_and_stopped` (new)
- Covers: CT-13
- Setup: `NIO_E2E=1`; the `e2e-app` fixture, whose `webServer.command` is `python3 -m http.server 4173 # nio-e2e-marker` and `url` `http://127.0.0.1:4173`; one passing and one failing test.
- Action: run `evidence.one_test(None, file, name, root)` for each with `implement.run`.
- Assert: the passing one exits 0, the failing one non-zero; after each, `pgrep -f nio-e2e-marker` finds nothing and port 4173 refuses a connection.

### TC-35 A failing e2e test keeps its trace and screenshot (AC-35; integration) [agent]
- File: `tests/test_extensions_e2e.py:test_failure_keeps_trace_and_screenshot` (new)
- Covers: CT-15, CT-16
- Setup: `NIO_E2E=1`; the `e2e-app` fixture's config as the e2e skill sets it (trace `retain-on-failure`, screenshot `only-on-failure`, `outputDir` `test-results` in `.gitignore`); one test failing on `expect(page).toHaveTitle`.
- Action: run the e2e check (`NIO_SLUG` set).
- Assert: exit 0; output holds `trace: test-results/…/trace.zip` and `screenshot: test-results/….png`, both files exist; `git status --porcelain` lists nothing under `test-results/`.

### TC-36 The pr evidence lists the e2e tests and their results (AC-36; integration) [agent]
- File: `tests/test_extensions.py:test_pr_evidence_lists_e2e_tests` (new)
- Covers: CT-13
- Setup: an effort at the pr gate (`tests/test_evidence.py`'s pr fixture) whose tests.md has TC-1 with `File: \`e2e/a.spec.ts:AC-1 loads\``, a `playwright.config.ts`, `tests.suite` a passing self-check; `npx_stub` exiting 1.
- Action: `evidence.collect(root, S, "pr", run)`.
- Assert: the run's `tests` hold `{"file": "e2e/a.spec.ts", "name": "AC-1 loads", "result": "failed"}`; with the stub exiting 0 the result is `passed`; `npx.log` holds one run per case.

### TC-37 No NIO code names the e2e extension (AC-37; unit) [agent]
- File: `tests/test_extensions.py:test_nothing_names_the_e2e_extension` (new)
- Covers: CT-14
- Setup: the repo's `src/nio/`.
- Action: read every file under `src/nio/` outside `src/nio/shipped/e2e/`; run `extensions.check` on the shipped manifest; copy the shipped folder to a temp source without `version` and add it.
- Assert: no file holds `shipped/e2e`, `e2e-tester` or `e2e.tests`; the check returns `[]`; the broken copy is refused with `missing field version`, as any extension is.

### TC-38 Shipped skills carry the block and no host-only tool (AC-38; unit) [agent]
- File: `tests/test_talk.py:test_extension_skills_carry_the_block` (new)
- Covers: CT-14, CT-16
- Setup: `problems(root)` reads `skills/*/SKILL.md` and `src/nio/shipped/*/skills/*/SKILL.md`; a temp copy of the repo with the e2e skill's block line `Before sending, ask:` removed.
- Action: `problems()` on the repo and on the copy; search every shipped skill for `TodoWrite`, `AskUserQuestion`, `SendMessage`, `subagent_type`, `Task tool`, `Agent tool`.
- Assert: the repo has no problem; the copy has `src/nio/shipped/e2e/skills/e2e/SKILL.md: block missing`; no shipped skill holds any of those names.

### TC-39 Add runs no command and lists them all (AC-39; integration) [agent]
- File: `tests/test_extensions.py:test_add_runs_nothing_lists_commands` (new)
- Covers: CT-1
- Setup: source `x` with `step("tests", check="touch ran-check")` and hook `{"event": "step-passed", "command": "touch ran-hook"}`.
- Action: add it.
- Assert: exit 0; neither `ran-check` nor `ran-hook` exists in the repo or the source; output holds `commands it brings (none run):`, `check x.tests: touch ran-check` and `hook step-passed: touch ran-hook`.

### TC-40 A failing hook is recorded and the flow moves on (AC-40; integration) [agent]
- File: `tests/test_extensions.py:test_failing_hook_never_blocks` (new)
- Covers: CT-11
- Setup: S at `planning` with a passing plan; `x` with hook `{"event": "step-passed", "command": "echo nope; exit 4"}`.
- Action: `nio flow done planning S --by BY`.
- Assert: exit 0; S's stage is `plan_jury`, as in the same run without `x`; the `hook` line has `code: 4` and `tail` `["nope"]`.

### TC-41 A hand-edited check stops the flow until it is added again (AC-41; integration) [agent]
- File: `tests/test_extensions.py:test_hand_edited_check_needs_add_again` (new)
- Covers: CT-1, CT-18
- Setup: S at `x.tests` (TC-9); then `.nio/extensions/x/manifest.json`'s check changed to `false` by hand.
- Action: `nio flow next S --by BY`; `nio flow done x.tests S --by BY`; `nio extensions add .nio/extensions/x`; `nio flow next S`.
- Assert: the first two exit non-zero with `extension x changed since it was added` and `nio extensions add .nio/extensions/x`; `flowfiles(root)` unchanged by them; after the add, next exits 0 at `x.tests` and `record.json["x"]` keeps its source and version with the new hash.

### TC-42 Steps that others follow, and names in use, are protected (AC-42; unit) [agent]
- File: `tests/test_extensions.py:test_followed_steps_and_names_protected` (new)
- Covers: CT-2, CT-4
- Setup: `a` with `step("one")`; `b` with `step("two", after="a.one")`, card `b-card`.
- Action: remove `a`; add `a` version `2.0.0` without steps; add `c` with `step("two")`; add `d` with card `b-card`; add `a` version `3.0.0` with steps `one` (after `plan_jury`) and `three` (after `b.two`), then `b` version `2.0.0` with `step("two", after="a.three")`.
- Assert: the first two exit 1 with `b.two follows a.one`; the third with `step two is already a step of extension b`; the fourth with `card b-card is already a card of extension b`; `a` 3.0.0 is added; `b` 2.0.0 exits 1 with `step two follows a.three, which never reaches a built-in step: b.two → a.three → b.two`; `snap(root)` unchanged by every refused call.

### TC-43 A plan-path trigger before the plan gate is refused (AC-43; unit) [agent]
- File: `tests/test_extensions.py:test_plan_trigger_before_plan_gate_refused` (new)
- Covers: CT-2
- Setup: `x` with `step("tests", after="spec_jury", trigger={"plan_path": "web/"})`; `y` the same with `after="plan_jury"`.
- Action: add `x`, then `y`.
- Assert: `x` exits 1 with `step tests: trigger plan_path reads the plan, which isn't approved before plan_jury; it follows spec_jury`, `snap` unchanged; `y` exits 0 and `.nio/extensions/y` exists.

### TC-44 Remove is refused at the step and leaves past efforts alone (AC-44; integration) [agent]
- File: `tests/test_extensions.py:test_remove_at_step_and_past_step` (new)
- Covers: CT-4, CT-6
- Setup: `x` with `step("tests")`; S1 at `x.tests`; S2 past it (its `pass x.tests → tasking` written).
- Action: remove `x`; finish S1's step; snapshot S2's `state.json` and `history.jsonl`; remove `x`; separately (fresh repo, same S2) add `x` version `2.0.0` with no steps.
- Assert: the first remove exits 1 with `effort S1 is at x.tests` and the folder is still there; while S1 is at `x.tests`, adding `x` version `2.0.0` with no steps exits 1 with `effort S1 is at x.tests, which the new version drops or moves` and `snap(root)` is unchanged; once S1 is abandoned (`nio flow abandon`), the remove is not refused by it; the second remove exits 0; in both cases S2's two files are byte-equal to the snapshot and `nio flow next S2` prints `state: tasking`.

### TC-45 Only web-first assertion failures count as a missing feature (AC-45; integration) [agent]
- File: `tests/test_extensions.py:test_e2e_check_failure_kinds` (new)
- Covers: CT-15
- Setup: `e2e_spec(root, ["AC-1"])`; six reports from `npx_stub`: `failed` with `Error: expect(page).toHaveTitle(expected) failed`; `failed` with the ANSI-coloured `\u001b[31mError: \u001b[39mexpect(\u001b[2mpage\u001b[22m).toHaveTitle(\u001b[32mexpected\u001b[39m) failed`; a top-level error `SyntaxError: Unexpected token` in `e2e/AC-1.spec.ts`; a top-level error `Error: Cannot find module './nope'`; status `timedOut` with `Test timeout of 30000ms exceeded.`; `failed` with `Error: expect(received).toBe(expected)`.
- Action: run the check on each.
- Assert: the first two exit 0; the others exit 1 with `setup error: e2e/AC-1.spec.ts: SyntaxError`, `setup error: e2e/AC-1.spec.ts: Error: Cannot find module`, `AC-1 AC-1 shows the page: fails on Test timeout of 30000ms exceeded., not on a web-first assertion`, `AC-1 AC-1 shows the page: fails on Error: expect(received).toBe(expected), not on a web-first assertion`.

### TC-46 Status keeps its speed with three extensions (AC-46; integration) [agent]
- File: `tests/test_flow.py:test_status_speed_with_three_extensions` (new)
- Covers: CT-5, CT-6
- Setup: `test_nfr3_status_speed`'s 20 efforts at `tasks_jury` with 50 history lines each, plus three added extensions, each with a step after `plan_jury`, a card and a hook.
- Action: `status_speed()` timing `nio flow status`.
- Assert: 20 rows; under `NIO_PERF=1` it takes under the same 2 seconds as `test_nfr3_status_speed`.

### TC-47 Commands past their timeout are stopped and recorded (AC-47; integration) [agent]
- File: `tests/test_extensions.py:test_timeouts_stop_commands` (new)
- Covers: CT-2, CT-8, CT-11
- Setup: `x` with `step("tests", check="sleep 5 # nio-t-check", timeout=1)` and hook `{"event": "step-passed", "command": "sleep 5 # nio-t-hook", "timeout": 1}`; S at `x.tests`; sources with `timeout` `0`, `1.5` and `"1"`.
- Action: `nio flow done x.tests S --by BY` (timed); then make the step pass (check `true`, added again) to fire the hook (timed); add each bad source.
- Assert: each call returns within 5 seconds; the `fail` line has `timed_out: true` and the output `check timed out after 1 seconds`; the `hook` line has `timed_out: true`; `pgrep -f nio-t-` finds nothing; each bad add exits 1 with `steps[0].timeout must be a whole number of seconds of at least 1`.

### TC-48 No extension, no change (AC-48; integration) [agent]
- File: `tests/test_extensions.py:test_no_extensions_changes_nothing` (new)
- Covers: CT-5, CT-6
- Setup: a repo with no `.nio/extensions`.
- Action: `flow.table(root)`; `uv run python tests/test_flow.py`.
- Assert: the five tables returned are `flow.STAGES`, `GATES`, `SKILL`, `INPUTS` and `EXIT` themselves (`is`); `tests/test_flow.py` exits 0 and `git diff main -- tests/test_flow.py` changes only by adding `test_status_speed_with_three_extensions`.

### TC-49 Half-done adds and removes, and broken extensions, can be cleared (AC-41; integration) [agent]
- File: `tests/test_extensions.py:test_half_states_are_recoverable` (new)
- Covers: CT-1, CT-4, CT-18
- Setup: `x` added; three copies of the repo: (a) `.nio/extensions/x/` deleted with its entry kept; (b) the entry deleted with the folder kept; (c) the manifest made invalid JSON by hand; plus (d) a leftover `.nio/extensions/.x.new/` beside a good `x`.
- Action: `nio flow next S` on each; then the command each error names; then `nio flow next S`.
- Assert: (a) and (b) print `extension x is half added or removed: run nio extensions remove x`; (c) prints `extension x changed since it was added`; `nio extensions remove x` exits 0 on (a), (b) and (c) and leaves neither folder nor entry; afterwards next exits 0; in (d) next exits 0 and `nio extensions list` shows only `x`.
