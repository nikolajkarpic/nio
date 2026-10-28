# Grill log: 2026-10-28-flow-state

Append-only. One entry per question, below-the-bar call or derived item.

## Session 1 · 2026-10-28 · @nio:grill, the human answers one at a time

## Facts · OP-1, OP-2, OP-3, OP-4, OP-5 · 2026-10-28
Facet: actors (OP-1), change (OP-2), state (OP-3), data (OP-4), cost (OP-5)
Found: RF-1 to RF-5 (research.md). No contradiction; RF-2 means researching is skipped as not built today (the grill does research inside its own stage).
Patched: UJ-1 evidence, researching guard row, plan_jury row, FR-29, FR-40; retired OP-1, OP-2, OP-3, OP-4, OP-5

## Asked · Q1 · OP-6 · 2026-10-28
Facet: state
Question: Pick one: does a stage count as done only once `nio flow done` recorded it, or as soon as its checks pass on the files?
Context: This decides whether existing efforts show their real stage without anyone replaying them, and whether an agent can skip the done step. The four dated past efforts have no history at all (no state file exists yet, per research). Reading the stage from the files is the same principle you chose in the brainstorm (read, don't copy).
Options:
1. Files decide, history records (Recommended): the stage is the first one whose checks don't pass yet, worked out from the files on every call; `done` runs the checks and writes the history line. Past efforts show their real stage at once. An agent that skips `done` still can't get past a failing check, but the history then has a gap for that stage.
2. Only `done` counts: a stage is passed only when `done` recorded it. The history is complete by construction, but every past effort starts at intake and must be walked through `done` stage by stage, and a manual run that forgets `done` looks stuck.
3. Files decide, gaps filled on the next call: as option 1, but when the files show a stage passed with no history line, the next `nio flow` call appends a backfilled line marked as found, not reported. A complete history without replays, at the cost of history lines no one actively reported.
Refs: OP-6 · FR-12, FR-17, SC-3 · RF-1 · #45 Brainstorm Q1

## Q1 · OP-6 · 2026-10-28
Question: Pick one: does a stage count as done only once `nio flow done` recorded it, or as soon as its checks pass on the files?
Options:
1. Files decide, history records (recommended)
2. Only `done` counts
3. Files decide, gaps backfilled
Answer: 1. Files decide, history records: the stage is the first one whose checks don't pass yet, worked out from the files on every call; `done` runs the checks and writes the history line. Past efforts show their real stage at once. An agent that skips `done` still can't get past a failing check, but the history then has a gap for that stage. [human]
Patched: FR-47 (new), AC-51 (new), SC-3 derived; retired OP-6; decision D-261028-4kji

## Asked · Q2 · contradiction (FR-18, OP-7, CLAUDE.md) · 2026-10-28
Facet: permissions
Question: Pick one: when a gate passes, does `nio flow` make the approval commit itself, or wait for you to ask?
Context: #45 decided that a passing gate commits automatically as `nio: approve <stage>`. The repo's rule (CLAUDE.md) says never commit without the human asking, and today every approval commit is made only after you say so (per the jury skill). Auto mode will need commits without you; manual runs today don't.
Options:
1. Ask unless auto (Recommended): with auto off, `done` on a gate stops and says "approve to commit"; your yes runs `nio flow done <gate> --commit`. With auto on (a later spec), the grant you gave at start counts as asking. CLAUDE.md stays true, and auto runs still don't wait.
2. Always commit: a passing gate commits at once, manual or auto. Fewer steps, but it breaks the repo rule, and a commit lands that you never asked for.
3. Never commit: `nio flow` never commits; the agent commits only when you ask, as today, even in auto mode. Simplest, but an unattended run piles up uncommitted gates until you come back.
Refs: OP-7 · FR-18, AC-19 · CLAUDE.md "Never commit without the human asking" · skills/jury/SKILL.md (Approval) · #45 decision 3, Brainstorm Q8

## Q2 · contradiction (FR-18, OP-7, CLAUDE.md) · 2026-10-28
Question: Pick one: when a gate passes, does `nio flow` make the approval commit itself, or wait for you to ask?
Options:
1. Ask unless auto (recommended)
2. Always commit
3. Never commit
Answer: 1. Ask unless auto: with auto off, `done` on a gate stops and says "approve to commit"; your yes runs `nio flow done <gate> --commit`. With auto on (a later spec), the grant you gave at start counts as asking. CLAUDE.md stays true, and auto runs still don't wait. [human]
Patched: FR-18, AC-19, FR-48 (new), AC-52 (new), FR-49 (derived), risk on CLAUDE.md removed; retired OP-7

## Derived · FR-49 · 2026-10-28
From FR-48 and FR-47: the stage moves on from the files once the ledger approves, so the pending approval commit must show beside it; an uncommitted change to the passed gate's ledger is what marks it, which leaves past efforts (all committed) clean. [derived: FR-48, FR-47]

## Asked · Q3 · OP-11 · 2026-10-28
Facet: verification
Question: Pick one: should the round cap, the count caps and the stuck rule also apply when auto mode is off?
Context: You set them for auto runs in the brainstorm (3 jury rounds, counts from a budgets setting, same check failing 3 times). Nothing in this spec can switch auto on, so as written they'd be built but never fire until a later spec, and their tests would have to fake the flag. Manual runs today went 3–5 rounds on spec gates (per the jury ledgers), with you watching.
Options:
1. Auto only, as decided (Recommended): they apply only with the auto flag on; manual runs behave as today, and you stay the brake. Their tests set the flag in a fixture until the auto switch exists. Nothing changes for how you work now.
2. Warn when off, pause when on: with auto off, `next` and `status` show a warning when a cap or the stuck rule trips, but nothing pauses. You see runaway gates in manual runs too, at the cost of a few more lines of output.
3. Always pause: they pause every effort, manual or auto. Consistent, but a manual spec gate on its 4th round would stop and need you to resume it, which the past runs show is common.
Refs: OP-11 · FR-39, FR-40, FR-41, AC-50 · #45 Brainstorm Q5, Q6 · .nio/specs/*/jury/spec.json (rounds 3–5)

## Q3 · OP-11 · 2026-10-28
Question: Pick one: should the round cap, the count caps and the stuck rule also apply when auto mode is off?
Options:
1. Auto only, as decided (recommended)
2. Warn when off, pause when on
3. Always pause
Answer: 1. Auto only, as decided: they apply only with the auto flag on; manual runs behave as today, and you stay the brake. Their tests set the flag in a fixture until the auto switch exists. Nothing changes for how you work now. [human]
Patched: FR-39, FR-40, FR-41 unchanged (already auto-only), AC-50 confirmed; retired OP-11

## Asked · Q4 · OP-8 · 2026-10-28
Facet: meaning
Question: Pick one: does this spec build task tracking (who claimed a task, attempts, failing-then-passing tests, which task is next), or does that ship with the implement stage?
Context: The implement stage isn't built (per research), so tasks have nothing to run them yet; this spec stops efforts at implementing and waits for you (your answer in the brainstorm). Building task tracking now means designing it before #43 settles how workers hand back results.
Options:
1. Ship it with implement (Recommended): this spec stops at implementing; task claims, attempts and the red/green checks are specced with #43, which knows the worker handoff. The state file keeps room for them. Less to build now, and no guess about handoffs.
2. Build it now: claims, attempts, the red/green checks and next-task picking land here, ready for #43. The flow is complete sooner, but the handoff format is guessed and may need a change request later.
3. Claims only: record which task is claimed and by whom, and leave the test checks and scheduling to #43. A middle ground, but a half machine that nothing drives yet.
Refs: OP-8 · FR-3, FR-22 · RF-2 · #43 · #45 Brainstorm Q11, Q15

## Q4 · OP-8 · 2026-10-28
Question: Pick one: does this spec build task tracking (who claimed a task, attempts, failing-then-passing tests, which task is next), or does that ship with the implement stage?
Options:
1. Ship it with implement (recommended)
2. Build it now
3. Claims only
Answer: 1. Ship it with implement: this spec stops at implementing; task claims, attempts and the red/green checks are specced with #43, which knows the worker handoff. The state file keeps room for them. Less to build now, and no guess about handoffs. [human]
Patched: FR-24 (`<stage>` only), non-goal added; retired OP-8

## Asked · Q5 · OP-9 · 2026-10-28
Facet: change
Question: Pick one: which kinds of spec should `nio flow` drive: only full specs, or also bug-fix and multi-slice specs?
Context: `nio new spec` already makes three kinds: full, bug-fix and multi-slice (per its route option). Only the full path has its stages defined in this spec; the bug-fix path (#44) is still being designed, and a multi-slice spec runs each slice as its own full spec. An effort the flow can't drive shows no stage.
Options:
1. Full only, others shown as unsupported (Recommended): `nio flow` drives full specs; a bug-fix or multi-slice folder shows in `status` as `unsupported: <route>` and `next` says so. Its machine comes with #44 or the epic work. Nothing is guessed about paths not yet designed.
2. Full and multi-slice: also drive a multi-slice spec by treating each slice as a full effort. Covers more now, but the parent spec's own stage and how slices roll up have to be decided here.
3. All three: also define the bug-fix path (repro, failing test, fix, jury) here. One machine for everything, but it designs #44's flow inside this spec.
Refs: OP-9 · Summary, FR-29 · src/nio/spec.py (routes full, lite, epic) · #44

## Q5 · OP-9 · 2026-10-28
Question: Pick one: which kinds of spec should `nio flow` drive: only full specs, or also bug-fix and multi-slice specs?
Options:
1. Full only (recommended)
2. Full and multi-slice
3. All three
Answer: 1. Full only: `nio flow` drives full specs; a bug-fix or multi-slice folder shows in `status` as `unsupported: <route>` and `next` says so. Its machine comes with #44 or the epic work. Nothing is guessed about paths not yet designed. [human]
Patched: FR-50 (new), AC-53 (new), FR-28 status words, non-goal added; retired OP-9

## Asked · Q6 · OP-10 · 2026-10-28
Facet: permissions
Question: Pick one: how does the flow tell that something is on the always-human list (DB scripts, secrets, breaking changes, anything irreversible, anything that costs money)?
Context: Those items must always stop for you (NORTH_STAR), but no code recognises them today. The spec's risk flags (money, data deletion, migration, auth and others) are set when the spec is drafted (per the spec template), and the jury already raises its tier on them. Auto mode is a later spec, so this only decides what that spec will build on.
Options:
1. Risk flags pause gates (Recommended): when the spec carries a flag on the always-human list (money, data deletion, migration, auth), an auto run pauses at each gate for your approval. Deterministic and already in every spec, but a risk the drafter didn't flag isn't caught.
2. A lens decides: a jury lens reads each diff and says whether it touches the list. Catches unflagged cases, but a model makes the call, which is the self-attestation the brainstorm warned about.
3. Defer to the auto spec: this spec doesn't recognise them at all; the auto switch's spec decides. Nothing built now, but the stop list here is incomplete until then.
Refs: OP-10 · FR-39–FR-42 · NORTH_STAR "Always goes to the human" · src/nio/templates/spec.md (risk) · src/nio/jury.py HIGH_RISK

## Q6 · OP-10 · 2026-10-28
Question: Pick one: how does the flow tell that something is on the always-human list (DB scripts, secrets, breaking changes, anything irreversible, anything that costs money)?
Options:
1. Risk flags pause gates (recommended)
2. A lens decides
3. Defer to the auto spec
Answer: 1. Risk flags pause gates: when the spec carries a flag on the always-human list (money, data deletion, migration, auth), an auto run pauses at each gate for your approval. Deterministic and already in every spec, but a risk the drafter didn't flag isn't caught. [human]
Patched: FR-51 (new), AC-54 (new), risk added; retired OP-10

## Asked · Q7 · OP-12 · 2026-10-28
Facet: data
Question: Pick one: when the spec itself changes after its gate approved it, where does the effort go back to?
Context: The spec is written in drafting and settled in grilling; its jury then judges it. A changed approved spec already withdraws the spec approval (per the jury's version check), and the plan gate already pauses until the spec jury re-checks it (per the jury skill). Going back too far redoes work; not far enough skips the check.
Options:
1. Back to the spec jury (Recommended): the jury re-checks only what changed (as it does today for a change request), and if it finds a gap the normal reject sends the effort to grilling. Smallest redo, and the grill runs only when the change needs it.
2. Back to grilling: every spec change goes through the grill again before the jury. Safer for big changes, but a one-word fix costs a grill session.
3. Back to drafting: the spec is redrafted. Only fits a rewrite; for edits it repeats every stage.
Refs: OP-12 · Owning stage table · FR-36 · skills/jury/SKILL.md (waiting-on-spec) · C-261028-7njg

## Q7 · OP-12 · 2026-10-28
Question: Pick one: when the spec itself changes after its gate approved it, where does the effort go back to?
Options:
1. Back to the spec jury (recommended)
2. Back to grilling
3. Back to drafting
Answer: 1. Back to the spec jury: the jury re-checks only what changed (as it does today for a change request), and if it finds a gap the normal reject sends the effort to grilling. Smallest redo, and the grill runs only when the change needs it. [human]
Patched: Owning stage table split into a pending change request and an edited approved file; spec.md row; retired OP-12

## Derived · Owning stage table, edited approved files · 2026-10-28
From Q7, FR-36 and FR-47: an approved file edited after its gate judged it fails that gate's guard (the judged version no longer matches), so the derived stage is that gate, and the jury re-checks what changed. A pending change request still sends the effort to the stage that writes the file, because the file has yet to be edited. [derived: FR-47, FR-36]

## Asked · Q8 · OP-13 · 2026-10-28
Facet: data
Question: Pick one: should you be able to mark an effort as abandoned, separate from parked?
Context: #45's machine has "any state → paused or abandoned (human only)". Parked (from the brainstorm) means "idle, coming back". Abandoned would mean "never coming back": it drops out of `status` noise and stops change requests from reopening it. Nothing is deleted either way; the folder stays in git.
Options:
1. Yes, human only, reversible (Recommended): `nio flow abandon <slug> "<why>"` records it; status shows `abandoned: <why>` at the bottom, and changes no longer move it. `nio flow start` brings it back. Clear signal for dead work, one more command to build.
2. Parked covers it: no abandoned state; a dead effort stays parked with a reason like "dropped". Less to build, but dead and paused work look the same and a change request still reopens a dead effort.
3. Yes, final: abandoned can't be resumed; a new effort must be started instead. Strongest signal, but a wrong abandon can't be undone without a hand edit.
Refs: OP-13 · FR-30, FR-31 · #45 machine ("any → paused | abandoned (human only)") · Brainstorm Q13

## Q8 · OP-13 · 2026-10-28
Question: Pick one: should you be able to mark an effort as abandoned, separate from parked?
Options:
1. Yes, human only, reversible (recommended)
2. Parked covers it
3. Yes, final
Answer: 1. Yes, human only, reversible: `nio flow abandon <slug> "<why>"` records it; status shows `abandoned: <why>` at the bottom, and changes no longer move it. `nio flow start` brings it back. Clear signal for dead work, one more command to build. [human]
Patched: FR-3 and AC-7 (abandon reason stored), FR-28 status words, FR-52, FR-53 (new), AC-55 (new); retired OP-13

## Asked · Q9 · FR-45, AC-12 · 2026-10-28
Facet: failure
Question: Pick one: what happens when two `nio flow` calls try to change the same effort at once?
Context: The design has a single writer (the brainstorm), but nothing stops two sessions, or you and an agent, from running `done` on the same effort at the same moment; both could append history or both commit. No daemon is allowed (NORTH_STAR), so any guard has to live in the files.
Options:
1. Lock file, second call refused (Recommended): the first writer holds a lock file in the effort folder for the moment it writes; a second writer is refused with "being written, try again", and a lock left by a crashed call older than a minute is taken over. Nothing is lost or doubled. Costs a small lock file, never committed.
2. Last writer wins: no lock; each call appends its line. Simplest, but two `done` calls can both pass a gate and both commit, doubling history lines.
3. Refuse when the files changed under it: each call notes the history length at start and refuses to write if it grew meanwhile. No lock file, but the gate commit can still race in between.
Refs: FR-45, AC-12 · #45 decision 2 (single writer) · NORTH_STAR "No database and no daemon"

## Q9 · FR-45, AC-12 · 2026-10-28
Question: Pick one: what happens when two `nio flow` calls try to change the same effort at once?
Options:
1. Lock file, second refused (recommended)
2. Last writer wins
3. Refuse if files changed
Answer: 1. Lock file, second refused: the first writer holds a lock file in the effort folder while it writes; a second writer is refused with "being written, try again", and a lock left by a crashed call older than a minute is taken over. Nothing is lost or doubled. Costs a small lock file, never committed. [human]
Patched: FR-45, AC-12, FR-54 (new), AC-56 (new)

## Asked · Q10 · FR-38, AC-41 · 2026-10-28
Facet: permissions
Question: Pick one: while a change request against a file is still waiting for your decision, can the effort pass that file's stage?
Context: A pending change request sends the effort back to the stage that writes the file (your earlier answer). If the stage could pass again before you rule on the request, the effort would carry on as if the change were settled; today's plan gate already pauses the same way while a spec change waits (per the jury skill).
Options:
1. Blocked until you rule (Recommended): `done` on that stage and every later one is refused while the request is pending; `next` says it waits on your ruling and names the request. Nothing moves past an open question about its own input. Costs a stall until you rule.
2. Warn only: `done` passes but prints the pending request. Faster, but work can finish on a file you may still change.
3. Block only gates: ordinary stages may pass, but no gate commits until you rule. A middle ground; work done meanwhile may be redone.
Refs: FR-38, AC-41 · FR-35 · skills/jury/SKILL.md (waiting-on-spec) · C-261028-7njg

## Q10 · FR-38, AC-41 · 2026-10-28
Question: Pick one: while a change request against a file is still waiting for your decision, can the effort pass that file's stage?
Options:
1. Blocked until you rule (recommended)
2. Warn only
3. Block only gates
Answer: 1. Blocked until you rule: `done` on that stage and every later one is refused while the request is pending; `next` says it waits on your ruling and names the request. Nothing moves past an open question about its own input. Costs a stall until you rule. [human]
Patched: FR-38, AC-41

## Q11 · the 44 remaining proposals · 2026-10-28
Question: Pick one: how should the grill settle the 44 smaller proposals still open?
Options:
1. You decide, I review at the end (recommended)
2. One numbered round
3. One at a time
Answer: 1. You decide, I review at the end: I take my recommended answer on each, log each with its reason, and at the finish gate list every one that changes what you can do or see, so you can overturn any. About one message from you instead of ~20 questions. [human]
Patched: FR-26 and AC-28 [human] (Brainstorm Q12 "with a reason"); two non-goals [human] (Q17 order, Q9); guards planning, plan_jury, tasks_jury [research: RF-6]; owning research.md row [research: RF-2]; the rest [agent], below

## Call · AC-1, FR-7 detail · 2026-10-28
`next` names the stage, skill, inputs and done command; no alternative changes what the human can do. [agent] Taken on the human's Q11 instruction; listed at the finish gate for review.

## Call · AC-3, FR-9, FR-10, AC-6 · 2026-10-28
`start` makes the effort current and creates its files with a start line; the only way to begin the history. [agent] Taken on the human's Q11 instruction; listed at the finish gate for review.

## Call · AC-4, AC-5, FR-11 · 2026-10-28
refuse and list efforts when nothing is current or the slug is unknown; writing nothing is the only safe answer. [agent] Taken on the human's Q11 instruction; listed at the finish gate for review.

## Call · AC-9, AC-10, FR-6 · 2026-10-28
a broken or hand-edited state or history file stops every command and names the file and line; the single-writer rule needs it. [agent] Taken on the human's Q11 instruction; listed at the finish gate for review.

## Call · AC-17, FR-16 · 2026-10-28
`done` on a stage not reached is refused, naming the current stage. [agent] Taken on the human's Q11 instruction; listed at the finish gate for review.

## Call · AC-18, FR-17 · 2026-10-28
`done` on a stage already passed is a no-op exiting 0, so repeating it is safe (research comment 3, idempotent steps). [agent] Taken on the human's Q11 instruction; listed at the finish gate for review.

## Call · AC-21, FR-20 · 2026-10-28
a failed gate commit records nothing, so history never claims a commit that didn't land. [agent] Taken on the human's Q11 instruction; listed at the finish gate for review.

## Call · AC-30 · 2026-10-28
`--human` on a passing guard is a normal pass with the reason noted, not an override. [agent] Taken on the human's Q11 instruction; listed at the finish gate for review.

## Call · AC-35, FR-32 · 2026-10-28
park needs a reason and is refused on a done effort, matching the brainstorm's `park <slug> "<why>"`. [agent] Taken on the human's Q11 instruction; listed at the finish gate for review.

## Call · AC-37, FR-34 · 2026-10-28
`nio run` with no arguments keeps working as today. [agent] Taken on the human's Q11 instruction; listed at the finish gate for review.

## Call · AC-42 · 2026-10-28
a pending change against `research.md` sends a parked effort to grilling (RF-2) and it stays parked. [agent] Taken on the human's Q11 instruction; listed at the finish gate for review.

## Call · AC-49, FR-43, FR-44 · 2026-10-28
a waiting or suspended effort prints its reason in the Talking-to-the-human shape and names no skill; `start` resumes it. [agent] Taken on the human's Q11 instruction; listed at the finish gate for review.

## Call · FR-46 · 2026-10-28
last activity comes from the newest history line, else the newest commit touching the folder, so past efforts sort sensibly. [agent] Taken on the human's Q11 instruction; listed at the finish gate for review.

## Call · Guards row intake · 2026-10-28
`intake.md` exists. [agent] Taken on the human's Q11 instruction; listed at the finish gate for review.

## Call · Owning stage rows intake.md, architecture.md · 2026-10-28
a change to the intake goes back to drafting, to `architecture.md` to arch_grilling (skipped as not built, so planning). [agent] Taken on the human's Q11 instruction; listed at the finish gate for review.

## Call · NFR-1 · 2026-10-28
`next` fits in 12 lines (#45: about 10). [agent] Taken on the human's Q11 instruction; listed at the finish gate for review.

## Call · NFR-2 · 2026-10-28
`next`, `status` and `park` make no model or network call (the guards are deterministic). [agent] Taken on the human's Q11 instruction; listed at the finish gate for review.

## Call · NFR-3 · 2026-10-28
`status` for 20 efforts under 2 seconds. [agent] Taken on the human's Q11 instruction; listed at the finish gate for review.

## Call · Non-goal: converting legacy folders · 2026-10-28
legacy folders are shown, never converted. [agent] Taken on the human's Q11 instruction; listed at the finish gate for review.

## Call · Risks: derived-state readers, routine overrides · 2026-10-28
kept as the drafter wrote them; they inform the jury and change nothing built. [agent] Taken on the human's Q11 instruction; listed at the finish gate for review.

## Call · fidelity fix FR-35, FR-36 · 2026-10-28
Finish-gate fidelity: FR-35 and FR-36 said "the stage that owns that file", but Q7 split the table into a pending change request and an edited approved file; each FR now points at its column. [agent]

## Asked · Q12 · contradiction (AC-39, Owning stage table, Q7) · 2026-10-28
Facet: state
Question: Pick one: when the tasks or plan files are edited after their jury approved them, does the effort go back to writing them, or to their jury?
Context: In the brainstorm you said a change sends the effort back to the stage that owns the file, and one acceptance criterion says an edited task list goes back to writing tasks. Today you chose that an edited spec goes back to its jury, which re-checks only what changed; the grill applied the same rule to the plan and tasks files. Both can't hold.
Options:
1. Back to their jury, like the spec (Recommended): the edit is already made, so the jury re-checks what changed and a reject sends it back to writing as usual. One rule for every approved file; the acceptance criterion is changed to the tasks jury.
2. Back to writing them: an edited plan or task list goes back to planning or tasking first, then its jury; the spec alone goes to its jury. Matches the brainstorm wording, but two rules and an extra step for a small edit.
3. Back to writing, for every file: the spec too goes back to grilling. One rule, but it reverses today's answer on the spec.
Refs: AC-39, FR-36 · Owning stage table · Q7 · #45 Brainstorm Q14

## Q12 · contradiction (AC-39, Owning stage table, Q7) · 2026-10-28
Question: Pick one: when the tasks or plan files are edited after their jury approved them, does the effort go back to writing them, or to their jury?
Options:
1. Back to their jury (recommended)
2. Back to writing them
3. Back to writing, every file
Answer: 1. Back to their jury, like the spec: the edit is already made, so the jury re-checks what changed and a reject sends it back to writing as usual. One rule for every approved file; the acceptance criterion is changed to the tasks jury. [human]
Patched: AC-39; Owning stage rows plan files and tasks.md [human]

## Finish gate · 2026-10-28
Fidelity: re-read every patched item against its answer; fixed FR-35 and FR-36 (Call above) and raised AC-39 as Q12. Passivity: the human accepted all 12 recommendations; asked which they'd push back on, naming each decision. Notes shown: 34 agent calls, derived FR-49 and SC-3.
Answer: Finish [human]

## Session 2 · 2026-10-28 · spec jury round 1 findings that change behaviour, the human answers

## Asked · Q13 · J-7, J-8 · 2026-10-28
Facet: state
Question: Pick one: how does "the stage is read from the files" handle a jury reject, your override, and an approval not yet committed?
Context: The jury found that reading the stage purely from the files breaks three cases (logic, scope and testability reviews, confirmed by the refuter): a rejected spec stays at the jury instead of going back to grilling; your override is undone on the next call because the files still fail the check; and an approved gate looks passed before you commit it, so `--commit` does nothing. Every past effort has `nio: approve` commits in git (per the git log).
Options:
1. Gates count once approved in git (Recommended): ordinary stages are still read from the files; a gate counts as passed only when a `nio: approve <gate>` commit or an override line in history exists; a rejected jury round sends the effort back as the flow table says until a newer round. Past efforts keep their real stage (their approval commits exist), `--commit` works, and overrides stick.
2. Everything from history: a stage counts as passed only when history records it; files only feed the checks. Simple and exact, but past efforts have no history, so they'd all show at intake (your first answer would be reversed).
3. Files only, overrides as marker files: keep pure file reading; an override writes a small marker file the check reads, and a reject is read from the ledger. Stays closest to your first answer, but adds marker files and still leaves the uncommitted-approval case to special-case.
Refs: J-7 (with J-11), J-8 · FR-47, FR-17, FR-23, FR-24, FR-48, AC-8, AC-24, AC-26, AC-52 · Q1, Q2

## Q13 · J-7, J-8 · 2026-10-28
Question: Pick one: how does "the stage is read from the files" handle a jury reject, your override, and an approval not yet committed?
Options:
1. Gates count once in git (recommended)
2. Everything from history
3. Files only + marker files
Answer: 1. Gates count once in git: ordinary stages are still read from the files; a gate counts as passed only when a `nio: approve <gate>` commit or an override line in history exists; a rejected jury round sends the effort back as the flow table says until a newer round. Past efforts keep their real stage, `--commit` works, and overrides stick. [human]
Patched: (with the session's other fixes, below)

## Asked · Q14 · J-1 · 2026-10-28
Facet: permissions
Question: Pick one: how is an agent kept from using your override (`--human`) to get past a check it can't pass?
Context: The abuse review found that any agent can type `--human "settled"` and pass any check (confirmed by the refuter). With no daemon and no login, the CLI can't truly tell you from an agent: an environment variable or a flag can be set by an agent too. The jury already works this way for its own `--by human` rulings: the skills forbid agents from using it, and the record shows it.
Options:
1. Forbidden in skills, shown until you see it (Recommended): every skill and agent card says only the human gives `--human`; each override shows in `status` and `next` as "override, not yet seen" until you run `nio flow seen <slug>`. Same trust model as the jury, and a misused override can't hide. It costs one extra command per override.
2. Ask at the terminal: `--human` asks you to type the reason again at an interactive prompt; with no terminal (as when an agent runs it) it's refused. Stops agents in most hosts, but you then can't override from inside a Claude Code chat with `!`, and a host with a terminal could still be driven by an agent.
3. Record only: forbid it in skills, record it in history, nothing more. Nothing new to build, but a misused override is visible only to someone who reads the history.
Refs: J-1 · FR-24, FR-26, UJ-3 · skills/jury/SKILL.md (`--by human` is the human's) · #45 Q12

## Q14 · J-1 · 2026-10-28
Question: Pick one: how is an agent kept from using your override (`--human`) to get past a check it can't pass?
Options:
1. Forbidden + shown until seen (recommended)
2. Ask at the terminal
3. Record only
Answer: 1. Forbidden + shown until seen: every skill and agent card says only the human gives `--human`; each override shows in `status` and `next` as "override, not yet seen" until you run `nio flow seen <slug>`. Same trust model as the jury, and a misused override can't hide. Costs one extra command per override. [human]
Patched: (below)

## Asked · Q15 · J-2 · 2026-10-28
Facet: data
Question: Pick one: what stops someone from hand-editing the state file to switch auto mode on or clear a pause?
Context: The state file holds the auto flag, pause and waiting-on (your first brainstorm answer), and it's committed. The abuse review found that a hand edit of an allowed value goes unnoticed (confirmed): an agent could set auto on, and gates would then commit without you. The history log is append-only and records every change the CLI makes.
Options:
1. History holds the fingerprint (Recommended): each history line carries a hash of the state file as the CLI left it; every command refuses when the file's hash differs from the last line's, naming the file. A hand edit is caught on the next call, and nothing else changes.
2. Read it all from history: drop the state file; the auto grant, park, abandon and pauses are history lines, and the current values are read from them. One file, nothing to tamper with separately, but it reverses part of your first answer (where the state file holds what no file holds).
3. Accept the risk: rely on skills forbidding the edit and on git showing the diff. Nothing to build, but a forged auto flag would commit gates until someone reads the diff.
Refs: J-2 · FR-3, FR-6, AC-9, UJ-1 · #45 Q1

## Q15 · J-2 · 2026-10-28
Question: Pick one: what stops someone from hand-editing the state file to switch auto mode on or clear a pause?
Options:
1. History holds the fingerprint (recommended)
2. Read it all from history
3. Accept the risk
Answer: 1. History holds the fingerprint: each history line carries a hash of the state file as the CLI left it; every command refuses when the file's hash differs from the last line's, naming the file. A hand edit is caught on the next call, and nothing else changes. [human]
Patched: (below)

## Asked · Q16 · J-5 · 2026-10-28
Facet: data
Question: Pick one: where does an auto run count "the same check failed 3 times"?
Context: Your stuck rule pauses an auto run after the same check fails the same way 3 times, but today a failed `done` writes nothing, so nothing can count (three reviews, confirmed). Manual runs aren't affected, since the rule is auto-only (your answer Q3).
Options:
1. A failure line in history, auto only (Recommended): in auto mode a failed `done` appends a `fail` line with the check and a hash of its output (timestamps and paths stripped); 3 matching lines in a row trip the rule. The history also shows every failed attempt, which is the audit trail the run needs. Manual runs still write nothing on failure.
2. A counter in the state file: the state file keeps the last failing check, its output hash and a count. Fewer history lines, but the count is overwritten, so the failed attempts leave no trace.
3. Always log failures: every failed `done`, manual or auto, appends a `fail` line. One rule, a fuller history, but manual sessions get noisy history from routine failed checks.
Refs: J-5 (with J-10, J-14) · FR-41, FR-13, FR-3, AC-14, AC-46, AC-47 · Q3

## Q16 · J-5 · 2026-10-28
Question: Pick one: where does an auto run count "the same check failed 3 times"?
Options:
1. Failure line in history, auto only (recommended)
2. Counter in the state file
3. Always log failures
Answer: 1. Failure line in history, auto only: in auto mode a failed `done` appends a `fail` line with the check and a hash of its output (timestamps and paths stripped); 3 matching lines in a row trip the rule. The history shows every failed attempt. Manual runs still write nothing on failure. [human]
Patched: (below)

## Asked · Q17 · J-19 · 2026-10-28
Facet: change
Question: Pick one: the approved tasks-stage spec says this work (#45) builds task tracking, but you moved it to the implement stage; which one changes?
Context: In Q4 you sent task tracking (claims, attempts, failing-then-passing tests) to the implement stage (#43). The tasks-stage spec, approved yesterday, says a task's status lives in this CLI's state and that #45 builds the task machine, and its tests wait for #45 (consistency review, confirmed). Changing an approved spec takes a change request you accept.
Options:
1. Change request on the tasks-stage spec (Recommended): I draft a change request moving "built by #45" to "built by #43" in that spec (its task status line, finishing steps and one deferred point), you accept it, and Q4 stands. The approved spec then matches, and the tasks gate re-checks just those lines.
2. Undo Q4: build task tracking here after all, as the tasks-stage spec expects. No change request, but this spec grows by a whole machine whose worker handoff isn't designed yet.
3. Leave both as they are: record the conflict as an accepted risk. Nothing to do now, but two approved specs disagree until #43 is specced.
Refs: J-19 · non-goal "The task machine" · Q4 · .nio/specs/2026-10-27-tasks-stage/spec.md FR-23, FR-25, DF-1, non-goals

## Q17 · J-19 · 2026-10-28
Question: Pick one: the approved tasks-stage spec says this work (#45) builds task tracking, but you moved it to the implement stage; which one changes?
Options:
1. Change request on tasks spec (recommended)
2. Undo Q4
3. Leave both, accept risk
Answer: 1. Change request on tasks spec: I draft a change request moving "built by #45" to "built by #43" in that spec (its task status line, finishing steps and one deferred point), you accept it, and Q4 stands. The approved spec then matches, and the tasks gate re-checks just those lines. [human]
Patched: (below)

## Asked · Q18 · J-22 · 2026-10-28
Facet: data
Question: Pick one: when you run `nio flow` without naming an effort, how does it know which one you mean?
Context: The spec keeps a local, uncommitted "current effort" note (from the brainstorm). The consistency review found this goes against a recorded decision that every new piece of NIO state lives in committed files (confirmed). Two hosts could also act on different efforts with nothing to say which.
Options:
1. The most recently active effort (Recommended): no slug means the effort with the newest history line; `nio flow start` just makes a line, so it becomes the newest. Nothing local to keep, every host agrees, and the decision holds. If you switch between two efforts, you name the slug.
2. Committed pointer: the current effort is written to a committed file. Hosts agree, but every switch makes a change to commit, and two people would fight over one file.
3. Keep it local, record an exception: a change request exempts a per-machine pointer from the decision. Closest to the brainstorm, but each host can point somewhere else.
Refs: J-22 · FR-9, FR-10, AC-3, Key entities · D-261024-ifge · #45 Q17

## Q18 · J-22 · 2026-10-28
Question: Pick one: when you run `nio flow` without naming an effort, how does it know which one you mean?
Options:
1. Most recently active (recommended)
2. Committed pointer
3. Local + recorded exception
Answer: 1. Most recently active: no slug means the effort with the newest history line; `nio flow start` writes a line, so it becomes the newest. Nothing local to keep, every host agrees, and the decision holds. If you switch between two efforts, you name the slug. [human]
Patched: (below)

## Asked · Q19 · J-3 · 2026-10-28
Facet: failure
Question: Pick one: what happens when a crash leaves a half-written line at the end of an effort's history?
Context: A broken history file makes every command refuse (my earlier call), including the ones you'd use to recover, and hand edits are forbidden (abuse review, confirmed). A crash mid-write leaves a last line with no line ending; a damaged line in the middle means someone edited the file.
Options:
1. Drop a torn last line, refuse anything else (Recommended): a last line with no line ending is ignored and cut off on the next write, with a note in history; damage anywhere else still refuses, and `status` shows that effort as `broken: <file, line>` instead of failing the whole list. Crashes heal themselves, tampering still stops the effort.
2. Repair command: add `nio flow repair <slug>` that drops unreadable lines and records what it dropped. Covers every case, but it's also a way to erase history lines on purpose.
3. Keep refusing: any damage stops every command until fixed by hand in git. Strictest, but a crash needs a hand edit that the rules forbid.
Refs: J-3 · FR-6, FR-4, AC-10, FR-1

## Q19 · J-3 · 2026-10-28
Question: Pick one: what happens when a crash leaves a half-written line at the end of an effort's history?
Options:
1. Drop torn last line only (recommended)
2. Repair command
3. Keep refusing
Answer: 1. Drop torn last line only: a last line with no line ending is ignored and cut off on the next write, with a note in history; damage anywhere else still refuses, and `status` shows that effort as `broken: <file, line>` instead of failing the whole list. Crashes heal themselves, tampering still stops the effort. [human]

## Patched · session 2 · 2026-10-28
Q13: FR-47, FR-55 (new), FR-56 (new), FR-49, AC-8, AC-63 (new), AC-64 (new). Q14: FR-57 (new), AC-57 (new). Q15: FR-6, FR-58 (new), AC-58 (new). Q16: FR-41, FR-13. Q17: change record C-261028-xcg6 (accepted), non-goal note. Q18: FR-9, FR-10, FR-11, AC-3, Key entities (pointer removed). Q19: FR-6, FR-59 (new), FR-60 (new), AC-10, AC-59 (new).
Agent fixes, behaviour as already answered: J-6 and J-21 (FR-21 names the stages not built, Guards rows for advocate_walking, arch_grilling, implementing, AC-22; AC-31 and AC-39 no longer use `done`, unreachable until #43); J-9 (AC-38 and FR-37 follow Q10: `next` waits on the record, the move recorded once); J-15 (FR-39 from round 2 on, AC-60); J-20 (Owning stage: intake.md and architecture.md ignore the edited-approved column); J-4 (FR-54 holder and atomic takeover, AC-61, refining Q9's "left by a crashed call"); J-17 (FR-61, AC-62); J-12 and J-18 (NFR-2, NFR-3 testable; kept under Q11); J-23 (FR-40 key names); J-13 (risk line).

## Q20 · J-12 · 2026-10-28
Question: Pick one: keep the two speed and no-network requirements for `nio flow`?
Options:
1. Keep, confirmed by you (recommended)
2. Keep no-network, drop speed
3. Accept as risk
Answer: 1. Keep, confirmed by you: both stay, now as your decision: a check that stays local and fast is what makes `next` cheap to call after every compaction. Each has a test (network blocked; 20 efforts of 50 history lines). [human]
Patched: NFR-2, NFR-3 [human]

## Q21 · J-17 · 2026-10-28
Question: Pick one: may you abandon an effort that is already done?
Options:
1. Refused, like park (recommended)
2. Allowed
3. Accept as risk
Answer: 1. Refused, like park: abandoning a done effort is refused like parking one; the test also covers an unsupported effort. Done work stays marked done. [human]
Patched: FR-61, AC-62

## Session 3 · 2026-10-28 · @nio:plan, calls below the grill's bar

## Call · CT-2 write order · 2026-10-28
`state.json` goes to `state.json.new` first, then the history line, then the rename; a crash leaves a temp file that matches the last line (rolled forward) or doesn't (ignored and deleted), so FR-6 and FR-58 hold after any crash (spec jury adversary note). [agent]

## Call · CT-2 unchained hash · 2026-10-28
Known limit, accepted under Q14 and Q15: an agent that edits `state.json` and appends a matching line by hand is not caught; the rule in every skill and card and the git diff guard it (spec jury adversary note). [agent]

## Call · CT-3 lock from another host · 2026-10-28
Known limit, as FR-54 says: a lock from another host is taken over after a minute with no liveness check; the holder re-reads its lock before writing and writes nothing if it was taken over (spec jury adversary note). [agent]

## Call · CT-3 .gitignore · 2026-10-28
The lock is ignored through `.nio/specs/<slug>/.gitignore` (`flow.lock`, `state.json.new`), inside the effort folder, so AC-3's "no file outside the effort folders" holds. [agent]

## Call · CT-9, CT-12 who writes · 2026-10-28
`status` never writes; `next` writes only on an effort with history and only when it has something to record; `done` refuses a parked effort (start or next resumes it). [agent]

## Call · CT-16 --by · 2026-10-28
Writing commands take `--by "<role> / <host> / <model>"`, default `human`, as `nio new --by`; skills tell the orchestrator to pass its own. [agent]

## Call · CT-11 FR-48 exit code · 2026-10-28
A gate whose guard passes without `--commit` (auto off) prints the `--commit` command and exits 0. [agent]

## Call · CT-17 run lookup · 2026-10-28
A history line's run is the newest run whose `flow.json` names the effort and the stage being left; `nio run` with one argument, an unknown slug or an unknown stage is refused. [agent]

## Call · CT-8 subagent count · 2026-10-28
Subagent runs used = the sum of juror attempts over the effort's ledgers, the only per-effort count the files hold (RF-5, RF-8). [agent]

## Asked · Q22 · OP-1 (plan) · 2026-10-28
Facet: data
Question: Pick one: when an approved file is edited, what is it compared with to notice the change?
Context: The spec says approved versions come from the jury ledger, but a ledger keeps one version for all of a gate's files together, not one per file, and no gate covers the research notes (per the plan's research). The spec also wants the history to name the edited file with its own approved and current versions. Every approval is already a `nio: approve` commit in git.
Options:
1. The file's copy in its approval commit (Recommended): each file is compared with its copy in the gate's `nio: approve` commit; outcomes, rounds and rejections still come from the ledger. Every row of the spec's owning-stage table works and nothing outside this feature changes; the spec's "read from the ledger" is read as covering the outcomes only, which the plan jury will check.
2. The ledger only: the history names the gate's combined versions, not the file's; the research notes row can't work, so the spec needs a change request and another spec jury pass.
3. Per-file versions in the ledger: exact, but it changes the jury code, which this feature only reads, and reopens the architecture note.
Refs: OP-1 · CT-7 · spec FR-2, FR-36, AC-39 · RF-8, RF-9

## Q22 · OP-1 (plan) · 2026-10-28
Question: Pick one: when an approved file is edited, what is it compared with to notice the change?
Options:
1. Its copy in the approval commit (recommended)
2. The ledger only
3. Per-file versions in ledger
Answer: 1. Its copy in the approval commit: each file is compared with its copy in the gate's `nio: approve` commit; outcomes, rounds and rejections still come from the ledger. Every owning-stage row works and nothing outside this feature changes; the spec's "read from the ledger" is read as covering outcomes only, which the plan jury will check. [human]
Patched: CT-7 (as drafted); retired OP-1 in plan.md

## Asked · Q23 · CT-16 `--by` default · 2026-10-28
Facet: permissions
Question: Pick one: when a `nio flow` command is run without saying who ran it, who does the history say it was?
Context: Every history line records who moved the effort. The plan copied `nio new`, where a missing `--by` means "human", so an agent that forgets `--by` would look like you, the misuse Q14 wanted visible.
Options:
1. Required, no default (recommended)
2. Default to unknown agent
3. Default to human
Refs: CT-16 · spec FR-5, FR-57, Q14

## Q23 · CT-16 `--by` default · 2026-10-28
Question: Pick one: when a `nio flow` command is run without saying who ran it, who does the history say it was?
Options:
1. Required, no default (recommended)
2. Default to unknown agent
3. Default to human
Answer: 1. Required, no default: every writing `nio flow` command needs `--by`; without it the command refuses and writes nothing. Nobody is recorded as you by accident; you type `--by human` (skills give agents their own value). [human]
Patched: CT-16 (and the command shapes in CT-10, CT-11, CT-13, CT-14)

## Session 4 · 2026-10-28 · plan jury round 1 findings that change behaviour or the architecture note, the human answers

## Asked · Q24 · J-6 (plan) · 2026-10-28
Facet: permissions
Question: Pick one: when a jury rejected a gate and you push it through with `--human`, what makes that stick?
Context: The plan's logic review found (confirmed) that `nio flow done <gate> --human` on a rejected gate records the override, but the next call reads the jury's saved "rejected" and sends the effort back again, because `nio flow` never rewrites the jury's file. `nio jury check --human` already closes a gate with your reason, and the flow then counts it as an override (spec, closed by the human).
Options:
1. Refuse at a gate, point to the jury close (Recommended): at a jury gate `done --human` refuses and prints `nio jury check <slug> <gate> --human "<reason>" --record`; ordinary stages keep `done --human`. One way to close a gate, recorded in both the jury's record and the flow history.
2. The override beats the rejection: an override line on a gate skips the rejected-round rule until its files change. Works from one command, but the jury's record still says rejected while the flow says passed.
3. Write both: `done --human` at a gate also runs the jury close for you. One command and both records agree, but `nio flow` then writes the jury's file, which the plan keeps read-only.
Refs: J-6 · CT-6, CT-11 · spec FR-24, FR-27, FR-56 · Q12 (#45)

## Q24 · J-6 (plan) · 2026-10-28
Question: Pick one: when a jury rejected a gate and you push it through with `--human`, what makes that stick?
Options:
1. Refuse at a gate, use jury close (recommended)
2. Override beats the rejection
3. Write both
Answer: 1. Refuse at a gate, use jury close: at a jury gate `done --human` refuses and prints `nio jury check <slug> <gate> --human "<reason>" --record`; ordinary stages keep `done --human`. One way to close a gate, recorded in both the jury's record and the flow history. [human]
Patched: (below; narrows spec FR-24 at gates, so it needs a change request on the spec)

## Asked · Q25 · J-1 (plan) · 2026-10-28
Facet: change
Question: Pick one: the approval commit needs git's exit code, which the existing git helper throws away; how should the plan get it?
Context: The architecture note you approved says `nio flow` reaches git only through the existing helper, which returns only git's output (per the plan's research). The approval commit must report git's error when a commit fails (spec), and spotting an edited file needs two jury functions the note doesn't list. The plan called git directly, which breaks the note (architecture review, confirmed).
Options:
1. Extend the helper, note the jury functions (Recommended): the existing git helper gains an optional "return the exit code and error" mode, with every current caller unchanged; a change request adds that and the two jury functions (one reads a file version, one lists a gate's files) to the note. Smallest change, and the note stays true.
2. Allow direct git calls: a change request lets `nio flow` call git itself for the commit. Fine, but a second way to run git in the codebase.
3. Make every git call report errors: change the helper for all callers. Consistent everywhere, but it touches code this feature otherwise only reads.
Refs: J-1 · CT-6, CT-11 · architecture.md · src/nio/records.py:git · RF-10
