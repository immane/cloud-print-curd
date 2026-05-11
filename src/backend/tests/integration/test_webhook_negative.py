import pytest


@pytest.mark.asyncio
async def test_webhook_missing_trade_no(client):
    response = await client.post("/v1/payments/webhook/test", json={"amount_cents": 100})
    assert response.status_code == 422 or response.status_code == 400
