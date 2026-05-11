Title: Implement JWT auth dependency and /v1/users/me
Part: auth

Description: Add JWT token verification dependency and implement user info endpoint returning DB-backed user data.

Inputs: users table (Task 6), JWT secret

Outputs: auth dependency, GET /v1/users/me

Acceptance criteria: Requests with Authorization header return the correct user JSON.

Estimated effort: 2h

Tags: auth, backend
