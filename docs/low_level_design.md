Title: Low Level Design
Path: docs/low_level_design.md

Purpose
-------
This document captures a consolidated low‑level design for the upload‑and‑pay Mini‑Program and its Manage (admin) panel. It consolidates decisions, data model, API surface, detailed request flows, infrastructure, security, and an implementation roadmap. Use this as the canonical engineering guide for implementation.

References
----------
- High level mini‑program spec: docs/design/mini_program_spec.md
- Admin/manage spec: docs/design/manage_spec.md
- Entities / data model: docs/design/entities.md
- API surface: docs/design/api_spec.md
- Research and background notes: docs/research/*.md

Goals & Constraints
-------------------
- Backend: Python 3.12, MySQL 8.
- Frontends: Separate Mini‑Program (WeChat, recommended uni‑app) and Admin web (React + Vite + Ant Design).
- Primary flows: file upload (presigned), order creation, payment via WeChat Pay (v3), order lifecycle management.
- Operational target: small team, low infra overhead, deployable on a single VPS or PaaS.

Technology Choices (final)
--------------------------
- Backend framework: FastAPI (async), Uvicorn workers behind Gunicorn or directly Uvicorn with process manager.
- ORM & migrations: SQLAlchemy 2.x (async support) + Alembic.
- Background worker: Dramatiq + Redis (lightweight, reliable) for checksum/thumbnail/processing.
- Object storage: AWS S3 or S3‑compatible (MinIO) in production; Qiniu optional (support included in research).
- Payments: WeChat Pay v3 (preferred). Implement v2 compatibility only if required.
- Mini‑Program frontend: uni‑app (Vue3) + Vant‑uni (recommended) or native WeApp if preferred.
- Admin frontend: React + Vite + Ant Design + TanStack Query.
- Testing: pytest, moto (S3 mocks), Playwright (E2E), Vitest for admin UI.
- CI: GitHub Actions — lint, tests, build, English MD check.

High Level Architecture
-----------------------
- Components:
  - FastAPI application (REST / OpenAPI).
  - MySQL primary database.
  - Redis (broker / cache).
  - Background worker (Dramatiq).
  - Object storage (S3 / MinIO / Qiniu).
  - WeChat Pay endpoints / webhook receiver.
  - Admin UI static site (React) served from CDN or server.
  - Mini‑Program client.

Deployment patterns:
- Development: docker‑compose with mysql, redis, minio, web, worker.
- Production: Docker images on single VPS (docker compose or systemd) or managed services (Cloud Run + managed MySQL + RDS Proxy) for reduced ops.

Data Model Summary
------------------
See docs/design/entities.md for full table definitions. Core entities:
- users, addresses, files, uploads, orders, order_items, payments, price_tables, library_categories, library_resources, admin_audit_logs, customer_service_sessions.

API Surface
-----------
Complete list in docs/design/api_spec.md. Key endpoints (examples):
- Auth: POST /v1/auth/wechat/login, /v1/auth/login, /v1/auth/refresh, /v1/auth/logout
- Files: POST /v1/files/create-upload, POST /v1/files/complete, GET /v1/files, GET /v1/files/{id}/download
- Library: GET /v1/library/categories, GET /v1/library/resources
- Orders: POST /v1/orders/create, POST /v1/orders/create-from-resource, GET /v1/orders, GET /v1/orders/{id}
- Payments: POST /v1/payments/webhook (provider webhooks)
- Admin: /admin/* endpoints protected by RBAC

Detailed Flows
--------------
1) Upload (recommended presigned POST flow)
  - Client: POST /v1/files/create-upload {filename,size,content_type}
  - Server: validate quota/type, create uploads record, generate presigned POST fields (S3 or Qiniu), return upload_id + upload_url + fields.
  - Client: wx.uploadFile to upload_url with returned form fields and file binary. Show progress via wx.onProgressUpdate.
  - Client: POST /v1/files/complete {upload_id, checksum?}
  - Server: verify object exists, verify checksum/size, set files.status=ready and return file record.

2) Order creation & payment (WeChat Pay v3)
  - Client: SELECT files/options -> POST /v1/orders/create {items, address_id}
  - Server: calculate/validate final price server‑side, create order (out_trade_no), call WeChat v3 /pay/transactions/jsapi, obtain prepay_id.
  - Server: generate client paySign (server signs with merchant private key), return params to client.
  - Client: call wx.requestPayment with returned params.
  - Server: WeChat async notifies /v1/payments/webhook; server verifies signature (Wechatpay‑Signature headers vs platform certs), update order status to PAID.

3) Admin order processing
  - Operator views orders via /admin/orders and uses PATCH /admin/orders/{id} to change status to PROCESSING -> PRINTED -> SHIPPED/COMPLETED.
  - Each admin action is recorded in admin_audit_logs (who, when, before/after).

Background processing
---------------------
- Tasks: thumbnail generation, page_count extraction, virus scanning (optional), OCR, persistent operations (image processing), file reprocessing.
- Use Dramatiq tasks enqueued on file complete or by admin reprocess.
- Ensure idempotency: tasks check DB status before running heavy ops.

Security Design
---------------
- TLS everywhere; enforce HTTPS and HSTS at ingress.
- Secrets in env vars or secret manager — never commit keys.
- WeChat merchant private key and platform certs stored securely; rotate and fetch platform certs periodically.
- Upload tokens: short TTL, restrict fsize/mime, use server controlled saveKey where appropriate.
- Private buckets for user content; generate signed download URLs for client downloads.
- Webhook verification: verify provider signatures and idempotency; log raw payloads for audit.
- RBAC: enforce server‑side. UI only reflects permissions.
- Rate limiting: presign endpoints and auth endpoints throttled to mitigate abuse.

Observability & Monitoring
-------------------------
- Logs: structured JSON logs to stdout; capture request id, user id, order id when available.
- Errors: Sentry for exceptions and alerting.
- Metrics: expose /metrics Prometheus endpoint (request latency, queue size, worker job counts, failed jobs, S3 errors).
- Health: /health and /ready endpoints for orchestration.

Testing Strategy
----------------
- Unit tests: pytest for business logic; mock S3 with moto, mock payments with provider sandbox or recorded fixtures.
- Integration tests: test DB migrations on ephemeral MySQL, test upload flow with LocalStack/MinIO.
- E2E tests: Playwright for admin UI flows and mini‑program simulator for client flows where feasible.
- CI: GitHub Actions — run lint, typecheck (mypy optional), tests, and an English MD check step that scans .md files for non‑English content.

Operational Considerations
--------------------------
- Backups: nightly MySQL backups and periodic storage lifecycle rules; retention policy per requirements.
- Scaling: single VPS initially; move DB to managed service before scaling; use CDN for static assets and admin UI.
- Disaster recovery: document RTO/RPO, test restore process.

Open Design Decisions / Optional Enhancements
--------------------------------------------
- Virus scanning: integrate ClamAV or third‑party scanning for high risk file uploads.
- Content moderation: WeChat / provider content security APIs for user generated content.
- Payment providers: add Stripe for global users in future.
- Use managed MySQL for production for simpler ops.

Implementation Roadmap (practical next tasks)
-------------------------------------------
Sprint 0 (setup)
- Create repo scaffolds: backend (FastAPI), admin (React), mini‑program (uni‑app).
- Add Dockerfile and docker‑compose with mysql, redis, minio, web, worker.
- Add precommit, linters (ruff/black), GitHub Actions skeleton.

Sprint 1 (core backend)
- Implement DB models + Alembic migrations from docs/design/entities.md.
- Implement auth (WeChat code exchange endpoint + JWT flows).
- Implement files upload intent, complete endpoints and worker scaffold.

Sprint 2 (orders & payments)
- Implement price table endpoints, orders create API, WeChat v3 prepay integration, webhook verification.
- Add payment records and reconciliation tests.

Sprint 3 (admin & frontend)
- Scaffold admin UI with Orders list and Order detail; implement API client.
- Build mini‑program skeleton with the three tabs and wire to upload + order flows.

Sprint 4 (hardening)
- Add background tasks (thumbnailing, page counting), monitoring, and alerts.
- Implement audit logs, RBAC enforcement, and add tests/coverage.

Appendices
----------
- See docs/design/api_spec.md for full endpoint definitions.
- See docs/design/entities.md for schema details and SQLAlchemy snippets.
- See docs/research/* for background research on frameworks, storage providers, payments, and mini‑program patterns.

Contact & ownership
-------------------
- Primary backend owner: (assign engineer)
- Frontend (mini‑program) owner: (assign)
- Admin UI owner: (assign)

Document history
----------------
- Created: initial consolidation of specs and research outputs.
