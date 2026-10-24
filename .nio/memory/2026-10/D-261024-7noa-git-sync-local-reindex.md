---
id: D-261024-7noa
type: decision
title: "Teams sync through git and re-index locally; hosted index later"
status: human
answers: why
date: 2026-10-24
by: "human"
paths: ["MEMORY_NORTH_STAR.md"]
tags: ["sync", "team"]
supersedes: []
---
## Decision
Git carries the records. Each machine re-indexes incrementally after every pull. A hosted Postgres index, with CI as its only writer, is a later option.
## Why
Records already travel with the code, so no second sync system is needed. Re-indexing a few changed records is fast. A hosted index only helps once the repo is too big to index locally.
## Rejected alternatives
- A shared hosted index from day one: another service to run before anyone needs it.
## Reuse
Never make a hosted index the only copy; it must be droppable with one reindex.
