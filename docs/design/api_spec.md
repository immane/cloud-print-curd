Title: API Specification
Path: docs/design/api_spec.md

Overview
--------
This document lists the REST API endpoints used by the Mini‑Program frontend and the Manage (admin) panel. It is an actionable reference for backend implementation and client integration. All responses use JSON unless otherwise noted. Authentication is via JWT access token in Authorization: Bearer <token> for user and admin APIs, except WeChat login endpoints which use code exchange.

Error envelope
--------------
All error responses use:
{
  "error": {
    "code": "string",
    "message": "human readable",
    "details": null | { ... }
  }
}

Auth / Security
---------------
- POST /v1/auth/login (email/password) -> returns {access_token, refresh_token, expires_in}
- POST /v1/auth/refresh -> returns new access_token
- POST /v1/auth/logout -> invalidate refresh token
- POST /v1/auth/wechat/login -> body {code} -> exchanges code for openid/session, creates/returns tokens
- Protected endpoints require Authorization: Bearer <access_token>

Common parameters
- Pagination: page, page_size (or cursor & limit for cursor pagination).

Public / User APIs
------------------
Auth
- POST /v1/auth/wechat/login
  - Body: { "code": "<wx_code>" }
  - Response: { "access_token": "", "refresh_token": "", "user": {id, display_name, avatar_url} }

- POST /v1/auth/login
  - Body: { "email": "", "password": "" }
  - Response: { access_token, refresh_token, user }

- POST /v1/auth/refresh
  - Body: { refresh_token }
  - Response: { access_token }

- POST /v1/auth/logout
  - Auth required
  - Body: {} -> revokes refresh token

User profile
- GET /v1/users/me
  - Auth required
  - Response: { id, display_name, avatar_url, balance_cents, roles }

Files & Uploads
- POST /v1/files/create-upload
  - Auth required
  - Body: { filename, size, content_type }
  - Response: { upload_id, storage_provider, upload_url, fields }  // fields for presigned POST

- POST /v1/files/complete
  - Auth required
  - Body: { upload_id, checksum? }
  - Response: { file: { id, filename, storage_key, status, page_count, preview_url } }

- GET /v1/files
  - Auth required
  - Query: page, page_size
  - Response: { items: [file], total }

- GET /v1/files/{id}
  - Auth required (owner or admin)
  - Response: file object

- GET /v1/files/{id}/download
  - Auth required
  - Response: { url: "presigned_download_url", expires_at }

- DELETE /v1/files/{id}
  - Auth required (owner) -> soft delete

Library (Public resources)
- GET /v1/library/categories
  - Response: [{id,name,order}]

- GET /v1/library/resources
  - Query: category_id, page, page_size
  - Response: [{id,title,thumbnail_url,page_count,file_key,preview_url}]

- GET /v1/library/resources/{id}
  - Response: resource details

Orders & Payments
- POST /v1/orders/create-from-resource
  - Auth required
  - Body: { resource_id, options: {paper_type,size,color,duplex,copies}, address_id }
  - Response: { order_id, total_cents, payment: { provider: 'wechat', params: {...} } }

- POST /v1/orders/create
  - Auth required
  - Body: { items: [{file_id, options}], address_id }
  - Response: { order_id, total_cents, payment }

- GET /v1/orders
  - Auth required
  - Query: status, page, page_size
  - Response: { items: [order], total }

- GET /v1/orders/{id}
  - Auth required (owner or admin)
  - Response: order details, items, timeline, payment records

- POST /v1/payments/webhook
  - Public endpoint (WeChat/Stripe calls)
  - Body: provider-specific signature headers and payload
  - Response: 200 OK when processed

- POST /v1/orders/{id}/refund
  - Auth required (Finance/Admin)
  - Body: { amount_cents, reason }
  - Response: { refund_id, status }

Prices
- GET /v1/prices/tip
  - Response: { text }

- GET /v1/prices
  - Query: paper_type?, size?
  - Response: [{paper_type,size,unit_price_cents,description,currency}]

Support & Customer Service
- GET /v1/support/session-info
  - Query: order_id
  - Response: { sessionFrom, sendMessageTitle, sendMessagePath }

Admin / Manage APIs (require admin JWT / RBAC)
------------------------------------------------
Auth & Users
- POST /admin/auth/login
  - Body: { username, password }
  - Response: { access_token }

- GET /admin/users
  - Query: search, page, page_size
  - Response: { items: [user], total }

- GET /admin/users/{id}
  - Response: user details, orders, files

- POST /admin/users/{id}/adjust-balance
  - Body: { amount_cents, reason }
  - Response: { success }

Orders
- GET /admin/orders
  - Query: status, assigned, from, to, page, page_size
  - Response: { items: [order], total }

- GET /admin/orders/{id}
  - Response: full order details, audit log for order

- PATCH /admin/orders/{id}
  - Body: { status?, assigned_to?, note? }
  - Response: updated order

- POST /admin/orders/{id}/refund
  - Body: { amount_cents, reason }
  - Response: refund record

Files and Processing
- GET /admin/files
  - Query: status, user_id, page
  - Response: files list

- POST /admin/files/{id}/reprocess
  - Triggers background worker to recompute metadata/thumbnail

Library & Prices
- GET /admin/library/categories
- POST /admin/library/resources
  - Body: { title, category_id, file_id, page_count, price_override_cents }

- GET /admin/prices/versions
  - Response: versions list

- POST /admin/prices/versions
  - Body: { name, rules_json }
  - Response: { version_id }

Customer Service / Conversations
- GET /admin/conversations
  - Query: status, user_id, order_id, page

- GET /admin/conversations/{id}
  - Response: threaded messages, participants, tags

- POST /admin/conversations/{id}/message
  - Body: { text, attachments[] }

Metrics & Admin
- GET /admin/metrics
  - Response: dashboard numbers: orders_today, revenue_today, new_users, pending_webhooks

Webhooks & Background
---------------------
- POST /webhooks/storage/notify
  - Provider storage callback for completed upload (optional if using upload complete flow)

- POST /webhooks/payment/{provider}
  - Provider specific webhooks (WeChat / Stripe) forwarded to /v1/payments/webhook

Attachment handling
-------------------
- Attachments for chat or admin uploads should follow the same upload intent flow: POST /v1/files/create-upload -> upload to storage -> POST /v1/files/complete -> attach metadata in message payload referencing file_id.

Rate limits & quotas
--------------------
- Rate limit authentication endpoints and presign endpoints to mitigate abuse. Suggested rates: 20 req/min per IP for unauthenticated presign requests, 100 req/min authenticated.

Notes & next steps
------------------
- This spec is a baseline; implement OpenAPI schema from these endpoints for codegen and client SDK generation.
- Add detailed JSON schemas (components/schemas) as implementation proceeds.

File created: docs/design/api_spec.md
