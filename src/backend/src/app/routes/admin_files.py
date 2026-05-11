from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.db import get_db
from src.app.dependencies.auth import require_admin
from src.app.models import File, User
from src.app.services.storage import create_presigned_download_url
from src.app.worker import compute_page_count, generate_thumbnail

router = APIRouter(prefix="/admin/files", tags=["admin-files"])


@router.get("")
async def list_files(
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin()),
    status_filter: Optional[str] = Query(None, alias="status"),
    user_id: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    conditions = []

    if status_filter:
        conditions.append(File.status == status_filter)
    if user_id is not None:
        conditions.append(File.user_id == user_id)

    base_query = select(File)
    if conditions:
        from sqlalchemy import and_ as _and
        base_query = base_query.where(_and(*conditions))

    count_query = select(func.count()).select_from(base_query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    items_query = (
        base_query
        .order_by(File.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(items_query)
    files = result.scalars().all()

    items = [
        {
            "id": f.id,
            "user_id": f.user_id,
            "filename": f.filename,
            "storage_provider": f.storage_provider,
            "content_type": f.content_type,
            "size_bytes": f.size_bytes,
            "page_count": f.page_count,
            "checksum": f.checksum,
            "status": f.status,
            "preview_url": f.preview_url,
            "metadata": f.metadata_json,
            "created_at": f.created_at.isoformat() if f.created_at else None,
            "updated_at": f.updated_at.isoformat() if f.updated_at else None,
        }
        for f in files
    ]

    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.post("/{file_id}/reprocess")
async def reprocess_file(
    file_id: int,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin()),
):
    result = await db.execute(select(File).where(File.id == file_id))
    file = result.scalar_one_or_none()

    if file is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    generate_thumbnail.send(file.id)
    compute_page_count.send(file.id)

    return {"message": "Reprocess queued"}


@router.get("/{file_id}/download")
async def download_file(
    file_id: int,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin()),
):
    result = await db.execute(select(File).where(File.id == file_id))
    file = result.scalar_one_or_none()

    if file is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    url = create_presigned_download_url(file.storage_key)
    return {
        "url": url,
        "filename": file.filename,
        "content_type": file.content_type,
    }
