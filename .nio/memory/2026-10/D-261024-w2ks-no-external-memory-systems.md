---
id: D-261024-w2ks
type: decision
title: "Do not use claude-mem, Cognee or Google Memory Bank"
status: human
answers: why
date: 2026-10-24
by: "human"
paths: ["MEMORY_NORTH_STAR.md"]
tags: ["dependencies"]
supersedes: []
---
## Decision
claude-mem is inspiration only, Cognee is at most an optional backend later, and Google Memory Bank is rejected.
## Why
Memory must be agent-agnostic, live in git and avoid lock-in. claude-mem keeps its state in a local database run by a worker, outside git; a hosted memory service is lock-in. Anything external may only hold a copy that one reindex can rebuild.
## Rejected alternatives
- Building on claude-mem: a database and worker outside git.
- Google Memory Bank: hosted, lock-in.
## Reuse
Evaluate any future memory tool on one test: can it be dropped with one reindex?
