---
id: D-261024-w4pa
type: decision
title: "Group records in one folder per area, not by month"
status: human
answers: why
date: 2026-10-24
by: "human"
paths: ["MEMORY_NORTH_STAR.md", ".nio/config.json"]
tags: ["layout"]
supersedes: ["D-261024-5gsg"]
---
## Decision
Records live in `.nio/memory/<area>/`, where an area is a part of the project (a subsystem or module). Areas are listed in `memory.areas` in team config; new ones need the human.
## Why
Month folders only repeated the date already in the ID and told a reader nothing. Memory still needs a structure people can browse, and an area answers "what did we decide about this part?". Areas are named parts of the project, not file paths, so they survive code moves.
## Rejected alternatives
- Month folders: repeat the date in the ID.
- Type folders: repeat the type letter in the ID.
- Flat folder: no structure for people browsing.
- Area, then type: most folders would hold one or two files.
## Reuse
Pick the record's main area; put other areas in tags. Verdicts go in their subject's area.
