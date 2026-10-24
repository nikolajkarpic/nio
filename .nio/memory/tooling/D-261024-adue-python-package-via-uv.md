---
id: D-261024-adue
type: decision
title: "Scripts ship as the Python package `nio`, installed with uv"
status: human
answers: why
date: 2026-10-24
by: "human"
paths: ["MEMORY_NORTH_STAR.md"]
tags: ["tooling"]
supersedes: []
---
## Decision
Whatever instructions cannot do reliably (IDs, lint, index, query, pack) lives in a Python package `nio`, installed with `uv tool install` or run with `uvx`.
## Why
Skills stay plain instructions any host can follow; the CLI covers what an agent would do unreliably by hand. Python has SQLite, FTS5, `sqlite-vec` and `fastembed` available, and uv installs it in one command.
## Rejected alternatives
- Shell scripts: no good vector or YAML tooling.
- MCP-only tools: lock NIO to hosts with MCP; MCP stays an optional extra.
## Reuse
Add a CLI command only when a skill step keeps going wrong as plain instructions.
