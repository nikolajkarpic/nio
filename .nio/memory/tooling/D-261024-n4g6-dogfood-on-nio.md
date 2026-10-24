---
id: D-261024-n4g6
type: decision
title: "NIO dogfoods its memory on this repo, starting with hand-written records"
status: human
answers: why
date: 2026-10-24
by: "human"
paths: ["MEMORY_NORTH_STAR.md"]
tags: ["v0", "dogfood"]
supersedes: []
---
## Decision
NIO keeps its own decisions in this repo's `.nio/memory/`, starting with hand-written records, and `@nio:remember` works by hand in any session.
## Why
The pipeline stages that fire memory events (jury, tasks) do not exist yet, so memory needs a manual entry point to be used at all. Writing the first records by hand tests the format before any code exists.
## Rejected alternatives
- Waiting for the pipeline to generate records: memory would sit untested.
## Reuse
Record each design decision about NIO here as it is made.
