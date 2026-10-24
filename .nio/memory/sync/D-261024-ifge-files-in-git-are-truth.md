---
id: D-261024-ifge
type: decision
title: "Memory records are markdown files in git; the index is a rebuildable cache"
status: human
answers: why
date: 2026-10-24
by: "human"
paths: ["MEMORY_NORTH_STAR.md"]
tags: ["storage", "git"]
supersedes: []
---
## Decision
Long-term memory is markdown records in `.nio/memory/`, committed to git. Graph, full-text and vector lookup live in `.nio/cache/index.db`, rebuilt from the files.
## Why
NIO's state must be readable and diffable with no database or daemon (`NORTH_STAR.md`, Principles). Git already gives sharing, history and review, so teammates sync memory with the code it explains. Keeping the index a cache means deleting it loses nothing.
## Rejected alternatives
- A database as the source of truth: needs a daemon or hosting, and its state is not diffable in a PR.
## Reuse
Any new NIO state: put the truth in committed files and derive anything faster from them.
