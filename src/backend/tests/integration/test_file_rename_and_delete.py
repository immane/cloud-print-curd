import pytest
from sqlalchemy import insert

from src.app.models import File, User
from src.app.services.auth import create_access_token


@pytest.mark.asyncio
async def test_file_rename_and_delete_flow(client, db_session):
    await db_session.execute(insert(User).values(id=1, display_name="u1", role="user"))
    await db_session.execute(
        insert(File).values(
            id=5,
            user_id=1,
            filename="old.pdf",
            storage_key="k",
            storage_provider="s3",
            status="ready",
        )
    )
    await db_session.commit()

    token = create_access_token(1, "user")

    rename = await client.patch(
        "/v1/files/5",
        headers={"Authorization": f"Bearer {token}"},
        json={"filename": "new.pdf"},
    )
    assert rename.status_code == 200
    assert rename.json()["filename"] == "new.pdf"

    delete = await client.delete("/v1/files/5", headers={"Authorization": f"Bearer {token}"})
    assert delete.status_code == 200
    assert delete.json()["status"] == "deleted"
