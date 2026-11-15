---
slug: checkout-refunds
retired: []
---
# Tasks: Refunds for paid orders

## E-1 Customer refunds a paid order (US-1)
- Tier: max: money moves, concurrent refunds must pay once
- Effort: med

### T-1 Refund a paid order in full
- Files: `app.py`
- Serves: AC-1
- Test: TC-1
- Depends on: none
- Parallel: no

### T-2 Reject a second refund
- Files: `app.py`
- Serves: AC-2
- Test: TC-2
- Depends on: T-1
- Parallel: no

### T-3 Refunds stay fast and pay once under load
- Files: `app.py`
- Serves: AC-1, AC-2
- Test: TC-3, TC-4
- Depends on: T-2
- Parallel: no
