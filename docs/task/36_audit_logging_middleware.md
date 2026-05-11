Title: Implement admin audit logging middleware
Part: security

Description: Add middleware or decorator to record admin actions into admin_audit_logs table.

Inputs: admin endpoints

Outputs: middleware code and DB migration (admin_audit_logs table)

Acceptance criteria: Admin actions (e.g., PATCH /admin/orders/{id}) create audit entries with before/after snapshots.

Estimated effort: 3h

Tags: backend, security
