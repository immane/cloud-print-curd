Title: Create Alembic configuration and initial migration
Part: setup

Description: Configure Alembic to use SQLAlchemy models and generate an initial empty migration.

Inputs: SQLAlchemy base (Task 4)

Outputs: alembic.ini, alembic/ env.py, versions/ initial migration file

Acceptance criteria: `alembic upgrade head` runs without error against local dev MySQL container.

Estimated effort: 2h

Tags: db, migrations
