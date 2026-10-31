---
slug: 2026-10-27-implementation-jury
retired: []                      # QS IDs removed from this plan; never reused
---
# Quickstart: implementation jury

## Prerequisites
- `uv sync`

## Scenarios

### QS-1 Jury an implemented epic (UJ-1; auto) [derived: UJ-1]

1. `uv run python tests/test_evidence.py --demo approved`
   Expected:
   ```
   contains: outcome: approved
   ```
- Pass when: every step matched

### QS-2 A rejected epic goes back to implement (UJ-2; auto) [derived: UJ-2]

1. `uv run python tests/test_evidence.py --demo rejected`
   Expected:
   ```
   contains: outcome: rejected
   ```
- Pass when: every step matched

### QS-3 The code is right and the spec is stale (UJ-3; auto) [derived: UJ-3]

1. `uv run python tests/test_evidence.py --demo stale`
   Expected:
   ```
   contains: waiting on change
   ```
- Pass when: every step matched

### QS-4 The lens plan is over the cap (UJ-4; auto) [derived: UJ-4]

1. `uv run python tests/test_evidence.py --demo cap`
   Expected:
   ```
   contains: over the cap
   ```
- Pass when: every step matched
