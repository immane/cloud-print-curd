# cloud-print-backend

Backend service for the Cloud Print platform.

## Stack

- Python 3.12+
- FastAPI + Uvicorn
- SQLAlchemy (async) + Alembic
- Redis + Dramatiq worker
- MySQL (default) / SQLite (tests)

## Project Layout

- `src/app/`: application code (routes, services, middleware, worker)
- `alembic/`: migration scripts
- `tests/`: unit / integration / contract / perf tests
- `tools/`: maintenance and replay tools
- `scripts/create_admin.py`: bootstrap admin account

## Local Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .[dev]
cp .env.example .env
```

Run API:

```bash
uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000
```

## Docker Compose

This project ships a compose setup for MySQL, Redis, MinIO, API and worker:

```bash
docker compose up --build
```

## Database Migration

```bash
alembic upgrade head
```

## Tests

Run all backend tests:

```bash
pytest
```

Examples:

```bash
pytest tests/unit
pytest tests/integration
pytest tests/contract
```

## Notes

- Copy `.env.example` and update secrets before production.
- Do not commit `.env` or local database credentials.
