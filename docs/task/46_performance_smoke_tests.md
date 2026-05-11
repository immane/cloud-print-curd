Title: Performance Smoke Tests
Part: testing

Description: Add a small suite of performance smoke tests (Locust or k6) to exercise upload presign endpoints and order creation to measure baseline throughput on the deployment target.

Inputs: test scenarios, locust or k6 scripts

Outputs: tests/perf/ scripts and a CI job to run quick smoke tests

Acceptance criteria:
- Smoke tests run and produce basic metrics (RPS, latencies) and do not crash the test environment.

Estimated effort: 6h

Tags: testing, perf
