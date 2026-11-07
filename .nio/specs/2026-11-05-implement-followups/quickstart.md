---
slug: 2026-11-05-implement-followups
retired: []                      # QS IDs removed from this plan; never reused
---
# Quickstart: Implement follow-ups

## Prerequisites
- `uv sync`

## Scenarios

### QS-1 A blocked task reaches the next gate commit (UJ-1; auto) [derived: UJ-1]

1. `uv run python tests/test_implement.py && echo ok`
   Expected:
   ```
   contains: ok
   ```
- Pass when: every step matched

### QS-2 Red on a task whose Test line defers a TC (UJ-2; auto) [derived: UJ-2]

1. `uv run python tests/test_implement.py && echo ok`
   Expected:
   ```
   contains: ok
   ```
- Pass when: every step matched

### QS-3 A juror checks a fix that moved work into Fixes (UJ-3; auto) [derived: UJ-3]

1. `uv run python tests/test_jury.py && echo ok`
   Expected:
   ```
   contains: ok
   ```
- Pass when: every step matched

### QS-4 The evaluator rates tasks (UJ-4; auto) [derived: UJ-4]

1. `uv run python tests/test_tasks.py && uv run python tests/test_agents.py && echo ok`
   Expected:
   ```
   contains: ok
   ```
- Pass when: every step matched

### QS-5 A task's review runs the full suite on a loaded machine (UJ-5; auto) [derived: UJ-5]

1. `NIO_PERF=1 uv run python tests/test_implement.py && uv run python tests/test_flow.py && echo ok`
   Expected:
   ```
   contains: ok
   ```
- Pass when: every step matched
