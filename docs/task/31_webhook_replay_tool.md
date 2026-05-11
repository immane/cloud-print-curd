Title: Add webhook testing harness and replay tool
Part: testing

Description: Create an endpoint and small script to replay recorded webhook payloads for testing signature verification and processing.

Inputs: recorded webhook samples

Outputs: script in tools/replay_webhook.py and a local route to accept replays

Acceptance criteria: Able to replay sample webhook and observe order status change in DB when signature verification passes (or in mocked mode).

Estimated effort: 3h

Tags: backend, testing
