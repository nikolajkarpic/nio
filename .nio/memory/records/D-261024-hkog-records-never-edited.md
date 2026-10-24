---
id: D-261024-hkog
type: decision
title: "Records are never edited; superseded is derived"
status: human
answers: why
date: 2026-10-24
by: "human"
paths: ["MEMORY_NORTH_STAR.md"]
tags: ["record-format", "merge"]
supersedes: []
outdated_by: ["D-261024-g5lm"]
---
## Decision
A changed decision is a new record that lists the old one in `supersedes`. The old file is never touched; the index derives that it is superseded.
## Why
If the old record had to flip its own `status`, two branches superseding it would both edit the same line and conflict in git. With no edits, git never conflicts inside `.nio/memory/`, and history stays a plain append log.
## Rejected alternatives
- Setting `status: superseded` on the old record: the one edit that caused merge conflicts.
## Reuse
Any link between records points backward from the newer record; reverse links come from the index.
