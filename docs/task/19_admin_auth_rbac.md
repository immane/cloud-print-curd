Title: Implement admin auth and RBAC middleware
Part: admin

Description: Add admin login route and RBAC enforcement layer to protect /admin/* endpoints.

Inputs: users table with role field

Outputs: /admin/auth/login, dependency middleware for admin routes

Acceptance criteria: Non-admins receive 403 when accessing admin endpoints; admin token works.

Estimated effort: 3h

Tags: backend, security
