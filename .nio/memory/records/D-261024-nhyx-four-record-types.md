---
id: D-261024-nhyx
type: decision
title: "Four record types; code context is derived, not stored"
status: human
answers: why
date: 2026-10-24
by: "human"
paths: ["MEMORY_NORTH_STAR.md"]
tags: ["record-format"]
supersedes: []
---
## Decision
Records are decision, verdict, lesson or change request. Code context (symbols, imports, calls) is never written as memory; it is derived from the code into the index.
## Why
Each type answers one of the three memory questions (why, reuse, jury) or carries a spec correction. Code changes on every commit, so a stored copy of it would be stale at once, while the code itself is always current.
## Rejected alternatives
- Storing code summaries as memory: duplicates the code and rots.
## Reuse
Before adding a new type, check whether it answers a memory question the four types do not.
