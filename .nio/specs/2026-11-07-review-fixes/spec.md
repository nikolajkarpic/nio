---
slug: 2026-11-07-review-fixes
route: full
epic: ""                         # "<epic slug>/R-<n>" when this is a slice of an epic
risk: [external-input, data-deletion] # auth | pii | money | external-input | data-deletion | migration | multi-party | public-api
retired: [OP-1, OP-2, OP-3, OP-4, OP-5, OP-6, OP-7, FR-7, FR-8, AC-11, AC-12] # IDs removed from this spec; never reused
---
<!-- Spec template. WHAT and WHY only, never HOW. Every item ends with its provenance: [human] (the grill
confirmed it), [research: RF-n] (a finding in research.md) or [default] (your proposal; the grill must confirm it).
IDs are permanent: number new items after the highest ever used, never renumber, list removed IDs in `retired`.
Remove a section that doesn't apply; never write N/A. `nio check spec 2026-11-07-review-fixes` checks all of this. -->
# Fix the review's findings in the speed-up PRs

## Summary
One bugfix effort for the defects an independent review (#100) found in the just-merged speed-up PRs: a juror can
forge the refuter's verdict and approve its own gate (#101), wave patches lose CRLF and crash on non-UTF-8 files (#102),
`nio jury next` loops forever on a rerun with no lens to run (#103), and three minor test and evidence gaps (#104).
Each fix is minimal and comes with a test that fails before it. [human]

## Actors and journeys
- **A-1 Orchestrator**: the main agent session driving `nio jury next` and the implement waves; does what each `next:` line says. [research: RF-11]
- **A-2 Juror**: a lens or refuter subagent with read and write tools; reads the content it judges, which may hold an injected instruction. [human]
- **A-3 Maintainer**: runs the self-checks and reads evidence; wants a test result that means what it says. [research: RF-12]

**UJ-1 A gate round with the refuter** (A-1, A-2) [research: RF-1]
1. The orchestrator runs `nio jury next`; lens jurors run in parallel and write their outputs.
2. `nio jury next` writes the refuter batch; the refuter writes `<gate>-refuter.md`.
3. `nio jury next` applies the refuter's verdicts and records the outcome; on `rerun` it names the lenses to re-run.
- Misuse: a lens juror writes `<gate>-refuter.md` itself, refuting its own or a peer's findings, so the gate approves with no refuter run.
- Evidence: #101, #103.

**UJ-2 A wave task lands or is shelved** (A-1) [research: RF-4]
1. A wave task edits files in its worktree; green passes.
2. `land` saves the task's patch and applies it to the main tree; or `shelve` saves the patch and restores the paths.
- Misuse: a task edits a CRLF file or adds a latin-1 file, and the saved patch no longer matches what the worker wrote.
- Evidence: #102.

## User stories

### US-1 Only the refuter's own output, after its batch, can refute (P1) [human]
- **Why this priority:** major safety defect: a juror can approve the gate it judges (#101).
- **Independent test:** the #101 repro as a test: a refuter file written before any refuter batch must not approve the gate.

- **AC-1** (FR-1) Given lens outputs and a `<gate>-refuter.md` written in the same run before any `nio jury next` call collected them, when `nio jury next` runs, then no finding is refuted, no round or outcome is recorded, and it refuses with "refuter output before its batch"; a second call with the file still there refuses the same way, and after the file is deleted the next call prints the refuter batch. [human]
  Observable: the error holds "refuter output before its batch" both times; the ledger has no `refuted` finding and no recorded round; no verdict record is written; after deletion the output holds "## Refuter batch". Level: integration.
- **AC-2** (FR-2) Given a refuter batch listing J-1 and a later refuter output that refutes J-1 and J-2, when `nio jury next` runs, then only J-1's verdict is applied. [agent]
  Observable: J-1 refuted; J-2 (pending in the ledger but not in the batch) stays pending; with a second J-1 block saying `confirmed` after the first, J-1 stays refuted; with a batch listing J-1 and J-3 and no J-3 block, J-3 stays pending. Level: integration.
- **AC-3** (FR-1, FR-2) Given a refuter batch and a refuter output written after it for the batch's IDs, when `nio jury next` runs, then the verdicts apply and the outcome is recorded as before. [agent]
  Observable: the batch's finding is `refuted` (or `confirmed`) as the refuter wrote, the outcome line is printed and a verdict record is written. Level: integration.
- **AC-13** (FR-9) Given a spec-gate run whose lens packs were written, when a lens juror also edits the spec it judges and `nio jury next` then runs on its output, then no output is collected, no round is recorded, and it refuses; after the spec is restored to the judged text, the next call collects the outputs. [human]
  Observable: the error holds "the spec changed after R-…'s packs were written" (the run's ID); the ledger's round is unchanged; no verdict record is written; after the restore the output holds the round's findings. Level: integration.
- **AC-14** (FR-9) Given an implementation-gate run whose lens packs were written, when a new commit for the epic's task lands before the outputs are collected, then it refuses the same way. [human]
  Observable: the error holds "changed after R-…'s packs were written"; the ledger's round is unchanged. Level: integration.

### US-2 Wave patches keep their bytes (P1) [human]
- **Why this priority:** major data loss: a shelved or failed-to-land patch is the only copy of the work (#102).
- **Independent test:** a wave task that edits a CRLF file and adds a latin-1 file lands byte for byte.

- **AC-4** (FR-3) Given a committed `b'a\r\nb\r\n'` file edited in a wave worktree to `b'a\r\nB\r\n'`, plus a new `b'new\r\nfile\r\n'` file and a new latin-1 `b'caf\xe9\n'` file, when `land` runs, then the patch applies and each main-tree file equals the worktree's bytes. [human]
  Observable: no error from `land`; each file's main-tree bytes equal its worktree bytes; the saved patch holds `\r`. Level: integration.
- **AC-5** (FR-4) Given the same changes in the main tree, when `shelve` runs, then the saved patch applies back with `git apply` and restores each file's exact bytes. [agent]
  Observable: after shelve, applying the saved patch gives the pre-shelve bytes of each file. Level: integration.
- **AC-6** (FR-3, FR-4) Given a wave task that only edits LF UTF-8 files, when it lands or is shelved, then the result is as before. [agent]
  Observable: the saved patch's bytes equal `git diff --binary` of the change, and the main-tree file equals the worktree's after `land`. Level: integration.

### US-3 A rerun with no lens to run ends in a real next step (P1) [human]
- **Why this priority:** major: the orchestrator follows `next:` and loops forever (#103).
- **Independent test:** the #103 repro as a test: after `dispose J-1 accepted-risk --by human` and a spec edit, `nio jury next` ends in a `next:` that is not a juror run.

- **AC-7** (FR-10) Given a rejected round whose only finding the human accepted as risk, and a wording edit to one spec item, when `nio jury next` runs, then it starts a fix-check run of every lens that voted in that round, and its `next:` line names those jurors. [human]
  Observable: the output lists a `run <lens>:` line for each lens that voted and a pack for each; a second call before any juror ran prints the same run and the same `run <lens>:` lines. Level: integration.
- **AC-8** (FR-5) Given the same state but an edit that changes only whitespace, when `nio jury next` runs, then its `next:` line says to show the human and no juror is named. [human]
  Observable: the `next:` line starts "next: show the human"; no `run <lens>:` line; no line says "run each juror". Level: integration.
- **AC-9** (FR-5) Given a rerun whose fixes name a lens, when `nio jury next` runs, then it still names that lens to run. [agent]
  Observable: the output holds a `run <lens>:` line for the lens of the fixed finding. Level: integration.

### US-4 Minor test and evidence gaps (P3) [human]
- **Why this priority:** minor findings (#104); fixed only where small (only the `-v` flag is; the other two stay in #104).
- **Independent test:** run `uv run python tests/test_pack.py -v`.

- **AC-10** (FR-6) Given a self-check script run with `-v`, when it runs, then all its tests run and `-v` is not read as a test name. [human]
  Observable: `uv run python tests/test_pack.py -v` prints no "no test named -v", runs more than 0 tests and exits 0. Level: integration.

## Functional requirements
- **FR-1** IF `nio jury next` or `nio jury collect` finds a `<gate>-refuter.md` not yet applied in a run for which the gate's ledger records no refuter batch THEN THE SYSTEM SHALL apply none of its verdicts, record nothing, and refuse with "refuter output before its batch". The ledger records a batch only in a call that printed it, so a file present before that call is refused by that call, and stays refused until it is deleted. [human]
- **FR-2** WHEN THE SYSTEM applies a refuter output THE SYSTEM SHALL apply verdicts only for the finding IDs the run's batches listed, the first verdict per ID counting; any other ID is ignored, and a listed ID with no verdict stays pending. [human]
- **FR-3** WHEN `land` saves and applies a wave task's patch THE SYSTEM SHALL keep the patch's bytes as git produced them, with no decoding and no newline translation. [human]
- **FR-4** WHEN `shelve` saves a task's patch THE SYSTEM SHALL keep the patch's bytes as git produced them, with no decoding and no newline translation. [human]
- **FR-5** IF a gate's outcome is `rerun` and no lens is named to re-run THEN THE SYSTEM SHALL name no juror and print a `next:` line that says to show the human. [human]
- **FR-6** THE SYSTEM SHALL let a self-check script run with flag words such as `-v` and not read them as test names. [human]
- **FR-9** IF new lens juror outputs arrive in a run whose judged version changed since the run's packs were written (the version is the git blob of the spec, plan or tasks text, or the epic's last commit, as the packs recorded it) THEN THE SYSTEM SHALL collect none of them and refuse with "the spec (or plan, tasks, implementation-E-n) changed after R-…'s packs were written", naming the two ways on: restore the judged version, or start a new run (`nio jury next` without `--run`). A refuter output needs no check of its own: a change after the lens outputs were collected makes the outcome `rerun`. [human]
- **FR-10** IF a gate's round was rejected, the artefact changed since in anything but whitespace (an item, a section's text, a table or the front matter), and no lens has a fix to check THEN THE SYSTEM SHALL re-run every lens that voted in that round on what changed, as it does for an approved gate that changed. [human]

## Non-functional requirements
- **NFR-1** THE SYSTEM SHALL have, for each of FR-1 to FR-6, FR-9 and FR-10, at least one test that fails on `main` at 548eacb and passes after the fix; the repros in #101, #102 and #103 become tests. [human]

## Success criteria
- **SC-1** The #101, #102 and #103 repros, run as tests, fail on `main` and pass after the fix. [human]
- **SC-2** A decision matrix (Decision | Options considered | Chosen | Why | Consequence) is in `.nio/specs/2026-11-07-review-fixes/decisions.md` and posted on #101. [human]
- **SC-3** The two #104 items not fixed (misuse tests on a self-check suite, a covered journey's `Expected:`) stay in #104 with a note saying why. [human]

## Non-goals
- A host guard (PreToolUse hook or permission rules) limiting where a juror writes (#101 proposal 3); #101 stays open for it. [human]
- Stopping a juror from overwriting a peer's output or reading a faster peer's output (#101); it needs the host guard. [human]
- Any refactor beyond the lines each fix needs. [human]

## Open points

## Decisions
- A refuter file counts only for a run whose batch was printed, and only for that batch's IDs (FR-1, FR-2; #101 proposal 1).
- Juror outputs are refused when the judged version changed since the packs were written; no whole-repo git snapshot (grill Q1, [agent], RF-3).
- A rerun with nothing to check re-runs every voting lens when items changed, else shows the human (grill Q2, [agent], RF-6, RF-7).
- Two #104 items stay in #104: covered journeys' `Expected:` and misuse tests on a self-check suite (grill Q3, Q4, [agent], RF-9, RF-10).
- `-v` keeps working: selfcheck skips flag words (grill Q5, [agent], RF-8).
