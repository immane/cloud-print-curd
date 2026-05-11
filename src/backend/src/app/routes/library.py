from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.db import get_db
from src.app.models import LibraryCategory, LibraryResource

router = APIRouter(prefix="/v1/library", tags=["library"])


@router.get("/categories")
async def list_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(LibraryCategory).order_by(LibraryCategory.order.asc(), LibraryCategory.id.asc()))
    categories = result.scalars().all()
    return [
        {"id": c.id, "name": c.name, "slug": c.slug, "order": c.order}
        for c in categories
    ]


@router.get("/resources")
async def list_resources(
    category_id: int | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    base = select(LibraryResource).where(LibraryResource.is_public.is_(True))
    if category_id is not None:
        base = base.where(LibraryResource.category_id == category_id)

    total = (await db.execute(select(func.count()).select_from(base.subquery()))).scalar() or 0
    items = (
        await db.execute(
            base.order_by(LibraryResource.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
    ).scalars().all()

    return {
        "items": [
            {
                "id": r.id,
                "title": r.title,
                "category_id": r.category_id,
                "file_id": r.file_id,
                "page_count": r.page_count,
                "price_override_cents": r.price_override_cents,
                "is_public": r.is_public,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in items
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/resources/{resource_id}")
async def get_resource(resource_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(LibraryResource).where(LibraryResource.id == resource_id))
    resource = result.scalar_one_or_none()
    if resource is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found")

    return {
        "id": resource.id,
        "title": resource.title,
        "category_id": resource.category_id,
        "file_id": resource.file_id,
        "page_count": resource.page_count,
        "price_override_cents": resource.price_override_cents,
        "is_public": resource.is_public,
        "rights_info": resource.rights_info,
        "created_at": resource.created_at.isoformat() if resource.created_at else None,
        "updated_at": resource.updated_at.isoformat() if resource.updated_at else None,
    }
