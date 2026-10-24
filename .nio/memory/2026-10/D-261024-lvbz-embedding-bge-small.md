---
id: D-261024-lvbz
type: decision
title: "Embed records with bge-small-en-v1.5, pinned in team config"
status: human
answers: why
date: 2026-10-24
by: "human"
paths: ["MEMORY_NORTH_STAR.md"]
tags: ["index", "vectors"]
supersedes: []
---
## Decision
Vectors use `bge-small-en-v1.5` through `fastembed`, pinned in `.nio/config.json` so every machine builds the same index.
## Why
It is small (65 MB), runs on CPU with no API key, and is fast enough to re-embed on every pull. A pinned model keeps vectors comparable across teammates.
## Rejected alternatives
- Hosted embedding APIs: cost, a key and network on every index run.
## Reuse
If recall on the first 30 real records is poor, change the pin and re-embed; records are unaffected.
