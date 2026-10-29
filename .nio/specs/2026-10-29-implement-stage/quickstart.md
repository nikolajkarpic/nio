---
slug: 2026-10-29-implement-stage
retired: []                      # QS IDs removed from this plan; never reused
---
# Quickstart: implement stage

## Prerequisites
- `uv` installed, run from the NIO checkout: `uv run nio --help` lists `flow`.
- A demo effort at implementing, built by the test helper in a temp folder, so nothing lands in the real repo:
  `export NIO=$PWD QS=$(uv run python tests/test_implement.py --demo) && cd $QS`.
  - It is `impl()` from `tests.md`: the refunds tasks, where T-1 has `Mode: split` and T-2 and T-3 have `Mode: direct`, and an empty `app.py`; QS-1 writes T-1's test.
  - Every scenario runs in `$QS`, in order. Each one carries on from the state the one before left.
- `n` stands for `uv run --project $NIO nio`, and `S` is the demo slug `2026-10-20-refunds`. Writing commands carry `--by human`.

## Scenarios

### QS-1 Work one task in split mode (UJ-1; auto) [default]
1. `n flow claim $S --by human`
   Expected:
   ```
   contains: task: T-1 Refund a paid order in full
   contains: mode: split
   contains: card: nio-worker-strong
   contains: pack: .nio/runs/
   ```
2. The test phase writes T-1's test (C-261029-aaxx):
   `printf 'import unittest\n\nimport app\n\n\nclass T(unittest.TestCase):\n    def test_refund(self):\n        self.assertEqual(getattr(app, "refund", lambda x: 0)(40), 40)\n' > tests/test_refund.py && n flow red $S T-1 --run "python -m unittest tests/test_refund.py" --by human`
   Expected:
   ```
   contains: red: T-1 accepted
   contains: tests/test_refund.py
   ```
3. `printf 'def refund(order):\n    return order\n' > app.py && n flow green $S T-1 --by human`
   Expected:
   ```
   contains: green: T-1 accepted
   contains: done: T-1
   ```
4. `git log -1 --format=%s && git branch --show-current`
   Expected:
   ```
   T-1: Refund a paid order in full
   nio/2026-10-20-refunds
   ```
- Pass when: every step matched, and `git rev-parse main` is the same as before step 1.

### QS-2 A worker finds the spec wrong (UJ-2; auto) [default]
1. `n flow claim $S --by human`
   Expected:
   ```
   contains: task: T-2
   contains: mode: direct
   ```
2. `printf -- '---\nstatus: blocked\nchange_request:\n  spec_says: "reject a second refund"\n  code_shows: "orders keep no refund count"\n  smallest_change: "add refunded to Order"\n---\n' > handoff.md && n flow block $S T-2 --handoff handoff.md --by human`
   Expected:
   ```
   contains: blocked: T-2
   contains: C-
   ```
3. `n flow next $S`
   Expected:
   ```
   contains: waiting_for_human
   contains: T-2
   ```
- Pass when: every step matched, and exactly one new `C-*.md` under `.nio/memory/project/` has `outcome: pending`.

### QS-3 Finish an epic (UJ-3; auto) [default]
1. You decide QS-2's change request, keeping the spec as it is (C-261029-aaxx): `sed -i 's/^outcome: pending/outcome: rejected/' $(grep -l "Spec problem in T-2" .nio/memory/*/C-*.md) && n flow unblock $S T-2 --human "spec settled" --by human && n flow claim $S --by human`
   Expected:
   ```
   contains: unblocked: T-2
   contains: task: T-2
   ```
2. `printf 'def refund(order):\n    return order\n\ndef second(order):\n    raise ValueError\n' > app.py && n flow green $S T-2 --run "python -m unittest tests/test_refund.py" --by human`
   Expected:
   ```
   contains: done: T-2
   ```
3. `n flow claim $S --by human && n flow green $S T-3 --run "python -m unittest tests/test_refund.py" --by human`
   Expected:
   ```
   contains: done: T-3
   contains: skipped: not built
   contains: notify:
   ```
4. `n flow next $S`
   Expected:
   ```
   contains: done
   ```
- Pass when: every step matched, and `n flow status` lists the demo effort as `done`.
