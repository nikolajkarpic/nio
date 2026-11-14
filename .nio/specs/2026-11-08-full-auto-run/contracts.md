---
slug: 2026-11-08-full-auto-run
retired: []                      # CT IDs removed from this plan; never reused
---
# Contracts: full-auto run

## Contracts

### CT-1 Grant auto with `nio flow start` (FR-1, FR-3, FR-4, FR-30, FR-31) [agent]
- Binding: `src/nio/flow.py:start` (existing)
- Kind: function
- Shape: `start(root, slug, by, auto=False)`; `nio flow start <slug> --auto --by human`. With `auto`, it first puts the work on the effort branch: `git switch nio/<slug>` when it exists, else `git switch -c nio/<slug>` (`implement.branch`), carrying the effort folder's uncommitted files along. Then, after the start or resume entry, it appends a `grant` line `{"kind": "grant", "from": <stage>, "to": <stage>}` whose `who` is `{"role": "human", "host": <host>, "model": <model>}`, and writes `auto: true`; prints `granted auto on <slug> at <stage> (branch nio/<slug>)` after its usual line. Every auto approval commit therefore lands on `nio/<slug>`, never on the base branch.
- Accepts: `by` must be exactly `human`; the spec draft must pass `spec.check(root, slug)` (not `--gate`); any stage from drafting on.
- Returns: `(0, lines)`.
- Fails: `by` other than `human` → `ValueError("only the human grants auto (--by human)")`, nothing written; `spec.check` errors → `ValueError("auto needs a spec draft that passes nio check spec: <first error>")`, nothing written; tracked changes outside `.nio/specs/<slug>/` (`git status --porcelain -- . ':!.nio/specs/<slug>'`) → `ValueError("commit or stash your other changes before auto switches to nio/<slug>")`, nothing written and no switch; auto already on → `(0, ["<slug> is already auto"])`, nothing written.
- Rules: "IF auto is asked for by anyone but the human (`--by` other than `human`) THEN THE SYSTEM SHALL refuse it and leave the flag off." (FR-30); "THE SYSTEM SHALL accept the grant of FR-1 at any stage from the end of drafting on" (FR-31). `who.host` is `claude-code` when `CLAUDECODE` is set, else `terminal`; `who.model` is `ANTHROPIC_MODEL` when set, else `unknown` (architecture.md, "Stored data"), so the grant's `who` always holds a non-empty host and model (AC-42).

### CT-2 Grant auto as drafting closes (FR-2, FR-3, FR-4, FR-30) [agent]
- Binding: `src/nio/flow.py:done` (existing)
- Kind: function
- Shape: `done(root, stage, slug, commit, human, by, auto=False)`; `nio flow done drafting <slug> --auto --by human`. With `auto`, the `pass` line drafting → researching (and its skips) is followed by CT-1's `grant` line (same `who`) in the same write, after CT-1's switch to `nio/<slug>` and with its refusals, and the state written has `auto: true`.
- Fails: `auto` on a stage other than drafting → `ValueError("--auto goes with nio flow done drafting, or nio flow start")`; `by` other than `human` → CT-1's refusal, nothing written; a failing drafting guard → its errors as today, nothing written.

### CT-3 Switch auto off (FR-32, FR-26) [agent]
- Binding: `src/nio/flow.py:manual` (new)
- Like: `src/nio/flow.py:park`
- Kind: function
- Shape: `manual(root, slug, by) -> (code, lines)`; `nio flow manual <slug> --by human`. Writes one `switch_off` line (`from`/`to` the stage where it stands) and `auto: false`; prints `switched <slug> to manual at <stage>`, then, for each gate whose ledger has a round, `restore <gate> as round <r> judged it: git cat-file -p refs/nio/<slug>/<gate>/<r>` (CT-22).
- Fails: `by` other than `human` → `ValueError("only the human switches auto off (--by human)")`; auto already off → `(0, ["<slug> is already manual"])`, nothing written.
- Rules: "a fix under way finishes its edits, and the next jury round waits for the human" (FR-32): nothing else changes; `stops` and `done` read `auto: false` from then on, so the driver's next `nio flow done` at a gate prints the human's commit command. Only this command turns auto off: `start`'s resume and `done --commit` keep `auto` as stored (FR-26).

### CT-4 The CLI flags and commands (FR-1, FR-2, FR-29, FR-32, FR-20) [agent]
- Binding: `src/nio/cli.py` (existing)
- Kind: cli
- Shape: `fs` (start) and `fd` (done) gain `--auto` (store_true); new subparsers under `fsub`: `manual <slug> --by`, `drive <slug> --by [--token] [--release]`, `pr <slug> --by`, each wired in the dispatch table like `start`.

### CT-5 The driver claim (FR-29, FR-38, NFR-2) [default]
- Binding: `src/nio/flow.py:drive` (new)
- Like: `src/nio/flow.py:lock`
- Kind: function
- Shape: `drive(root, slug, by, token=None, release=False, now=None) -> (code, lines)`; `nio flow drive <slug> --by "<role> / <host> / <model>" [--token <token>] [--release]`. Writes `.nio/specs/<slug>/driver.lock` as JSON `{"token", "by", "host", "at"}`; `lock()`'s `.gitignore` list gains `driver.lock*`. A call without `--token` asks for a new claim: it creates a token (`secrets.token_hex(8)`) and prints `driving: <slug>` and `token: <token>`; the driver passes that token on every later call. A takeover adds `took over from <by>, last refreshed <at>`. `--release --token <token>` removes the file when its token matches.
- Accepts: a claim whose `token` equals the caller's is refreshed: the new JSON is written to `driver.lock.<pid>.<hex>`, the claim re-read, and when it still holds the caller's token, `os.replace`d over it; a claim with `at` over 30 minutes old is taken over (rename to `driver.lock.<pid>.<hex>`, re-read, create with `O_EXCL`, as `lock` does); no claim → created with `O_EXCL`.
- Fails: a claim under 30 minutes old with another token, whatever its `by` → `(1, ["<slug> is driven by <by> on <host>, last refreshed <at>; stop"])`, file unchanged; a refresh whose re-read finds another token → the same refusal, the temp file removed. Of two concurrent creates, the `FileExistsError` one gets this refusal.
- Rules: "the claim is taken atomically, so of two drivers starting at once exactly one gets it; the driver refreshes its claim at each stage and at least every 10 minutes while it waits on a long command" (FR-38). No process test, per change request C-261108-mplt (pending; architecture.md). Writes no history line.

### CT-6 The stop list under auto (FR-18, FR-19, FR-33, FR-40, FR-25, FR-10, FR-11, FR-12, FR-34, FR-36, FR-37, FR-39, FR-35) [agent]
- Binding: `src/nio/flow.py:stops` (existing)
- Kind: function
- Shape: with `auto` on, in this order:
  1. the gate's ledger (spec, plan, tasks, or the open epic gate from `implement.open_gate` while implementing) composed `human` (`led["outcome"] == "human"`) and no `resume` line names this gate and round → `pause`, `why` = `"<gate> jury needs the human: " + the outcome's first reason`;
  2. the per-gate round pause as today, its limit `3 + 2 × (raise lines for that gate)`;
  3. the jury cap: `budgets.juries` when set, else `2 × gates`, where gates = the route's gates before implementing (`spec`, `plan`, `tasks` on full; `tasks` on lite) plus one per epic in `tasks.md` once it exists; plus `2 × (raise lines)`. `used` sums the epic ledgers' rounds too. Over the cap → `suspend` `cap`;
  4. `budgets.subagents` only when set (no default) → `suspend` `cap`;
  5. the change pause as today.
- Rules: "set the per-effort jury cap the stop list already enforces (flow-state FR-40) to 2 × the gates the effort's route runs" (FR-18); "IF config sets `budgets.juries` THEN THE SYSTEM SHALL use that value instead of FR-18's." (FR-19); "WHILE the auto flag is on and config sets no `budgets.subagents` THE SYSTEM SHALL cap no subagents" (FR-33). `cap(root, slug)` (new, in the same file) returns the number so tests read it.
- State: follows the spec's state table "Auto run" (running → waiting, running → suspended)

### CT-7 Resume raises the cap and keeps auto (FR-40, FR-26) [agent]
- Binding: `src/nio/flow.py:start` (existing)
- Kind: function
- Shape: once `entry["to"]` is known, when the state is `auto` and the pause `resumed` cleared is `suspended: cap` or `suspended: stuck`, the `resume` entry is followed by `{"kind": "raise", "from": <stage>, "to": <stage>, "evidence": {"gate": <GATES[entry["to"]]'s gate, the open epic gate while implementing, or "">, "rounds": 2, "cap": 2}}` in the same write. `resumed` keeps its return shape. `auto` is never changed by a resume.
- Rules: "give the stopped gate 2 more rounds and raise the effort's jury cap by 2, recording both in history" (FR-40).
- State: follows the spec's state table "Auto run" (suspended → running, waiting → running)

### CT-8 A risky spec still waits for the human's commit (FR-28) [research: RF-5]
- Binding: `src/nio/flow.py:risky` (existing)
- Kind: function
- Shape: unchanged: `done` refuses `--commit` from anyone but the human and makes no auto commit when `risky` is true, printing `nio flow done <stage> --commit <slug> --by human`. The driver stops on that line (CT-16).

### CT-9 `[auto]` is a provenance tag (FR-13, FR-14) [agent]
- Binding: `src/nio/spec.py:TAG` (existing)
- Kind: function
- Shape: `TAG` gains `auto`; `TAGS` reads `[human], [default], [agent], [auto], [research: RF-n], [derived: <IDs>] or [deferred: DF-n]`. `spec.check(gate=True)` treats `[auto]` as settled, as it does `[human]`, whatever `state.json` says.
- Rules: "let the spec gate pass with `[auto]` items once the spec jury has approved them, whether the auto flag is on or off; switching auto off reopens none of them" (FR-14).

### CT-10 The spec jury judges every `[auto]` default (FR-15) [agent]
- Binding: `src/nio/jury.py:_pack_text` (existing)
- Kind: function
- Shape: at the spec gate, when the spec has items tagged `[auto]`, each lens pack gains a line `Defaults the run chose (judge each): <IDs>`, the IDs in spec order.

### CT-11 Dispositions by the run (FR-9, FR-10, FR-11, FR-16) [agent]
- Binding: `src/nio/jury.py:_dispose_one` (existing)
- Kind: function
- Shape: `BY` gains `auto`; `DISPOSITIONS` gains `held`. `nio jury dispose <slug> <gate> J-n spec-fix|plan-fix --by auto --note "<what changed>"` and `nio jury dispose <slug> <gate> J-n held --by auto --note "<the [human] line ID, the cut, or the risk change>"`.
- Fails: `--by auto` while the effort's `auto` is false → `ValueError("--by auto needs the effort's auto flag on")`; `held` with any `by` but `auto` → `ValueError("held is the run's: --by auto")`; `--by auto` with `accepted-risk`, `out-of-scope` or `overruled` → the existing human-only refusal.
- Rules: `held` leaves `status: disposed`, so the human may re-dispose it (`--by human`), as they may any disposed finding. A re-disposition keeps the one before it in the finding's `was` field, `{"disposition", "by", "note"}`, so the report still lists what the run did (CT-14).

### CT-12 The gate composer under auto (FR-9, FR-16, FR-17, FR-34, FR-39) [agent]
- Binding: `src/nio/jury.py:composed` (existing)
- Kind: function
- Shape: `composed(root, slug, gate, led, current, rejected=(), auto=False)`; `check` passes `flow.load(root, slug)[0]["auto"]`. Under auto, before `compose`'s own reading:
  - minors are left out of `live` at every gate (as at an epic's gate today) and never reject or hand over;
  - a blocker or major with `validation: pending` whose ID is in `led["asked"][run]` for a run whose refuter output is in `led["collected"]` → `human`, `["no refuter verdict: J-n", ...]`;
  - a CT-13 hit while `current` differs from the judged version → `human` with CT-13's lines;
  - where `compose` returns `human` with "one list for the human", → `rejected` with `["unresolved: J-a, J-b"]`, so the fixer acts.
  The final fix check's flags, a finding failed 2 rounds, and noted majors stay `human` as today (FR-34).
  In every mode, auto or not, `compose` reads a finding disposed `held` as handed over: outcome `human`, `["held for the human: J-n: <note>", ...]`, until the human re-disposes it.
  A CT-13 hit stops counting once a `resume` line in history names this gate and the ledger's round (`evidence.waiting.gate` and `.round`, as `resumed` writes them): the human resumed the effort after seeing it, so `composed` falls through to `compose`'s own reading (`rerun` on the changed artefact).
- Rules: "WHILE the auto flag is on, WHEN a jury round ends THE SYSTEM SHALL leave minor and refuted findings unfixed, accept them as the gate's risk in place of the human, and list them in the run report." (FR-17)
- State: follows the spec's decision table "Fixer action on a finding"

### CT-13 The round check (FR-11, FR-12, FR-36, FR-37) [agent]
- Binding: `src/nio/jury.py:cuts` (new)
- Like: `src/nio/jury.py:changed`
- Kind: function
- Shape: `cuts(root, slug, gate, led) -> list[str]`. Reads the version the ledger's last round judged (`git cat-file -p <version>`, kept by `blob(..., write=True)`) and the artefact now (`artefact`); compares items by ID (`spec.sections`, `spec.items`). Returns one line per hit, in this order: `[human] line changed: <ID>`, `[human] line gone: <ID>`, `removed: <FR|AC|US ID>`, `non-goal added: <text, 60 chars>`, `risk changed: <old> → <new>`. `[]` at an epic's gate, when the ledger has no recorded version, or with no hit. A recorded version whose object `git cat-file` can't read (and no `refs/nio/<slug>/<gate>/<round>` holds) returns `["judged version missing: <blob>"]`, which composes `human` like any hit.
- Rules: "WHEN a fix round ends with any FR, AC or user story removed, or an entry added to Non-goals, compared with the previous round THE SYSTEM SHALL pause for the human, naming each" (FR-37); "WHEN a fix adds, removes or changes a flag in the spec's `risk:` list THE SYSTEM SHALL pause for the human before the next round, naming the change" (FR-36).

### CT-14 The run report (FR-22, FR-23, FR-17, FR-39) [default]
- Binding: `src/nio/flow.py:report` (new)
- Like: `src/nio/usage.py:report`
- Kind: function
- Shape: `report(root, slug) -> list[str]`, Markdown lines read only from `history.jsonl`, the ledgers (`jury/<gate>.json`, epics included) and `spec.md`:
  - `# Run report: <slug>`; `Granted: <grant line's at> by human (history line <n>)`;
  - `## Gates`: one line per `pass`/`override` line of a gate stage and per `epic` line: `- <gate>: <approved|closed>, round <r>, verdict <V-id> (history line <n>)`;
  - `## Accepted as risk`: refuted blockers first, then refuted majors, then open minors: `- J-n [<severity>] <title> (<gate>, refuted: <reason> | minor), verdict <V-id>`;
  - `## Fixed by the run`: each finding with `by: auto`, or whose `was.by` is `auto` (then also `, then <disposition> by the human`): `- J-n [<severity>] <title>: <note> (<gate>, verdict <V-id>)`;
  - `## Defaults the run chose`: each spec item tagged `[auto]`: `- <ID> <first 80 chars>, judged by spec verdict <V-id>`.
  `<n>` is the line's 1-based number in `history.jsonl`; `<V-id>` comes from `verdict()`.
- Rules: "THE SYSTEM SHALL name, next to each auto approval, fix and `[auto]` default in the run report, the verdict record or history line that allowed it." (FR-23)

### CT-15 Open the pull request (FR-20, FR-21, FR-24, FR-41) [default]
- Binding: `src/nio/flow.py:pr` (new)
- Like: `src/nio/flow.py:commit_gate`
- Kind: function
- Shape: `pr(root, slug, by) -> (code, lines)`; `nio flow pr <slug> --by "<...>"`. Refused unless the stage is `done` and `auto` is on. Runs `gh pr view nio/<slug> --json url,state`: an `OPEN` one → `(0, ["pull request open: <url>"])`, nothing else. Else `git push -u origin nio/<slug>`, then `gh pr create --head nio/<slug> --title "<spec title>" --body-file <tmp with report()>` → `(0, ["opened <url>"])`. Never runs `gh pr merge` or a git merge.
- Fails: `gh` missing, the push or `gh pr create` exiting non-zero → one `pause` line, `waiting: {"why": "pull request: <first stderr line>"}`, and `(1, talk lines + the report lines)`; commits and branch untouched. On resume (`nio flow start`) the effort stands at `done`, so the driver only runs `nio flow pr` again.
- Rules: "THE SYSTEM SHALL never merge the pull request of an auto run." (FR-21); "IF the pull request can't be opened THEN THE SYSTEM SHALL pause for the human, print the run report and keep the effort's commits, without retrying." (FR-24)
- State: follows the spec's state table "Auto run" (running → pr_open, running → pr_pending, pr_pending → pr_open)

### CT-16 The driver skill (FR-5, FR-6, FR-16, FR-25, FR-26, FR-27, FR-28, FR-35, NFR-2) [agent]
- Binding: `skills/auto/SKILL.md` (new)
- Like: `skills/implement/SKILL.md`
- Kind: file
- Shape: `@nio:auto`, input a slug whose `nio flow status` line says `auto`. Steps:
  1. `nio flow drive <slug>`, keeping the `token:` it prints; on refusal stop, telling the human which driver runs it.
  2. Loop: `nio flow drive <slug> --token <token>` (refresh), `nio flow next <slug> --by "<...>"`; when it names a skill, run that skill in a fresh subagent where the host has them, else in its own session; then the `done:` command it printed. At a gate the jury skill runs its `## Under auto` section (CT-21).
  3. Long jury rounds and test runs start in the background; wait for the completion notice, never polling; refresh the claim at least every 10 minutes while waiting.
  4. Stop on any `waiting_for_human`, `suspended`, or a printed `--commit` command: tell the human the reason and the command, in the "Talking to the human" shape; `nio flow drive <slug> --token <token> --release`.
  5. At `done`: `nio flow pr <slug>`; then release and report the URL. Never merge.
  The skill carries the "Talking to the human" block word for word and the flow-state line with the `--by human` ban (CT-19).
- Rules: "THE SYSTEM SHALL provide a driver that repeats `nio flow next`, the skill it names, and `nio flow done` until the effort pauses, is suspended or is done." (FR-5); "the manual skills keep #85 open" (FR-27).

### CT-17 The fixer card (FR-9, FR-10, FR-11) [agent]
- Binding: `src/nio/agents/fixer.md` (new)
- Like: `src/nio/agents/worker.md`
- Kind: file
- Shape: rendered as `nio-fixer` by `nio agents sync`; tools Read, Grep, Glob, Edit, Bash. Input: the slug, gate and the IDs the step listed as unresolved. For each refuter-confirmed blocker or major: when the fix would change or drop a `[human]` line, remove an FR, AC or user story, add a Non-goals entry or change `risk:`, edit nothing for it and run `nio jury dispose <slug> <gate> J-n held --by auto --note "<what it would touch>"`; else edit the gate's files and run `nio jury dispose <slug> <gate> J-n spec-fix|plan-fix --by auto --note "<what changed>"`. Minors and refuted findings: nothing. Never edit `state.json`, `history.jsonl` or a file outside the gate's.
- Rules: "IF a fix would change or drop a `[human]`-tagged line THEN THE SYSTEM SHALL pause for the human, naming the finding and the line." (FR-10)

### CT-18 The grill under auto (FR-7, FR-8) [agent]
- Binding: `skills/grill/SKILL.md` (existing)
- Kind: file
- Shape: a section `## Under auto` says: when `nio flow status` shows the effort `auto`, ask nothing; turn each open point into an item with the recommended answer, tagged `[auto]`, retag each `[default]` `[auto]`, remove `## Open points`, move each OP ID to `retired`, and log one `## Auto · <IDs> · <date>` entry in `grill.md` listing each choice and its reason.
- Rules: "WHILE the auto flag is on THE SYSTEM SHALL turn each open point into a default tagged `[auto]`, and retag each `[default]` item `[auto]`, instead of asking the human." (FR-7)

### CT-19 Agents never write `--by human` (FR-30) [agent]
- Binding: `skills/jury/SKILL.md` (existing)
- Kind: file
- Shape: the shared flow-state line, in every skill and agent card that has it (9 skills, 17 cards, and the two new files), gains the sentence `Never pass \`--by human\`: only the human grants or revokes auto, or approves a gate.`; the `RULE` text `tests/test_flow.py` checks is updated to match.

### CT-20 A passing gate under auto reads as working (FR-5) [agent]
- Binding: `src/nio/flow.py:where` (existing)
- Kind: function
- Shape: where `where` sets `waiting_for_human: approve <gate>` today (`ready == "pass"`), under `state["auto"]` with `risky(root, slug)` false it sets `status = "working"` and `command = f"nio flow done {stage} {slug}"`; `next` then prints `done: nio flow done <stage> <slug> --by ...`. A risky spec, or auto off, reads as today.
- Rules: "THE SYSTEM SHALL provide a driver that repeats `nio flow next`, the skill it names, and `nio flow done` until the effort pauses, is suspended or is done." (FR-5)

### CT-21 The jury skill under auto (FR-9, FR-17) [agent]
- Binding: `skills/jury/SKILL.md` (existing)
- Kind: file
- Shape: a section `## Under auto`: when `nio flow status` shows the effort `auto`, a `rejected` outcome goes to `nio-fixer` (CT-17) on the unresolved IDs; the session never disposes `--by agent`, never grills the human and never asks them to accept a risk; any `human` outcome ends the session with the reason, for the driver to stop on.
- Rules: "WHILE the auto flag is on, WHEN a jury round ends with refuter-confirmed blocker or major findings THE SYSTEM SHALL have the fixer edit the stage's files to fix each and start the next round." (FR-9)

### CT-22 Each judged version stays reachable (FR-12, FR-32) [agent]
- Binding: `src/nio/jury.py:collect` (existing)
- Kind: function
- Shape: where a round's version is stored (`blob(..., write=True)`), also `git update-ref refs/nio/<slug>/<gate>/<round> <blob>`, so `git gc` keeps it and CT-3 and CT-13 can read it.

## Data model
- **Auto grant** (spec Key entity) in `src/nio/flow.py:record` (existing) [agent]
  - a `grant` history line: `from`, `to` the stage; `who`: `{"role": "human", "host", "model"}`, `unknown` for what isn't detected. "the history line that switched the flag on: who, when, at which stage" (Key entity)
- **`[auto]` default** (spec Key entity) in `src/nio/spec.py:TAG` (existing) [agent]
  - a spec item ending `[auto]`. "a spec item the run chose in place of an open point, judged by the spec jury, listed in the report" (Key entity)
