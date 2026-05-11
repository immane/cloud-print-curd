Title: Integrate WeChat Pay v3 create-order flow (server side)
Part: payments

Description: Implement server call to WeChat v3 transactions/jsapi to create prepay_id and return client payment params (use test credentials or mock if none available).

Inputs: WeChat merchant credentials (or sandbox mocks), order creation (Task 15)

Outputs: payment integration module, updated order record with prepay_id

Acceptance criteria: POST /v1/orders/create returns a `payment` object with required fields for wx.requestPayment (when using mock, return a stub). Verify webhook handling separately.

Estimated effort: 8h

Tags: payments, backend
