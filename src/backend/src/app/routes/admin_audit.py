from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.db import get_db
from src.app.dependencies.auth import require_admin
from src.app.models import AdminAuditLog, User

router = APIRouter(prefix="/admin/audit-logs", tags=["admin-audit"])


@router.get("")
async def list_audit_logs(
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin()),
    entity_type: Optional[str] = Query(None),
    entity_id: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
):
    conditions = []

    if entity_type:
        conditions.append(AdminAuditLog.target_type == entity_type)
    if entity_id:
        conditions.append(AdminAuditLog.target_id == entity_id)

    base_query = select(AdminAuditLog)
    if conditions:
        from sqlalchemy import and_ as _and
        base_query = base_query.where(_and(*conditions))

    count_query = select(func.count()).select_from(base_query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    items_query = (
        base_query
        .order_by(AdminAuditLog.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(items_query)
    logs = result.scalars().all()

    items = [
        {
            "id": log.id,
            "admin_user_id": log.admin_user_id,
            "action": log.action,
            "target_type": log.target_type,
            "target_id": log.target_id,
            "before": log.before,
            "after": log.after,
            "ip_address": log.ip_address,
            "created_at": log.created_at.isoformat() if log.created_at else None,
        }
        for log in logs
    ]

    return {"items": items, "total": total}
