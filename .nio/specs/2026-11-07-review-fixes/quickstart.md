---
slug: 2026-11-07-review-fixes
retired: []                      # QS IDs removed from this plan; never reused
---
# Quickstart: fix the review's findings in the speed-up PRs

## Prerequisites
- `uv` installed, run from the NIO checkout: `uv run nio jury --help` lists `next`.

## Scenarios

### QS-1 A gate round with the refuter (UJ-1; auto) [agent]
1. `uv run python tests/test_jury.py test_ac1_refuter_before_its_batch_is_refused test_ac7_accepted_risk_and_edit_reruns_voters test_ac8_whitespace_edit_shows_the_human test_ac13_spec_changed_while_jurors_ran`
   Expected:
   ```
   contains: ran 4 tests, 0 failed
   ```
- Pass when: every step matched.

### QS-2 A wave task lands or is shelved (UJ-2; auto) [agent]
1. `uv run python tests/test_waves.py test_ac4b_land_keeps_bytes test_ac5b_shelve_keeps_bytes`
   Expected:
   ```
   contains: ran 2 tests, 0 failed
   ```
- Pass when: every step matched.
