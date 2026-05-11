Title: Implement order creation endpoint (server price validation)
Part: orders

Description: POST /v1/orders/create should accept items, validate final price with server price rules, create order row, and return order data.

Inputs: price table, files table, users

Outputs: route, orders table migration

Acceptance criteria: Orders created with total matching server calculation and status CREATED.

Estimated effort: 4h

Tags: backend, orders
