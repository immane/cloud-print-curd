Title: Implement /health and /ready endpoints
Part: setup

Description: Add `/health` and `/ready` endpoints to the FastAPI app that return basic readiness and liveness JSON.

Inputs: backend scaffold

Outputs: src/app/routes/health.py registered in app

Acceptance criteria: GET /health returns 200 and GET /ready returns 200 when DB connection is not required.

Estimated effort: 30m

Tags: backend, api
