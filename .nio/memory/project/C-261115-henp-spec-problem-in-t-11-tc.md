---
id: C-261115-henp
type: change
title: "Spec problem in T-11: TC-17 Assert: the IDs are exactly the three records pointing at the effort, sorted (CT-6: records whose `paths` hold an entry starting with `.nio/specs/<slug>/`, or whose `against` equals the slug)"
answers: why              # why | reuse | jury
date: 2026-11-15
by: "driver / claude-code / claude-opus-5-5"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
against: ".nio/specs/2026-11-15-effort-drilldown-install/tests.md"
outcome: accepted         # pending | accepted | rejected
paths: [".nio/specs/2026-11-15-effort-drilldown-install/tests.md"]
tags: []
supersedes: []
---
## What is wrong
The spec says: TC-17 Assert: the IDs are exactly the three records pointing at the effort, sorted (CT-6: records whose `paths` hold an entry starting with `.nio/specs/<slug>/`, or whose `against` equals the slug)

The code shows: tests/test_flow.py:3174. The `effort('planning')` fixture (tests/test_flow.py:78, approve('spec')) already writes a real verdict record to .nio/memory with `paths: [.nio/specs/2026-10-20-refunds/jury/spec.md]`. CT-6 correctly matches it, so `flow.memory` returns 4 records: C-261115-bbbb, D-261115-dddd, V-261115-aaaa and the fixture's own verdict (random ID per run). The assert expects exactly 3.
## Proposed change
Change the TC-17 test, not CT-6. Either filter the fixture's own verdict out, or assert the three expected IDs are a subset and that the src/other.py decision is absent. Alternatively, build the repo at a stage before the spec-jury approval if that stage writes no verdict.

Handoff: fd4329e91e6cad724d367832b890d18adfca417a3d2511694799a165d7745b68
## Human decision
Accepted by the human on 2026-11-15 in the orchestrator session: "Expect all 4 exactly: the test lists the helper's verdict as a 4th expected record and still checks the exact set, so it would catch both a missing and an extra record." TC-17's Setup now notes the fixture's own spec-jury verdict, and its Assert expects exactly those four IDs. CT-6 is unchanged.
