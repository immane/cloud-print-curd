from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.db import get_db
from src.app.dependencies.auth import require_admin
from src.app.models import PriceTable, User
from src.app.services.pricing import calculate_price

router = APIRouter(prefix="/admin/prices", tags=["admin-prices"])


class CreateVersionRequest(BaseModel):
    name: str
    rules_json: dict


class UpdateVersionRequest(BaseModel):
    rules_json: Optional[dict] = None
    name: Optional[str] = None


@router.get("/versions")
async def list_versions(
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin()),
):
    result = await db.execute(
        select(PriceTable).order_by(PriceTable.version.desc())
    )
    versions = result.scalars().all()

    return [
        {
            "id": v.id,
            "version": v.version,
            "name": v.name,
            "published": v.published,
            "created_at": v.created_at.isoformat() if v.created_at else None,
            "published_at": v.published_at.isoformat() if v.published_at else None,
        }
        for v in versions
    ]


@router.post("/versions")
async def create_version(
    body: CreateVersionRequest,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin()),
):
    max_version_result = await db.execute(
        select(func.max(PriceTable.version))
    )
    max_version = max_version_result.scalar() or 0
    new_version = max_version + 1

    price_table = PriceTable(
        version=new_version,
        name=body.name,
        published=False,
        rules=body.rules_json,
        created_by=admin_user.id,
    )
    db.add(price_table)
    await db.flush()
    await db.refresh(price_table)

    return {"version_id": price_table.id}


@router.put("/versions/{version_id}")
async def update_version(
    version_id: int,
    body: UpdateVersionRequest,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin()),
):
    result = await db.execute(
        select(PriceTable).where(PriceTable.id == version_id)
    )
    version = result.scalar_one_or_none()

    if version is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Price version not found",
        )

    if body.name is not None:
        version.name = body.name
    if body.rules_json is not None:
        version.rules = body.rules_json

    await db.flush()
    await db.refresh(version)

    return {
        "id": version.id,
        "version": version.version,
        "name": version.name,
        "published": version.published,
        "created_at": version.created_at.isoformat() if version.created_at else None,
        "published_at": version.published_at.isoformat() if version.published_at else None,
    }


@router.post("/versions/{version_id}/publish")
async def publish_version(
    version_id: int,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin()),
):
    result = await db.execute(
        select(PriceTable).where(PriceTable.id == version_id)
    )
    version = result.scalar_one_or_none()

    if version is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Price version not found",
        )

    await db.execute(
        update(PriceTable)
        .where(PriceTable.published == True)
        .values(published=False)
    )

    version.published = True
    version.published_at = datetime.now(timezone.utc)

    await db.flush()
    await db.refresh(version)

    return {
        "id": version.id,
        "version": version.version,
        "name": version.name,
        "published": version.published,
        "published_at": version.published_at.isoformat() if version.published_at else None,
    }


@router.post("/export-sample")
async def export_sample(
    payload: dict,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin()),
):
    result = await db.execute(
        select(PriceTable).where(PriceTable.published == True).order_by(PriceTable.version.desc())
    )
    version = result.scalars().first()
    rules = version.rules if version else {}
    calculation = calculate_price(payload.get("items", []), rules)
    return {
        "price_table_version": version.version if version else None,
        "input": payload,
        "calculation": calculation,
    }
