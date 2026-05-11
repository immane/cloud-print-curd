Title: Add User model and migration
Part: db

Description: Implement users table model in SQLAlchemy and create Alembic migration to add the table (per entities.md).

Inputs: docs/design/entities.md, Alembic config

Outputs: model file src/app/models/user.py, alembic migration adding users table

Acceptance criteria: Table `users` exists in MySQL after `alembic upgrade head` and basic insert/select works.

Estimated effort: 2h

Tags: db, models
