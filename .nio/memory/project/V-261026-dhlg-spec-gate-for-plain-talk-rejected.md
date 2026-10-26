---
id: V-261026-dhlg
type: verdict
title: "spec gate for plain-talk: rejected (round 2)"
answers: jury             # why | reuse | jury
date: 2026-10-26
by: "jury"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
subject: "spec:plain-talk"
outcome: rejected
tier: low
paths: [".nio/specs/plain-talk/jury/spec.md"]
tags: []
supersedes: []
---
## Ruling
The spec jury ruled **rejected** for `plain-talk` in round 2 (1 merged, 18 open). Ledger: `.nio/specs/plain-talk/jury/spec.md`.
## Jurors
| Lens | Host | Model | Vote |
| --- | --- | --- | --- |
| consistency | claude-code | opus-5.5 | block |
| consistency | claude-code | opus-5.5 | block |
| consistency | claude-code | opus-5.5 | block |
| logic | claude-code | opus-5.5 | block |
| scope | claude-code | opus-5.5 | approve |
| testability | claude-code | opus-5.5 | block |
## Reasons
- unresolved: J-1, J-2, J-3, J-5, J-6, J-7, J-8, J-9, J-10, J-11, J-12, J-13, J-14, J-15, J-16, J-17, J-18, J-19
- J-1 [blocker/contradiction] The logged entry header drops the word `Asked`, which the grill's resume rule depends on: open
- J-2 [blocker/contradiction] Facts' sources move from the question body to `Refs:`, against an approved grill requirement: open
- J-3 [major/contradiction] `nio jury answers` does not keep working unchanged with the labelled lines: open
- J-5 [minor/inconsistency] A round gives one message several `Refs:` lines, against the definition of the Refs line, and the round's opening line is never logged: open
- J-6 [minor/contradiction] A command shown in the body can carry an ID or slug, which the no-ID rule forbids: open
- J-7 [minor/inconsistency] "area" in the first line breaks the rule against NIO terms the human does not start by name: open
- J-8 [minor/scope] NFR-1 is untraced and unconfirmed: open
- J-9 [minor/scope] AC-14 and AC-13 go beyond what the intake asks for: open
## What was rejected
Nothing.
