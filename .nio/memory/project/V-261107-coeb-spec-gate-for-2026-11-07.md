---
id: V-261107-coeb
type: verdict
title: "spec gate for 2026-11-07-fewer-gate-turns: rejected (round 1)"
answers: jury             # why | reuse | jury
date: 2026-11-07
by: "jury"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
subject: "spec:2026-11-07-fewer-gate-turns"
outcome: rejected
tier: medium
paths: [".nio/specs/2026-11-07-fewer-gate-turns/jury/spec.md"]
tags: []
supersedes: []
---
## Ruling
The spec jury ruled **rejected** for `2026-11-07-fewer-gate-turns` in round 1 (1 dropped, 4 merged, 13 open, 5 refuted). Ledger: `.nio/specs/2026-11-07-fewer-gate-turns/jury/spec.md`.
## Jurors
| Lens | Host | Model | Vote |
| --- | --- | --- | --- |
| adversary | claude-code | claude-sonnet-5-5 | block |
| consistency | claude-code | claude-haiku-5-5 | block |
| logic | claude-code | claude-sonnet-5-5 | block |
| scope | claude-code | claude-haiku-5-5 | approve |
| testability | claude-code | claude-sonnet-5-5 | block |
## Reasons
- unresolved: J-1, J-5, J-6, J-9, J-12, J-13, J-14, J-15, J-16, J-17, J-18, J-22, J-23
- J-1 [major/gap] Juror-written file name and path are not validated: open
- J-5 [major/ambiguity] Output-line mismatch report and the "never finding bodies" rule can hide errors: open
- J-6 [major/inconsistency] Pending row has no batch to run: open
- J-12 [major/contradiction] A repeated step command both records once and starts a new run: open
- J-13 [major/gap] `needs-more` and `rerun` conditions are not covered by the table or the ACs: open
- J-14 [major/gap] Several-ID dispose does not say what happens when the note count is wrong: open
- J-22 [major/untestable] The turn-count criterion has no fixed baseline or counting rule: open
- J-9 [minor/inconsistency] Refuter already writes its file; the spec presents it as new: open
- J-15 [minor/ambiguity] Rewriting the packs when the step command is repeated is undefined: open
- J-16 [minor/scope] The first-review step adds plan, render and first-pack writing beyond the intake's proposal: open
- J-17 [minor/scope] Per-ID `--note` form in dispose is not in the intake: open
- J-18 [minor/scope] All-or-nothing refusal for several-ID dispose is not in the intake: open
- J-23 [minor/untestable] AC-8 and FR-9 cannot fail deterministically: open
## What was rejected
- J-2 Two concurrent step calls can double-record or start two runs: refuted (UJ-1 has one orchestrator calling the step command in sequence, and AC-5 covers the repeat case. The spec describes no concurrent or interrupted call, so this is speculative and belongs to the plan rather than the spec.)
- J-4 The rejected row can loop, and a stale refuter file is a replay: refuted (FR-3 applies when no finding needs validating, which comes from the ledger's per-finding validation state and not from a file on disk. A refuter file that covers only some findings leaves the rest pending, so FR-2 still applies. The rejected-loop claim is speculation, and the spec relies on `nio jury check`'s existing rules (non-goals).)
- J-7 Memory pack and trigger missing from the packs the command writes: refuted (FR-12 says "the content the skill gives it today" and NFR-2 says "the same pack content as before". Together these already cover the per-lens extras (memory pack, grill answers). How the command does it is HOW, which the spec template excludes.)
- J-8 Pack path and usage log differ from D-261024-zbne: refuted (FR-12's `jury/packs/<lens>.md` is where the skill writes juror packs today (the finding itself says so). The path is therefore not a change this spec introduces. Usage logging is an implementation detail, and NFR-2 keeps pack content unchanged.)
- J-10 The step command has no name: refuted (The spec is WHAT and WHY only. "The step command" is used consistently, and its name and arguments are plan-level choices. Every AC states its observable behaviour, so a test can be written once the plan names the command.)
- J-19 One spec bundles separable changes: dropped (a cited ID or quote is not in the artefact)
