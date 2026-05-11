Title: Add Dockerfile and docker-compose for local dev
Part: setup

Description: Add Dockerfile for the FastAPI app and a docker-compose.yml that includes mysql, redis, minio (or localstack) and the web service.

Inputs: backend scaffold from Task 1

Outputs: Dockerfile, docker-compose.yml, .env.example

Acceptance criteria: `docker compose up --build` starts all services and web responds on exposed port.

Estimated effort: 2h

Tags: infra, docker, dev
