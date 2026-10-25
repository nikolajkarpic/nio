---
slug: jury
route: full
epic: ""                         # "<epic slug>/R-<n>" when this is a slice of an epic
risk: []                         # auth | pii | money | external-input | data-deletion | migration | multi-party | public-api
retired: [OP-1, OP-2, OP-7, OP-9, OP-10, OP-11, OP-5, A-5, OP-6, OP-3, OP-4, OP-8]                      # IDs removed from this spec; never reused
---
<!-- Spec template. WHAT and WHY only, never HOW. Every item ends with its provenance: [human] (the grill
confirmed it), [research: RF-n] (a finding in research.md) or [default] (your proposal; the grill must confirm it).
IDs are permanent: number new items after the highest ever used, never renumber, list removed IDs in `retired`.
Remove a section that doesn't apply; never write N/A. `nio check spec jury` checks all of this. -->
# The jury skill: run the lenses on a settled spec and reach a verdict

## Summary
`@nio:jury` takes a spec the grill settled to a verdict. It picks the lenses the spec triggers, runs each as an
independent juror with a fresh context pack, has the refuter validate the serious findings, disposes of findings
within each actor's authority, and composes the gate outcome with `nio jury`. The verdict format, the ledger and the
`nio jury collect | dispose | check` commands already exist (#27); this skill is the part that picks lenses and builds
packs, left out of #27. It covers the spec gate; the plan and tasks gates come with their stages. [human]

## Actors and journeys
- **A-1 Human**: owns the spec; wants a verdict they can trust without reading every lens output, and is the only one who accepts a risk or rules a finding out of scope. [human]
- **A-2 Jury agent**: the agent running the skill in the human's session, on any host; picks lenses, builds packs, runs jurors and the refuter, records dispositions, composes the outcome. [research: RF-1]
- **A-3 Juror**: one lens run as an independent subagent with a fresh context pack; returns reasoning and at most 5 findings. [human]
- **A-4 Refuter**: validates the blocker and major findings of a gate in one batch, confirming or refuting each. [human]

**UJ-1 Run the spec jury to a verdict** (A-1, A-2, A-3, A-4) [research: RF-1]
1. The jury agent confirms the spec passes `nio check spec <slug> --gate` and reads the lenses it lists.
2. Triage picks the rung; the agent builds one pack per lens and runs the jurors.
3. The agent collects their outputs into the ledger, runs the refuter on the batch, and collects again.
4. The agent disposes what it may, sends behaviour changes to the grill and the rest to the human.
5. `nio jury check` composes the outcome; the human is told the verdict and what the agent decided.
- Misuse: the agent drops a lens, edits a lens output, disposes a finding outside its authority, or reports
  "approved" without running `nio jury check`.
- Evidence: issues #27 and #47.

**UJ-2 Fix and re-review** (A-1, A-2, A-3) [research: RF-1]
1. The gate is rejected; the agent applies the spec-fixes it may and the grill settles the rest.
2. Only the blocking lenses re-run, on the changed sections and their own findings.
3. A finding that fails 2 rounds goes to the human.
- Misuse: every lens re-runs on every fix, or a lens keeps re-running without end.
- Evidence: issue #47.

## User stories

### US-1 Run the lenses the spec triggers (P1) [agent]
- **Why this priority:** without it nothing feeds `nio jury collect`; picking lenses and building packs is the part
  #27 left out.
- **Independent test:** run the skill on a settled spec with `risk: [pii]`; testability, logic and security each get
  one pack and one output in the run folder, and no pack holds the author's reasoning.

- **AC-1** (FR-1) Given a spec that fails `nio check spec <slug> --gate`, when the jury starts, then no lens runs and the human is told to finish the grill first. [derived: FR-1]
  Observable: no file under `.nio/runs/<run>/jury/`; the message names the gate errors. Level: integration.
- **AC-2** (FR-2) Given a settled spec with `risk: [pii]` and 5 FRs, when the jury picks lenses, then it runs testability, logic and security, and no others unless triage added one with a reason. [human]
  Observable: the lens outputs in the run are exactly `spec-testability`, `spec-logic` and `spec-security` (plus any lens triage named with its reason). Level: integration.
- **AC-3** (FR-3) Given a spec flagged `auth`, when the jury starts, then the rung is high; given a spec with no flags, the rung is low. [human]
  Observable: the ledger and the verdict record carry tier high and low respectively. Level: integration.
- **AC-4** (FR-4) Given the logic lens is about to run, when its pack is built, then the pack holds the spec, the card's `## At spec` section, the `nio check spec` output and the lens output template, and nothing from the grill log, the conversation or another juror. [human]
  Observable: the pack's contents list matches exactly; no `## At plan` text, no `grill.md` text, no other lens's output. Level: integration.
- **AC-5** (FR-5) Given the spec was drafted by one model, when a juror runs, then it runs on a different model where the host offers one. [human]
  Observable: the `by:` field of each lens output names a model other than the drafter's, or the human was told why not. Level: integration.
- **AC-6** (FR-6) Given a juror finishes, when its output is written, then it is at `.nio/runs/<run>/jury/spec-<lens>.md` (`-<n>` for a second or third juror) in the lens output format. [human]
  Observable: `nio jury collect` reports the file as valid. Level: integration.
- **AC-25** (FR-24) Given the scope and consistency lenses are triggered, when their packs are built, then scope's pack holds `intake.md` and consistency's holds the memory pack, and no other lens gets either. [research: RF-10]
  Observable: the two packs contain those files; the other packs don't. Level: integration.
- **AC-27** (FR-26) Given the security lens is triggered and has no card, when the jury starts, then no lens runs and the human is told the security card is missing. [human]
  Observable: no output in the run's jury folder; the message names the missing card. Level: integration.
- **AC-28** (FR-27) Given `nio pack` for the spec returns an approved decision, and FR-4 maps to no intake sentence, when the jury picks lenses, then consistency and scope both run and their reasons are shown. [human]
  Observable: the lens list includes consistency (reason: the decision's ID) and scope (reason: FR-4 not in the intake). Level: integration.
- **AC-29** (FR-28) Given a host without subagents, when a lens must run, then the jury agent doesn't play it: it writes the juror's pack to the run folder, asks the human to run it in a fresh session, and the verdict records that it was run by hand. [human]
  Observable: the pack file exists, no lens output was written by the jury agent's own session, and the verdict notes the manual run. Level: e2e.

### US-2 Validate the findings before anyone acts on them (P1) [agent]
- **Why this priority:** self-reported confidence clusters high and fluent findings sway readers; only grounded and
  refuter-confirmed findings may block.
- **Independent test:** feed a run with one blocker, one minor and one invalid output; the invalid lens re-runs once,
  the refuter sees only the blocker, and the minor is never sent to it.

- **AC-7** (FR-7) Given every planned lens output of a round exists, when the agent collects, then it runs `nio jury collect <slug> spec --run <run>` with one `--expect` per planned lens and the rung triage picked. [human]
  Observable: the ledger's `expect` lists every planned lens and its `tier` is the triage rung. Level: integration.
- **AC-8** (FR-8) Given collect prints a refuter batch with 3 findings, when the agent validates, then one refuter run covers all 3, writes `spec-refuter.md`, and the agent collects again. [human]
  Observable: one refuter output per round; after the second collect no finding is `pending`. Level: integration.
- **AC-9** (FR-9) Given a lens output is invalid, missing or `context: needs-more`, when the outcome is `rerun`, then the agent re-runs that lens once under the same file name, and a second failure goes to the human. [human]
  Observable: the juror's `attempts` is 2 after the re-run; a second failure gives outcome `human`. Level: integration.
- **AC-10** (FR-10) Given the refuter refuted a finding, when the human is shown the verdict, then the finding is listed as refuted with the refuter's reason. [human]
  Observable: the message to the human names the refuted finding and its reason. Level: e2e.

### US-3 Dispose of findings within each actor's authority (P1) [agent]
- **Why this priority:** a jury whose agent can wave findings away is no gate; one that sends every typo to the human
  wastes them.
- **Independent test:** a ledger with a wording fix, a behaviour change, an accepted risk and a grill-deferred point;
  each ends with the disposer the authority table names.

- **AC-11** (FR-11) Given a confirmed finding whose fix changes no behaviour, when the agent disposes it, then it applies the fix to the spec, records `spec-fix --by agent` with a note, and `nio check spec <slug> --gate` still passes. [human]
  Observable: the ledger row shows `spec-fix (agent)`; the gate check exits 0. Level: integration.
- **AC-12** (FR-12) Given a confirmed finding whose fix changes behaviour, when the agent reaches it, then it does not edit the spec itself but hands the finding to a grill session, and the disposition is recorded `--by grill` after the human answers. [human]
  Observable: the ledger row shows `spec-fix (grill)`, and `grill.md` has the question that settled it. Level: e2e.
- **AC-13** (FR-13) Given a finding the agent thinks is an accepted risk, when it would dispose it, then it asks the human and records `accepted-risk --by human` only on the human's word. [human]
  Observable: no `accepted-risk` or `out-of-scope` row has a disposer other than human. Level: e2e.
- **AC-14** (FR-14) Given a finding that came from a grill-deferred point, when the agent would dispose it, then it doesn't: the human disposes it or a grill session settles it. [derived: FR-14]
  Observable: no deferred finding has disposer `agent`. Level: integration.
- **AC-15** (FR-15) Given the agent disposes a finding as `open-question`, when it continues, then a new `OP-n` is in the spec and the next step is a grill session, not a lens re-run. [derived: FR-15]
  Observable: the spec has the new OP; no lens runs until `nio check spec <slug> --gate` passes again. Level: integration.
- **AC-26** (FR-25) Given the agent disposes a finding as a spec-fix that changes no behaviour, when the gate is decided, then that judgement is listed for the human. [research: RF-7]
  Observable: `nio jury check` lists the finding under "for the human to review". Level: integration.

### US-4 Reach the outcome and tell the human (P1) [agent]
- **Why this priority:** the verdict is the gate; the human is always notified, even on approval.
- **Independent test:** drive a ledger to each outcome; the skill takes the action the outcome table names for each.

- **AC-16** (FR-16) Given all findings are confirmed or disposed, when the agent composes, then it runs `nio jury check <slug> spec --record` and acts on its outcome as the outcome table says. [human]
  Observable: the action taken matches the table row for the printed outcome. Level: integration.
- **AC-17** (FR-17) Given the outcome is approved, when the agent reports, then the human sees the outcome, the verdict record's ID, every disposition the agent made, and the next stage. [human]
  Observable: the message has those four parts; the `V-*` record's `paths` names the ledger. Level: e2e.
- **AC-18** (FR-18) Given the outcome is human, when the agent reports, then it shows each reason `nio jury check` printed with the findings behind it and waits for the human's decision. [human]
  Observable: no further lens, refuter or disposition runs before the human answers. Level: e2e.

### US-5 Re-review only what the fix touched (P2) [agent]
- **Why this priority:** re-running every lens after each fix spends tokens for marginal gains.
- **Independent test:** reject a spec on one logic finding, fix it, re-run; only logic re-runs, and a lens whose
  cited IDs the fix touched re-runs too.

- **AC-19** (FR-19) Given logic blocked and testability approved, when the agent re-runs after a fix that touched no ID testability cited, then only logic re-runs, on the changed sections and its own findings, and the `nio check spec` checks re-run in full. [human]
  Observable: the new round has a logic output and no testability output; `nio check spec <slug> --gate` ran before it. Level: integration.
- **AC-20** (FR-19) Given testability approved citing FR-3, when a fix changes FR-3, then testability re-runs too. [human]
  Observable: the new round has a testability output. Level: integration.
- **AC-21** (FR-20) Given a finding failed 2 rounds, when the agent composes, then it presents the finding to the human and runs no third round on it. [human]
  Observable: outcome `human` lists the finding; no third logic output is written for it. Level: integration.
- **AC-24** (FR-23) Given a round was collected, when the spec is fixed and the jury runs again, then the changed IDs come from the spec as it was at that round. [agent]
  Observable: the ledger holds the spec's version for each round; the re-run pack names exactly the IDs that changed. Level: integration.

### US-6 Escalate and cap the jurors (P2) [agent]
- **Why this priority:** one juror can be wrong on a serious finding; unbounded jurors cost too much.
- **Independent test:** a lens with a blocker gets 3 jurors and a 2-of-3 decision; a spec whose plan exceeds the cap
  stops for the human's choice.

- **AC-22** (FR-21) Given the refuter confirmed a blocker raised by a 1-juror lens, when the agent escalates, then that lens runs with 3 independent jurors and the majority decides. [human]
  Observable: outputs `spec-<lens>`, `spec-<lens>-2` and `spec-<lens>-3` exist; the ledger shows the vote. Level: integration.
- **AC-23** (FR-22) Given the planned lens runs for the gate exceed the cap (default 6, counting each juror), when the agent would start them, then it shows the planned runs and their cost and waits for the human to run all, drop the lowest-hit-rate lenses, or pick. [human]
  Observable: no lens runs before the human's choice; the choice is logged. Level: e2e.

## Functional requirements
- **FR-1** IF the spec does not pass `nio check spec <slug> --gate` THEN THE SYSTEM SHALL run no lens and send the human back to the grill. [research: RF-6]
- **FR-2** WHEN the jury starts at the spec gate THE SYSTEM SHALL run the core lenses testability and logic plus every lens `nio check spec` lists for the spec's risk flags and size. [human]
- **FR-3** WHEN the jury starts THE SYSTEM SHALL set the gate's rung from the spec's risk flags (none → low; any flag → medium; auth, money, data-deletion or migration → high) and record it as the verdict's tier. [human]
- **FR-4** WHEN a juror runs THE SYSTEM SHALL give it a fresh context pack holding only the spec, its card's `## At spec` section, the `nio check spec` output and the lens output template, never the author's reasoning or another juror's output. [human]
- **FR-5** THE SYSTEM SHALL run each juror on a different model from the spec's author where the host offers one. [human]
- **FR-6** WHEN a juror finishes THE SYSTEM SHALL have its output at `.nio/runs/<run>/jury/spec-<lens>[-<n>].md` in the lens output format. [human]
- **FR-7** WHEN every planned output of a round exists THE SYSTEM SHALL run `nio jury collect` with each planned lens as `--expect` and the triage rung as `--tier`. [human]
- **FR-8** WHEN collect prints a refuter batch THE SYSTEM SHALL run the refuter once on the whole batch and collect again. [human]
- **FR-9** IF a lens output is missing, invalid or `needs-more` THEN THE SYSTEM SHALL re-run that lens once under the same file name and send a second failure to the human. [human]
- **FR-10** THE SYSTEM SHALL show refuted findings to the human with the refuter's reason, never hide them. [human]
- **FR-11** WHEN a confirmed finding's fix changes no behaviour THE SYSTEM SHALL let the agent apply it and record it as `spec-fix --by agent` with a note. [human]
- **FR-12** WHEN a confirmed finding's fix changes behaviour THE SYSTEM SHALL settle it through a grill session and record it `--by grill`. [human]
- **FR-13** THE SYSTEM SHALL record `accepted-risk` and `out-of-scope` only on the human's word, `--by human`. [human]
- **FR-14** IF a finding came from a point the grill deferred THEN THE SYSTEM SHALL leave its disposition to the human or a grill session. [research: RF-8]
- **FR-15** WHEN the agent disposes a finding as `open-question` THE SYSTEM SHALL add it to the spec as an open point and return to the grill before any lens re-runs. [research: RF-7]
- **FR-16** WHEN no finding waits for the refuter THE SYSTEM SHALL run `nio jury check <slug> spec --record` and take the action the outcome table gives for its outcome. [human]
- **FR-17** WHEN the outcome is approved THE SYSTEM SHALL notify the human with the verdict record, every disposition the agent made, and the next stage. [human]
- **FR-18** WHEN the outcome is human THE SYSTEM SHALL present each reason with its findings and wait for the human's decision. [human]
- **FR-19** WHEN the spec changes after a rejected round THE SYSTEM SHALL re-run the `nio check spec` checks in full, re-run only the blocking lenses on the changed sections and their findings, and re-run an approving lens only if the change touched an ID it cited. [human]
- **FR-20** IF a finding has failed 2 rounds THEN THE SYSTEM SHALL send it to the human instead of re-running its lens. [human]
- **FR-21** WHEN the refuter confirms a blocker finding THE SYSTEM SHALL re-run the lens that raised it with 3 independent jurors, and 2 of 3 decide; majors and refuted blockers never escalate. [human]
- **FR-22** IF the planned lens runs for a gate exceed the configured cap (default 6, each juror counted) THEN THE SYSTEM SHALL show the planned runs and their cost and let the human run all, drop the lowest-hit-rate lenses, or pick, skipping nothing silently. [human]

## Rules

### Decision table: next action by outcome
| outcome (approved, rejected, rerun, pending, human) | → action | Src |
| --- | --- | --- |
| approved | notify the human (FR-17) and stop | [research: RF-7] |
| rejected | dispose each open finding by the authority table, then re-run per FR-19 | [research: RF-7] |
| rerun | re-run each lens named as missing, invalid or `needs-more`, then collect | [research: RF-7] |
| pending | run the refuter on the batch, then collect | [research: RF-7] |
| human | present the reasons and wait for the human (FR-18) | [research: RF-7] |

### Decision table: who may dispose a finding
| disposition (spec-fix, open-question, accepted-risk, out-of-scope) | changes behaviour (yes, no) | deferred by the grill (yes, no) | → disposer | Src |
| --- | --- | --- | --- | --- |
| spec-fix | no | no | agent | [human] |
| spec-fix | yes | - | grill | [human] |
| spec-fix | no | yes | human or grill | [research: RF-7] |
| open-question | - | no | agent | [human] |
| open-question | - | yes | human or grill | [research: RF-7] |
| accepted-risk | - | - | human | [human] |
| out-of-scope | - | - | human | [human] |

## Key entities
- **Lens**: one concern a juror judges (testability, logic, adversary, security, scope, consistency), defined by an agent card with an `## At spec` section. [human]
- **Context pack**: what one juror reads; fresh per juror, built by the skill. [human]
- **Lens output**: a juror's reasoning and findings, in the run folder, gitignored. [human]
- **Refuter batch**: the blocker and major findings `nio jury collect` prints for validation. [human]
- **Ledger**: `.nio/specs/<slug>/jury/spec.md` (and its `.json`), written only by `nio jury`, committed. [human]
- **Verdict record**: the `V-*` record `nio jury check --record` writes to memory, pointing at the ledger. [human]
- **Rung**: low, medium or high, picked by triage; recorded as the ledger's tier. [human]
- **FR-23** WHEN the jury collects a round THE SYSTEM SHALL record the version of the spec it judged, so the next round can tell which IDs a fix changed. [agent]
- **FR-24** WHEN the scope or consistency lens runs THE SYSTEM SHALL add `intake.md` to the scope lens's pack and the memory pack to the consistency lens's pack, and to no other lens's. [research: RF-10]
- **FR-25** THE SYSTEM SHALL let the agent judge whether a fix changes behaviour, and list every such judgement for the human at the gate. [research: RF-7]
- **FR-26** IF a lens the gate needs has no agent card THEN THE SYSTEM SHALL block the gate before any lens runs and name the missing card. [human]
- **FR-27** WHEN the jury picks lenses THE SYSTEM SHALL also run the consistency lens IF `nio pack` for the spec returns an approved or current decision, and the scope lens IF the spec names a new dependency or an FR that no intake sentence maps to, showing the human each trigger's reason. [human]
- **FR-28** IF the host has no subagents THEN THE SYSTEM SHALL NOT play a lens in the jury agent's own session; it SHALL write each juror's pack to the run folder, ask the human to run it in a fresh session, and record the manual run on the verdict. [human]

## Non-functional requirements
- **NFR-1** THE SYSTEM SHALL run at most the configured number of lens runs per gate (default 6, each juror counted) without the human's choice. [human]
- **NFR-2** THE SYSTEM SHALL accept at most 5 findings per lens output. [human]

## Success criteria
- **SC-1** Every spec the jury approves has a ledger with `unresolved: 0` and a `V-*` record that points at it. [derived: FR-16]
- **SC-2** No `accepted-risk` or `out-of-scope` disposition in any ledger was made by anyone but the human. [derived: FR-13]
- **SC-3** A gate never runs more lens runs than its cap without a logged human choice. [derived: FR-22]

## Non-goals
- A triage agent that adds lenses: later, if hit rates show lenses missing; in v1 the risk flags set the rung. [human]
- The plan and tasks gates: their artefacts and stages don't exist yet; their lenses are listed in #47 for when they do. [research: RF-9]
- The verdict format, the ledger and the `nio jury collect | dispose | check` commands: decided and built in #27. [human]
- Cross-host jurors (#4). [human]
- The flow guards that call `nio jury check` (#45). [human]
- A self-reported confidence number on findings (#27 amends #47). [human]
- The user advocate lens: it walks the journeys before the grill (#37), not at the jury. [human]
- A cheap model checking each verdict's quality before the human sees it (NORTH_STAR): later. [agent]

## Glossary
- **Juror**: one run of one lens. Several jurors can run the same lens (`-2`, `-3`).
- **Round**: one batch of lens outputs merged into the ledger; re-runs after a fix start a new round.
- **Blocking lens**: a lens with a confirmed blocker or major finding still open.
- **Failed round**: a round in which a finding seen before is reported again.

## Risks and evidence against
- Verbalized confidence clusters at 80–100, so a confidence filter cuts almost nothing; findings are grounded and refuted instead (Xiong et al., ICLR 2024). [human]
- Fluent author rationale sways judges, so packs leave it out (ACL 2026). [human]
- A juror on the drafter's model prefers text it recognises as its own (Panickssery 2024). [human]

## Decisions
- Without subagents, a lens runs in a fresh session started by the human, never in the jury agent's own (grill, 2026-10-25).
- The skill triggers consistency (approved or current memory in `nio pack`) and the non-count scope triggers (a new dependency, an FR missing from the intake), with reasons shown (grill, 2026-10-25).
- The jury ships with the five missing v1 lens cards (testability, adversary, security, scope, consistency); from then on a triggered lens without a card blocks the gate (grill, 2026-10-25).
- Only a blocker the refuter confirmed escalates its lens to 3 jurors (grill, 2026-10-25).
- #47's escalation wins over NORTH_STAR's: 3 jurors only for lenses with high-severity findings; no triage agent in v1, the risk flags set the rung (grill, 2026-10-25).
- The `V-*` record is written by `nio jury check --record` directly, not promoted: verdicts skip promotion: D-261024-kljr (memory, 2026-10-24).
- The verdict's outcome and tier are always set by the jury, never defaulted: D-261024-5nuq (memory, 2026-10-24).

