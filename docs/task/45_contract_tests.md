Title: API Contract Tests (OpenAPI based)
Part: testing

Description: Generate OpenAPI schema from docs/design/api_spec.md and add contract tests that validate backend responses against the schema (using schemathesis or openapi-core).

Inputs: OpenAPI schema, schemathesis or similar tool

Outputs: tests/contract/ tests and CI step

Acceptance criteria:
- Contract tests validate that key endpoints conform to the OpenAPI schema and fail on schema mismatches.

Estimated effort: 6h

Tags: backend, testing, contract
