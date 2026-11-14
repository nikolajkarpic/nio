---
slug: 2026-11-14-effort-jury
route: full
epic: ""                         # "<epic slug>/R-<n>" when this is a slice of an epic
risk: [multi-party, migration]   # auth | pii | money | external-input | data-deletion | migration | multi-party | public-api
retired: [OP-1, OP-2, OP-3, OP-4, OP-5, OP-6, OP-7, OP-8, OP-9, OP-10, OP-11, OP-12, OP-13, OP-14]  # IDs removed from this spec; never reused
---
<!-- Spec template. WHAT and WHY only, never HOW. Every item ends with its provenance: [human] (the grill
confirmed it), [research: RF-n] (a finding in research.md) or [default] (your proposal; the grill must confirm it).
IDs are permanent: number new items after the highest ever used, never renumber, list removed IDs in `retired`.
Remove a section that doesn't apply; never write N/A. `nio check spec 2026-11-14-effort-jury` checks all of this. -->
# Replace the per-epic implementation juries with one jury on the whole effort diff before the PR

## Summary
Today every epic of an effort gets its own implementation jury, run by the orchestrator that built it, which under
delegation approves its own gates; nobody judges the whole change, and per-epic gates plus their fix loops take
55–69% of implementing time. This spec replaces the per-epic implementation juries with one jury, the `pr` gate, on
the full `main...HEAD` diff: an epic now closes when its tasks' own tests have passed, and the whole suite runs once,
at the `pr` gate; at the end the run opens the pull request, and a fresh agent that did not build the effort drives the implementation lenses, the refuter and one new
integration lens, then posts its verdict on the pull request as a comment. Only the human approves, by recording the
gate with a human-only command (#77 lever 10, #100). The re-measure of the time saved is done separately by running an effort. [human]

## Actors and journeys
- **A-1 Human owner**: runs efforts through nio, wants them faster and the whole change reviewed; the only one who may approve the `pr` gate or merge the pull request. [human]
- **A-2 Building orchestrator**: the agent (or driver) that implemented the effort's tasks; it may not drive or approve the `pr` gate. [human]
- **A-3 Fresh gate driver**: an agent session that did not build the effort and drives the `pr` gate's jury. [human]
- **A-4 Jurors**: the implementation lenses, the integration lens and the refuter, reading the whole effort diff. [human]

**UJ-1 Whole-effort review on the pull request** (A-2, A-3, A-4, A-1) [derived: FR-1, FR-2, FR-3, FR-11, FR-15, FR-16]
1. The building orchestrator finishes the last task of the last epic; at each epic's end only its tasks' own tests ran, no jury.
2. The run pushes the branch and opens the pull request.
3. A fresh driver starts the `pr` gate on the full `main...HEAD` diff, out-of-flow commits included, and the whole suite runs once.
4. The jurors and the refuter judge the diff; confirmed findings become fix tasks in the `PR fixes` epic, built through the normal implement steps, then the suite, a push that updates the pull request, and the gate's fix check, under the round cap.
5. The driver posts its verdict on the pull request as one comment starting `APPROVED` or `REQUEST_CHANGES` and naming the head commit judged (a later round edits that comment), and the run stops.
6. The human reads the comment and the outcome, and approves by recording the gate with the human-only command, or rules on what is still open; a merge alone records nothing.
- Misuse: the building orchestrator drives the `pr` gate itself, or an agent approves the gate or merges the pull request.
- Evidence: issues #77 (lever 10) and #100; 2026-11-08 measurement of per-epic gate rounds (2, 2, 3, 2, 7, 3, 2, 2); RF-1 (the builder closed 39 of 41 epic gates); RF-2 (hand fixes on two of three branches).

## User stories

### US-1 One implementation jury per effort, on the whole diff (P1) [human]
- **Why this priority:** per-epic gates cost an estimated 50–70 min per effort, and nobody judges the whole change today.
- **Independent test:** build a two-epic effort to its last task and check that no epic jury ran, each epic closed on its tasks' own tests, the whole suite ran once at the `pr` gate, and the `pr` gate's packs cover the full `main...HEAD` diff.

- **AC-1** (FR-1) Given an effort with two epics, when the last task of the first epic is done and its tasks' own tests pass, then no implementation jury starts, the whole suite does not run, and the effort goes on to the second epic's tasks. [human]
  Observable: no `implementation-E-1` ledger or pack exists; the closing task's review step (a test run, not a juror) ran the epic's tasks' tests, not the full suite; `nio flow status` names the next task of E-2. Level: integration.
- **AC-16** (FR-1) Given the last task of an epic is done, when one of its tasks' own tests fails, then the epic does not close, the effort stays in `implementing`, and it does not go on. [human]
  Observable: the closing task's review step (its test run) names the failing tests; `nio flow status` shows `implementing` and no task of the next epic. Level: integration.
- **AC-2** (FR-2) Given every task of every epic is done, when the flow moves on, then the effort enters the `pr` gate and nowhere else. [human]
  Observable: `nio flow status` shows the `pr` gate as the current stage; the effort is not `done`; the gate's evidence holds one whole-suite run. Level: integration.
- **AC-3** (FR-3) Given a commit on the branch that no task made (a hand fix or a merge resolution), when the `pr` gate's packs are built, then that commit's changes are in the judged diff. [human]
  Observable: the packs' diff contains the hand-made change's lines. Level: integration.
- **AC-4** (FR-4) Given an effort whose spec has no risk flags, when the `pr` gate's lenses are chosen, then correctness, conformance, adversary, consistency, integration and the refuter all run. [human]
  Observable: the lens list printed for the gate names all five lenses and the refuter. Level: integration.
- **AC-5** (FR-5) Given a spec with risk flags, when the `pr` gate's lenses are chosen, then the lenses those flags add today also run. [human]
  Observable: the lens list includes each risk lens the flag table maps to. Level: integration.
- **AC-6** (FR-7, FR-15) Given the `pr` gate's round ends with a confirmed blocker, when the driver routes it, then a fix task is made in the `PR fixes` epic, built through the normal implement steps, the whole suite runs, and the gate's fix check follows, within `jury.max_rounds`. [derived: FR-7, FR-15, FR-17]
  Observable: a new fix task under the `PR fixes` epic cites the finding in `From:`; its review ran the suite; the next round's packs exist; no round past the cap starts except the automatic one. Level: integration.
- **AC-17** (FR-13) Given an effort diff over `jury.split_lines` changed lines, when the `pr` gate's packs are built, then each requirement-checking lens gets one pack per epic, holding that epic's diff, and the integration lens gets one pack over the whole change at summary level. [human]
  Observable: the packs of correctness, conformance, adversary and consistency number one per epic, plus one more holding the commits outside any epic (out-of-flow commits and the `PR fixes` epic); the integration pack covers every changed file. Level: integration.
- **AC-27** (FR-13) Given an effort diff over `jury.split_lines` with a hand-fix commit and a `PR fixes` task, when the `pr` gate's packs are built, then the hand fix's and the fix task's lines are in the extra pack of each requirement-checking lens and in no epic's pack. [human]
  Observable: the extra pack of each of those lenses contains both changes' lines; no per-epic pack does. Level: integration.
- **AC-18** (FR-14) Given a lite-route effort whose tasks are all done, when the flow moves on, then it enters the `pr` gate, and no implementation jury ran at its epics' ends. [human]
  Observable: no `implementation-E-n` ledger exists; `nio flow status` shows the `pr` gate. Level: integration.

### US-2 An integration lens judges the change as a whole (P2) [human]
- **Why this priority:** cross-epic fit, duplicated helpers and dead code are what no per-epic jury can see; they come after the gate itself.
- **Independent test:** give the `pr` gate a diff where two epics add the same helper and check the integration lens raises it.

- **AC-7** (FR-6) Given a diff in which two epics each add a helper doing the same thing, when the integration lens runs, then it raises a finding naming both. [human]
  Observable: an integration finding cites both files. Pass rule: on the fixed fixture diff, it holds in at least 2 of 3 runs. Level: e2e.
- **AC-8** (FR-6) Given a diff that adds a function nothing calls, when the integration lens runs, then it raises a dead-code finding. [human]
  Observable: an integration finding names the function. Pass rule: on the fixed fixture diff, it holds in at least 2 of 3 runs. Level: e2e.
- **AC-9** (FR-6) Given a diff with no duplication, dead code or cross-epic mismatch, when the integration lens runs, then it raises no finding of those kinds. [human]
  Observable: the lens output lists no integration finding. Pass rule: on the fixed fixture diff, it holds in at least 2 of 3 runs. Level: e2e.

### US-3 The `pr` gate is independent of the builder and only the human approves it (P1) [human]
- **Why this priority:** under delegation the builder approves its own gates today; the whole point is an independent judgement.
- **Independent test:** run an auto effort to the `pr` gate and check the pull request is open with one verdict comment, and the gate stays open until the human records it with the human-only command.

- **AC-10** (FR-8) Given the last task of the last epic is done, when the driver that built it ends its unit, then the `pr` gate is a new unit, and its driver is a fresh one started from `nio flow brief` alone. [human]
  Observable: `nio flow next` names the `pr` gate as the next unit; the jury and implement skills start a new driver for it with the brief as its only input. Level: integration.
- **AC-11** (FR-9) Given the `pr` jury's verdict is approved and the effort's auto flag is on, when an agent runs `nio flow done` for the gate without the human-only command, then it is refused and the gate waits for the human. [human]
  Observable: non-zero exit; the effort is still at the `pr` gate; no approval commit. Level: integration.
- **AC-21** (FR-9) Given the `pr` jury's verdict is approved and the effort's auto flag is off, when an agent runs `nio flow done` for the gate without the human-only command, then it is refused and the gate waits for the human. [human]
  Observable: non-zero exit; the effort is still at the `pr` gate; no approval commit. Level: integration.
- **AC-22** (FR-9) Given the effort is at the `pr` gate, when the pull request is merged and no approval was recorded with the human-only command, then the gate stays open and the effort is not `done`. [human]
  Observable: `nio flow status` still shows the `pr` gate; no `nio: approve pr` commit. Level: integration.
- **AC-23** (FR-9, FR-10) Given a finding of the `pr` gate is unruled, when the human runs the human-only approve command, then it is refused and names the unruled finding. [human]
  Observable: non-zero exit naming the finding's ID; the effort is still at the `pr` gate. Level: integration.
- **AC-12** (FR-9) Given the `pr` jury's verdict is approved and no finding is unruled, when the human records the gate with the human-only command, then the effort moves on and the approval is committed. [human]
  Observable: `nio flow status` no longer shows the `pr` gate; a `nio: approve pr` commit exists. Level: integration.
- **AC-13** (FR-10) Given the `pr` gate stops at the round cap with open findings, when the human rules on each, then the gate closes as the round-cap rules say. [human]
  Observable: each finding's disposition is set `--by human`; the gate is closed. Level: integration.
- **AC-14** (FR-11) Given the gate's verdict is ready, when the driver finishes, then the outcome (verdict, findings fixed, findings open, findings the system closed) is shown to the human in one message. [human]
  Observable: the driver's summary lists the verdict and each finding with its disposition. Level: integration.
- **AC-19** (FR-16) Given an effort reaches the `pr` gate, auto or not, when the gate's jury has its verdict, then the pull request is open on the pushed branch and holds one comment from the gate's driver whose first word is `APPROVED` or `REQUEST_CHANGES`, followed by the head commit judged, the verdict and the findings; then the run stops, and nothing is merged. [human]
  Observable: `gh pr view` shows the open pull request and the comment naming the head commit; the branch is unmerged; the effort waits at the `pr` gate. Level: e2e.
- **AC-24** (FR-16) Given a pull request is already open for the branch and the gate has posted its verdict comment, when the gate pushes again and a later round ends, then no second pull request is opened and the same comment is edited to the new verdict. [human]
  Observable: `gh pr list` shows one pull request for the branch; `gh pr view` shows one verdict comment, holding the latest verdict and head commit. Level: e2e.
- **AC-25** (FR-16) Given the push, the pull request's opening or the comment fails, when the gate tries it, then the run stops with a message naming the step that failed and the gate stays open. [human]
  Observable: non-zero exit; the message names push, pull request or comment; the effort is still at the `pr` gate. Level: integration.
- **AC-26** (FR-16) Given a verdict comment names head commit H, when a commit lands on the branch after H, then the verdict is stale and the human-only approve command refuses until a round judges the new head. [human]
  Observable: the approve command exits non-zero naming the verdict as stale; the comment's commit differs from `git rev-parse HEAD`. Level: integration.
- **AC-20** (FR-17) Given the `PR fixes` epic's tasks are all done, when the flow moves on, then the branch is pushed, the open pull request is updated, no new pull request or gate starts, and the gate's fix check runs. [human]
  Observable: `gh pr list` shows one pull request whose head is the last fix commit; the gate's next round's packs exist; the `pr` gate's ledger is the same one. Level: integration.

### US-4 Efforts already implementing when this lands keep working (P2) [human]
- **Why this priority:** in-flight efforts have approved epic gates and open epic ledgers; they must not break or be judged twice by accident.
- **Independent test:** take an effort with E-1's gate approved and E-2 in progress, upgrade, and check E-2 closes on its tasks' own tests and the `pr` gate follows.

- **AC-15** (FR-12) Given an effort in `implementing` with some epic gates already closed, when this change lands, then its closed gates stay closed, its remaining epics (an epic part-way through its tasks included) close on their tasks' own tests, and its `pr` gate judges the whole effort diff, already-juried epics included; no history line written before it is rewritten. [human]
  Observable: `history.jsonl` lines written before the change are byte-identical; `nio flow status` names the next task or the `pr` gate, not an error; the `pr` gate's packs include E-1's changes. Level: integration.
- **AC-28** (FR-12) Given an effort whose epic is already in its old implementation jury (mid-round, capped, or with open fix tasks) when this change lands, when the flow moves on, then that epic finishes its old jury first, its findings kept, and only then does the next epic start. [human]
  Observable: the epic's old ledger still lists its open findings; `nio flow status` names that jury's next step, not a task of the next epic. Level: integration.

## Functional requirements
- **FR-1** WHEN an epic's tasks are done THE SYSTEM SHALL close the epic only when its tasks' own tests pass, with no reviewers, no rounds and no whole-suite run, and then go on to the next epic's tasks; when one fails the effort stays in `implementing`. [human]
- **FR-2** WHEN every task of every epic, fix tasks included, is done THE SYSTEM SHALL move the effort to one `pr` jury gate before it can be done, and run the whole test suite once there. [human]
- **FR-3** WHEN the `pr` gate's packs are built THE SYSTEM SHALL judge the full `main...HEAD` diff, so commits made outside the flow are covered. [human]
- **FR-4** WHEN the `pr` gate's lenses are chosen THE SYSTEM SHALL always run correctness, conformance, adversary, consistency and integration, and the refuter on their findings. [human]
- **FR-5** WHEN the spec carries risk flags THE SYSTEM SHALL also run at the `pr` gate the lenses those flags add at a gate today. [human]
- **FR-6** WHEN the integration lens runs THE SYSTEM SHALL have it judge cross-epic fit, duplication, dead code and needless complexity across the whole diff. [human]
- **FR-7** THE SYSTEM SHALL apply the existing jury rules to the `pr` gate: the stop rule, the round cap `jury.max_rounds`, the automatic round, the capped batch and fix tasks for confirmed findings. [human]
- **FR-8** THE SYSTEM SHALL run the `pr` gate as its own unit of work, in a fresh driver started from `nio flow brief` alone, never in the driver that built the effort's tasks. [human]
- **FR-9** THE SYSTEM SHALL record the `pr` gate's approval only through a human-only command, and only when no finding is unruled and the verdict is not stale; it SHALL refuse any other approval, whatever the effort's auto flag or the jury's verdict, and a merge of the pull request alone SHALL record nothing. [human]
- **FR-10** WHEN the human rules on the `pr` gate's open findings THE SYSTEM SHALL close the gate under the same rulings as any capped gate. [human]
- **FR-11** WHEN the `pr` gate's jury has a verdict THE SYSTEM SHALL give the human its outcome: the verdict, the findings fixed, the findings still open and the findings the system closed itself. [human]
- **FR-12** WHEN this change lands THE SYSTEM SHALL leave the history of efforts already implementing unchanged, keep their closed epic gates, close their remaining epics, an epic part-way through its tasks included, on their tasks' own tests, let an epic already in its old implementation jury finish that jury first, and judge their whole effort diff, already-juried epics included, at the `pr` gate. [human]
- **FR-13** WHEN the effort diff is over `jury.split_lines` changed lines (1,500 by default) THE SYSTEM SHALL give each requirement-checking lens one epic's diff per juror, plus one more juror on the commits outside any epic (out-of-flow commits and the `PR fixes` epic), run in parallel, and only the integration lens the whole change at summary level. [human]
- **FR-14** WHEN an effort runs the lite route THE SYSTEM SHALL give it the `pr` gate, with its pull request and verdict comment, instead of its implementation juries. [human]
- **FR-15** WHEN the `pr` gate routes a finding to a fix task THE SYSTEM SHALL put it in one closing `PR fixes` epic, created on the first such task, and run it through the normal implement steps, then the whole suite, then the gate's fix check. [human]
- **FR-16** WHEN an effort reaches the `pr` gate, auto or not, THE SYSTEM SHALL push the branch and open the pull request (reusing one already open for the branch), have the gate's fresh driver post one comment whose first word is `APPROVED` or `REQUEST_CHANGES` followed by the head commit judged, the verdict and findings, edit that same comment after each later round, then stop and wait for the human, and never merge; a verdict is stale once the branch head moves past its commit; a failed push, pull request or comment SHALL stop the run with a message naming the step. [human]
- **FR-17** WHEN the `PR fixes` epic's tasks are all done THE SYSTEM SHALL push the branch to update the open pull request and run the `pr` gate's fix check, never a new pull request or a new gate. [human]

## Rules
### State table: effort after its tasks (start: implementing; final: done)
| State | last task of a non-last epic done, its tasks' tests pass (next epic starts) | last task of the last epic done, its tasks' tests pass (pull request opened, whole suite runs) | last task of an epic done, one of its tasks' tests fails (epic stays open) | `PR fixes` tasks all done (push updates the pull request, fix check) | round ends with confirmed blocker, below cap (fix tasks in `PR fixes`, next round) | round reaches the cap with findings open (capped batch for the human) | verdict posted on the pull request (waits for the human) | human approves the gate with the human-only command, no finding unruled | agent approves the gate, or the pull request is merged without that command | Src |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| implementing | → implementing | → pr gate | → implementing | ignore | ignore | ignore | ignore | reject: no pr gate yet | reject: no pr gate yet | [human] |
| pr gate | ignore | ignore | ignore | → pr gate | → pr gate | → pr gate | → pr gate | → done | reject: only the human-only command approves the pr gate | [human] |
| done | ignore | ignore | ignore | ignore | ignore | ignore | ignore | ignore | ignore | [human] |

### Decision table: who may close the `pr` gate
| Closer (human, building agent, fresh agent, merge) | Auto flag (on, off) | → outcome | Src |
| --- | --- | --- | --- |
| human | - | through the human-only command: gate closes when no finding is unruled and the verdict is not stale; refused otherwise | [human] |
| merge | - | a merge of the pull request records nothing; the gate stays open | [human] |
| building agent | - | refused | [human] |
| fresh agent | on | refused; waits for the human | [human] |
| fresh agent | off | refused; waits for the human | [human] |

## Key entities
- **`pr` gate**: the one implementation jury gate of an effort, after its last task, on its open pull request; its own ledger and rounds. [human]
- **Effort diff**: the full `main...HEAD` diff of the effort's branch, out-of-flow commits included; `main` is the remote's default branch, and commits that land there after the branch began are not in it. [human]
- **Integration lens**: a new lens card judging cross-epic fit, duplication, dead code and needless complexity. [human]
- **Fresh gate driver**: an agent session started for the `pr` gate alone, from `nio flow brief`, that made none of the effort's task commits. [human]
- **`PR fixes` epic**: the closing epic that holds the `pr` gate's fix tasks, created on the first one. [human]
- **Verdict comment**: the one pull request comment the gate's driver posts, first word `APPROVED` or `REQUEST_CHANGES`, then the head commit judged, the verdict and findings; edited in place after each later round. [human]

## Success criteria
- **SC-1** An effort with N epics runs exactly one implementation jury gate, the `pr` gate, whatever N is. [human]
- **SC-2** No effort reaches `done` without the human approving its `pr` gate, and nio merges no pull request. [human]
- **SC-3** A change committed outside the flow on the effort's branch is always inside the judged diff. [human]

## Non-goals
- The re-measure of the time saved; it is done separately by running an effort. [human]
- Lightening the per-epic juries to conformance only, as #100 floated; this spec removes them instead. [human]
- Merging the pull request; nio still never merges. [human]
- A formal GitHub review approval on the pull request; GitHub refuses one from the account that opened it. [research: RF-12]

## Glossary
- **`pr` gate**: the whole-effort implementation jury, on the open pull request. Never "final gate" or "PR review".
- **Effort diff**: the `main...HEAD` diff of the effort's branch, where `main` is the remote's default branch. Never "branch diff".
- **Out-of-flow commit**: a commit on the branch that no task made, such as a merge resolution or a hand fix.
- **Fresh gate driver**: the agent that drives the `pr` gate and built none of the effort.
- **`PR fixes` epic**: the closing epic of an effort that holds the `pr` gate's fix tasks.
- **Verdict comment**: the pull request comment, first word `APPROVED` or `REQUEST_CHANGES`, that carries the `pr` gate's verdict.

## Risks and evidence against
- Bigger diffs give jurors less context per change: conformance was already "limited" on E-1 of an earlier effort (#77 lever 10); FR-13 splits a large diff by epic. [human]
- Findings land after later epics have built on the code, so a fix can ripple through several epics (#77 lever 10). [human]
- E-2 of one effort alone had 13 confirmed majors; one gate on the whole effort may raise more findings than the round cap can settle (#77 lever 10). [human]
- #77 recommended deferring this lever until levers 2, 3 and 7 were re-measured. [human]

## Decisions
- The `pr` gate keeps the jury stop rule: after the first review only confirmed blockers start rounds, plus one final fix check: D-261026-r52z (memory, 2026-10-26).
- Evidence reuses the epic-close review suite run only when it ran the configured suite and passed; at the `pr` gate it is collected once on the effort diff, where the whole suite runs once (RF-8): D-261106-grjt (memory, 2026-11-06).
- Tests carry no spec IDs; the conformance lens matches tests to ACs on the effort diff too: D-261027-b44u (memory, 2026-10-27).
- An epic closes when its tasks' own tests have passed (already proved at each task's green); no reviewers, no rounds, no whole-suite run; the whole suite runs once, at the `pr` gate; a failing test at an epic's last task keeps the effort in `implementing`. This follows D-261106-ltsr (memory), so no change request: the human, Q8 (supersedes Q1).
- The `pr` gate's fix tasks go into one closing `PR fixes` epic, built through the normal implement steps, the suite, then the fix check: the human, Q2.
- At the `pr` gate the run opens the pull request and the fresh driver posts a verdict comment (`APPROVED` or `REQUEST_CHANGES`), then stops; never merges; a comment, not a GitHub review approval (RF-12): the human, Q3.
- Over `jury.split_lines` (1,500 changed lines by default) the requirement lenses get one epic's diff each, the integration lens the whole change at summary level: the human, Q4; the setting's name is an agent call.
- Efforts already implementing switch at once: an epic part-way through its tasks closes on the new rule, an epic already in its old implementation jury finishes that jury first, and their `pr` gate covers the whole diff: the human, Q5, refined by Q9.
- Lite-route efforts get the `pr` gate instead of their implementation juries: the human, Q6.
- The `pr` gate's own default `jury.max_runs` (the existing cap on lens runs per gate, each juror counted; not the round cap `jury.max_rounds`) is 7, so every lens the risk table can add runs without asking; a configured value still wins (RF-10): an agent call.
- `main` in the effort diff is the remote's default branch, as the pre-push hook finds it (RF-5, RF-6): an agent call.
- The `pr` gate's approval is recorded only through a human-only command; a merge records nothing; the verdict names the head commit judged and goes stale when it moves; an open pull request is reused and its one verdict comment edited each round; a failed push, pull request or comment stops the run; after the `PR fixes` epic the push updates the pull request and the fix check runs; with a split diff, commits outside any epic get one more pack; the e2e lens ACs pass in 2 of 3 runs on a fixed fixture: the human, Q9.
- The `pr` gate runs in its own fresh driver; nio can't tell sessions apart, so independence comes from the unit, not from refusing an identity (RF-7, RF-11): derived from Q3.
- The remaining proposals (FR-5, AC-5, AC-9, FR-10, AC-13, the `done` state row) and the agent calls (fresh driver from the brief alone, `pr` gate `jury.max_runs` 7, `main` = the remote's default branch, `jury.split_lines` 1,500) were confirmed as written: the human, Q7.
