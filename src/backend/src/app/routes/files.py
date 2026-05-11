import asyncio
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.config import settings
from src.app.db import get_db
from src.app.dependencies.auth import ADMIN_ROLES, get_current_user
from src.app.models import File, Upload
from src.app.models.user import User
from src.app.services.storage import (
    create_presigned_download_url,
    create_presigned_post,
    get_object_info,
    verify_object,
)
from src.app.worker import compute_page_count, generate_thumbnail

router = APIRouter(prefix="/v1/files", tags=["files"])

ALLOWED_CONTENT_TYPES = [
    ct.strip() for ct in settings.allowed_content_types.split(",") if ct.strip()
]
MAX_SIZE_BYTES = settings.max_upload_size_mb * 1024 * 1024


class CreateUploadRequest(BaseModel):
    filename: str
    size: int
    content_type: str


class CompleteUploadRequest(BaseModel):
    upload_id: str
    checksum: Optional[str] = None


class RenameFileRequest(BaseModel):
    filename: str


@router.post("/create-upload")
async def create_upload(
    body: CreateUploadRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if body.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Content type '{body.content_type}' is not allowed",
        )

    if body.size <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size must be greater than 0",
        )

    if body.size > MAX_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds maximum allowed size of {settings.max_upload_size_mb}MB",
        )

    upload_id = uuid.uuid4().hex
    storage_key = f"uploads/{current_user.id}/{upload_id}/{body.filename}"

    presigned = await asyncio.to_thread(
        create_presigned_post, storage_key, body.content_type, body.size
    )

    upload = Upload(
        user_id=current_user.id,
        upload_id=upload_id,
        storage_key=storage_key,
        expected_size=body.size,
        expected_content_type=body.content_type,
        status="pending",
        fields=presigned["fields"],
    )
    db.add(upload)
    await db.flush()

    return {
        "upload_id": upload_id,
        "storage_provider": settings.storage_provider,
        "upload_url": presigned["url"],
        "fields": presigned["fields"],
    }


@router.post("/complete")
async def complete_upload(
    body: CompleteUploadRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Upload).where(
            Upload.upload_id == body.upload_id,
            Upload.user_id == current_user.id,
        )
    )
    upload = result.scalar_one_or_none()
    if upload is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Upload not found",
        )

    if upload.status == "verified":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Upload has already been completed",
        )

    if not upload.storage_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Upload has no storage key",
        )

    exists = await asyncio.to_thread(verify_object, upload.storage_key)
    if not exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Object not found in storage",
        )

    info = await asyncio.to_thread(get_object_info, upload.storage_key)
    filename = upload.storage_key.rsplit("/", 1)[-1] if "/" in upload.storage_key else upload.storage_key

    file_record = File(
        user_id=current_user.id,
        filename=filename,
        storage_key=upload.storage_key,
        storage_provider=settings.storage_provider,
        content_type=info.get("content_type") or upload.expected_content_type,
        size_bytes=info.get("size") or upload.expected_size,
        checksum=body.checksum,
        status="ready",
    )
    db.add(file_record)

    upload.status = "verified"

    await db.flush()
    await db.refresh(file_record)

    generate_thumbnail.send(file_record.id)
    compute_page_count.send(file_record.id)

    return {
        "id": file_record.id,
        "user_id": file_record.user_id,
        "filename": file_record.filename,
        "storage_key": file_record.storage_key,
        "storage_provider": file_record.storage_provider,
        "content_type": file_record.content_type,
        "size_bytes": file_record.size_bytes,
        "page_count": file_record.page_count,
        "checksum": file_record.checksum,
        "status": file_record.status,
        "created_at": file_record.created_at.isoformat() if file_record.created_at else None,
        "updated_at": file_record.updated_at.isoformat() if file_record.updated_at else None,
    }


@router.get("")
async def list_files(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    conditions = [
        File.user_id == current_user.id,
        File.status != "deleted",
    ]
    if status_filter:
        conditions.append(File.status == status_filter)

    base_query = select(File).where(*conditions)

    count_query = select(func.count()).select_from(base_query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    offset = (page - 1) * page_size
    items_query = (
        base_query
        .order_by(File.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    items_result = await db.execute(items_query)
    items = items_result.scalars().all()

    return {
        "items": [
            {
                "id": f.id,
                "filename": f.filename,
                "content_type": f.content_type,
                "size_bytes": f.size_bytes,
                "page_count": f.page_count,
                "checksum": f.checksum,
                "status": f.status,
                "preview_url": f.preview_url,
                "created_at": f.created_at.isoformat() if f.created_at else None,
                "updated_at": f.updated_at.isoformat() if f.updated_at else None,
            }
            for f in items
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/{file_id}")
async def get_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(File).where(File.id == file_id))
    file_record = result.scalar_one_or_none()

    if file_record is None or file_record.status == "deleted":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found",
        )

    if file_record.user_id != current_user.id and current_user.role not in ADMIN_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    return {
        "id": file_record.id,
        "user_id": file_record.user_id,
        "filename": file_record.filename,
        "storage_key": file_record.storage_key,
        "storage_provider": file_record.storage_provider,
        "content_type": file_record.content_type,
        "size_bytes": file_record.size_bytes,
        "page_count": file_record.page_count,
        "checksum": file_record.checksum,
        "status": file_record.status,
        "preview_url": file_record.preview_url,
        "created_at": file_record.created_at.isoformat() if file_record.created_at else None,
        "updated_at": file_record.updated_at.isoformat() if file_record.updated_at else None,
    }


@router.get("/{file_id}/download")
async def download_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(File).where(File.id == file_id))
    file_record = result.scalar_one_or_none()

    if file_record is None or file_record.status == "deleted":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found",
        )

    if file_record.user_id != current_user.id and current_user.role not in ADMIN_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    url = await asyncio.to_thread(create_presigned_download_url, file_record.storage_key)
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=3600)

    return {
        "url": url,
        "expires_at": expires_at.isoformat(),
    }


@router.delete("/{file_id}")
async def delete_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(File).where(File.id == file_id))
    file_record = result.scalar_one_or_none()

    if file_record is None or file_record.status == "deleted":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found",
        )

    if file_record.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    file_record.status = "deleted"
    await db.flush()

    return {"status": "deleted"}


@router.patch("/{file_id}")
async def rename_file(
    file_id: int,
    body: RenameFileRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(File).where(File.id == file_id))
    file_record = result.scalar_one_or_none()

    if file_record is None or file_record.status == "deleted":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found",
        )

    if file_record.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    name = body.filename.strip()
    if not name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename cannot be empty",
        )

    file_record.filename = name
    await db.flush()

    return {
        "id": file_record.id,
        "filename": file_record.filename,
        "status": file_record.status,
    }
