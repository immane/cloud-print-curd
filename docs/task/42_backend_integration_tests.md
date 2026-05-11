Title: Backend Integration Tests
Part: testing

Description: Add integration tests that use a test database and a local S3-compatible server (MinIO or LocalStack) to exercise the upload flow, file complete flow, order creation, and webhook processing. Use pytest fixtures to spin up containers or use docker-compose test configuration.

Inputs: docker-compose.yml with test services or GitHub Actions job using services, pytest

Outputs: tests/integration/ pytest modules, fixtures for DB and storage, sample webhook payloads for payment provider

Acceptance criteria:
- Integration tests can run locally (with docker compose) and in CI, exercising end-to-end upload->complete->order->webhook flows.

Estimated effort: 12h

Tags: backend, testing, integration
