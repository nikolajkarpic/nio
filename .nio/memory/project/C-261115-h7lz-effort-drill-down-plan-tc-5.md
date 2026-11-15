---
id: C-261115-h7lz
type: change
title: "Effort drill-down plan: TC-5 moves from the timeline story to the cost story"
answers: why              # why | reuse | jury
date: 2026-11-15
by: "driver / claude-code / claude-opus-5-5"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
against: ".nio/specs/2026-11-15-effort-drilldown-install/plan.md"
outcome: accepted          # pending | accepted | rejected
paths: [".nio/specs/2026-11-15-effort-drilldown-install/plan.md", ".nio/specs/2026-11-15-effort-drilldown-install/tasks.md"]
tags: [tasks-gate, effort-drilldown, build-order]
supersedes: []
---
## What is wrong
The approved plan lists TC-5 under the build order's US-1 entry (timeline). TC-5 asserts that after a bad
history line the juries, tasks, memory and cost sections of `nio flow show` still work. Those sections are
built in later epics (US-2, US-3, US-5 and US-4, which depends on all of them), so in E-2 (T-5) TC-5 cannot
pass. The tasks jury raised this as J-2; tasks.md also named TC-5 in T-1's title.

## Proposed change
In plan.md's build order, TC-5 moves from the US-1 entry to the US-4 entry (cost), the last section story,
which depends on Foundation, US-1, US-2, US-3 and US-5. In tasks.md, TC-5 moves to T-10's Test line (T-10 wires
the cost section into `show`, the last section) and out of T-5's Test line and T-1's title. Nothing else changes.

## Human decision
Accepted by the human on 2026-11-15, in the tasks-gate session, ruling J-2 `fix`: "Fix it: move TC-5 to the
cost task (T-10) via a change request to the plan; human approved the change request".
