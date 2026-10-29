---
slug: checkout-refunds
retired: []
---
# Tasks: Refunds for paid orders

## E-1 Customer refunds a paid order (US-1)

### T-1 Refund a paid order in full
- Files: `app.py`
- Serves: AC-1
- Test: TC-1
- Depends on: none
- Parallel: no
- Tier: strong: money moves, and the state table guards it
- Effort: med
- Mode: split: separate test and code workers

### T-2 Reject a second refund
- Files: `app.py`
- Serves: AC-2
- Test: TC-2
- Depends on: T-1
- Parallel: no
- Tier: cheap: one guard, following T-1
- Effort: low
- Mode: split: separate test and code workers

### T-3 Refunds stay fast and pay once under load
- Files: `app.py`
- Serves: AC-1, AC-2
- Test: TC-3, TC-4
- Depends on: T-2
- Parallel: no
- Tier: max: concurrent refunds must pay once
- Effort: high
- Mode: split: separate test and code workers
