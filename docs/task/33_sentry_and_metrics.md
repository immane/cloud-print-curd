Title: Implement Sentry integration and /metrics endpoint
Part: monitoring

Description: Add Sentry SDK initialization and a Prometheus-compatible /metrics endpoint exposing basic app metrics.

Inputs: SENTRY_DSN env var (optional)

Outputs: Sentry init in app, /metrics route

Acceptance criteria: Errors are reported to Sentry (if configured); /metrics returns Prometheus metrics.

Estimated effort: 3h

Tags: monitoring, ops
