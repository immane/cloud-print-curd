import pytest

@pytest.mark.asyncio
async def test_contract_basic_endpoints(client):
    assert (await client.get("/health")).status_code == 200
    assert (await client.get("/v1/prices")).status_code == 200
    assert (await client.get("/v1/prices/tip")).status_code == 200
    assert (await client.get("/v1/library/categories")).status_code == 200
