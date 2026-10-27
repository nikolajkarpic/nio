---
slug: checkout-refunds
retired: []
---
# Contracts: Refunds for paid orders

## Contracts

### CT-1 Refund an order (FR-1, FR-2) [research: RF-5]
- Binding: `app.py:refund_order` (new)
- Kind: function
- Shape: `refund_order(order_id: str, by: str) -> Refund`
- Accepts: the ID of an order in state `paid`
- Returns: the refund, for the full order total
- Fails: order already refunded → `AlreadyRefunded("already refunded")`, no payment created
- Rules: "refund the full order amount" (FR-1)
- State: follows the spec's state table order

### CT-2 Refund over HTTP (FR-1, FR-2, NFR-1) [default]
- Binding: `app.py` (existing)
- Kind: http
- Shape: `POST /orders/<id>/refund`
- Fails: `AlreadyRefunded` → 409 `{"error": "already refunded"}`
