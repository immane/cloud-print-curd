Title: Implement WeChat code exchange endpoint (auth/wechat/login)
Part: auth

Description: Implement POST /v1/auth/wechat/login that accepts {code} and returns a JWT (mocking the actual WeChat call if no credentials provided).

Inputs: backend scaffold, JWT secret env var

Outputs: src/app/routes/auth_wechat.py, token generation util

Acceptance criteria: POST with any code returns a valid JWT and GET /v1/users/me with that token returns a user object stub.

Estimated effort: 3h

Tags: auth, backend
