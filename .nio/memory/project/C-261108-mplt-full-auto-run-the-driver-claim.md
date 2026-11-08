---
id: C-261108-mplt
type: change
title: "Full-auto run: the driver claim goes stale on its refresh time alone, not on a gone process"
answers: why              # why | reuse | jury
date: 2026-11-08
by: "planner / claude-code / claude-opus-5-5"                # role / host / model, or human
run: "R-261108-ypjt"              # run ID; empty when written by hand
against: ".nio/specs/2026-11-08-full-auto-run/spec.md"               # the spec, plan or record that is wrong
outcome: accepted         # pending | accepted | rejected
paths: [.nio/specs/2026-11-08-full-auto-run/spec.md, .nio/specs/2026-11-08-full-auto-run/architecture.md]
tags: [full-auto-run, driver-claim]
supersedes: []
---
## What is wrong
FR-38 and AC-38 treat a driver as running only while its claim names a process that is alive on its machine. Every `nio` call is a short-lived process, so the claim has no long-lived process to name: the only candidates are a walk up the parent processes to the host session (Linux-only, fragile) or a process ID the driver chooses (the agent's word). The architecture note (.nio/specs/2026-11-08-full-auto-run/architecture.md, "Stored data") settles the claim on its refresh time alone; the human chose that on 2026-11-08.
## Proposed change
- FR-38 becomes: "THE SYSTEM SHALL treat a driver as running while its claim was refreshed within the last 30 minutes; the claim is taken atomically, so of two drivers starting at once exactly one gets it; the driver refreshes its claim at each stage and at least every 10 minutes while it waits on a long command; a claim older than 30 minutes is stale and may be taken over by a new driver. [human]"
- AC-38 becomes: "Given a driver claim last refreshed 31 minutes ago, when a new driver starts, then it takes the effort over; given a claim refreshed 5 minutes ago, it is refused. Observable: the claim names the new driver in the first case; in the second, non-zero exit naming the running driver and the claim unchanged. Level: unit. [human]"
- Risks gains: "A driver that crashed holds the effort for up to 30 minutes, since its claim goes stale only by age. [human]"
## Human decision
Accepted by the human on 2026-11-08: refresh time alone; a crashed driver may hold the effort up to 30 minutes.
