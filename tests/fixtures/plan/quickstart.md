---
slug: checkout-refunds
retired: []
---
# Quickstart: Refunds for paid orders

## Prerequisites
- A dev server: `python app.py --port 8000`

## Scenarios

### QS-1 Customer refunds a paid order (UJ-1; auto) [default]
1. `curl -s -X POST localhost:8000/orders/o1/refund`
   Expected:
   ```
   {"state": "refunded", "amount": 40.00}
   ```
2. `curl -s -X POST localhost:8000/orders/o1/refund`
   Expected:
   ```
   contains: already refunded
   ```
- Pass when: every step matched
