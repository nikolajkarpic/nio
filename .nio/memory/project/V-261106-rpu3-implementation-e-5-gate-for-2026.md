---
id: V-261106-rpu3
type: verdict
title: "implementation-E-5 gate for 2026-11-05-implement-followups: rejected (round 1)"
answers: jury             # why | reuse | jury
date: 2026-11-06
by: "jury"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
subject: "implementation-E-5:2026-11-05-implement-followups"
outcome: rejected
tier: medium
paths: [".nio/specs/2026-11-05-implement-followups/jury/implementation-E-5.md"]
tags: []
supersedes: []
---
## Ruling
The implementation-E-5 jury ruled **rejected** for `2026-11-05-implement-followups` in round 1 (1 disposed, 4 open, 2 refuted). Ledger: `.nio/specs/2026-11-05-implement-followups/jury/implementation-E-5.md`.
## Jurors
| Lens | Host | Model | Vote |
| --- | --- | --- | --- |
| adversary | claude-code | claude-sonnet-5-5 | approve |
| conformance | claude-code | claude-sonnet-5-5 | approve |
| consistency | claude-code | claude-haiku-5-5 | block |
| correctness | claude-code | claude-sonnet-5-5 | approve |
## Reasons
- unresolved: J-4
- J-4 [major/inconsistency] The tasks skill starts its run with a form the CLI refuses: disposed fix-task
- J-2 [minor/risk] Evaluator-left default `Effort: med` is undetectable, and the dead exact-match exemption is a silent-pass path: open
- J-3 [minor/gap] A stale or missing copy is accepted or crashes: open
- J-6 [minor/inconsistency] The rating guard compares a sentinel the drafter never writes, and the tests use that form: open
- J-7 [minor/gap] A missing or unreadable copy crashes the check with a traceback: open
## What was rejected
- J-1 Plain `nio check tasks` now accepts unrated tasks, so only the optional flag stops them: refuted (FR-9, AC-26/27 and CT-7 define the rejection of unrated tasks only for `nio check tasks --rated-from`; CT-11 and AC-28 make the tasks skill pass that flag after the evaluator. No requirement says plain `nio check tasks` or `--approved` must reject `to be rated`, so asking for that goes beyond this spec.)
- J-5 Nothing forces the evaluator to rate Mode, so a skipped Mode passes both checks: refuted (FR-9 and AC-27 require only that non-rating lines stay unchanged and that no line still reads `to be rated`. Nothing requires the evaluator's Mode edit to be detectable, and CT-7 says nothing about a drafter `Mode: to be rated` sentinel. The finding asks for a requirement the spec doesn't have.)
