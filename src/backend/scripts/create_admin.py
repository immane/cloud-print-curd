#!/usr/bin/env python3
"""Create or update an admin user in the database.

Usage:
  python scripts/create_admin.py --email admin@example.com --password admin

This script uses the project's async_session_factory and ORM models.
"""
import argparse
import asyncio
from sqlalchemy import select

from src.app.services.auth import get_password_hash
from src.app.db import async_session_factory
from src.app.models import User


async def main(email: str, password: str):
    async with async_session_factory() as db:
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        hashed = get_password_hash(password)
        if user is None:
            user = User(
                email=email,
                password_hash=hashed,
                display_name="Admin",
                role="admin",
            )
            db.add(user)
            await db.flush()
            print(f"Created admin user id={user.id} email={email}")
        else:
            user.password_hash = hashed
            user.role = "admin"
            await db.flush()
            print(f"Updated existing user id={user.id} email={email} to role=admin")
        await db.commit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--email", default="admin@example.com", help="admin email")
    parser.add_argument("--password", default="admin", help="admin password (plaintext)")
    args = parser.parse_args()
    asyncio.run(main(args.email, args.password))
