Title: Add CI pipeline jobs (GitHub Actions): lint, tests, build
Part: ci

Description: Create GitHub Actions workflow to run linter, unit tests, and build steps for backend and admin frontend.

Inputs: repo with tests and build scripts

Outputs: .github/workflows/ci.yml

Acceptance criteria: Push triggers workflow that runs lint and tests; failing tests cause failure.

Estimated effort: 4h

Tags: ci, devops
