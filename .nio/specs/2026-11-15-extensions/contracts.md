---
slug: 2026-11-15-extensions
retired: []                      # CT IDs removed from this plan; never reused
---
# Contracts: Extensions

Names used below: an extension's **stage** for step `<step>` of extension `<ext>` is `<ext>.<step>`; a step that
declares a gate adds a second stage `<ext>.<step>.jury`, whose jury gate is `<ext>.<step>` (ledger
`jury/<ext>.<step>.json`). Extension and step names match `[a-z][a-z0-9-]*`, so the dot always separates them.
`refused: <reason>` means exit 1, the reason printed, and nothing written.

## Contracts

### CT-1 Add an extension (FR-1, FR-2, FR-3, FR-4, FR-37) [agent]
- Binding: `src/nio/extensions.py:add` (new)
- Like: `src/nio/agents.py:load`
- Kind: cli
- Shape: `nio extensions add <path | git URL | name>` → `add(root, source) -> (code, lines)`. The argument is a path when it is an existing folder; a git URL when it contains `://`, starts `git@` or ends `.git`; else a name, looked up in `~/.nio/extensions/<name>` first (`records.home()`), then NIO's shipped set `src/nio/shipped/<name>` (FR-3). A git URL is fetched with `git clone --depth 1 <url> <temp>` through `records.git`; its version is the clone's `git rev-parse HEAD` (FR-2). The source folder holds `manifest.json` at its top. The manifest is checked with CT-2 against the other added extensions (the one being replaced left out); then the source is copied without `.git/` into `.nio/extensions/.<name>.new/`, the old copy (if any) renamed to `.<name>.old/`, the new one renamed to `<name>/`, `.nio/extensions/record.json` written through a temp file and `os.replace` with `<name>: {"source", "version", "hash"}` (Data model), and `.<name>.old/` deleted; folders starting with `.` are never extensions (CT-5). A replace reads the added extensions and the efforts' stages without CT-18's guard (`active(root, guard=False)`), so a changed or broken copy can still be replaced. Source is the path as given, the URL, `~/.nio/extensions/<name>`, or `shipped`; version is the manifest's `version`, the fetched revision, or for `shipped` NIO's package version (`importlib.metadata.version("nio")`). Adding from `.nio/extensions/<name>` itself re-checks it and re-records only its hash (the way to accept a hand edit, CT-5).
- Returns: `(0, lines)`: `added <name> <version> from <source>`, then `commands it brings (none run):` and one line per command, `check <ext>.<step>: <command>` and `hook <event>: <command>`, or `commands it brings: none`; last `commit .nio/extensions to share it with the team`.
- Fails: any CT-2 refusal; a replace whose new manifest lacks a stage, or gives it another `after`, that an effort not abandoned sits at → `refused: effort <slug> is at <ext>.<step>, which the new version drops or moves` (FR-7); no such folder, name or manifest → `refused: no extension at <source>` (or `named <name>`); `git clone` fails → `refused: git clone <url> failed: <its first error line>`. On any refusal `.nio/extensions` is byte-equal to before.
- Rules: "copies an extension and runs none of its commands; it prints every check and hook command the extension brings" (FR-37, D-261115-ggt2). Replacing keeps one copy (FR-4); it never touches history or state of any effort (FR-7).

### CT-2 Manifest check (FR-5, FR-11, FR-20, FR-22, FR-26, FR-39, FR-40, NFR-2) [agent]
- Binding: `src/nio/extensions.py:check` (new)
- Like: `src/nio/agents.py:check`
- Kind: function
- Shape: `check(folder, manifest, others, stages) -> list[str]`, the refusal reasons in this order, empty when it may be added; `others` are the other added extensions' manifests, `stages` the built-in stage order plus their stages. The manifest format, field by field, is the Data model's Manifest.
- Returns: reasons, the first printed by CT-1 as `refused: <reason>`:
  - FR-5: `manifest.json is missing` · `manifest.json is not JSON: <error>` · `manifest.json: missing field <path>` · `manifest.json: <path> must be <what>` · `manifest.json: unknown field <path>`, `<path>` like `steps[0].after`; a step's `skill` file and each card's `agents/<card>.md` must exist in the folder (`manifest.json: <path> names <file>, which isn't in the extension`).
  - FR-20: the keys `remove`, `skip`, `replace`, `reorder` and `before`, at the top or in a step → `<key> would change built-in <each built-in step or gate it names>: extensions only add steps`; a step named like a built-in stage → `step <name> would replace built-in <name>`; `after: done` → `step <name> can't follow done`.
  - FR-11: `step <name> follows <after>, which is neither a built-in step nor a step of an added extension`; a step whose `after` chain, through the other extensions' steps, never reaches a built-in stage → `step <name> follows <after>, which never reaches a built-in step: <the chain, e.g. a.s → b.t → a.s>`.
  - FR-40: a `plan_path` trigger on a step whose `after` comes before `plan_jury` in the stage order → `step <name>: trigger plan_path reads the plan, which isn't approved before plan_jury; it follows <after>`.
  - FR-22: `card <card> has the name of a shipped card` (shipped cards: the `*.md` names under `resources.files("nio").joinpath("agents")`, read directly, never through `agents.layers`, which reads the active extensions).
  - FR-39: `step <name> is already a step of extension <other>` · `card <card> is already a card of extension <other>`.
  - FR-26: `hook on <event>: NIO fires only step-passed, step-skipped, gate-approved, gate-rejected, epic-closed, waiting-on-human, effort-done`.
  - NFR-2: `manifest.json: <path>.timeout must be a whole number of seconds of at least 1`.
- Rules: "Extensions only add: no built-in step or gate can be removed, reordered or skipped" (Summary). The decision table "Add refused" orders the reasons.

### CT-3 List extensions (FR-6) [agent]
- Binding: `src/nio/extensions.py:listing` (new)
- Like: `src/nio/flow.py:status`
- Kind: cli
- Shape: `nio extensions list` → `(0, lines)`, per added extension in name order: `<name> · <version> · <source>`, then `  steps: <ext>.<step> (after <after>)[, ...]`, `  cards: <card>[, ...]`, `  hooks: <event>: <command>[; ...]`, each `none` when empty. No extension → `no extensions in .nio/extensions`.
- Fails: as CT-5 (a changed or broken extension is named, exit 1).

### CT-4 Remove an extension (FR-7, FR-39) [agent]
- Binding: `src/nio/extensions.py:remove` (new)
- Like: `src/nio/flow.py:abandon`
- Kind: cli
- Shape: `nio extensions remove <name>` first rewrites `record.json` without the entry (temp file and `os.replace`), then deletes `.nio/extensions/<name>/`; a name with an entry and no folder, or a folder and no entry, counts as added, so running it again clears a half-done add or remove. It reads the extensions and the efforts' stages without CT-18's guard (`active(root, guard=False)`), so a changed or broken extension can be removed → `(0, ["removed <name>", "commit .nio/extensions to share it with the team"])`.
- Fails: not added → `refused: no extension named <name> in .nio/extensions`; an effort not abandoned whose current stage (`flow.where`) is one of its stages → `refused: effort <slug> is at <ext>.<step>; finish that step, or abandon the effort (nio flow abandon), first` (an abandoned effort is frozen where it was and never blocks a remove); another added extension's step follows one of its stages → `refused: <other>.<step> follows <name>.<step>`. The same FR-39 check refuses a CT-1 replace whose new manifest drops a stage another extension's step follows.
- Rules: "history lines of the removed step stay as written, and an effort past a removed or replaced step is not sent back" (FR-7): no effort file is written.

### CT-5 Active extensions (FR-8, NFR-3) [agent]
- Binding: `src/nio/extensions.py:active` (new)
- Like: `src/nio/agents.py:load`
- Kind: function
- Shape: `active(root, guard=True) -> list[dict]`: the manifests under `.nio/extensions/`, each with `dir` (its folder), in name order, folders starting with `.` left out; with `guard`, CT-18 runs first; only `.nio/extensions` counts (FR-8: the shipped set and `~/.nio/extensions` are only sources for CT-1). No `.nio/extensions` folder → `[]` without reading anything else.
- Rules: "treat an extension as active only once it is in the project's `.nio/extensions`" (FR-8).

### CT-18 The hand-edit guard (FR-21, FR-38) [agent]
- Binding: `src/nio/extensions.py:verify` (new)
- Like: `src/nio/agents.py:check`
- Kind: function
- Shape: `verify(root, manifests)`, run by `active(root)` with `guard`.
- Fails (`ValueError`, which every `nio flow` command and `nio extensions list` print as `error: <message>` with exit 1, moving no effort): a folder whose hash differs from `record.json`'s → `extension <name> changed since it was added: review the change, then run nio extensions add .nio/extensions/<name> (or add it again from its source)` (FR-38); a folder with no entry, or an entry with no folder (a half-done add or remove) → `extension <name> is half added or removed: run nio extensions remove <name>, or add it again from its source`; a manifest that fails CT-2 against the others → `extension <name> breaks the add-only rule: <CT-2 reason>` (FR-21).

### CT-6 The flow's stage table per project (FR-9, FR-10, FR-13, FR-18, FR-19, NFR-1, NFR-3) [agent]
- Binding: `src/nio/flow.py:table` (new)
- Like: `src/nio/flow.py:skips`
- Kind: function
- Shape: `table(root) -> (stages, gates, skill, inputs, exit)`. With `extensions.active(root) == []` it returns the module's `STAGES`, `GATES`, `SKILL`, `INPUTS` and `EXIT` themselves (NFR-3). Else it walks the built-in order and, after each stage, inserts the steps whose `after` names it, in extension-name order and, within one extension, manifest order (FR-10); after a step comes its `.jury` stage when it declares a gate, then the steps that follow it; a step left unplaced (its `after` chain never reaches a built-in stage, which CT-2 refuses) raises `ValueError` naming it. `stages[<ext>.<step>] = (next, None)`; `stages[<ext>.<step>.jury] = (next, "<ext>.<step>")`; `gates[<ext>.<step>.jury] = ("<ext>.<step>", "nio: approve <ext>.<step>")`; `skill[<ext>.<step>]` is the skill file's path from the repo root, `skill[<gate stage>] = "@nio:jury"`; `inputs` of a step are `spec.md` and the plan files; `exit[<ext>.<step>] = "its check exits 0: <command>"`, `exit[<gate stage>] = "the <ext>.<step> jury approved, or the human closed it with a reason"`. Every read of those five tables in `flow.py` (`where`, `done`, `moves`, `guard`, `stops`, `approvals`, `jury_files`, `next_step`, `stage_arg`) and at `cli.py:282` goes through `table(root)` (RF-13).
- Rules (`where`): an extension stage is in an effort's flow only once reached: the newest `pass`, `override` or `skip` line leaving the stage before it in the table has `to` equal to it. An unreached extension stage is passed over, writing nothing, so adding an extension never moves an effort already past its spot, and removing one leaves `state.json` and `history.jsonl` untouched (FR-7). A reached step is passed once a `pass`, `skip` or `override` line from it follows; until then it is the effort's stage, `ready` None. A reached gate stage is judged by the existing gate rules (ledger, approval commit, override, rejection back to its step); its guard is the `spec_jury` rule on its own ledger: `pass` when the standing is `approved` with no finding open, `closed` when the human closed it, else `fail` naming the outcome, never `plan.approved` or `tasks.approved`. `approvals` maps each `nio: approve <ext>.<step>` commit to its gate stage through the table's gates.
- `nio flow next` at an extension step prints `skill: <path>` and `next: run the skill at <path>` (FR-13); `nio flow status` names the stage `<ext>.<step>` in its row, and `nio flow show`'s timeline, the stage list the status pane shows (RF-16), holds each pass and skip line from or to it in history order (FR-18).
- Under auto an extension gate stage is approved by the driver's `nio flow done` exactly as `GATES` entries are today (RF-9), and the stop list reads its ledger the same way (FR-19).
- State: follows the spec's state table "Extension step" (reached → active, reached → skipped).

### CT-7 Trigger rules and the recorded skip (FR-12, FR-14, FR-15) [agent]
- Binding: `src/nio/extensions.py:applies` (new)
- Like: `src/nio/flow.py:moves`
- Kind: function
- Shape: `applies(root, slug, step) -> (bool, text)`. No `trigger` → `(True, "")`. `{"spec_level": "<level>"}` → true when some AC in spec.md is at that level, read with CT-17 (RF-10); text `the spec has no AC at Level: <level>`. `{"plan_path": "<path>"}` → true when a backticked path in a contracts.md `Binding:` line or a tests.md `File:` line starts with `<path>` (RF-5); text `the plan touches no file under <path>`. A missing spec or plan file reads as not applying.
- Rules: `flow.moves` adds, for each extension step reached whose trigger doesn't apply, `{"kind": "skip", "from": <ext>.<step>, "to": <next>, "reason": "skipped: <text>"}`, and the same line for its `.jury` stage, then goes on (FR-12). A step whose trigger applies is the stage `done` moves to (FR-13).
- State: follows the spec's state table "Extension step" (reached → skipped).

### CT-8 An extension step's check at `nio flow done` (FR-16, FR-17, NFR-2) [agent]
- Binding: `src/nio/flow.py:guard` (existing)
- Kind: function
- Shape: for a stage `<ext>.<step>`, the guard runs the step's `check` with `implement.run(root, command, timeout, env)` (RF-14; `run` gains `env`, extra variables: `NIO_SLUG`, `NIO_STAGE` and `NIO_EXTENSION_DIR`, the extension's folder), `timeout` the step's, else 300. Exit 0 → `pass`. Else `fail` with output `check failed: exit <code>` or `check timed out after <timeout> seconds`, then the last 50 lines of its output.
- Returns: `done` writes, on a failing extension check, one `fail` line `{"from": <stage>, "to": <stage>, "evidence": {"code": <code or null>, "timed_out": bool, "tail": <the 50 lines>}}` whether or not auto is on (FR-17), exits 1 and prints the output; the stuck rule under auto counts it as today. On exit 0 it writes `pass` to the next stage (or its gate stage) and CT-7's skips after it.
- Rules: "pass the step only when it exits 0" (FR-16); "stop a hook or check command that runs longer than its timeout, 300 seconds unless the manifest sets another, and record it as failed" (NFR-2): the process group is killed (RF-14).
- State: follows the spec's state table "Extension step" (active → checking → judging | active).

### CT-9 An extension step's jury gate (FR-19, FR-23) [agent]
- Binding: `src/nio/jury.py:plan` (existing)
- Kind: function
- Shape: the jury reads its gates' files and core lenses through `jury.gates(root) -> {gate: (files, core lenses)}`: `GATES` and `CORE` plus, per extension step with `gate: {"lenses": [...]}`, gate `<ext>.<step>` with files `[<step's output>, "spec.md"]` and the step's lenses as core. `gate_arg`, `plan`, `next`, `load` and the packs use it (RF-19). At an extension gate, `plan` checks only that the output file exists (`no <output> yet: run <ext>.<step> first`), adds no risk-flag lens, and names a lens card missing from `agents.load` as for any gate. Approval, round cap, rejection and closing by the human are the existing gate rules; a rejection sends the effort back to `<ext>.<step>` through CT-6's back pointer (FR-23).
- Rules: "run that gate with the extension's lens cards and move on only once the gate is approved as the built-in gates are; a rejection sends the effort back to the step" (FR-23).
- State: follows the spec's state table "Extension step" (judging → passed | active).

### CT-10 Extension cards in the card layers (FR-22, FR-24) [agent]
- Binding: `src/nio/agents.py:layers` (existing)
- Kind: function
- Shape: `layers(root)` returns shipped, then each active extension's `agents/` folder in name order, then personal, then team. `nio agents sync` renders an extension's cards for each host as it does shipped cards, as `nio-<card>`. A team card in `.nio/agents` still replaces a card by name; an extension card named like a shipped one never gets this far (CT-2).

### CT-11 Hooks on NIO events (FR-25, FR-26, FR-27, NFR-2, NFR-3) [agent]
- Binding: `src/nio/extensions.py:fire` (new)
- Like: `src/nio/implement.py:run`
- Kind: event
- Shape: `fire(root, slug, event, stage, who, run)` runs every active extension's hooks on `event`, in extension-name order then manifest order (FR-25), each with `implement.run(root, command, timeout, env)`, `env` `NIO_EVENT`, `NIO_SLUG`, `NIO_STAGE` and `NIO_EXTENSION_DIR`; timeout the hook's, else 300. It appends one `hook` line per hook through `flow.record`: `{"from": stage, "to": stage, "evidence": {"extension", "event", "command", "code", "timed_out", "tail": <last 20 lines>}}`. It never raises for a hook's result, and the stage the flow moved to stands (FR-27).
- Fired once a command's writes, and its approval commit when it makes one, have succeeded, outside the effort's lock: `flow.done`, `flow.next_step`, `flow.epic_done` and `implement.finish` end by calling `extensions.after(root, slug, n, old_state)`, `n` the history's length before the command, which fires from the lines added since; a command that fails or rolls back fires nothing. A `pass` or `override` line from a gate stage → `gate-approved`, then `step-passed`; a `pass` from an extension step to its own `.jury` stage → nothing (the step is only judging); from any other stage → `step-passed`; a `skip` from a step → `step-skipped` (the `skip` of its `.jury` stage fires nothing); a `pass`/`override` to `done` → `effort-done` (after its own event); an `epic_test` line with `passed: true` or an `epic` line → `epic-closed`; a state whose `waiting` or `pause` is set where the state before had neither → `waiting-on-human`. `hook` lines fire nothing. `jury` fires `gate-rejected` when it records a round's outcome `rejected`. With no active extension nothing runs and nothing is written (NFR-3).
- Rules: "a failing hook never stops or blocks the flow" (FR-27).

### CT-12 A task covering an e2e AC names its test (FR-31) [agent]
- Binding: `src/nio/tasks.py:check` (existing)
- Kind: function
- Shape: on a full spec, a task whose `Serves:` holds an AC at `Level: e2e` (CT-17) must cite in `Test:` a TC aimed at that AC (RF-21); else the error `T-n serves AC-n (Level: e2e) but its Test: cites no TC aimed at it`.

### CT-13 Playwright as a known runner (FR-31, FR-32, FR-34) [agent]
- Binding: `src/nio/evidence.py:one_test` (existing)
- Kind: function
- Shape: `one_test(suite, file, name, root=None)`: when `root` holds a `playwright.config.ts`, `.js` or `.mjs` and `file` ends `.spec.ts`, `.spec.js` or `.spec.mjs`, the command is `npx playwright test <file> -g <shlex.quote(re.escape(name))>` whatever the suite's runner; else as today. `implement.RUNNERS` gains `playwright`: match `\bplaywright test\b`, error lines `Process from config.webServer was not able to start` and `from config.webServer` (RF-7), none line `No tests found`. `implement.epic_tests` passes `root`; the Playwright TCs become one command, `npx playwright test <each file once> -g <shlex.quote("|".join(re.escape(name)))>`, never split at a space; the other TCs are joined as today; the two commands are joined with ` && ` (RF-17), so an epic covering an e2e AC runs its e2e test (FR-31). `evidence.collect` runs every Playwright test of tests.md alone through `one_test` at the pr gate and records its own result, never reading it from the suite's output (RF-18), so the pr evidence lists each e2e test and its result (FR-34).
- Rules: "run the tests with Playwright, whose config in the project names the app's start command and ready address" (FR-32): NIO starts no app itself.

### CT-14 The shipped e2e extension (FR-28, FR-29, FR-35, FR-36) [agent]
- Binding: `src/nio/shipped/e2e/manifest.json` (new)
- Like: none: the first shipped extension; it uses only the user-facing format of CT-2
- Kind: file
- Shape: `{"name": "e2e", "version": "1.0.0", "steps": [{"name": "tests", "after": "plan_jury", "skill": "skills/e2e/SKILL.md", "card": "e2e-tester", "output": "e2e.md", "trigger": {"spec_level": "e2e"}, "check": "python3 \"$NIO_EXTENSION_DIR/check.py\"", "timeout": 900}], "cards": ["e2e-tester"], "hooks": []}`. Beside it: `skills/e2e/SKILL.md` and `agents/e2e-tester.md` (CT-16), `check.py` (CT-15). `pyproject.toml` ships `src/nio/shipped` as package data, as `src/nio/agents` is (RF-8).
- Rules: "build the shipped e2e extension only from the user-facing extension format, with no NIO code that names it" (FR-35): no file under `src/nio/` outside `src/nio/shipped/e2e/` holds `shipped/e2e`, `e2e-tester` or `e2e.tests`.

### CT-15 The e2e check (FR-30, FR-33, FR-41) [agent]
- Binding: `src/nio/shipped/e2e/check.py` (new)
- Like: `src/nio/implement.py:wrong_reason`
- Kind: cli
- Shape: `python3 check.py`, standard library only, in the repo root, reading `NIO_SLUG`. The e2e ACs are spec.md's ACs whose own `Level:` is `e2e`, read as CT-17 reads it (the script imports no NIO code); each needs a tests.md TC aimed at it whose `File:` names `<file>:<name>`, the file existing and holding a test whose title holds the AC ID and `<name>` (else `AC-n has no e2e test`, exit 1). It runs `npx playwright test <those files> --reporter=json` with `PLAYWRIGHT_JSON_OUTPUT_NAME` set to a temporary file (RF-22) and reads the report:
  - the output holds a `config.webServer` start failure (RF-7) → `setup error: the app didn't start: <that line>`, exit 1, no test counted (AC-31);
  - a report-level error (a syntax or import error) → `setup error: <file>: <its first line>`, exit 1;
  - a test that passed → `<AC> <title>: passes before any code is written`, exit 1;
  - a failed test whose first error message, ANSI codes and a leading `Error: ` removed, starts `expect(page)` or `expect(locator)` → failing because the feature is missing (FR-41);
  - any other failed or timed-out test → `<AC> <title>: fails on <its first error line>, not on a web-first assertion`, exit 1;
  - else exit 0 with `e2e: <n> tests fail on their assertions, as they should before implementation`, and per test its trace and screenshot paths from the report's attachments, `trace: <path>`, `screenshot: <path>` (FR-33).
- Rules: "count an e2e test as failing because the feature is missing only when Playwright reports it failed on a web-first assertion (`expect(page)` or `expect(locator)`) with the app started; any other failure is a setup error that fails the e2e check and names the test" (FR-41).

### CT-16 The e2e skill and tester card (FR-29, FR-32, FR-33, FR-36) [agent]
- Binding: `src/nio/shipped/e2e/skills/e2e/SKILL.md` (new)
- Like: `skills/tasks/SKILL.md`
- Kind: file
- Shape: plain markdown with the "Talking to the human" block word for word; no host-only tool name. Steps: read the spec's ACs at `Level: e2e` and tests.md's TCs aimed at them; start the `e2e-tester` card (`src/nio/shipped/e2e/agents/e2e-tester.md`, tier strong, effort med, tools read, edit, shell) once with them; it writes one Playwright test per such AC at its TC's `File:`, titled `<AC-ID> <the File's test name>`, asserting the AC's Observable with web-first assertions only, and makes sure `playwright.config` names `webServer` (`command`, `url`), `use.trace: 'retain-on-failure'`, `use.screenshot: 'only-on-failure'`, adding only keys that are missing and never changing a value already set (an `outputDir` already set is kept, else `test-results`), and that the `outputDir` is in `.gitignore` (FR-32, FR-33); it lists the tests in `e2e.md` next to the spec (the step's output). Then run the `done:` command `nio flow next` printed; stop when it passes, or hand its output back to the human.
- Rules: "keep every shipped extension's skill plain markdown that names no host-only tool and carries the "Talking to the human" block" (FR-36).

### CT-17 An AC's level is its own `Level:` (FR-14, FR-31) [agent]
- Binding: `src/nio/spec.py:level` (new)
- Like: `src/nio/spec.py:cites`
- Kind: function
- Shape: `level(block) -> str | None`: the last `Level: <level>` of an AC's block, the one after its `Observable:`, so a Given or When that quotes `Level: e2e` (as AC-13 does) isn't read as the AC's level. `plan.check`'s TC level check, CT-12 and CT-7 read the level through it.

## Data model
- **Extension record** (spec Key entity) in `src/nio/extensions.py:add` (new) [agent]
  - `.nio/extensions/record.json`: `{<name>: {"source": str, "version": str, "hash": str}}`, committed. `hash`: sha256 over every file under `.nio/extensions/<name>/`, sorted by path, each as `<relative path>\0<bytes>`. "It also holds a hash of the copied files (FR-38)." (Key entities)
- **Manifest** (spec Key entity) in `src/nio/extensions.py:check` (new) [research: RF-12]
  - `manifest.json`: `name` (str, required, the folder's name once copied), `version` (str, required), `steps` (list, required), `cards` (list of card names, required, each `agents/<card>.md`), `hooks` (list, required); nothing else.
  - a step: `name`, `after`, `skill`, `check` (str, required); `card`, `output` (str; `output` required with `gate`); `trigger` (`{"spec_level": "unit" | "integration" | "e2e"}` or `{"plan_path": str}`); `timeout` (whole seconds ≥ 1); `gate` (`{"lenses": [card names of this extension]}`).
  - a hook: `event` (one of FR-26's seven), `command` (str), `timeout` (whole seconds ≥ 1, optional).
- **Hook** (spec Key entity) in `src/nio/extensions.py:fire` (new) [agent]
  - its result: a `hook` history line, as CT-11's Shape. "record its extension, event, exit code and the tail of its output in the effort's record" (FR-27)
- **Extension step** (spec Key entity) in `src/nio/flow.py:done` (existing) [agent]
  - its check's failure: a `fail` history line with `code`, `timed_out`, `tail`, as CT-8's Returns. "record the exit code and the tail of its output" (FR-17)
- **Extension step** (spec Key entity) in `src/nio/shipped/e2e/skills/e2e/SKILL.md` (new) [agent]
  - the e2e step changes the target project's `playwright.config.*` (missing keys only) and `.gitignore` (its `outputDir`), and writes `e2e.md` and the TCs' test files; nothing else.
