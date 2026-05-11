Title: Create backend repo scaffold
Part: setup

Description: Initialize a Python FastAPI project skeleton with project layout, basic dependencies, and a README.

Inputs: none

Outputs: repo files: pyproject.toml or requirements.txt, src/app/main.py (FastAPI app), README.md, .gitignore

Acceptance criteria: `uvicorn src.app.main:app --reload` starts and serves `/health` returning 200 JSON {"status": "ok"}.

Estimated effort: 1h

Tags: backend, infra, setup
