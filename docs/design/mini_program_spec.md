Title: Mini‑Program Business Specification
Path: docs/design/mini_program_spec.md

Overview
--------
This document defines the WeChat Mini‑Program business logic and UI layout for the upload‑and‑pay printing app. It is written in English and intended as a single‑source spec for frontend and backend work. The app has three bottom tabs: Home, Library, and Me.

Navigation and high level
-------------------------
- Bottom tab bar (persistent): Home | Library | Me
- Persistent floating customer‑service button on the bottom right that opens WeChat customer service (wx.openCustomerServiceConversation) or the chosen IM SDK conversation.

Tab 1 — Home
------------
Layout (top→down):
1. Header: app title/logo and top right icons (search, notifications optional).
2. Slider / Carousel: images loaded from backend (GET /v1/home/slider). Each slide: {image_url, link_type, link_payload}.
3. Shortcut row: two large tiles/buttons — "Printing Tutorial" and "Price List".
   - Printing Tutorial: opens a single image fetched from backend (GET /v1/home/tutorial) and shows full‑screen preview.
   - Price List: opens price list view. The price list view top area shows a friendly tip text fetched from backend (GET /v1/prices/tip), then displays prices grouped by paper type and size.
4. Optional promotional banners or quick actions below.

Behavior & API
- Slider: GET /v1/home/slider → [{id,image_url,link_type,link_payload}]
- Tutorial: GET /v1/home/tutorial → {image_url, title, updated_at}
- Price tip: GET /v1/prices/tip → {text}
- Price list: GET /v1/prices?paper_type={}&size={} or GET /v1/prices to fetch all. Response shape: [{paper_type, size, unit_price_cents, description, currency}]. (You will supply the exact list in a later MD.)

UI notes
- Price list must support grouping and quick search/filter by paper type or size.
- Sticky footer on price list with a small legend for units (per sheet / per copy) and a contact / order button.

Tab 2 — Library (Public Resources)
----------------------------------
Layout (top→down):
1. Tag/category bar (horizontal scroll) — categories fetched from backend (GET /v1/library/categories).
2. Resource grid/list for the selected tag — each entry shows thumbnail, title, page count, and an "Order" button.

Behavior & API
- GET /v1/library/categories → [{id, name, order}]
- GET /v1/library/resources?category_id={id}&page={}&page_size={} → [{id, title, thumbnail_url, page_count, file_key, preview_url}]
- POST /v1/orders/create-from-resource {resource_id, options} → creates an order prepared for payment (returns order_id and payment params).

UI notes
- Resource items: show page count; disable Order button if resource not allowed (e.g., protected).
- Clicking a resource opens a preview modal (if preview_url provided) with a prominent "Order" CTA.

Tab 3 — Me (User Area)
----------------------
Layout (top→down):
1. Profile header: avatar, display name, and account balance.
2. Orders quick panel: icons and counts for statuses: Pending Payment, Pending Print, To Receive, Completed, After‑sales. Tap opens full orders list filtered by status.
3. Files list: user uploaded or prepared files (thumbnail, filename, pages, size, status), with actions (Edit options, Create Order, Delete).
4. Price List (link to same price list as Home).
5. Address Management (link to address list CRUD).
6. FAQ / Common Questions (link to help content pages served from backend).
7. Logout button.

Behavior & API
- GET /v1/users/me → {id, display_name, avatar_url, balance_cents, roles}
- GET /v1/orders?user_id={me}&status={}&page={} → list of orders
- GET /v1/files?user_id={me}&page={} → list of files uploaded by user
- POST /v1/files/create-upload → returns upload intent: {upload_id, upload_url, fields} (for presigned POST) or {upload_id, presigned_put_url}
- POST /v1/files/complete {upload_id, metadata} → confirm upload, create file record
- POST /v1/orders/create {items, user_id, address_id, options} → create order and return payment params
- POST /v1/auth/logout

Files and upload flow
---------------------
Recommended flow (presigned POST to S3 / Qiniu):
1. Client requests upload intent: POST /v1/files/create-upload (body: filename, size, content_type). Backend validates and returns upload token/fields and a temporary storage key.
2. Client uploads directly to storage using wx.uploadFile with returned form fields.
3. Client calls POST /v1/files/complete with upload_id and optional checksum. Backend validates object and finalizes file record.

UI behavior for files list
- Each file entry shows thumbnail, filename, page_count (if available), size, upload date, and a status badge: Uploaded / Processing / Ready / Deleted.
- Available actions: Preview, Create Order, Delete (soft delete), Rename.

Ordering & payment flow
-----------------------
Flow summary:
1. User selects files and print options (paper type, size, color, copies).
2. Client calculates preview price locally if price table present; final price must be validated server‑side.
3. Client calls POST /v1/orders/create with selected items and options.
4. Backend creates order, reserves stock/quota if needed, and returns payment params for WeChat Mini‑Program (v3 prepay params).
5. Client calls wx.requestPayment with returned params.
6. Backend handles async notify from WeChat and updates order status.

Order statuses
- CREATED: order created, awaiting payment
- PENDING_PAYMENT: awaiting user's payment (same as CREATED)
- PAID: payment received
- PROCESSING: job sent to print queue
- PRINTED / SHIPPED: printed and shipped/ready for pickup
- COMPLETED: delivered/collected and closed
- REFUNDED: refunded
- CANCELLED: cancelled by user or admin

Customer service
----------------
- Floating button opens WeChat customer service: call wx.openCustomerServiceConversation({sessionFrom: JSON.stringify({type:'order',id:order_id})}) or route to chosen IM SDK.
- Backend endpoint to provide prefilled session text or message card data: GET /v1/support/session-info?order_id={}

Design & interaction notes
--------------------------
- Sticky CTA: pages where payment/action is primary should show a sticky footer with summary and primary CTA (e.g., "Pay Now", "Create Order").
- Inline validation: show file size/type validation immediately upon selection.
- Progressive disclosure: keep print options compact; expand advanced options in a secondary panel.
- Error handling: show toast messages for transient errors and modal confirmations for destructive actions (delete/cancel).

Security & privacy notes
------------------------
- All API calls must use TLS.
- Sensitive credentials (storage keys, WeChat merchant keys) must remain server‑side.
- Upload tokens should be short lived and scope limited.
- Orders and files should be access controlled; users can access only their files unless resource is public.

Extensibility
-------------
- Price rule changes: backend should provide versioned price tables; clients cache with TTL and validate final price at checkout.
- Support for library resources: resource entries include optional license/rights and preview thumbnails.

Next steps / placeholders
-------------------------
- The exact price table schema and entries will be provided in a follow‑up MD; current API shapes assume unit_price_cents and grouping by paper_type and size.
- Implement backend endpoints for upload intent, file complete, orders create, and WeChat payment integration (v3) per research docs.

File created: docs/design/mini_program_spec.md
