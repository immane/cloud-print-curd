from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.db import get_db
from src.app.dependencies.auth import require_admin
from src.app.models import Order, User

router = APIRouter(prefix="/admin/search", tags=["admin-search"])


@router.get("")
async def admin_search(
    q: str = Query(..., min_length=1),
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin()),
):
    orders_result = await db.execute(
        select(Order)
        .where(Order.out_trade_no.contains(q))
        .limit(20)
    )
    orders = orders_result.scalars().all()

    users_result = await db.execute(
        select(User).where(
            or_(
                User.display_name.contains(q),
                User.email.contains(q),
            )
        ).limit(20)
    )
    users = users_result.scalars().all()

    return {
        "orders": [
            {
                "id": o.id,
                "out_trade_no": o.out_trade_no,
                "total_cents": o.total_cents,
                "status": o.status,
                "user_id": o.user_id,
                "created_at": o.created_at.isoformat() if o.created_at else None,
            }
            for o in orders
        ],
        "users": [
            {
                "id": u.id,
                "display_name": u.display_name,
                "email": u.email,
                "phone": u.phone,
                "role": u.role,
                "created_at": u.created_at.isoformat() if u.created_at else None,
            }
            for u in users
        ],
    }
