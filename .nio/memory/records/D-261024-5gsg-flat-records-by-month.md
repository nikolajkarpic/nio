---
id: D-261024-5gsg
type: decision
title: "Store records flat, grouped by month"
status: human
answers: why
date: 2026-10-24
by: "human"
paths: ["MEMORY_NORTH_STAR.md"]
tags: ["layout"]
supersedes: []
outdated_by: ["D-261024-w4pa"]
---
## Decision
Records live in `.nio/memory/<yyyy-mm>/`, one file per record. No folder tree that mirrors the repo, no separate decisions folder.
## Why
A decision often touches several directories, so a mirrored tree has no single right place for it and goes stale when code moves. The `paths` field plus the index answers "what touches this file" instead. Month folders keep any one directory small.
## Rejected alternatives
- Repo-mirrored tree: breaks on renames and multi-path decisions.
- One folder per record type: the type is already in the ID prefix.
## Reuse
Find records by `paths` and the index, never by folder.
