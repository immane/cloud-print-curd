import io

import pytest
from pypdf import PdfWriter
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.app.db import Base
from src.app.models import File
from src.app import worker as worker_module


class DummyS3:
    def __init__(self, data: bytes):
        self.data = data

    def get_object(self, Bucket, Key):
        return {"Body": io.BytesIO(self.data)}


@pytest.mark.asyncio
async def test_compute_page_count(monkeypatch):
    writer = PdfWriter()
    writer.add_blank_page(width=300, height=300)
    writer.add_blank_page(width=300, height=300)
    buf = io.BytesIO()
    writer.write(buf)

    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)

    async with factory() as db:
        await db.execute(
            insert(File).values(
                id=11,
                user_id=1,
                filename="a.pdf",
                storage_key="k",
                storage_provider="s3",
                content_type="application/pdf",
                status="ready",
            )
        )
        await db.commit()

    monkeypatch.setattr(worker_module, "get_s3_client", lambda: DummyS3(buf.getvalue()))
    monkeypatch.setattr(worker_module, "async_session_factory", factory)

    await worker_module._compute_page_count(11)

    async with factory() as db:
        file_obj = (await db.execute(select(File).where(File.id == 11))).scalar_one()
        assert file_obj.page_count == 2

    await engine.dispose()
