---
slug: 2026-11-05-parallel-waves
retired: []                      # QS IDs removed from this plan; never reused
---
# Quickstart: parallel waves

## Prerequisites
- `uv` installed, run from the NIO checkout: `uv run nio --help` lists `flow`.
- A demo effort at implementing, built by the test helper in a temp folder, so nothing lands in the real repo:
  `export NIO=$PWD QS=$(uv run python tests/test_waves.py --demo) && cd $QS`. It is `waves()` from `tests.md`: one
  epic whose T-1 and T-2 are `Parallel: yes` and in direct mode.
- `n` stands for `uv run --project $NIO nio`, and `S` is the demo slug `2026-10-20-refunds`. Writing commands carry `--by human`.

## Scenarios

### QS-1 Run a wave (UJ-1; auto) [default]
1. `n flow claim $S --by human | tee /tmp/qs-claim.txt`
   Expected:
   ```
   contains: task: T-1
   contains: task: T-2
   contains: worktree: .nio/runs/
   ```
2. Each worker edits its own files in its worktree:
   `W1=$(grep -A5 'task: T-1' /tmp/qs-claim.txt | sed -n 's/^worktree: //p') W2=$(grep -A5 'task: T-2' /tmp/qs-claim.txt | sed -n 's/^worktree: //p') && echo 'v = 1' > $W1/m1.py && echo 'v = 1' > $W2/m2.py && n flow green $S T-2 --run true --by human`
   Expected:
   ```
   contains: green: T-2 accepted
   contains: done: T-2
   ```
3. `n flow green $S T-1 --run true --by human`
   Expected:
   ```
   contains: done: T-1
   ```
4. `git log -2 --format=%s && git worktree list | wc -l`
   Expected:
   ```
   contains: T-1: 
   contains: T-2: 
   contains: 1
   ```
- Pass when: every step matched: two tasks were claimed together, each landed as its own commit in the order its green arrived, and no worktree is left.
