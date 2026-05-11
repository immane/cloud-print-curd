from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.db import get_db
from src.app.dependencies.auth import require_admin
from src.app.models import File, Order, User

router = APIRouter(prefix="/admin/users", tags=["admin-users"])


class AdjustBalanceRequest(BaseModel):
    amount_cents: int
    reason: str


@router.get("")
async def list_users(
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin()),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    base_query = select(User)

    if search:
        from sqlalchemy import or_ as _or
        base_query = base_query.where(
            _or(
                User.display_name.contains(search),
                User.email.contains(search),
                User.phone.contains(search),
            )
        )

    count_query = select(func.count()).select_from(base_query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    items_query = (
        base_query
        .order_by(User.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(items_query)
    users = result.scalars().all()

    items = [
        {
            "id": u.id,
            "email": u.email,
            "phone": u.phone,
            "display_name": u.display_name,
            "avatar_url": u.avatar_url,
            "role": u.role,
            "balance_cents": u.balance_cents,
            "created_at": u.created_at.isoformat() if u.created_at else None,
            "updated_at": u.updated_at.isoformat() if u.updated_at else None,
        }
        for u in users
    ]

    return {"items": items, "total": total}


@router.get("/{user_id}")
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin()),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    orders_count = (
        await db.execute(
            select(func.count(Order.id)).where(Order.user_id == user_id)
        )
    ).scalar() or 0

    files_count = (
        await db.execute(
            select(func.count(File.id)).where(File.user_id == user_id)
        )
    ).scalar() or 0

    recent_orders_result = await db.execute(
        select(Order)
        .where(Order.user_id == user_id)
        .order_by(Order.created_at.desc())
        .limit(5)
    )
    recent_orders = recent_orders_result.scalars().all()

    return {
        "id": user.id,
        "email": user.email,
        "phone": user.phone,
        "display_name": user.display_name,
        "avatar_url": user.avatar_url,
        "role": user.role,
        "balance_cents": user.balance_cents,
        "metadata": user.metadata_json,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "updated_at": user.updated_at.isoformat() if user.updated_at else None,
        "orders_count": orders_count,
        "files_count": files_count,
        "recent_orders": [
            {
                "id": o.id,
                "out_trade_no": o.out_trade_no,
                "total_cents": o.total_cents,
                "status": o.status,
                "created_at": o.created_at.isoformat() if o.created_at else None,
            }
            for o in recent_orders
        ],
    }


@router.post("/{user_id}/adjust-balance")
async def adjust_balance(
    user_id: int,
    body: AdjustBalanceRequest,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin(allowed_roles=["admin"])),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    old_balance = user.balance_cents
    user.balance_cents += body.amount_cents

    from src.app.models import AdminAuditLog
    audit_entry = AdminAuditLog(
        admin_user_id=admin_user.id,
        action="adjust_balance",
        target_type="user",
        target_id=str(user_id),
        before={
            "balance_cents": old_balance,
            "adjustment_cents": body.amount_cents,
            "reason": body.reason,
        },
        after={
            "balance_cents": user.balance_cents,
        },
    )
    db.add(audit_entry)
    await db.flush()
    await db.refresh(user)

    return {"success": True, "new_balance": user.balance_cents}
