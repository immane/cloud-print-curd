import pytest
from sqlalchemy import insert

from src.app.models import File, Order, User
from src.app.services.auth import create_access_token


@pytest.mark.asyncio
async def test_webhook_updates_order(client, db_session):
    await db_session.execute(insert(User).values(id=1, display_name="u1", role="user"))
    await db_session.execute(
        insert(Order).values(
            id=10,
            user_id=1,
            out_trade_no="CPTEST123",
            total_cents=100,
            status="CREATED",
            currency="CNY",
        )
    )
    await db_session.commit()

    response = await client.post(
        "/v1/payments/webhook/test",
        json={"out_trade_no": "CPTEST123", "amount_cents": 100},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "processed"
