Cloud Print — Backend

Project Overview
- Name: cloud-print-backend
- Description: A cloud printing service backend implemented with FastAPI. It includes file storage (S3/MinIO), a MySQL database, Redis for cache/task queue (Dramatiq), and other components.
- Language/Tools: Python >= 3.12, FastAPI, SQLAlchemy (async), Alembic, Dramatiq, Uvicorn

Repository Structure (important parts)
- src/backend/: backend source and build files
  - src/: Python package source (src.app)
  - Dockerfile, docker-compose.yml, pyproject.toml
  - .env.example

Quick Start (local development)
1. It's recommended to create a virtual environment and install dependencies:
   python -m venv .venv
   source .venv/bin/activate
   pip install -U pip
   pip install -e src

2. Copy the example environment file and edit it:
   cp src/backend/.env.example .env
   Edit .env (especially database, Redis, S3/MinIO credentials, and JWT secret)

3. Run database and dependent services (locally or via docker-compose):
   docker compose -f src/backend/docker-compose.yml up -d

4. Run the application (development):
   uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000

Container / Production Run
1. Build Docker image (run from src/backend):
   docker build -t cloud-print-backend src/backend

2. Start with docker-compose (includes mysql/redis/minio):
   docker compose -f src/backend/docker-compose.yml up --build

Environment Variables (key ones)
- Copy src/backend/.env.example and ensure the following are set in production:
  - DATABASE_URL / DATABASE_URL_SYNC
  - REDIS_URL
  - STORAGE_PROVIDER / STORAGE_ENDPOINT / STORAGE_ACCESS_KEY / STORAGE_SECRET_KEY
  - JWT_SECRET
  - SENTRY_DSN (optional)

Developer helper scripts
- src/backend/scripts/create_admin.py: create or update an admin account (see script help)

Database migrations
- Alembic is configured (alembic.ini and alembic/ directory present). Example:
  alembic upgrade head

Tests
- Install dev dependencies including pytest, then run tests. Example:
  pip install -e .[dev]
  pytest

Contributing and Code Style
- The project recommends using ruff and mypy for static checks (included in dev dependencies).
- Before committing, ensure no sensitive values (JWT secrets, DB passwords) are accidentally committed.

License
- Main repository license: MIT — see LICENSE.
- License notes and subproject inheritance: see LICENSES.md.

Contact
- For help or contributions, please open an issue in this repository.
