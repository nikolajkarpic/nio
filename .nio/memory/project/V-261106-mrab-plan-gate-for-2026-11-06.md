---
id: V-261106-mrab
type: verdict
title: "plan gate for 2026-11-06-faster-checks: rejected (round 1)"
answers: jury             # why | reuse | jury
date: 2026-11-06
by: "jury"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
subject: "plan:2026-11-06-faster-checks"
outcome: rejected
tier: medium
paths: [".nio/specs/2026-11-06-faster-checks/jury/plan.md"]
tags: []
supersedes: []
---
## Ruling
The plan jury ruled **rejected** for `2026-11-06-faster-checks` in round 1 (1 merged, 7 open, 1 refuted). Ledger: `.nio/specs/2026-11-06-faster-checks/jury/plan.md`.
## Jurors
| Lens | Host | Model | Vote |
| --- | --- | --- | --- |
| architecture-fit | claude-code | claude-opus-5-5 | block |
| test-proof | claude-code | claude-opus-5-5 | block |
## Reasons
- unresolved: J-1, J-2, J-4, J-6, J-7, J-8, J-9
- J-1 [major/inconsistency] CT-5's "commit subject is T-n" condition never fails, so TC-10 and TC-18 expect behaviour CT-5 doesn't have: open
- J-2 [major/inconsistency] US-3 is built before the CT-4 field it relies on: open
- J-6 [major/gap] TC-6 can't see whether a signal-killed file stops xargs, because all its files start in one batch: open
- J-7 [major/risk] TC-5 is a wall-clock test inside the parallel suite, which the plan itself says would fail under load: open
- J-4 [minor/gap] CT-1 leaves out test_flow.py's own `nio` subprocess helper: open
- J-8 [minor/gap] TC-3's flow.lock assertion can never fail: open
- J-9 [minor/gap] TC-20's "doesn't close its epic" half has no such task in its setup: open
## What was rejected
- J-3 Running test_flow's CLI calls in-process can import fastembed, breaking test_nfr2_offline's check: refuted (`index.embed` imports fastembed lazily (index.py:48), and only `query`, `index` and `pack` reach it (query.py, cli.py:343). The `cli` helper in test_flow.py only runs `nio flow ...`, and flow commands never call `embed`. `test_nfr2_offline` runs in the test_flow process, and the `nio(...)` helper CT-1 doesn't convert stays a subprocess. So going in-process cannot put fastembed into that process's `sys.modules`.)
