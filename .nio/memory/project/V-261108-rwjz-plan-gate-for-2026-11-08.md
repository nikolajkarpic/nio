---
id: V-261108-rwjz
type: verdict
title: "plan gate for 2026-11-08-full-auto-run: human (round 3)"
answers: jury             # why | reuse | jury
date: 2026-11-08
by: "jury"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
subject: "plan:2026-11-08-full-auto-run"
outcome: human
tier: medium
paths: [".nio/specs/2026-11-08-full-auto-run/jury/plan.md"]
tags: []
supersedes: []
---
## Ruling
The plan jury ruled **human** for `2026-11-08-full-auto-run` in round 3 (9 disposed, 9 fixed, 5 merged, 3 refuted). Ledger: `.nio/specs/2026-11-08-full-auto-run/jury/plan.md`.
## Jurors
| Lens | Host | Model | Vote |
| --- | --- | --- | --- |
| architecture-fit | claude-code | claude-opus-5-5 | block |
| logic |  |  | invalid |
| risk-rollback | claude-code | opus-5.5 | block |
| risk-rollback | claude-code | claude-opus-5-5 | block |
| risk-rollback | claude-code | claude-opus-5-5 | block |
| test-proof | claude-code | claude-opus-5-5 | approve |
## Reasons
- plan-logic: invalid after 2 attempts
- J-3 [major/risk] The driver claim identifies its holder by the `--by` string, which two sessions share: disposed plan-fix
- J-5 [major/inconsistency] CT-1 records host and model in `evidence.ran_in`, while AC-42 checks `who`: disposed plan-fix
- J-7 [major/gap] After the human accepts a round-check hit, nothing can start the next round: disposed plan-fix
- J-8 [blocker/risk] Auto approval commits land on the base branch before the run has its own branch: disposed plan-fix
- J-9 [major/gap] A held finding reads as resolved once auto is off: disposed plan-fix
- J-24 [major/ambiguity] The round check can pass silently when the judged version is missing: disposed plan-fix
- J-22 [minor/risk] Driver-claim takeover temp files are not git-ignored: disposed plan-fix
- J-25 [minor/risk] A human re-dispose overwrites the fixer's record that the report needs: disposed plan-fix
- J-26 [minor/gap] No recovery path is named for a fixer edit the human rejects: disposed plan-fix
## What was rejected
- J-11 The human's draft is rewritten with no committed copy to restore: refuted (The human's own words are protected by FR-10, FR-12 and CT-13's `[human]` checks. What the grill removes are open points that become `[auto]` items listed with IDs in CT-14's report, and each fix has a note and a verdict. Nothing in the spec requires restoring open-point text, so this is a wish rather than an allowed bad outcome.)
- J-18 The fixer overwrites the human's draft with no way back but an unreferenced git blob: refuted (Nothing in the spec requires restoring the pre-fix text. The human's own words are guarded by FR-10 and CT-13's `[human]` checks, and every round stores the judged version as a blob (`blob(..., write=True)`). The prior refuter already refuted this wish as J-11. The finding is also cut off in the batch.)
- J-23 The grill under auto erases the open points with no copy to recover: refuted (The grill turns open points into `[auto]` items that the spec jury judges and the report lists (CT-14, FR-14), and FR-14 says switching auto off reopens none of them, so the "answer OP-3 myself" path is not promised. Nothing requires keeping the original open-point text, as the ledger's J-11 refutation says. The mid-grill re-run duplicate is speculative, because the CT-18 text does not describe a non-idempotent flow.)
