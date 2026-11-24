---
id: V-261115-kheh
type: verdict
title: "plan gate for 2026-11-15-extensions: rejected (round 1)"
answers: jury             # why | reuse | jury
date: 2026-11-15
by: "jury"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
subject: "plan:2026-11-15-extensions"
outcome: rejected
tier: medium
paths: [".nio/specs/2026-11-15-extensions/jury/plan.md"]
tags: []
supersedes: []
---
## Ruling
The plan jury ruled **rejected** for `2026-11-15-extensions` in round 1 (4 disposed, 2 merged, 12 open). Ledger: `.nio/specs/2026-11-15-extensions/jury/plan.md`.
## Jurors
| Lens | Host | Model | Vote |
| --- | --- | --- | --- |
| architecture-fit | claude-code | opus | block |
| logic | claude-code | sonnet | block |
| risk-rollback | claude-code | opus-5.5 | block |
| test-proof | claude-code | opus-5.5 | block |
## Reasons
- unresolved: J-1, J-2, J-3, J-4, J-5, J-6, J-7, J-8, J-9, J-12, J-14, J-16
- J-1 [major/inconsistency] The manifest check, the active list and the card layers call each other in a loop: open
- J-2 [major/gap] At an extension gate stage, `flow.guard` falls into the tasks gate's approval check: open
- J-3 [major/contradiction] A `gate-approved` hook runs before the approval commit that may be rolled back: open
- J-4 [major/contradiction] Joining Playwright tests "as today" produces a broken command: open
- J-5 [major/inconsistency] US-3 is built before the flow reads extensions, so TC-21 can't pass when US-3 is done: open
- J-6 [major/contradiction] An abandoned effort blocks removal forever, and the advice given doesn't unblock it: open
- J-7 [major/gap] A tampered or broken extension can't be removed, because remove runs through the guard that refuses it: open
- J-8 [major/gap] Replacing an extension with a version that drops or moves the step an effort sits at isn't refused: open
- J-10 [minor/inconsistency] A gated step fires `step-passed` when it moves to judging, and never when it actually passes: disposed accepted-risk
- J-13 [minor/scope] The e2e tester rewrites the project's Playwright config and .gitignore, which the plan doesn't list as data it changes: disposed accepted-risk
- J-17 [minor/inconsistency] TC-20 and TC-22 pass on arrival in US-3, since US-1 delivers their refusals: disposed accepted-risk
- J-18 [minor/risk] The ANSI stripping of the web-first rule is proven only under NIO_E2E: disposed accepted-risk
## What was rejected
Nothing.
