---
id: V-261031-7q7j
type: verdict
title: "implementation-E-2 gate for 2026-10-27-implementation-jury: rejected (round 1)"
answers: jury             # why | reuse | jury
date: 2026-10-31
by: "jury"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
subject: "implementation-E-2:2026-10-27-implementation-jury"
outcome: rejected
tier: medium
paths: [".nio/specs/2026-10-27-implementation-jury/jury/implementation-E-2.md"]
tags: []
supersedes: []
---
## Ruling
The implementation-E-2 jury ruled **rejected** for `2026-10-27-implementation-jury` in round 1 (11 disposed, 1 open). Ledger: `.nio/specs/2026-10-27-implementation-jury/jury/implementation-E-2.md`.
## Jurors
| Lens | Host | Model | Vote |
| --- | --- | --- | --- |
| adversary | claude-code | claude-sonnet-5-5 | block |
| conformance | claude-code | sonnet-5-5 | approve |
| consistency | claude-code | claude-haiku-5-5 | block |
| correctness | claude-code | claude-sonnet-5-5 | block |
## Reasons
- unresolved: J-1, J-2, J-3, J-4, J-5, J-6, J-7, J-8, J-10, J-11, J-12
- J-1 [major/gap] test tampering: test_ac29_epic_skipped in tests/test_implement.py is deleted: disposed fix-task
- J-2 [major/gap] Core lenses are not enforced; an approval can skip conformance and correctness: disposed fix-task
- J-3 [major/gap] `--pick` is accepted when the plan is not over the cap, so one command silently drops risk lenses and the record blames the human: disposed fix-task
- J-4 [major/gap] An `auto` journey whose steps don't parse is recorded as passed without running anything: disposed fix-task
- J-5 [major/gap] With a test runner the CLI can't address, every scripted attack becomes "not configured" and every test "unknown", and both count as evidence: disposed fix-task
- J-6 [major/gap] `results.json` is never tied to the gate's epic or to the commit being judged: disposed fix-task
- J-7 [major/contradiction] Tampering dispose rule in CT-20 doesn't match the code's fix-task exception: disposed fix-task
- J-8 [major/gap] The consistency lens's decision check has no decisions in its pack: disposed fix-task
- J-9 [minor/inconsistency] results.json holds a `suite` key the CT-7 Shape doesn't list: open
## What was rejected
Nothing.
