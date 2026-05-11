from __future__ import annotations

import io
from datetime import datetime, timedelta, timezone

import dramatiq
from dramatiq.brokers.redis import RedisBroker
from PIL import Image
from pypdf import PdfReader
from sqlalchemy import select

from src.app.config import settings
from src.app.db import async_session_factory
from src.app.models import File
from src.app.services.storage import delete_object, get_s3_client

broker = RedisBroker(url=settings.redis_url)
dramatiq.set_broker(broker)


@dramatiq.actor(max_retries=2)
def generate_thumbnail(file_id: int) -> None:
    import asyncio

    asyncio.run(_generate_thumbnail(file_id))


@dramatiq.actor(max_retries=2)
def compute_page_count(file_id: int) -> None:
    import asyncio

    asyncio.run(_compute_page_count(file_id))


@dramatiq.actor(max_retries=1)
def cleanup_old_files() -> None:
    import asyncio

    asyncio.run(_cleanup_old_files())


async def _generate_thumbnail(file_id: int) -> None:
    async with async_session_factory() as db:
        file_obj = (await db.execute(select(File).where(File.id == file_id))).scalar_one_or_none()
        if file_obj is None or file_obj.status == "deleted":
            return

        if not file_obj.content_type or not file_obj.content_type.startswith("image/"):
            return

        client = get_s3_client()
        obj = client.get_object(Bucket=settings.storage_bucket, Key=file_obj.storage_key)
        body = obj["Body"].read()

        image = Image.open(io.BytesIO(body))
        image.thumbnail((320, 320))
        output = io.BytesIO()
        image.convert("RGB").save(output, format="JPEG", quality=85)
        output.seek(0)

        thumb_key = f"thumbnails/{file_obj.id}.jpg"
        client.put_object(
            Bucket=settings.storage_bucket,
            Key=thumb_key,
            Body=output.getvalue(),
            ContentType="image/jpeg",
        )
        file_obj.preview_url = thumb_key
        await db.commit()


async def _compute_page_count(file_id: int) -> None:
    async with async_session_factory() as db:
        file_obj = (await db.execute(select(File).where(File.id == file_id))).scalar_one_or_none()
        if file_obj is None or file_obj.status == "deleted":
            return
        if file_obj.content_type != "application/pdf":
            return

        client = get_s3_client()
        obj = client.get_object(Bucket=settings.storage_bucket, Key=file_obj.storage_key)
        body = obj["Body"].read()
        reader = PdfReader(io.BytesIO(body))
        file_obj.page_count = len(reader.pages)
        await db.commit()


async def _cleanup_old_files() -> None:
    cutoff = datetime.now(timezone.utc) - timedelta(days=settings.file_retention_days)
    async with async_session_factory() as db:
        results = await db.execute(select(File).where(File.created_at < cutoff, File.status != "deleted"))
        old_files = results.scalars().all()
        for file_obj in old_files:
            try:
                delete_object(file_obj.storage_key)
            except Exception:
                pass
            file_obj.status = "deleted"
        await db.commit()
