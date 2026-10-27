# Intake

## Human, 2026-10-27

> we need to evaluate the imeplentation for spec and we need to do corectens jury, secyrity jury, and other kind of lenses for the implementation

> Okey this should run after we have epics already and after we implement the tasks so that we can jury that implementation

> We do not need to have exact match

(the last line answers: must a juror's code quote match the code word for word?)

## Source: https://github.com/nikolajkarpic/nio/issues/29

### What needs designing

**Evaluating the implementation against the spec**, after each epic. Spec-kit's `implement` ends with "check that implemented features match the original specification" (one line) and trusts checkboxes. `converge` is better: "completion claims are not evidence", with gap types `missing | partial | contradicts | unrequested`, and it appends new tasks without ever rewriting old ones.

Two complementary passes (verify-tasks puts it well: converge finds what is *not built*; verify finds what is *falsely marked built*):

1. **Per-AC evidence.** For every AC in the epic: the test that exercises it (file:line), whether that test ran and passed, and the code that implements it. Missing evidence is a finding. Evidence is *observed* (ran a test, read the code), never *asserted* (the worker said so).
2. **Phantom-completion check** in a fresh context (verify-tasks): the file exists, the file is in the diff, the symbol is defined, the symbol is referenced somewhere (not dead code), and finally a stub check (empty body, TODO), marked as interpretive. Asymmetric error model: "when in doubt, flag".

Plus:
- **Test tampering:** tests deleted, weakened or skipped in the diff are always flagged (NORTH_STAR: "changing a test so it passes").
- **Scope:** `unrequested` code goes to the jury, as work outside the task.
- **Adversarial tester:** runs the spec's journeys, misuse lines (#34, #38) and edge cases against the build.
- **Both directions of drift:** when the code is right and the spec is stale (spec-kit#4940), that's a change request, never a silent spec edit.

### What the design must define

- The evaluation report format and its verdict record. Outcomes as in spec-kit-evaluator: `pass | warn | iterate | clarify | block`, with block on no evidence.
- What the CLI checks deterministically (files, symbols, diff, test run) and what jurors judge.
- How findings become new tasks (append-only, never renumbered) or change requests.



## Decided: the implementation jury (2026-10-27)

**When it runs:** only on real epics from the tasks stage (#42), after the implement stage (#43) has finished their tasks. There's no stand-in subject. Building this gate depends on #42 and #43.

| Gate | CLI first (free) | Core lenses | Triggered (risk flags, #47) |
|---|---|---|---|
| Implementation (per epic) | runs the tests and scripted attacks; per-AC evidence; phantom completion; test tampering; lint and type checks | **conformance** (code against AC, FR and contracts, by gap type), **correctness** (bugs the spec doesn't name: error paths, edge cases, state and decision tables honoured, concurrency) | **security**, **adversary**, **consistency**, **risk and rollback** |

- **Cards:** following #47, existing cards gain an `## At implementation` section. New cards: `conformance`, `correctness` and `risk and rollback`.
- **Jurors only read:** the CLI runs the tests and attacks (misuse lines, #38) and puts the results in the pack. A juror with a hunch asks for a specific run in its finding, and the result feeds the next round. No sandbox is needed.
- **Pack:** the epic's diff, the ACs, FRs and contracts it touches, and the run results. Jurors may open any other file (Read/Grep/Glob).
- **Budget:** the same cap of 6 lens runs per epic. Over the cap, the human sees the planned runs and their cost and picks.
- **Outcomes:** the spec jury's set (approved | rejected | rerun | pending | human). **rejected** means fix tasks were appended to the epic, which goes back to implement and is juried again. Minor findings are listed in the approved verdict, with no separate warn. The #52 convergence rules apply unchanged.
- **Findings become tasks:** they're appended to the epic with new IDs and never rewrite or renumber old ones (gap model above). Spec drift becomes a change request.
- **Grounding:** code quotes don't need an exact match. Cited requirement IDs are still checked to exist, and the refuter validates blocker and major findings against the code.



### Comments

**Decided (2026-10-25): take spec-kit `converge`'s gap model** (`templates/commands/converge.md` @ `67e0f72`).

- Every evaluation finding carries a gap type: **missing** (absent from the code), **partial** (present but doesn't fully satisfy the item), **contradicts** (conflicts with the spec, plan or principles) or **unrequested** (code nothing asked for). Each finding cites the FR, AC or CT it traces to and the evidence (a file or area).
- **Check the code, not the checkboxes:** "completion claims are not evidence". Every task is re-checked whatever its status.
- **Append only:** remediation becomes new tasks with new IDs appended to the epic, and old tasks are never rewritten or renumbered. When nothing is wrong, nothing is written.
- **unrequested** only surfaces scope creep and never deletes code. The task it creates is "justify or remove".
- `quickstart.md` (#41) holds the per-journey runs the evaluator executes as evidence.

---

## Implementation gate: lenses (open, from 2026-10-27)

#47 sets the lenses for the spec, plan and tasks gates, but not the implementation gate. Draft row, run per epic on the diff (#43):

| Gate | CLI first (free) | Core lenses | Triggered (same risk flags) |
|---|---|---|---|
| Implementation | tests ran and passed; every AC has a test at a file:line; touched files are in the diff; symbols are defined and referenced; no tests deleted, skipped or weakened; lint and type checks pass | **conformance** (this issue's evaluator: gap types against AC, FR and contracts), **correctness** (bugs the spec doesn't name: error paths, edge cases, state and decision tables honoured, concurrency) | **security** (auth, permissions, secrets, PII), **adversary** (external input, public API: runs the misuse lines as attacks, #38), **consistency** (touches existing modules), **risk and rollback** (migration, data deletion) |

Following #47, existing cards gain an `## At implementation` section, and only new concerns get new cards.

### Open questions: brainstorm all of these before implementing
1. **Correctness and conformance:** two lenses (spec conformance vs. bugs beyond the spec), or one?
2. **Running code:** implementation jurors are read-only today. Do they run tests and attacks themselves, or judge only the evidence the CLI collects?
3. **Input pack:** does each juror get the diff plus the ACs and contracts it touches, or whole files?
4. **Budget:** does the cap of 6 lens runs per gate (#47) also apply here?

---

**Decided (2026-10-27): correctness and conformance are two core lenses at the implementation gate.**
- **conformance** checks the code against every AC, FR and contract, using this issue's gap types (missing, partial, contradicts, unrequested).
- **correctness** hunts bugs the spec doesn't name: error paths, edge cases, state and decision tables honoured, concurrency.
- Both always run, so that's 2 core runs per epic.

---

**Decided (2026-10-27): the CLI runs the code; jurors only read.**
- `nio` runs the tests and the scripted attacks (misuse lines, #38) and puts the results in the juror pack.
- Jurors stay read-only (Read/Grep/Glob). A juror with a hunch asks for a specific run in its finding, the CLI runs it, and the result feeds the next round.
- No juror needs a sandbox.

---

**Decided (2026-10-27): the juror pack is the diff plus slices, and jurors may open more.**
- Each juror gets the epic's diff, the ACs, FRs and contracts the diff touches, and the CLI's test and attack results.
- Jurors may open any other file with Read/Grep/Glob (unchanged callers, for example). The pack is the default view, not a fence.

---

**Decided (2026-10-27): the implementation gate uses the same cap of 6 lens runs per epic as #47.**
- Over the cap, `nio flow` shows the planned runs and their cost, and the human picks: run all, drop the lowest-hit-rate lenses, or choose. Nothing is skipped silently.

---

**All implementation-gate questions are settled.**

| Gate | CLI first (free) | Core lenses | Triggered |
|---|---|---|---|
| Implementation (per epic) | runs tests and scripted attacks; per-AC evidence; phantom completion; test tampering; lint and type checks | conformance, correctness | security, adversary, consistency, risk and rollback |

- Jurors are read-only. The CLI runs code, and jurors ask for extra runs in their findings.
- Pack: the diff, the ACs, FRs and contracts it touches, and the run results. Jurors may open other files.
- Cap: 6 runs per epic, and going over means the human chooses.

---

**Decided (2026-10-27): the implementation jury runs only on real epics, after their tasks are implemented.**
- No stand-in subject (such as a spec plus a git range). The subject is an epic from the tasks stage (#42) whose tasks the implement stage (#43) has finished.
- So findings become new tasks appended to that epic, as decided above. Task files always exist by then.
- Building this gate depends on #42 and #43.

---

**Decided (2026-10-27): the implementation gate reuses the spec jury's outcomes** (approved | rejected | rerun | pending | human, from `jury.py`).
- **rejected** means fix tasks were appended to the epic. The epic goes back to implement, then the gate runs again.
- There's no separate warn: minor findings are listed in the approved verdict.
- The #52 convergence rules apply unchanged.

---

**Decided (2026-10-27): code quotes don't need an exact match at the implementation gate.**
- A juror may paraphrase or abbreviate the code it points to. The word-for-word quote check (#27) isn't applied to code.
- Requirement IDs (AC, FR, CT) a finding cites are still checked to exist, as at every gate.
- The refuter (`nio-refuter`) still validates blocker and major findings against the code before anything reaches the human.

---

**All of #29's implementation-jury questions are settled.** Building it depends on #42 (tasks/epics) and #43 (implement stage).

---

