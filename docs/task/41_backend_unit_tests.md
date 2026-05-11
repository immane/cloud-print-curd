Title: Backend Unit Tests (pytest)
Part: testing

Description: Add a comprehensive suite of unit tests for the backend using pytest. Focus areas: business logic, price calculation, model methods, auth helpers, storage token generation, and small utilities. Use mocks for external services (S3/Qiniu, WeChat API, payments).

Inputs: backend codebase, pytest, testing requirements in dev dependencies

Outputs: tests/ directory with pytest test modules, tox/pytest.ini or pyproject config, sample mocks for S3 and WeChat.

Acceptance criteria:
- Running `pytest -q` executes unit tests and exits 0 for the codebase.
- Core modules covered: price calculation (>=90% deterministic tests), auth token helpers, upload token generation, small utility functions.
- Tests mock external dependencies and do not require actual network calls.

Estimated effort: 8h

Tags: backend, testing, unit
