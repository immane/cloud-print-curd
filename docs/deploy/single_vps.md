# Single VPS Deployment Guide

## Prerequisites
- Ubuntu 22.04 VPS
- Docker and Docker Compose plugin installed
- Domain with DNS pointed to VPS

## Steps
1. Clone repository to `/opt/cloud-print`.
2. Copy `src/backend/.env.example` to `src/backend/.env` and fill production values.
3. Build and start services:
   - `docker compose -f src/backend/docker-compose.yml up -d --build`
4. Run migrations:
   - `docker compose -f src/backend/docker-compose.yml exec web alembic upgrade head`
5. Verify health:
   - `curl http://127.0.0.1:8000/health`
6. Put Nginx in front of backend/admin static site and enable TLS with certbot.

## Operations
- Restart: `docker compose -f src/backend/docker-compose.yml restart`
- Logs: `docker compose -f src/backend/docker-compose.yml logs -f web worker`
- Backups: daily `mysqldump` + object storage lifecycle rules
