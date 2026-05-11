import pytest

from src.app.services.wechat import create_jsapi_order, exchange_code


@pytest.mark.asyncio
async def test_exchange_code_mock():
    data = await exchange_code("abc12345")
    assert data["openid"].startswith("mock_openid")


@pytest.mark.asyncio
async def test_create_jsapi_order_mock():
    result = await create_jsapi_order("openid", "order123", 1000, "desc")
    assert result["provider"] == "wechat"
    assert "params" in result
