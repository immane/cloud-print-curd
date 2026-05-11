import pytest
from sqlalchemy import insert

from src.app.models import User
from src.app.services.auth import create_access_token


@pytest.mark.asyncio
async def test_health(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_users_me(client, db_session):
    await db_session.execute(
        insert(User).values(
            id=1,
            email="test@example.com",
            display_name="tester",
            role="user",
        )
    )
    await db_session.commit()

    token = create_access_token(1, "user")
    response = await client.get("/v1/users/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["id"] == 1
