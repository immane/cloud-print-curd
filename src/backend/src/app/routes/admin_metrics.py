from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.db import get_db
from src.app.dependencies.auth import require_admin
from src.app.models import File, Order, User

router = APIRouter(prefix="/admin/metrics", tags=["admin-metrics"])


@router.get("")
async def get_metrics(
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin()),
):
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

    orders_today_result = await db.execute(
        select(func.count(Order.id)).where(Order.created_at >= today)
    )
    orders_today = orders_today_result.scalar() or 0

    revenue_today_result = await db.execute(
        select(func.coalesce(func.sum(Order.total_cents), 0)).where(
            Order.created_at >= today,
            Order.status.in_(["PAID", "COMPLETED", "SHIPPED"]),
        )
    )
    revenue_today_cents = revenue_today_result.scalar() or 0

    new_users_today_result = await db.execute(
        select(func.count(User.id)).where(User.created_at >= today)
    )
    new_users_today = new_users_today_result.scalar() or 0

    pending_webhooks_result = await db.execute(
        select(func.count(Order.id)).where(Order.status == "PENDING")
    )
    pending_webhooks = pending_webhooks_result.scalar() or 0

    orders_by_status_result = await db.execute(
        select(Order.status, func.count(Order.id)).group_by(Order.status)
    )
    orders_by_status = {row[0]: row[1] for row in orders_by_status_result.all()}

    total_files_result = await db.execute(select(func.count(File.id)))
    total_files = total_files_result.scalar() or 0

    return {
        "orders_today": orders_today,
        "revenue_today_cents": revenue_today_cents,
        "new_users_today": new_users_today,
        "pending_webhooks": pending_webhooks,
        "orders_by_status": orders_by_status,
        "total_files": total_files,
    }
