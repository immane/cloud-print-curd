import pytest


@pytest.mark.asyncio
async def test_health_returns_json_content_type(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")
