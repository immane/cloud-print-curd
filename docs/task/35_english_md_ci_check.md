Title: Implement English-only .md CI check
Part: ci

Description: Add a GitHub Action step or script that scans .md files and fails if non-English text is detected (use simple heuristics or `franc` library).

Inputs: list of .md files in repo

Outputs: script tool and CI step

Acceptance criteria: PR with a non-English .md file causes CI to fail.

Estimated effort: 2h

Tags: ci, docs
