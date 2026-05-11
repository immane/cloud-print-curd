Title: Implement order create UI in mini‑program and call payment
Part: frontend

Description: Build checkout UI that collects options, calls /v1/orders/create, receives payment params, and calls wx.requestPayment.

Inputs: price table endpoint, /v1/orders/create, WeChat payments

Outputs: Checkout components and payment flow handling

Acceptance criteria: For mocked payment, app handles success and failure flows and navigates to order detail.

Estimated effort: 8h

Tags: frontend, mini-program, payments
