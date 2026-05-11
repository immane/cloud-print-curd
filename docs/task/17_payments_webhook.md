Title: Implement payments webhook receiver and verification
Part: payments

Description: POST /v1/payments/webhook to receive WeChat notifications and verify signatures against platform certs; update order status to PAID.

Inputs: platform certs (or sandbox), provider webhook body samples

Outputs: webhook route, payments table migration

Acceptance criteria: Valid signed webhook updates order status and creates a payments record; invalid webhooks are rejected.

Estimated effort: 6h

Tags: payments, security
