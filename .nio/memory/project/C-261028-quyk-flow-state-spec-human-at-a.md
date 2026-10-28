---
id: C-261028-quyk
type: change
title: "Flow-state spec: --human at a jury gate goes through nio jury check"
answers: why              # why | reuse | jury
date: 2026-10-28
by: "agent / claude-code / opus"                # role / host / model, or human
run: "R-261028-stif"              # run ID; empty when written by hand
against: ".nio/specs/2026-10-28-flow-state/spec.md"# the spec, plan or record that is wrong
outcome: accepted         # pending | accepted | rejected
paths: [".nio/specs/2026-10-28-flow-state/spec.md"]
tags: [flow-state, override]
supersedes: []
---
## What is wrong
FR-24 lets `nio flow done <stage> --human` pass any failing guard, gates included. On a gate the jury rejected, the override is undone on the next call, because the ledger still says rejected and `nio flow` never writes it (FR-56). Plan jury finding J-6 (logic).
## Proposed change
FR-24 applies to stages that are not gates. At a jury gate (spec_jury, plan_jury, tasks_jury), `nio flow done <gate> --human` refuses and prints `nio jury check <slug> <gate> --human "<reason>" --record`; FR-27 then counts that closure as the override. Add an AC for the refusal.
## Human decision
Accepted by the human (2026-10-28, flow-state grill Q24).
