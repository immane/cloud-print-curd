Title: Implement core admin APIs: /admin/orders list/detail and PATCH
Part: admin

Description: Implement admin endpoints to list, view, and change order status, recording audit logs.

Inputs: orders table, admin_audit_logs table

Outputs: admin routes, audit log insertion

Acceptance criteria: Admin can change status and an audit log entry is created with before/after values.

Estimated effort: 4h

Tags: backend, admin
