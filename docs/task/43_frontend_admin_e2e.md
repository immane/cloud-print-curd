Title: Admin Frontend E2E Tests (Playwright)
Part: testing

Description: Add Playwright end-to-end tests for the admin React app covering login, view orders list, open order detail, change status, and export. Tests should run against a staging backend (or local dev with docker-compose).

Inputs: admin UI build script, Playwright test harness

Outputs: tests/e2e/admin/ Playwright tests and CI step to run them

Acceptance criteria:
- Playwright test run succeeds against local dev environment.

Estimated effort: 8h

Tags: frontend, testing, e2e
