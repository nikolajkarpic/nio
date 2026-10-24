---
id: D-261024-6rf3
type: decision
title: "Records are markdown with flat YAML frontmatter; config stays JSON"
status: human
answers: why
date: 2026-10-24
by: "human"
paths: ["MEMORY_NORTH_STAR.md"]
tags: ["record-format"]
supersedes: []
---
## Decision
A record is a short markdown body for agents plus flat YAML frontmatter for tools, parsed strictly with a YAML 1.2 loader and a schema per type. Config files stay JSON.
## Why
Agents read prose and scripts need exact fields for the index, lint and conflict checks; frontmatter gives both in one file, in the same format as `SKILL.md`. Config is settings for tools, validated by a JSON Schema, so JSON fits it better.
## Rejected alternatives
- Nested frontmatter: harder to parse reliably; structured data goes in a body table.
- JSON records: unpleasant for agents and humans to read.
## Reuse
Quote any value YAML could misread (`no`, dates).
