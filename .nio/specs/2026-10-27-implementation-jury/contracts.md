---
slug: 2026-10-27-implementation-jury
retired: []                      # CT IDs removed from this plan; never reused
---
# Contracts: implementation jury

## Contracts

### CT-1 Epic subject and the refusal (FR-1, FR-2) [derived: FR-1]
- Binding: `src/nio/jury.py:epic_gate` (new)
- Like: `src/nio/tasks.py:finished`
- Kind: function
- Shape: `epic_gate(root, slug, gate) -> "E-n"`
- Accepts: a gate name `implementation-E-n`; the epic and its tasks from `implement.tasks_of`, states from `implement.status`
- Returns: the epic's ID when every task, fix tasks included, is `done`
- Fails: the epic isn't in `tasks.md`, or the name is a bare `implementation` → ValueError saying the subject must be an epic; no ledger is written
- Fails: a task isn't done → ValueError naming the task's ID; no ledger is written
- Rules: "WHEN asked to jury an epic from the tasks stage whose tasks the implement stage has all finished THE SYSTEM SHALL start the implementation gate on that epic." (FR-1)
- Rules: "IF the subject is not an epic from the tasks stage, or any of its tasks is not finished, THEN THE SYSTEM SHALL refuse to start the gate and name what is missing." (FR-2)
- State: follows the spec's state table epic at the implementation gate

### CT-2 Run in a throwaway copy (FR-40, FR-41) [derived: FR-40]
- Binding: `src/nio/evidence.py:in_copy` (new)
- Like: `src/nio/implement.py:run`
- Kind: function
- Shape: `in_copy(root, commit, commands, limit) -> [{"command", "result", "output", "cut"}]`
- Accepts: the epic's last commit; commands only from config, `tests.md` and `quickstart.md`; `tests.setup` first when set; `limit` from `jury.run_timeout`, 600 when unset
- Returns: one entry per command, `result` is `passed`, `failed` or `not configured`; output over 200 KB keeps its first and last 100 KB and a `cut N bytes` line
- Fails: the time limit passes → `failed`, with "timed out after" and the limit, and the next command runs
- Shape of the copy: a `git clone --local --no-checkout` into a `tempfile.TemporaryDirectory`, detached at the commit, with its `origin` remote removed, so it shares no refs, config or hooks with the human's repo and can't push to it; removed when the runs end, however they end
- Fails: the clone can't be created → ValueError naming git's error, and nothing runs
- Rules: "WHEN the CLI runs the epic's tests, lint and type checks, attacks, journey runs or a juror's requested run THE SYSTEM SHALL run it in a throwaway copy of the repo at the epic's final commit, stop it after a time limit (10 minutes by default, `jury.run_timeout` in config) and record a run that times out as failed." (FR-40)
- Rules: "WHEN a run's output exceeds 200 KB THE SYSTEM SHALL keep its first and last 100 KB in the results and say how much was cut." (FR-41)

### CT-3 Start the gate: `nio jury evidence` (FR-3, FR-6, FR-7, FR-11, FR-12, FR-42) [derived: FR-3]
- Binding: `src/nio/evidence.py:collect` (new)
- Like: `src/nio/implement.py:suite`
- Kind: cli
- Shape: `nio jury evidence <slug> E-n --run <run>`
- Accepts: an effort's slug, an epic ID, a run from `nio run`. It takes no command text
- Returns: writes `.nio/runs/<run>/results.json`, sends the findings of CT-4, CT-6 and a failed check to CT-20, and prints the path; `tests.lint` or `tests.typecheck` unset prints `not configured` and the gate goes on (architecture.md)
- Fails: the epic isn't finished → the CT-1 error, exit 1
- Fails: a suite crash before any test ran → recorded in the results; the gate goes on (AC-17)
- Rules: "WHEN the gate starts THE SYSTEM SHALL run the project's tests and record, for each test, whether it ran and passed." (FR-3)
- Rules: "THE SYSTEM SHALL take as evidence only what it observed (a run it made, code it read), never a task's status or a worker's claim." (FR-6)
- Rules: "WHEN the gate starts THE SYSTEM SHALL re-check every task of the epic, whatever its status." (FR-7)
- Rules: "WHEN the gate starts THE SYSTEM SHALL run the project's lint and type checks and record their results." (FR-11)
- Rules: "WHEN the gate starts THE SYSTEM SHALL run the spec's misuse lines as scripted attacks and the per-journey runs in quickstart.md, and record their results." (FR-12)
- Rules: "IF the epic's lint or type check fails THEN THE SYSTEM SHALL record a finding at severity major naming the failing check and its first errors." (FR-42)

### CT-4 Phantom completion (FR-6, FR-7, FR-8) [derived: FR-6]
- Binding: `src/nio/evidence.py:phantoms` (new)
- Like: `src/nio/implement.py:review`
- Kind: function
- Shape: `phantoms(root, tasks, base, head) -> [finding]`
- Accepts: every task of the epic whatever its status; `base` is the parent of the epic's first `T-n:` commit, `head` its last
- Returns: one major finding per missing file, file outside the diff, undefined symbol or symbol with no word-boundary hit outside its own definition, by search of tracked files; a symbol whose only other hits are in strings or comments is CT-5's uncertain hint
- Rules: "THE SYSTEM SHALL take as evidence only what it observed (a run it made, code it read), never a task's status or a worker's claim." (FR-6)
- Rules: "WHEN the gate starts THE SYSTEM SHALL re-check every task of the epic, whatever its status." (FR-7)
- Rules: "WHEN the gate starts THE SYSTEM SHALL check, for each file and symbol the epic's tasks name, that the file exists and is in the epic's diff and that the symbol is defined and referenced outside its own definition." (FR-8)

### CT-5 Hints for every pack (FR-9, FR-13, FR-36, FR-39) [derived: FR-9]
- Binding: `src/nio/evidence.py:hints` (new)
- Like: `src/nio/implement.py:wrong_reason`
- Kind: function
- Shape: `hints(root, base, head) -> [{"kind", "file", "name", "line", "interpretive"}]`
- Accepts: the epic's diff
- Returns: one hint per stub, uncertain reference, no-assertion test, and changed or removed assertion line; hints never enter the ledger
- Rules: "WHEN a symbol in the diff has an empty body or only a TODO THE SYSTEM SHALL flag it as a possible stub, marked interpretive, as a hint in every lens pack, not as a ledger finding; a lens that confirms it raises the finding." (FR-9)
- Rules: "IF a check can't tell whether something is complete THEN THE SYSTEM SHALL flag it rather than pass it, as a hint in every lens pack, not as a ledger finding; a lens that confirms it raises the finding." (FR-13)
- Rules: "IF the epic's diff changes or removes an assertion line in an existing test THEN THE SYSTEM SHALL flag it with zero model calls, as a hint in every lens pack, and the correctness lens SHALL judge whether the change weakened the test; only a confirmed weakening is tampering (FR-10)." (FR-36)
- Rules: "WHEN a test in the epic's diff has no assertion THE SYSTEM SHALL flag it with zero model calls, as a hint in every lens pack, not as a ledger finding." (FR-39)

### CT-6 Test tampering (FR-10) [derived: FR-10]
- Binding: `src/nio/evidence.py:tampering` (new)
- Like: `src/nio/implement.py:changed`
- Kind: function
- Shape: `tampering(root, base, head) -> [finding]`
- Accepts: the epic's diff; skip markers per known runner
- Returns: a major finding per deleted or newly skipped test, marked `tampering`; only `--by human` may accept it (CT-20)
- Rules: "IF the epic's diff deletes or skips a test, or the correctness lens confirms an FR-36 flag weakened a test, THEN THE SYSTEM SHALL record it as test tampering at severity major, whatever reason is given; only the human may accept it as risk, with a reason." (FR-10)

### CT-7 Run results file (FR-3, FR-11, FR-12, FR-41) [derived: FR-3]
- Binding: `src/nio/evidence.py:RESULTS` (new)
- Like: `src/nio/jury.py:load`
- Kind: file
- Shape: `.nio/runs/<run>/results.json`: `{"commit", "tests": [{"name", "file", "line", "result"}], "checks", "attacks", "journeys", "hints", "requests", "evidence": [{"ac", "file", "line", "result"}]}`
- Accepts: written only by CT-3, CT-11 and CT-21; a later `nio jury evidence` on the same run keeps `requests`
- Returns: what packs and collect read
- Rules: "WHEN the gate starts THE SYSTEM SHALL run the project's tests and record, for each test, whether it ran and passed." (FR-3)
- Rules: "WHEN the gate starts THE SYSTEM SHALL run the project's lint and type checks and record their results." (FR-11)
- Rules: "WHEN the gate starts THE SYSTEM SHALL run the spec's misuse lines as scripted attacks and the per-journey runs in quickstart.md, and record their results." (FR-12)
- Rules: "WHEN a run's output exceeds 200 KB THE SYSTEM SHALL keep its first and last 100 KB in the results and say how much was cut." (FR-41)

### CT-8 Lens plan for an epic (FR-14, FR-15, FR-16) [derived: FR-14]
- Binding: `src/nio/jury.py:plan` (existing)
- Kind: function
- Shape: `nio jury plan <slug> implementation-E-n [--pick <lens,lens>]`; `IMPL_LENSES` in `jury.py`, the spec's trigger table row for row, used at this gate instead of `spec.LENSES`
- Accepts: the spec's risk flags and the epic's diff
- Returns: conformance and correctness always, the rest from the spec's decision table, each with its reason and tier; over the cap it lists the runs and the choices. `--pick` records `picked` and `dropped` in the epic's ledger; collect refuses lens outputs while the plan is over the cap and no pick is recorded
- Fails: a pick that drops conformance or correctness → ValueError naming the lens
- Fails: the epic isn't finished → the CT-1 error
- Rules: "THE SYSTEM SHALL run the conformance and correctness lenses on every epic at the implementation gate." (FR-14)
- Rules: "WHEN a spec risk flag or the epic's diff triggers security, adversary, consistency or risk and rollback (see Rules) THE SYSTEM SHALL add that lens to the epic's plan." (FR-15)
- Rules: "IF an epic's planned lens runs exceed the cap (6, or `jury.max_runs`) THEN THE SYSTEM SHALL show the human the planned runs, each with its lens card's model tier (cheap, medium or strong) as its cost, and run only what the human picks: all, or a chosen set, plus all but the lowest-hit-rate lenses once NIO records hit rates per lens; the drop and the choice apply to triggered lenses only, and the two core lenses always run." (FR-16)

### CT-9 Lens pack (FR-17, FR-18) [derived: FR-17]
- Binding: `src/nio/evidence.py:pack` (new)
- Like: `src/nio/jury.py:fixcheck`
- Kind: function
- Shape: `pack(root, slug, gate, lens, run) -> text`
- Accepts: the diff, the results, the hints, and spec and contract items
- Returns: the diff, the text of the ACs, FRs and contracts the diff touches and no others, the results and the hints; a re-review is a fix check of the lens's findings, with the diff since the commit the last round judged. An item is touched when a task of the epic names it in `Serves:` or its contract's binding is a file in the diff
- Rules: "WHEN a lens runs THE SYSTEM SHALL give it a pack holding the epic's diff, the ACs, FRs and contracts the diff touches, and the run results." (FR-17)
- Rules: "THE SYSTEM SHALL let a juror open any file of the project to read it." (FR-18)

### CT-10 Implementation lens cards (FR-4, FR-5, FR-19, FR-34, FR-35) [derived: FR-4]
- Binding: `src/nio/agents/conformance.md` (new)
- Like: `src/nio/agents/test-proof.md`
- Kind: file
- Shape: `conformance.md`, `correctness.md`; an `## At implementation` section in those and `risk-rollback.md`, `security.md`, `adversary.md`, `consistency.md`
- Accepts: read, grep and glob only
- Returns: conformance matches each AC to a test by its name and description and confirms it from the body; correctness judges assertion hints and code
- Rules: "WHEN the conformance lens runs THE SYSTEM SHALL have it match every AC the epic covers to the tests that prove it, by file and line, judging each test by its name and description and confirming from its body that it really exercises the AC, with the test's result from FR-3; tests never need to carry spec IDs." (FR-4)
- Rules: "IF the conformance lens finds an AC the epic covers with no matching test, or whose test did not run or did not pass, THEN THE SYSTEM SHALL record a missing-evidence finding for that AC at severity blocker." (FR-5)
- Rules: "THE SYSTEM SHALL give jurors no way to run code or change files." (FR-19)
- Rules: "THE SYSTEM SHALL ship conformance, correctness and risk and rollback lens cards for the implementation gate." (FR-34)
- Rules: "THE SYSTEM SHALL give each existing lens card the implementation gate uses an `## At implementation` section." (FR-35)

### CT-11 A juror's requested run (FR-20) [derived: FR-20]
- Binding: `src/nio/evidence.py:requested` (new)
- Like: `src/nio/jury.py:fixcheck`
- Kind: function
- Shape: `requested(root, led, run) -> (results, for the human)`
- Accepts: a finding's `run:` field, which must be a `TC-n` of `tests.md`; never command text
- Returns: up to 3 runs per round across all jurors, their results in the next packs; everything else listed for the human
- Fails: the runner has no known way to run one test, or the run can't start → `couldn't run` and the error in the next packs
- Rules: "WHEN a finding asks for a specific run THE SYSTEM SHALL make that run and put its result in the next round's packs, only if it names one of the project's tests or the spec's attacks, and at most 3 runs per round across all jurors; any other request is not run and is listed for the human." (FR-20)

### CT-12 Finding format and collect (FR-5, FR-10, FR-21, FR-22, FR-23, FR-24) [derived: FR-5]
- Binding: `src/nio/jury.py:parse_lens` (existing)
- Kind: function
- Shape: `grounded` and `add` change at this gate too. `- gap: missing | partial | contradicts | unrequested` beside `kind`; `- where: <file or area>`; `evidence` keeps its meaning. Optional: `- run: TC-n`; `- right: spec | code` on a contradicts finding (unset means spec; grill Q26); `- tampering: yes` from correctness; conformance outputs `## Matches` lines, `- AC-n -> file:line`
- Accepts: a lens output at an `implementation-E-n` gate
- Returns: the same ledger entries as other gates, with `gap`; no word-for-word quote check; blockers and majors go to the refuter
- Fails: no gap, cite or where → `INVALID` naming the field
- Fails: a cite the spec and contracts don't define → dropped, the reason naming it (`add`, instead of its fixed reason)
- Rules: "IF the conformance lens finds an AC the epic covers with no matching test, or whose test did not run or did not pass, THEN THE SYSTEM SHALL record a missing-evidence finding for that AC at severity blocker." (FR-5)
- Rules: "IF the epic's diff deletes or skips a test, or the correctness lens confirms an FR-36 flag weakened a test, THEN THE SYSTEM SHALL record it as test tampering at severity major, whatever reason is given; only the human may accept it as risk, with a reason." (FR-10)
- Rules: "THE SYSTEM SHALL require every finding at the implementation gate to carry a gap type, in its own field beside the lens output's `kind` (missing, partial, contradicts or unrequested), the AC, FR or CT it traces to, and its evidence as a file or area." (FR-21)
- Rules: "IF a finding cites an AC, FR or CT that the spec or its contracts don't define THEN THE SYSTEM SHALL drop it as ungrounded." (FR-22)
- Rules: "WHEN a finding quotes code THE SYSTEM SHALL accept a paraphrased or abbreviated quote without a word-for-word check." (FR-23)
- Rules: "WHEN a lens raises a blocker or a major THE SYSTEM SHALL have the refuter validate it against the code before it reaches the human; a finding the CLI-first checks make goes to the ledger as confirmed, with no refuter." (FR-24)

### CT-13 Compose the outcome (FR-25, FR-28, FR-31, FR-32, FR-38, FR-43) [derived: FR-25]
- Binding: `src/nio/jury.py:compose` (existing)
- Kind: function
- Shape: `compose(led, current)`; at this gate `current` is the epic's last `T-n:` commit, and minors are left out of `unresolved`, `stale` and the fix-check IDs; a `noted` major with no later ruling gives human; a lens-`cli` finding needs no juror's fix verdict, and one the CLI marked `not fixed` counts as unresolved
- Accepts: the epic's ledger
- Returns: approved, rejected, rerun, pending or human, with #52's rules; minors never make it rejected or human
- Rules: "THE SYSTEM SHALL compose the gate's outcome from the spec jury's set: approved, rejected, rerun, pending or human." (FR-25)
- Rules: "WHEN the gate finds nothing wrong THE SYSTEM SHALL write no task." (FR-28)
- Rules: "WHEN the outcome is approved THE SYSTEM SHALL list the minor findings in the approved verdict." (FR-31)
- Rules: "THE SYSTEM SHALL apply the spec jury's convergence rules (#52) to the implementation gate's rounds unchanged, except that minor findings are handled by FR-43 and a new major raised in a re-review goes to the human (AC-38)." (FR-32)
- Rules: "IF a planned lens has delivered no valid output THEN THE SYSTEM SHALL compose rerun, never approved, and human after its second invalid output, as at the spec gate." (FR-38)
- Rules: "THE SYSTEM SHALL never let a minor finding make the outcome rejected or human, nor append a task for it; minors are only listed in the verdict (FR-31)." (FR-43)
- State: follows the spec's state table epic at the implementation gate

### CT-14 Fix tasks (FR-26, FR-27, FR-29, FR-37) [derived: FR-26]
- Binding: `src/nio/tasks.py:append_fix` (new)
- Like: `src/nio/tasks.py:show`
- Kind: function
- Shape: `append_fix(root, slug, epic, finding) -> "T-n" | None`
- Accepts: an open blocker or major the spec's decision table routes to a task
- Returns: a task under the epic's `#### Fixes`, the next free ID, `From: J-n (implementation-E-n, round n)`; unrequested says justify or remove. `None` when the finding already has a task. The fields: `Files` from `where`, `Serves` from the cites, `Test` the finding's `run` or a TC covering its cite, else `new: <cite>`, which `tasks.check` accepts only with `From:`; `Depends on: none`; `Parallel: no`; `Tier: strong: a fix from a jury finding`; `Effort: med`; `Mode: single: a fix from a jury finding`. Written through a temporary file and a rename. The finding becomes `disposed` with the new disposition `fix-task` (in `DISPOSITIONS` and `FIXES`, this gate only), so its lens gets a fix verdict
- Rules: "WHEN the outcome is rejected THE SYSTEM SHALL append one fix task per open blocker or major finding that the decision table routes to a task (where a confirmed finding goes), each citing exactly that finding, with new IDs, never a second task for a finding that already has one, and send the epic back to the implement stage." (FR-26)
- Rules: "THE SYSTEM SHALL never rewrite, renumber or remove an existing task of the epic." (FR-27)
- Rules: "WHEN a finding's gap type is unrequested THE SYSTEM SHALL append a "justify or remove" task and never delete the code itself." (FR-29)
- Rules: "WHEN the human chooses fix for an item on the end-of-review list THE SYSTEM SHALL append it to the epic as a fix task for the implement stage, and run the one final fix check once those tasks are finished; code never changes outside a task." (FR-37)

### CT-15 Change requests and the hold (FR-30, FR-44) [derived: FR-30]
- Binding: `src/nio/jury.py:raise_change` (new)
- Like: `src/nio/jury.py:change_record`
- Kind: function
- Shape: `raise_change(root, slug, gate, finding) -> "C-..."`
- Accepts: a contradicts finding with `right: code`
- Returns: a pending change record against the spec, whose body names the finding and gate; spec.md is unchanged. The existing record when one already names them, so a repeat or a stop before the ledger save raises no second. Accepted, every record ruled: the gate composes again. Rejected: a fix task (CT-14) and back to implementing
- Rules: "IF a finding shows the code is right and the spec is stale THEN THE SYSTEM SHALL raise a change request and never edit the spec." (FR-30)
- Rules: "WHEN the outcome is rejected and every open blocker or major finding went to a change request THE SYSTEM SHALL hold the epic until the human rules on each change request: accepted, the finding is settled and the gate composes again; rejected, the finding becomes a fix task and the epic goes back to the implement stage." (FR-44)
- State: follows the spec's state table epic at the implementation gate

### CT-16 Verdict for an epic (FR-31, FR-33) [derived: FR-31]
- Binding: `src/nio/jury.py:verdict` (existing)
- Kind: function
- Shape: `verdict(root, led, outcome, reasons)`, subject `implementation-E-n:<slug>`
- Accepts: the epic's ledger
- Returns: one record per round and outcome naming the epic, listing minors when approved and any `dropped` lens from the ledger
- Rules: "WHEN the outcome is approved THE SYSTEM SHALL list the minor findings in the approved verdict." (FR-31)
- Rules: "WHEN an epic's gate ends THE SYSTEM SHALL write a verdict record naming the epic, the outcome and the round, listing its minor findings when approved." (FR-33)

### CT-17 The flow around the gate (FR-1, FR-26, FR-44) [derived: FR-1]
- Binding: `src/nio/implement.py:epic_end` (existing)
- Kind: function
- Shape: `epic_end` writes neither `epic` nor `pass` and prints the gate as next; `flow.done` takes `nio flow done implementation-E-n <slug>`, which writes the `epic` line; `nio flow next` names `@nio:jury` while a gate is open; `nio flow claim` refuses the next epic until the `epic` line exists
- Accepts: history and the epic's ledger
- Returns: the `epic` line is written when the gate is approved or closed; its `reason` is the outcome. With the last epic's line, the same call writes the `pass` line implementing -> done and prints `merge:`; it commits the ledger, `tasks.md`, verdict and change records as `nio: approve implementation-E-n`. `nio jury check --record` on any other outcome commits them as `nio: jury implementation-E-n round n`, through `flow.commit_gate`
- Returns: an old `skipped: not built` line stays closed; `nio flow next` lists those epics as never reviewed (grill Q28). Rolling this code back needs every open gate closed first: old code has no writer for a missing line
- Fails: claim while a gate is open → exit 1 naming the epic and the gate
- Rules: "WHEN asked to jury an epic from the tasks stage whose tasks the implement stage has all finished THE SYSTEM SHALL start the implementation gate on that epic." (FR-1)
- Rules: "WHEN the outcome is rejected THE SYSTEM SHALL append one fix task per open blocker or major finding that the decision table routes to a task (where a confirmed finding goes), each citing exactly that finding, with new IDs, never a second task for a finding that already has one, and send the epic back to the implement stage." (FR-26)
- Rules: "WHEN the outcome is rejected and every open blocker or major finding went to a change request THE SYSTEM SHALL hold the epic until the human rules on each change request: accepted, the finding is settled and the gate composes again; rejected, the finding becomes a fix task and the epic goes back to the implement stage." (FR-44)
- State: follows the spec's state table epic at the implementation gate

### CT-18 The secrets flag (FR-45, FR-46) [derived: FR-45]
- Binding: `src/nio/spec.py:RISKS` (existing)
- Kind: config
- Shape: `secrets` in `RISKS` and the security row of `LENSES`
- Accepts: a spec's `risk:` list
- Returns: the security lens at the spec gate and this gate; the plan gate's trigger stays auth and pii, so its lenses don't change
- Rules: "THE SYSTEM SHALL add `secrets` to the spec's risk flags, set when the work stores, sends or shows tokens, keys, passwords or other secrets; permission changes stay under `auth`." (FR-45)
- Rules: "WHEN a spec carries the `secrets` flag THE SYSTEM SHALL bring in the security lens at the spec gate too, as it does for `auth`." (FR-46)

### CT-19 The jury skill at this gate (FR-1, FR-14) [derived: FR-1]
- Binding: `skills/jury/SKILL.md` (existing)
- Kind: file
- Shape: a section on the implementation gate; `jury evidence` added to `hooks.ALLOW`
- Accepts: an effort at implementing with a finished epic
- Returns: the agent runs `nio jury evidence` first, then lenses, refuter and check, as at other gates
- Rules: "WHEN asked to jury an epic from the tasks stage whose tasks the implement stage has all finished THE SYSTEM SHALL start the implementation gate on that epic." (FR-1)
- Rules: "THE SYSTEM SHALL run the conformance and correctness lenses on every epic at the implementation gate." (FR-14)

### CT-20 The CLI's findings in the ledger (FR-10, FR-24, FR-42) [derived: FR-24]
- Binding: `src/nio/jury.py:record_cli` (new)
- Like: `src/nio/jury.py:add`
- Kind: function
- Shape: `record_cli(root, slug, gate, findings) -> ["J-n"]`
- Accepts: the findings of CT-3, CT-4, CT-6 and CT-21, each with a title, severity, gap, cite and where; a task's cite is its `Serves:`
- Returns: ledger entries with lens `cli`, kind `gap`, validation `confirmed`, never in a refuter batch and never a vote; a repeat with the same title adds none. On the next `nio jury evidence` and `join`, the CLI gives the fix verdict for a `fix-task` entry, since no juror can: gone from the checks → `fixed`; still reported → `not fixed`, the same J-n, handled as a lens's `not fixed` verdict with no second task
- Fails: `dispose` of a `tampering` finding by anything but `--by human` → ValueError
- Rules: "IF the epic's diff deletes or skips a test, or the correctness lens confirms an FR-36 flag weakened a test, THEN THE SYSTEM SHALL record it as test tampering at severity major, whatever reason is given; only the human may accept it as risk, with a reason." (FR-10)
- Rules: "WHEN a lens raises a blocker or a major THE SYSTEM SHALL have the refuter validate it against the code before it reaches the human; a finding the CLI-first checks make goes to the ledger as confirmed, with no refuter." (FR-24)
- Rules: "IF the epic's lint or type check fails THEN THE SYSTEM SHALL record a finding at severity major naming the failing check and its first errors." (FR-42)

### CT-21 Joining a lens's matches to the results (FR-4, FR-5, FR-39) [derived: FR-5]
- Binding: `src/nio/evidence.py:join` (new)
- Like: `src/nio/jury.py:add`
- Kind: function
- Shape: `join(root, slug, epic, matches, results) -> findings`, called by `nio jury collect` on the conformance output
- Accepts: the lens's `AC-n -> file:line` lines; the ACs the epic covers; `results.json`
- Returns: writes `evidence`, the file, line and result always read from the results, never from the lens. One blocker missing-evidence finding, to CT-20, per AC with no match, or a match that failed, didn't run, or has a no-assertion hint
- Rules: "IF the conformance lens finds an AC the epic covers with no matching test, or whose test did not run or did not pass, THEN THE SYSTEM SHALL record a missing-evidence finding for that AC at severity blocker." (FR-5)
- Rules: "WHEN a test in the epic's diff has no assertion THE SYSTEM SHALL flag it with zero model calls, as a hint in every lens pack, not as a ledger finding." (FR-39)

## Data model
- **Epic** (spec Key entity) in `src/nio/tasks.py:parse` (existing) [derived: FR-1]
  - tasks: the epic's section of `tasks.md`, `#### Fixes` included.
- **Task** (spec Key entity) in `src/nio/tasks.py:parse` (existing) [derived: FR-27]
  - From: the finding a fix task cites. "never rewrite, renumber or remove an existing task of the epic" (FR-27)
- **Run results** (spec Key entity) in `src/nio/evidence.py:RESULTS` (new) [derived: FR-3]
  - tests, checks, attacks, journeys, hints, requests, evidence: gitignored under the run; a finding quotes what it rests on.
- **Finding** (spec Key entity) in `src/nio/jury.py:load` (existing) [derived: FR-21]
  - gap: missing, partial, contradicts or unrequested, in `jury/implementation-E-n.json`. Also where, right, tampering, and the ledger's picked and dropped.
- **Change request** (spec Key entity) in `src/nio/records.py:new` (existing) [derived: FR-30]
  - outcome: pending, accepted or rejected, with `against` the spec.
- **Verdict record** (spec Key entity) in `src/nio/jury.py:verdict` (existing) [derived: FR-25]
  - subject: `implementation-E-n:<slug>`.
