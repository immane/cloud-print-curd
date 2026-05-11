Title: Manage (Admin) Panel Specification
Path: docs/design/manage_spec.md

Overview
--------
This document specifies the operator (manage/admin) web application that complements the Mini‑Program user app described in docs/design/mini_program_spec.md. The manage panel is a desktop‑focused React app (or equivalent) used by staff to manage orders, files, users, pricing, library resources, and support. The design prioritizes efficient list operations, quick search, clear status transitions, auditability, and minimal operational friction.

High level goals
- Provide a single place for staff to: monitor and process print orders, manage library resources, maintain price tables, manage user accounts and balances, view and respond to customer service requests, and view system metrics.
- Fast workflows for bulk operations (status updates, reassign, refund).
- Full audit logs for regulatory and dispute purposes.

Users, roles & permissions
- Roles:
  - Admin: full access to everything (users, prices, orders, refunds, settings).
  - Operator: process orders, update statuses, send notifications, view user details, but cannot change price tables or billing settings.
  - Finance: access to payments, refunds, billing reports, and manual refund operations.
  - Support: access to customer conversations, order lookups, and canned responses.
- Permissions matrix: implement RBAC on backend and enforce in UI (hide/disable actions client‑side).

Key pages & layout
- Top nav: brand, global search (order id / user / file), notifications, user menu (profile, sign out).
- Left sidebar (collapsible): Dashboard, Orders, Files, Library, Prices, Users, Payments, Customer Service, Reports, Settings, Audit Logs.

1) Dashboard
- Purpose: real-time overview and quick actions.
- Panels:
  - Key metrics: orders (today / pending / processing / completed), revenue today, balance outstanding, new users today.
  - Incoming queue: latest 20 orders (with quick action buttons: View / Accept / Assign / Cancel).
  - System health: background worker status, storage health, last webhook processed time, Sentry errors count.
  - Quick filters: jump to pending payments / urgent orders.

2) Orders (primary operator view)
- Main grid columns:
  - Order ID, User (link), Status (badge), Items (count), Total (currency), Payment status, Created at, Updated at, Assigned operator, Actions.
- Filters:
  - Status (multi), Created date range, Payment status, Assigned operator, Search by order id / user / file key.
- Actions (row level): View details modal, Change status (dropdown), Assign operator, Add note, Refund (Finance only), Export order PDF, Open customer conversation.
- Bulk actions: Change status, Export CSV, Assign operator, Refund batch (Finance only).
- Order details modal/page:
  - Full order snapshot: items, options, price breakdown, receipts (payment raw payload), shipping/address, timeline (status history), file thumbnails with download links (signed URLs), audit log for this order, action log.

3) Files
- Purpose: inspect uploads, reprocess files, view processing status, and download originals.
- Grid columns: File ID, Owner (link), Filename, Pages, Size, Status, Storage key, Uploaded at, Actions.
- Actions: Preview (open in viewer), Requeue processing (thumbnail, OCR), Mark as ready, Delete (soft), Download (signed URL), Attach / detach to order.

4) Library (public resources)
- Manage categories and resources.
- Resource table: ID, Title, Category, Page count, Preview, IsPublic, Created at, Actions (Edit / Delete / Upload preview / Set price override).
- Editor: upload file, set thumbnail, set rights/license text, set page count and metadata, and optional per‑resource price overrides.

5) Prices
- Manage price tables and rules.
- UI: Versions list (published / draft) with ability to create a new price table version.
- Price editor: grouped view by paper_type -> size -> unit_price (cents) -> min_pages / max_pages -> enabled flag.
- Preview & publish flow: preview how price rules will apply to sample cart; publish creates new version and notifies cache invalidation endpoints.

6) Users
- User list: ID, display_name, email/phone, balance, last_seen, role, actions (impersonate, adjust balance, view orders, suspend).
- Impersonation: open a mini admin session (token) to reproduce user issues (audit logged).

7) Payments & Refunds
- Payments list: transactions, provider, provider_id, amount, status, order link, captured_at.
- Refund workflow: initiate refund (full/partial), track provider refund_id, and reconcile.

8) Customer Service
- Conversation list: search by user/order, unread count, last message preview, assign to agent, tags.
- Conversation view: threaded chat, operator quick replies, attach files (server uploads), view order context in a side panel.

9) Reports & Audits
- Reports: daily revenue, orders per status, top resources, storage usage.
- Audit logs: immutable chronological event logs (who changed what and when). Provide export & retention controls.

Table & data UX patterns
- Use server-side pagination and sortable columns. Prefer cursor pagination for large datasets.
- Show inline counts and summaries for filters (e.g., Pending: 12).
- Use badges for statuses with consistent colors and help tooltips describing each status.

APIs for manage panel (suggested)
- GET /admin/metrics
- GET /admin/orders?status=&assigned=&from=&to=&page=&page_size=
- GET /admin/orders/{id}
- PATCH /admin/orders/{id} {status, assigned_to, note}
- POST /admin/orders/{id}/refund {amount_cents, reason}
- GET /admin/files?status=&user_id=&page=
- POST /admin/files/{id}/reprocess
- GET /admin/library/categories
- POST /admin/library/resources
- PUT /admin/prices/versions
- POST /admin/users/{id}/adjust-balance {amount_cents, reason}
- GET /admin/audit-logs?entity_type=&entity_id=&page=

Security & operations
- Authentication: OIDC or JWT with short expiry and refresh tokens; require 2FA for admin users.
- Audit logging: all admin actions must be logged (user, action, request payload, before/after values, timestamp, IP).
- Rate limiting & CSRF protections for critical endpoints (refunds, balance adjustments).
- Secrets: store payment provider keys and storage credentials in a secrets manager.

Testing & QA
- Unit tests for UI components and hooks.
- Integration tests for critical flows: order lifecycle transitions, refund flow, file reprocess.
- E2E tests (Playwright) for operator flows: accept order → mark printed → complete.

Deployment & monitoring
- Deploy as a standalone static site behind Nginx or as a Dockerized Node app; use CI to build and deploy.
- Monitor: Sentry for frontend errors, Prometheus + Grafana for backend metrics surfaced via /metrics, uptime checks.

Bootstrap checklist (minimal)
1. Create admin repo scaffold (React + Vite + Ant Design + TypeScript).
2. Implement auth flow (login, 2FA), RBAC checks, and user impersonation token endpoint.
3. Implement Orders list + order details page with server API stubs.
4. Implement Files list + preview using signed download URLs.
5. Implement Prices editor and publish endpoint.
6. Add audit logging and simple dashboard metrics.

Notes
-----
- Keep UI responsive but optimized for desktop workflows.
- Server must enforce all permissions — UI should only reflect permissions and never be relied on for security.

File created: docs/design/manage_spec.md
