---
id: D-261024-jwfg
type: decision
title: "Index is SQLite with FTS5 and sqlite-vec, vectors included in v0"
status: human
answers: why
date: 2026-10-24
by: "human"
paths: ["MEMORY_NORTH_STAR.md"]
tags: ["index", "vectors"]
supersedes: []
---
## Decision
`nio index` builds `.nio/cache/index.db`: graph tables, FTS5 full-text and int8 vectors with `sqlite-vec`, incremental by content hash.
## Why
One local file needs no server and can always be rebuilt. Vectors are cheap enough to include from the start: measured at about 40 ms per record, so 1,000 records embed in about 40 s and a typical pull re-embeds only a handful.
## Rejected alternatives
- Postgres with pgvector: needs a server; kept as a later, optional store.
- Deferring vectors until recall is measured: the cost is small enough not to wait.
## Reuse
Swap the store only behind `nio index`; records never change.
