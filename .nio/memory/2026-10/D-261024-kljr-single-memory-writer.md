---
id: D-261024-kljr
type: decision
title: "One configured writer owns memory; other agents add candidates"
status: human
answers: why
date: 2026-10-24
by: "human"
paths: ["MEMORY_NORTH_STAR.md"]
tags: ["writing"]
supersedes: []
---
## Decision
Only the configured memory-writer role writes `.nio/memory/`. Other agents append candidates to the run's `promote.md`; the writer promotes them with the admission rule and dedup. Verdicts and change requests are written directly.
## Why
Many agents writing memory directly produce duplicates and junk. One writer applying one admission rule keeps records useful. Verdicts and change requests skip promotion because traceability needs every one.
## Rejected alternatives
- Every agent writes records: duplicates and low-quality records.
## Reuse
New pipeline stages emit an event and append candidates; they never write records themselves.
