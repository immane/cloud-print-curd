import pytest


@pytest.mark.asyncio
async def test_users_me_without_token(client):
    response = await client.get("/v1/users/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_with_invalid_token(client):
    response = await client.post("/v1/auth/refresh", json={"refresh_token": "invalid"})
    assert response.status_code == 401
