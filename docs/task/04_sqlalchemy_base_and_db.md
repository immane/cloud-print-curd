Title: Implement SQLAlchemy base and DB connection util
Part: setup

Description: Add SQLAlchemy async engine setup with configuration from environment variables and a session dependency for FastAPI.

Inputs: connection string in .env.example

Outputs: src/app/db.py, DB session dependency, simple test script

Acceptance criteria: Running a small script can create and drop a test table using async engine.

Estimated effort: 2h

Tags: backend, db
