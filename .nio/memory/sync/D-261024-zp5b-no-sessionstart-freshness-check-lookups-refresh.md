---
id: D-261024-zp5b
type: decision
title: "No session-start freshness check; lookups refresh the index"
status: human
answers: why              # why | reuse | jury
date: 2026-10-24
by: "human"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
serves: []                # AC IDs this decision serves
task: ""                  # task ID, if any
paths: ["src/nio/query.py", "MEMORY_NORTH_STAR.md"]
tags: ["freshness", "session"]
supersedes: []            # IDs of records this replaces
---
## Decision
v0 has no separate session-start freshness check. Lookups (`nio query`, `nio pack`) rebuild the index before answering (D-261024-f7rs), and `nio status` reports freshness when asked.
## Why
The check was meant to stop an agent from reading a stale index at the start of a session. Since every lookup already refreshes the index first, a stale index can never answer, so the check would only warm the cache early. An instruction to run it would rely on agents remembering, which is the habit NIO assumes they lack; a host `SessionStart` hook is host-specific and belongs with the journal hooks later.
## Rejected alternatives
- A recall skill step "run `nio status` at session start": agents skip it, and it protects nothing lookups do not.
- A host `SessionStart` hook now: Claude Code only, before the hooks work is designed.
## Reuse
Revisit if lookups stop refreshing the index themselves, for example once a hosted index arrives.
