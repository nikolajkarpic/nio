---
id: D-261024-htos
type: decision
title: "Context packs are chosen by quality, not a token budget"
status: human
answers: why              # why | reuse | jury
date: 2026-10-24
by: "human"                # role / host / model, or human
run: ""              # run ID; empty when written by hand
serves: []                # AC IDs this decision serves
task: ""                  # task ID, if any
paths: ["src/nio/pack.py"]
tags: ["pack", "context", "budget"]
supersedes: []            # IDs of records this replaces
---
## Decision
A pack has no token cap and no "top 3". Every decision and lesson on the scope's files, AC or task (tier A) is printed in full; records found only by text (tier B) are index lines, the top 10 for now. Path and AC hits outrank text; within a tier, order is relevance alone. Nothing is cut silently: the heading states the pack's size.
## Why
The 1,500-token cap and top 3 in the first spec had no evidence behind them. A record on the exact files the agent will change is relevant by definition, so cutting it to fit a number lowers quality. Text matches can be loose, so they cost one line each and the agent opens the ones that look useful with `nio get`. A huge pack is a signal that the scope is too broad or memory too fragmented, and trimming would hide it. Limits get set from measured packs and `memory-used` lines after the v0 test, not guessed.
## Rejected alternatives
- About 1,500 tokens with the full text of the top 3: a magic number with no research behind it.
- Ranking all channels equally: a loose text match could push out a record on the exact file.
- Tier B in full: loose matches would fill the pack with noise.
## Reuse
The tier B cutoff of 10 is provisional; calibrate it with the embedding model on the first ~30 real records.
