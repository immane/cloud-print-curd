from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.db import get_db
from src.app.dependencies.auth import require_admin
from src.app.models import LibraryCategory, LibraryResource, User

router = APIRouter(prefix="/admin/library", tags=["admin-library"])


class CreateCategoryRequest(BaseModel):
    name: str
    slug: str
    order: int = 0


class CreateResourceRequest(BaseModel):
    title: str
    category_id: Optional[int] = None
    file_id: Optional[int] = None
    page_count: Optional[int] = None
    price_override_cents: Optional[int] = None


class UpdateResourceRequest(BaseModel):
    title: Optional[str] = None
    category_id: Optional[int] = None
    file_id: Optional[int] = None
    page_count: Optional[int] = None
    price_override_cents: Optional[int] = None
    is_public: Optional[bool] = None


@router.get("/categories")
async def list_categories(
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin()),
):
    result = await db.execute(
        select(LibraryCategory).order_by(LibraryCategory.order)
    )
    categories = result.scalars().all()

    return [
        {
            "id": c.id,
            "name": c.name,
            "slug": c.slug,
            "order": c.order,
            "created_at": c.created_at.isoformat() if c.created_at else None,
            "updated_at": c.updated_at.isoformat() if c.updated_at else None,
        }
        for c in categories
    ]


@router.post("/categories")
async def create_category(
    body: CreateCategoryRequest,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin()),
):
    existing = await db.execute(
        select(LibraryCategory).where(LibraryCategory.slug == body.slug)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Category slug already exists",
        )

    category = LibraryCategory(
        name=body.name,
        slug=body.slug,
        order=body.order,
    )
    db.add(category)
    await db.flush()
    await db.refresh(category)

    return {
        "id": category.id,
        "name": category.name,
        "slug": category.slug,
        "order": category.order,
        "created_at": category.created_at.isoformat() if category.created_at else None,
        "updated_at": category.updated_at.isoformat() if category.updated_at else None,
    }


@router.post("/resources")
async def create_resource(
    body: CreateResourceRequest,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin()),
):
    resource = LibraryResource(
        title=body.title,
        category_id=body.category_id,
        file_id=body.file_id,
        page_count=body.page_count,
        price_override_cents=body.price_override_cents,
    )
    db.add(resource)
    await db.flush()
    await db.refresh(resource)

    return {
        "id": resource.id,
        "title": resource.title,
        "category_id": resource.category_id,
        "file_id": resource.file_id,
        "page_count": resource.page_count,
        "price_override_cents": resource.price_override_cents,
        "is_public": resource.is_public,
        "created_at": resource.created_at.isoformat() if resource.created_at else None,
        "updated_at": resource.updated_at.isoformat() if resource.updated_at else None,
    }


@router.put("/resources/{resource_id}")
async def update_resource(
    resource_id: int,
    body: UpdateResourceRequest,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin()),
):
    result = await db.execute(
        select(LibraryResource).where(LibraryResource.id == resource_id)
    )
    resource = result.scalar_one_or_none()

    if resource is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Library resource not found",
        )

    if body.title is not None:
        resource.title = body.title
    if body.category_id is not None:
        resource.category_id = body.category_id
    if body.file_id is not None:
        resource.file_id = body.file_id
    if body.page_count is not None:
        resource.page_count = body.page_count
    if body.price_override_cents is not None:
        resource.price_override_cents = body.price_override_cents
    if body.is_public is not None:
        resource.is_public = body.is_public

    await db.flush()
    await db.refresh(resource)

    return {
        "id": resource.id,
        "title": resource.title,
        "category_id": resource.category_id,
        "file_id": resource.file_id,
        "page_count": resource.page_count,
        "price_override_cents": resource.price_override_cents,
        "is_public": resource.is_public,
        "created_at": resource.created_at.isoformat() if resource.created_at else None,
        "updated_at": resource.updated_at.isoformat() if resource.updated_at else None,
    }
