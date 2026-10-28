---
slug: 2026-10-28-flow-state
retired: []                      # CT IDs removed from this plan; never reused
---
# Contracts: flow state

## Contracts

### CT-1 Read an effort's flow files (FR-3, FR-6, FR-58, FR-59) [default]
- Binding: `src/nio/flow.py:load` (new)
- Like: `src/nio/jury.py:load`
- Kind: function
- Shape: `load(root, slug) -> (state, lines)`; `state` is the parsed `state.json` (the defaults below when it is missing), `lines` the parsed history lines, oldest first, without a torn last line
- Accepts: an effort folder `.nio/specs/<slug>/`; `state.json` and `history.jsonl` may both be missing (an effort with no history)
- Returns: `(state, lines)`; a missing `state.json` reads as `{"auto": false, "pause": null, "abandon": null, "waiting": null, "claims": {}, "attempts": {}, "run": ""}`
- Fails: raises `flow.Broken(file, where)`, which every command prints as `error: <slug>: <file>, <where>` with exit 1, when `state.json` is not a JSON object (`where` = `not valid JSON`); when it holds a key outside `STATE_KEYS` (`where` = `key <name>`); when a history line other than a torn last one is not valid JSON (`where` = `line <n>`, counted from 1); or when `sha256(state.json bytes)` differs from the `state` hash on the last complete `end` line (`where` = `hash mismatch`)
- Rules: "IF `state.json` or a line of `history.jsonl` other than a torn last line (FR-59) can't be read, or `state.json` holds a key outside FR-3's list, or its hash differs from the one the last history line recorded (FR-58), THEN THE SYSTEM SHALL refuse every `nio flow` command on that effort and name the file and the key or line" (FR-6); "IF the last line of `history.jsonl` has no line ending THEN THE SYSTEM SHALL ignore it, cut it off on the next write, and record that it did" (FR-59)
- Rules: a last line with no line ending that parses as JSON and whose `state` hash equals `sha256(state.json)` (or of a matching `state.json.new`, below) counts as complete; the next write adds its missing `\n` and nothing is cut. Only a last line failing either test is torn [agent]
- Rules: the last complete line must carry `"end": true` (CT-2 marks the final line of each call's batch); complete lines after the last `end` line are the torn tail of a batch that was cut off mid-write, and are read like a torn last line [agent]
- Rules: a crash between the writes of CT-2 leaves `state.json.new` behind; `load` reads `state.json.new` in place of `state.json` when its hash equals the `state` hash of the last complete `end` line, and ignores it otherwise, so the effort reads as that line says (CT-2 finishes the job on the next write) [agent]
- Rules: an effort with `history.jsonl` but no `state.json` is broken (`state.json`, `missing`); `state.json` without `history.jsonl` is broken (`history.jsonl`, `missing`), since no line holds its hash [agent]

### CT-2 Record a history line and the state it leaves (FR-1, FR-4, FR-5, FR-25, FR-58, FR-59) [default]
- Binding: `src/nio/flow.py:record` (new)
- Like: `src/nio/jury.py:save`
- Kind: function
- Shape: `record(root, slug, entries, state, who, run, at=None) -> None`, called only while holding the effort's lock (CT-3); `entries` is a list of `{"kind", "from", "to", "evidence", "reason", "change"}`, appended in order
- Accepts: `kind` one of `start`, `pass`, `override`, `skip`, `fail`, `back`, `park`, `abandon`, `resume`, `seen`, `repair`, `pause`, `suspend`; `who` = `{"role", "host", "model"}` from `--by "<role> / <host> / <model>"`; `run` from CT-17's lookup; `at` (a UTC datetime) is for tests only and sets every line's `at`, the hash still being computed over the bytes written to `state.json` [agent]
- Returns: nothing; each appended line is one JSON object ending in `\n`: `{"kind", "at" (UTC ISO 8601, seconds), "who", "from", "to", "evidence": {"paths": [...], "verdict": "<V- ID or ''>", "output": "<sha256 of the guard output or ''>"}, "run", "state": "<sha256 of state.json as written>"}`, plus `reason` when given, `change` (a C ID, or `{"file", "judged", "current"}` with git blob hashes) on `back` and `resume` lines, `evidence.output_text`, the failing guard output itself, on `override` and `fail` lines, `evidence.blobs` (`{file: git blob}` for each of the gate's files, through `jury.blob`) and `evidence.round` (the gate ledger's `round`) on an `override` line from a gate, and `"end": true` on the last line of the call's batch
- Fails: an `OSError` is raised as it comes; nothing is caught and retried
- Rules: "append one line to `.nio/specs/<slug>/history.jsonl` and never rewrite an earlier line" (FR-4); "record on every history line who (role, host, model), when, from, to, the evidence (paths, verdict ID, test output hash) and the current run ID" (FR-5); "record on every history line a hash of `state.json` as the command left it" (FR-58); "write each human override as its own history line and never merge or deduplicate it with another line" (FR-25)
- Rules: a torn tail (CT-1) is cut off, truncating the file to the end of the last complete `end` line, before appending; a `repair` line goes first, whose `reason` gives the cut's first line number, its byte count and the cut bytes hex-encoded, so nothing is lost and the torn text no longer appears as such (FR-59) [agent]
- Rules: write order: (1) write the new state to `state.json.new`, `fsync`; (2) append all of the call's lines, each carrying the new state's hash and the last one `"end": true`, in a single `write` followed by `fsync`; (3) `os.replace("state.json.new", "state.json")`. A crash before (2) starts leaves a temp file whose hash matches no `end` line: CT-1 ignores it and the next write deletes it. A crash during (2) leaves either nothing new or a prefix of the batch with no `end` line, which CT-1 reads as a torn tail and the next write cuts and notes (FR-59), deleting the temp file. A crash after (2) leaves a temp file matching the last `end` line: CT-1 reads it and the next write renames it into place. In every case the next call sees a state that agrees with the last complete `end` line, as FR-6 and FR-58 require, and no line is recorded twice [agent]
- Rules: known limit, accepted under grill Q14 and Q15: the `state` hash is not chained to the previous line, so an agent that edits `state.json` and appends a matching line by hand is not caught; the guard against that is the rule in every skill and card (CT-18) and the diff in git [agent]
- Rules: every write of `state.json` comes with at least one line, so its hash is always on the last line [derived: FR-58]

### CT-3 The effort's lock (FR-45, FR-54) [default]
- Binding: `src/nio/flow.py:lock` (new)
- Like: none: nothing in the code locks a file today
- Kind: function
- Shape: `with lock(root, slug):` around every write to an effort; the lock file is `.nio/specs/<slug>/flow.lock`, holding `{"pid", "host", "at"}`
- Accepts: an effort folder; `host` is `socket.gethostname()`
- Returns: the lock is held for the body and removed on exit, also on an exception
- Fails: the lock is held and not stale → raises `flow.Busy`, printed as `error: <slug> is being written by another nio flow call (pid <pid> on <host>); try again` with exit 1, and nothing is written
- Rules: "create a lock file in the effort folder that git ignores, atomically, naming its process and host, and SHALL take it over only when it is older than one minute and its process on this host is gone, or its host is another one" (FR-54); "IF another `nio flow` call holds the effort's lock file THEN THE SYSTEM SHALL refuse to write, say the effort is being written, and change nothing" (FR-45)
- Rules: created with `os.open(..., O_CREAT | O_EXCL)`; a stale lock (mtime more than 60 seconds ago, and its `host` is another one or its `pid` is gone on this host, by `os.kill(pid, 0)`) is taken over by renaming it to a unique `flow.lock.<pid>.<random>` first, so of two callers taking it over only one wins, then creating the lock anew and deleting the renamed file [agent]
- Rules: on exit the lock is removed only when it still holds this caller's own `pid`, `host` and `at`, so a holder whose lock was taken over never deletes the new holder's lock [agent]
- Rules: before the lock is first created in an effort folder, `.nio/specs/<slug>/.gitignore` gets the lines `flow.lock*` and `state.json.new` when missing, so a renamed stale lock is ignored too; it is the only `.gitignore` this feature writes, and it lives inside the effort folder [agent]
- Rules: before it writes, the holder re-reads the lock; when it no longer holds its own `pid` and `host` (taken over meanwhile), it raises `flow.Busy` and writes nothing, so a takeover never doubles a line [agent]
- Rules: every refusal that needs no lock (an empty reason, a legacy, unsupported or done effort, a stage not reached or already passed) is made before the lock or `.gitignore` is touched, so a refused command leaves the folder byte-identical [agent]
- Rules: known limit: a lock from another host can't be checked for liveness, so it is taken over once older than a minute, as FR-54 says; since the lock is git-ignored, this happens only when two hosts share the folder (a network disk), and a call on the other host that still runs then finds its lock gone and writes nothing (the rule above) [agent]

### CT-4 Which effort a command acts on (FR-9, FR-11, FR-29, FR-50) [default]
- Binding: `src/nio/flow.py:pick` (new)
- Like: `src/nio/tasks.py:route`
- Kind: function
- Shape: `pick(root, slug=None) -> slug`; `kind(root, slug) -> "legacy" | "unsupported: <route>" | "effort"`
- Accepts: a slug or nothing
- Returns: the slug given, or, with none, the effort whose last complete history line has the newest `at`
- Fails: a slug with no folder under `.nio/specs/` → `error: no effort <slug> under .nio/specs/`; no slug and no effort with a history line → `error: no current effort; start one with: nio flow start <slug> --by "<role> / <host> / <model>"`; each followed by one line per effort it can act on (`  <slug>`), exit 1, nothing written
- Rules: "act on the effort with the newest history line, keeping no pointer of its own" (FR-9); "IF no slug is given and no effort has a history line, or the slug has no folder under `.nio/specs/`, THEN THE SYSTEM SHALL refuse, list the efforts it can act on, and write nothing" (FR-11)
- Rules: a folder whose name doesn't match `^\d{4}-\d{2}-\d{2}-` is `legacy`; a dated folder is `unsupported: <route>` only when its `spec.md` exists with a frontmatter `route` other than `full`; a dated folder with no `spec.md`, or a `spec.md` with no `route` yet, is an effort (at intake or drafting, as CT-6 derives) [agent]; the efforts listed are the dated ones that are not unsupported, so legacy and unsupported folders are never listed and never written by any command (FR-29, FR-50) [derived: FR-29, FR-50]

### CT-5 The guards (FR-12, FR-13, FR-14, FR-15, FR-27) [default]
- Binding: `src/nio/flow.py:guard` (new)
- Like: `src/nio/tasks.py:may_start`
- Kind: function
- Shape: `guard(root, slug, stage) -> (result, output, evidence)`; `result` is `pass`, `fail` or `closed` (a gate the human closed with `nio jury check --human`); `output` the lines that say what is missing; `evidence` the paths read, the verdict ID and the output hash for CT-2
- Accepts: a stage of the state table "Flow" other than `done`
- Returns: per the decision table "Guards", computed only by these calls: intake: `intake.md` exists; drafting: `spec.md` exists and `spec.check(root, slug)` returns no errors; grilling: `spec.check(root, slug, gate=True)` returns no errors; spec_jury: `jury.standing(root, slug, "spec")` is `approved` with no finding `open`, or `closed`; planning: `plan.check(root, slug, gate=True)` returns no errors; plan_jury: `plan.approved(root, slug)[0]`; tasking: `tasks.check(root, slug)` returns no errors; tasks_jury: `tasks.approved(root, slug)[0]`; researching, advocate_walking and arch_grilling are never run (not built); implementing never passes
- Fails: a guard that fails returns its errors as `output` (`ERROR <message>` lines, or the ledger's outcome, `the spec jury's outcome is <outcome>`, at spec_jury)
- Rules: "THE SYSTEM SHALL decide a guard only from files and the results of commands it runs, never from an agent's claim or a worker's handoff text" (FR-14); "WHEN a jury gate was closed by the human with a reason (`nio jury check --human`) THE SYSTEM SHALL treat its guard as passed by a human override and record that reason" (FR-27): `closed` carries the reason from the ledger's `closed` entry
- Rules: at plan_jury and tasks_jury the human's closure is read through `jury.standing(root, slug, gate) == "closed"` as at spec_jury, so a closure is an override at every gate [derived: FR-27]

### CT-6 Where an effort is (FR-2, FR-8, FR-21, FR-22, FR-23, FR-47, FR-49, FR-55, FR-56) [default]
- Binding: `src/nio/flow.py:where` (new)
- Like: `src/nio/jury.py:state`
- Kind: function
- Shape: `where(root, slug) -> dict` with `stage`, `status` (one of FR-28's words, with its why), `skill`, `inputs`, `exit`, `command`, `skipped` (the not-built stages right before `stage`), `changes` (CT-7), `overrides` (not yet seen, CT-15)
- Accepts: an effort `pick` and `load` accept
- Rules: `GATES = {"spec_jury": ("spec", "nio: approve spec"), "plan_jury": ("plan", "nio: approve plan"), "tasks_jury": ("tasks", "nio: approve tasks")}` in `flow.py`: each gate stage's jury gate name and approval message, the one map CT-6's search, CT-7's judged versions and CT-11's commit use, matching the existing commits (`git log --grep "^nio: approve "`) [agent]
- Returns: `stage` is "the first stage in the state table "Flow" that has not passed" (FR-47), walking from intake: a gate (spec_jury, plan_jury, tasks_jury) has passed when its guard passes and either a commit found by `records.git(root, "log", "--format=%H", "--grep", "^<message>$", "--", ".nio/specs/<slug>")` holds, in its copy of `jury/<gate>.json`, the same `round` as the ledger now, or a history line has kind `override`, `from` that gate and `evidence.round` equal to the ledger's `round` now (FR-55); an approval or override from an earlier round no longer counts [agent]; any other stage has passed when its guard passes, it is not built (researching, advocate_walking, arch_grilling), or a history line has kind `override` and `from` it (FR-47); implementing never passes (FR-22)
- Returns: before its guard is read, a gate whose ledger's saved `outcome` is `rejected` while `jury.blob(jury.artefact(root, slug, gate))` equals the ledger's version for its `round` sets `stage` to its "jury rejects" target (grilling, planning, tasking) and names the round (FR-23, FR-56)
- Returns: `status` is `waiting_for_human: Q<n>` when `grill.md` has an `## Asked · Q<n>` entry with no later `## Q<n>` entry (FR-8, RF-13); `waiting_for_human: approve <gate>` with `command` `nio flow done <stage> --commit <slug> --by human` when the stage is a gate whose guard passes with no approval commit or override (FR-49); `waiting_for_human: implement not built` at implementing (FR-22); `done` at done; else `working`. The stored marks and the stop list come first (CT-8, CT-12 to CT-14)
- Rules: "read gate outcomes, rounds and judged versions from `jury/<gate>.json`, the pending question from `grill.md`, and pending change requests from `C-*` records, and SHALL keep no copy of them" (FR-2); "count a gate as passed only when its guard passes on the files and either a commit `nio: approve <gate>` touched the effort folder or history holds an override line for it" (FR-55); "once those files change, the stage is the gate again, for its re-review" (FR-56)
- Rules: `skill` per stage: intake and drafting `@nio:spec`, grilling `@nio:grill`, the three gates `@nio:jury`, planning `@nio:plan`, tasking `@nio:tasks`; `inputs` are the files the skill reads (planning: `spec.md`, `architecture.md` when present, `research.md`, `grill.md`); `exit` is the stage's row of the decision table "Guards", word for word [derived: FR-7, FR-15]
- Rules: `where` never writes; it is the same for every caller, so `next`, `done` and `status` agree [derived: FR-47]

### CT-7 A change sends the effort back (FR-35, FR-36, FR-37, FR-38, FR-52) [default]
- Binding: `src/nio/flow.py:changes` (new)
- Like: `src/nio/jury.py:change_record`
- Kind: function
- Shape: `changes(root, slug, lines) -> list[dict]`, each `{"change": "<C-ID>" | "<file>", "target": "<stage>", "judged": "<blob>", "current": "<blob>", "pending": bool}`; `where` sets `stage` to the earliest of its own stage and every target
- Accepts: the effort's history lines (CT-1)
- Returns: one entry per `C-*` record under `.nio/memory/` with `outcome: pending` whose `against:`, with a leading `.nio/specs/` removed, is `<slug>/<file>` for one of the effort's files (RF-12), targeted by the first column of the decision table "Owning stage" (FR-35); and one per approved file whose blob now differs from its judged blob, targeted by the second column (FR-36). A file's judged blob is its blob in the newest approval commit of its gate (CT-6's map) touching the folder, or, when an `override` line from that gate is newer, the blob that line's `evidence.blobs` recorded; the gate is spec_jury for `research.md` and `spec.md`, plan_jury for the plan files, tasks_jury for `tasks.md` (compared without its `#### Fixes` sections, RF-9); blobs come from `jury.blob` and `jury.artefact`; a file with no such commit or line, or whose column says `ignore`, gives no entry
- Fails: an unreadable change record is skipped and named in `where`'s output as `unreadable change record <path>`, never fatal (a record lint is `nio check`'s job) [agent]
- Rules: "move the effort, from any state, back to the stage the decision table "Owning stage" gives" (FR-35, FR-36); "record the move once, not on every later call, and name the change in the history line: the C ID, or the file with its judged and current versions" (FR-37): the first writing call (`next`, `start`, `done`, `park`, `abandon`, `seen`) that sees an entry no `back` line names yet appends `{"kind": "back", "from": <the last line's to>, "to": <target>, "change": <the C ID, or {"file", "judged", "current"}>, "evidence": {"paths": [<file>]}}`
- Rules: an edited-file entry stops counting once a `pass` or `override` line leaves its target stage after the `back` line that named it, so a `research.md` edit sent to grilling is settled by passing grilling again [agent]
- Rules: "IF a pending `C-*` record is against one of the effort's files THEN THE SYSTEM SHALL refuse `nio flow done` for the owning stage and every later stage until the record is no longer pending, and `nio flow next` SHALL report the effort `waiting_for_human` on that record" (FR-38): status `waiting_for_human: <C-ID> pending`
- Rules: an abandoned effort is never moved: `changes` is not applied and its stage stays the `from` of its `abandon` line, "until `nio flow start` resumes it" (FR-52)

### CT-8 The stop list (FR-39, FR-40, FR-41, FR-42, FR-51) [default]
- Binding: `src/nio/flow.py:stops` (new)
- Like: `src/nio/jury.py:compose`
- Kind: function
- Shape: `stops(root, slug, here, state, lines) -> dict | None`: the pause or suspension a writing call must record before anything else, or none; `here` is `where`'s result
- Accepts: only efforts whose `state.json` has `"auto": true`; with the flag off it returns none (FR-39 to FR-42 all say "WHILE the effort's auto flag is on")
- Returns: for the effort's current gate (the gate stage it is at, or the gate whose rejected round sent it back, CT-6), when its ledger `round` is 3 or more and its standing is neither `approved` nor `closed`, or its `round` is 2 or more with no finding `fixed_in` that round while a finding raised in an earlier round is still `open` (RF-8): a pause, `waiting` = `{"why": "<gate> jury ran <n> rounds without approval" | "<gate> jury round <n> closed none of round <n-1>'s findings", "gate", "round"}`, listing every open finding ID; not again for a gate and round a `resume` line names (FR-39)
- Returns: at a gate stage whose guard fails (its jury must run a round), when `budgets.juries` (config, CT-17's data model) is not more than the juries used, the sum of `round` over the effort's ledgers, or `budgets.subagents` is not more than the subagent runs used, the number of keys in `collected` (every lens and refuter output collected, which `jury.py` never resets, RF-17) summed over the effort's ledgers [agent]: `pause` = `{"kind": "suspended", "why": "cap"}`, and `next` prints `juries used: <n>` and `subagent runs used: <n>` (FR-40)
- Returns: an entry of CT-7 that no `back` or `resume` line names yet: a pause `waiting_for_human: <change> would move it back to <target>`, with no `back` line, so `stage` stays the last line's `to` until `nio flow start` resumes it (FR-42)
- Rules: "WHEN the last 3 history lines are `fail` lines with the same guard and hash it SHALL suspend the effort as `suspended: stuck`" (FR-41); the hash is the sha256 of the guard output after removing every ISO date or time (`\d{4}-\d{2}-\d{2}([T ]\d{2}:\d{2}(:\d{2})?)?`) and every path (the repo root prefix, then any token holding a `/`) [agent]
- Rules: "WHILE the effort's auto flag is on and its spec's `risk:` holds `money`, `data-deletion`, `migration` or `auth`, WHEN a gate's guard passes THE SYSTEM SHALL wait for the human's `--commit` instead of committing, as with the auto flag off" (FR-51)
- Rules: precedence when several hold: the round cap and the no-progress pause (FR-39) are checked first, then the count caps (FR-40), then the change pause (FR-42); FR-41's stuck rule is checked by `done` when it records a `fail` line; one call records at most one of them [agent]
- Rules: this spec only reads the auto flag; nothing here sets it (Non-goals) [derived: FR-39]

### CT-9 `nio flow next` (FR-7, FR-31, FR-43, NFR-1, NFR-2) [default]
- Binding: `src/nio/flow.py:next_step` (new)
- Like: `src/nio/jury.py:check`
- Kind: cli
- Shape: `nio flow next [<slug>] [--by "<role> / <host> / <model>"]` → when working, at most 12 lines: `effort: <slug>`, `state: <stage> (<status>)`, `skill: <skill>`, `inputs: <files>`, `exit: <exit criteria>`, `done: nio flow done <stage> <slug> --by <value>` (the caller's own `--by` when `next` was given one, else the literal `--by "<role> / <host> / <model>"`), then `skipped: <stages> (not built)` when `skipped` is not empty, and one line `override not seen: <stage>: <reason>` listing every unseen override, separated by `; `, so each is shown and the output stays within 12 lines
- Accepts: an effort `pick` accepts; legacy → `legacy: <slug> has no flow layout; nothing to do` and unsupported → `unsupported: <route>: nio flow drives full-route specs only`, both exit 0, no skill, nothing written
- Returns: exit 0. When the status is not `working`, the output follows NORTH_STAR's "Talking to the human" shape and names no skill: line 1 what the human must do (`Answer the grill's question Q<n>`, `Approve or push back: run the command below`, `Settle the change request <C-ID>`, `Run this command to resume`, `Nothing to run: the implement stage isn't built`), then the state and why in at most 3 lines, the command quoted on its own line when there is one (with `--by human`, as `nio flow start <slug> --by human`), and a last line `Refs: <IDs and files>`
- Fails: as CT-1 and CT-4
- Rules: "print the current state, the skill to run, the input files, the exit criteria and the `nio flow done` command that reports it" (FR-7); "print `nio flow next` in at most 12 lines when the effort is not paused" (NFR-1); "WHILE an effort waits for the human or is suspended, WHEN `nio flow next` runs THE SYSTEM SHALL print the reason in the "Talking to the human" shape and name no skill" (FR-43)
- Rules: "WHEN `nio flow start` or `nio flow next` runs on a parked effort THE SYSTEM SHALL resume it and record the resume in history" (FR-31)
- Rules: `next` writes only when given `--by`, on an effort that has `history.jsonl`, and only when it has something to record (a resume, a `back` line, a stop-list pause, a torn line to cut); without `--by` it prints the same output plus one line `would record: <kind>[, <kind>] (run with --by to record)` and writes nothing; otherwise it takes no lock, so a past effort with no history is never written by `next` (AC-51, AC-64) [agent]

### CT-10 `nio flow start` (FR-10, FR-44, FR-53) [default]
- Binding: `src/nio/flow.py:start` (new)
- Like: `src/nio/plan.py:new`
- Kind: cli
- Shape: `nio flow start <slug> --by "<role> / <host> / <model>"` → `started <slug> at <stage>` or `resumed <slug> at <stage>`
- Accepts: a dated full-route effort; legacy and unsupported are refused (`error: <slug> is legacy|unsupported: <route>; nio flow writes nothing in it`, exit 1)
- Returns: on an effort with no `history.jsonl`: creates `state.json` (CT-1's defaults) and `history.jsonl` with one `start` line, `from` null, `to` the stage `where` gives (FR-10); on a parked, suspended, abandoned or stop-list-paused effort: clears `pause`, `abandon` or `waiting`, appends one `resume` line naming what it cleared and, for FR-42, the change, then applies any `back` line CT-7 owes (FR-44, FR-53); on a working effort with history: appends a `start` line, which makes it the effort with the newest line (FR-10)
- Fails: as CT-1, CT-3 and CT-4
- Rules: "WHEN `nio flow start <slug>` runs THE SYSTEM SHALL create its `state.json` and `history.jsonl` if missing and record a start line, which makes it the effort with the newest history line" (FR-10)

### CT-11 `nio flow done` (FR-12, FR-13, FR-16, FR-17, FR-18, FR-19, FR-20, FR-21, FR-24, FR-26, FR-48, FR-62) [default]
- Binding: `src/nio/flow.py:done` (new)
- Like: `src/nio/jury.py:check`
- Kind: cli
- Shape: `nio flow done <stage> [<slug>] [--commit] [--human "<reason>"] --by "<role> / <host> / <model>"` → `moved <slug>: <stage> → <next stage>` and one `skipped <stage> (not built)` line per skip, or the failing guard's output
- Accepts: `<stage>` one of the state table "Flow"'s stages; an effort `pick` accepts
- Returns: exit 0 on a pass, an override or a stage already passed; exit 1 otherwise
- Fails: `--human` at a jury gate (spec_jury, plan_jury, tasks_jury) → "refuse, record nothing, and print `nio jury check <slug> <gate> --human "<reason>" --record`" (FR-62), printed with the jury's gate name (`nio jury check <slug> spec --human "<reason>" --record` at spec_jury), exit 1, checked before any guard; a stage after the current one → `error: <slug> is at <current>, not <stage>`, exit 1, nothing written (FR-16); `--human ""` (empty or blank) → `error: --human needs a reason`, exit 1, nothing written, checked before any guard (FR-26); a pending change record against a file whose owning stage is this stage or an earlier one → `error: <C-ID> is outcome: pending against <file>; settle it first`, exit 1 (FR-38); a parked, suspended or abandoned effort, or one with a stored stop-list wait → CT-9's waiting output (`nio flow start` resumes it), exit 1, nothing written; a guard fails → its output, exit 1, nothing written except FR-41's `fail` line in auto mode (FR-13); the gate commit fails → git's stderr, exit 1, `history.jsonl`, `state.json` and the index restored as they were (FR-20)
- Rules: a stage already passed → "change nothing, add no history line and exit 0" (FR-17); a pass appends a `pass` line, then a `skip` line with `reason` `skipped: not built` for each not-built stage after it, and moves to the next built stage (FR-12, FR-21); "WHEN a transition that is not a gate happens THE SYSTEM SHALL make no commit" (FR-19)
- Rules: at a gate whose guard passes: with `--commit`, or with the auto flag on and no FR-51 risk flag, the lines are written, then `git add -A -- .nio/specs/<slug>` and `git commit -m <message> -- .nio/specs/<slug>` run, `<message>` from CT-6's map (`nio: approve spec` for spec_jury), so the commit holds only the effort folder (FR-18); otherwise "make no commit, record nothing, and print the exact `nio flow done <gate> --commit` command for the human to approve" (FR-48), printed as `nio flow done <stage> --commit <slug> --by human` with exit 0
- Rules: rollback of a failed gate commit: before the append, save the byte length of `history.jsonl`, the bytes of `state.json` (or that it was missing) and the index's tree (`git write-tree`); when `git add` or `git commit` fails, truncate `history.jsonl` to the saved length, rewrite `state.json` from the saved bytes, delete `state.json.new`, and run `git read-tree <saved tree>`; the working tree's other files are never touched (FR-20) [agent]
- Rules: a crash between the append and the commit leaves the `pass` line and the new state in the working tree, uncommitted. The gate then still has no approval commit, so CT-6 shows it waiting for approval (FR-49); the next `done <gate> --commit` finds the newest line is an uncommitted `pass` from this gate at the ledger's current round, appends nothing, and only stages and commits [agent]
- Rules: "WHEN `nio flow done <stage> --human "<reason>"` runs and a guard fails THE SYSTEM SHALL pass the stage and append a history line holding the failing guard output and the reason" (FR-24): kind `override`, the output in `evidence.output_text` beside its hash; this applies to stages that are not jury gates (FR-62); a guard that passes with `--human` given records kind `pass` with the reason, and no `override` line (AC-30); a gate guard `closed` by the human (CT-5) records kind `override` with the ledger's reason, `evidence.blobs` and `evidence.round`, and needs no `--commit` (FR-27, FR-55)
- Rules: git runs through `records.git` in its full mode (CT-19), which returns the exit code and stderr; `flow.py` calls no `subprocess` of its own [human]

### CT-12 `nio flow status` (FR-28, FR-46, FR-57, FR-60, NFR-2, NFR-3) [default]
- Binding: `src/nio/flow.py:status` (new)
- Like: `src/nio/query.py:status`
- Kind: cli
- Shape: `nio flow status` → one line per folder under `.nio/specs/`: `<slug> · <stage> · <auto|manual> · <status> · <last activity>`, `<last activity>` as `YYYY-MM-DD HH:MM` UTC, then ` · override not seen: <stage>: <reason>` per unseen override; a legacy folder as `<slug> · legacy · <last activity>`, an unsupported one as `<slug> · unsupported: <route> · <last activity>`, a broken one as `<slug> · broken: <file>, <where>`
- Accepts: no arguments
- Returns: exit 0; lines in order of last activity, newest first, abandoned efforts last; a folder with no activity at all (no line, no commit) shows `-` and sorts after every folder with activity, before the abandoned ones
- Rules: "print one line per effort, newest activity first, with its state, auto or not, one of `working`, `waiting_for_human: <why>`, `suspended: <cap|stuck>`, `parked: <why>`, `unsupported: <route>`, `abandoned: <why>` or `done`, and its last activity, with abandoned efforts listed last" (FR-28); "take an effort's last activity from its newest history line, or, when it has none, from the newest commit that touched its folder" (FR-46); "WHEN `nio flow status` meets an effort that FR-6 refuses THE SYSTEM SHALL show it as `broken: <file, line or key>` and list the other efforts as usual" (FR-60)
- Rules: the status word's order: abandoned, parked, suspended, a stored or stop-list wait, then CT-6's derived wait, `done`, `working`; a parked effort still shows the stage `where` derives (AC-42) [derived: FR-28, FR-35]
- Rules: `status` never takes a lock and never writes; the `back` line a change owes is written by the effort's next writing call [agent]
- Rules: "answer `nio flow next`, `nio flow status` and `nio flow park` with no model or network call" (NFR-2): `flow.py` imports nothing from `nio.index` or `nio.pack` (RF-15); "print `nio flow status` for 20 efforts of 50 history lines each in under 2 seconds" (NFR-3)

### CT-13 `nio flow park` (FR-30, FR-32) [default]
- Binding: `src/nio/flow.py:park` (new)
- Like: `src/nio/jury.py:dispose`
- Kind: cli
- Shape: `nio flow park <slug> "<why>" --by ...` → `parked <slug>: <why>`
- Returns: sets `pause` = `{"kind": "parked", "why": <why>}` and appends one `park` line with the reason; creates `state.json` and `history.jsonl` first when missing, writing only the `park` line (FR-30) [agent]
- Fails: an empty or blank reason → `error: park needs a reason`; a done effort → `error: <slug> is done; nothing to park`; legacy or unsupported → as CT-10; exit 1 and nothing written (FR-32)
- Rules: "WHEN `nio flow park <slug> "<why>"` runs THE SYSTEM SHALL mark the effort parked with that reason and record it in history" (FR-30)

### CT-14 `nio flow abandon` (FR-52, FR-53, FR-61) [default]
- Binding: `src/nio/flow.py:abandon` (new)
- Like: `src/nio/jury.py:dispose`
- Kind: cli
- Shape: `nio flow abandon <slug> "<why>" --by ...` → `abandoned <slug>: <why>`
- Returns: sets `abandon` = `<why>` and appends one `abandon` line, `from` the stage `where` gives; `status` then shows `abandoned: <why>` with that stage until `nio flow start` resumes it (FR-52, FR-53)
- Fails: "IF `nio flow abandon` is given an empty reason, or the effort is legacy, unsupported or done, THEN THE SYSTEM SHALL refuse and record nothing" (FR-61): exit 1, the folder byte-identical
- Rules: "no skill or agent card SHALL tell an agent to abandon an effort unless the human asked for it" (FR-52), carried by CT-18

### CT-15 `nio flow seen` and unseen overrides (FR-57) [default]
- Binding: `src/nio/flow.py:seen` (new)
- Like: `src/nio/jury.py:dispose`
- Kind: cli
- Shape: `nio flow seen <slug> --by ...` → `seen <n> overrides on <slug>`, appending one `seen` line; with none unseen, `nothing to see on <slug>`, exit 0, no line
- Returns: an override is unseen while no `seen` line follows it in history; CT-6 lists the unseen ones for `next` and `status`
- Rules: "THE SYSTEM SHALL show each override in `nio flow status` and `nio flow next` as an override not yet seen, with its stage and reason, until `nio flow seen <slug>` records that the human saw it" (FR-57)

### CT-16 The `nio flow` command line (FR-7, FR-9, FR-28) [default]
- Binding: `src/nio/cli.py:main` (existing)
- Kind: cli
- Shape: a `flow` subparser with subcommands `next [slug]`, `start slug`, `done stage [slug] [--commit] [--human REASON]`, `status`, `park slug why`, `abandon slug why`, `seen slug`, each writing one requiring `--by` (no default: without it the command refuses and writes nothing; `next` takes it optionally and records a move only when it is given; Q23); the Python functions take `by` as a required argument too; each calls its `flow` function and turns `ValueError`, `flow.Broken` and `flow.Busy` into `error: <message>` with exit 1, as the `jury` branch does
- Rules: `--by human` records `{"role": "human", "host": "", "model": ""}`; the skills tell an orchestrator to pass its own `--by` (CT-18) [human]

### CT-17 `nio run` names its effort (FR-5, FR-33, FR-34) [default]
- Binding: `src/nio/records.py:new_run` (existing)
- Kind: function
- Shape: `new_run(root, link=None) -> run ID`: a plain folder creator; given `link` (a dict), it also writes it as `.nio/runs/<run>/flow.json`, and it checks nothing in it. The CLI's `run` branch takes `nio run [<slug> <stage|T-n>]`, checks them, and passes `{"effort": <slug>, "stage" or "task": <value>, "at": <UTC ISO>}`
- Accepts: no arguments (as today), or a slug with a folder under `.nio/specs/` and a stage in `flow.STAGES` (the state table "Flow"'s stages) or a `T-<n>`
- Fails: in the CLI's `run` branch, before `new_run` is called: one argument only, an unknown slug or an unknown stage → `error: ...`, exit 1, no run folder created [agent]
- Returns: the run ID, printed as today
- Rules: "WHEN `nio run <slug> <stage|T-n>` runs THE SYSTEM SHALL write the effort and the stage or task into the run folder" (FR-33); "WHEN `nio run` runs with no arguments THE SYSTEM SHALL create a run as it does today" (FR-34)
- Rules: a history line's `run` is the newest run whose `flow.json` names the effort and the stage being left (or a task), else `state.json`'s `run`, else `""`; the line's run is then stored as `state.json`'s `run` (FR-5) [agent]

### CT-18 The flow rule in every skill and agent card (FR-1, FR-52, FR-57) [default]
- Binding: `skills/plan/SKILL.md` (existing)
- Kind: file
- Shape: every `skills/*/SKILL.md` and every `src/nio/agents/*.md` carries the line: "Flow state: only `nio flow` writes `state.json` and `history.jsonl`; never edit them. Only the human gives `--human` to `nio flow done`, runs `nio flow seen`, or asks for `nio flow abandon`." Each other mention of either file in those files names a `nio flow` command
- Rules: "no skill or agent card SHALL tell an agent to edit them" (FR-1); "every skill and agent card SHALL say that only the human gives `--human` or runs `nio flow seen`" (FR-57); "no skill or agent card SHALL tell an agent to abandon an effort unless the human asked for it" (FR-52)

### CT-19 Git with its exit code (FR-20) [human]
- Binding: `src/nio/records.py:git` (existing)
- Kind: function
- Shape: `git(root, *args, full=False)`; with `full=True` it returns `(exit code, stdout, stderr)`; without it, stdout lines as today, so every current caller is unchanged (architecture.md, C-261028-dclz)
- Rules: "IF the gate commit fails THEN THE SYSTEM SHALL print git's error, record no transition and leave the state unchanged" (FR-20); CT-11 runs `git add`, `git commit`, `git write-tree` and `git read-tree` through it

## Data model
- **state.json** (spec Key entity) in `src/nio/flow.py:STATE_KEYS` (new) [default]
  - keys: exactly `auto` (bool), `pause` (`{"kind": "parked" | "suspended", "why"}` or null), `abandon` (string or null), `waiting` (the stop-list wait or null), `claims` and `attempts` (objects, left empty until #43), `run` (string). "THE SYSTEM SHALL store in `.nio/specs/<slug>/state.json` only the auto flag, the pause reason, the abandon reason, what the effort waits on, task claims and attempts, and the current run" (FR-3)
  - written as `json.dumps(state, indent=2, sort_keys=True) + "\n"`, so its hash is stable
- **History line** (spec Key entity) in `src/nio/flow.py:record` (new) [default]
  - one JSON object per line, fields as CT-2's Returns. "never rewrite an earlier line" (FR-4)
- **Effort** (spec Key entity) in `src/nio/flow.py:pick` (new) [default]
  - a dated folder `.nio/specs/YYYY-MM-DD-<name>/` whose `spec.md`, if there is one with a `route`, is full-route; its lock `flow.lock` and `.gitignore` (CT-3)
- **budgets** config key in `src/nio/records.py:config` (existing) [derived: FR-40]
  - `budgets.juries`, `budgets.subagents`: positive integers, per effort, read only with the auto flag on; missing means no cap
