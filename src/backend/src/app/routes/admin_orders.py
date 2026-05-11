import json
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.app.db import get_db
from src.app.dependencies.auth import require_admin
from src.app.models import (
    AdminAuditLog,
    Order,
    OrderItem,
    Payment,
    User,
)

router = APIRouter(prefix="/admin/orders", tags=["admin-orders"])


def _order_to_dict(order: Order) -> dict:
    return {
        "id": order.id,
        "user_id": order.user_id,
        "out_trade_no": order.out_trade_no,
        "total_cents": order.total_cents,
        "currency": order.currency,
        "status": order.status,
        "payment_provider": order.payment_provider,
        "provider_payment_id": order.provider_payment_id,
        "paid_at": order.paid_at.isoformat() if order.paid_at else None,
        "address_id": order.address_id,
        "metadata": order.metadata_json,
        "assigned_to": order.metadata_json.get("assigned_to") if order.metadata_json else None,
        "note": order.metadata_json.get("note") if order.metadata_json else None,
        "created_at": order.created_at.isoformat() if order.created_at else None,
        "updated_at": order.updated_at.isoformat() if order.updated_at else None,
    }


class OrderUpdateRequest(BaseModel):
    status: Optional[str] = None
    assigned_to: Optional[int] = None
    note: Optional[str] = None


class RefundRequest(BaseModel):
    amount_cents: int
    reason: str


@router.get("")
async def list_orders(
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin()),
    status_filter: Optional[str] = Query(None, alias="status"),
    assigned: Optional[int] = Query(None),
    from_date: Optional[str] = Query(None, alias="from"),
    to_date: Optional[str] = Query(None, alias="to"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
):
    conditions = []

    if status_filter:
        conditions.append(Order.status == status_filter)

    if assigned is not None:
        conditions.append(
            func.json_extract(Order.metadata_json, "$.assigned_to") == str(assigned)
        )

    if from_date:
        conditions.append(Order.created_at >= from_date)
    if to_date:
        conditions.append(Order.created_at <= to_date)

    if search:
        search_cond = or_(
            Order.out_trade_no.contains(search),
            Order.user.has(User.display_name.contains(search)),
        )
        conditions.append(search_cond)

    base_query = select(Order)
    if conditions:
        base_query = base_query.where(and_(*conditions))

    count_query = select(func.count()).select_from(base_query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    items_query = (
        base_query
        .order_by(Order.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(items_query)
    orders = result.scalars().all()

    items = []
    for order in orders:
        items.append({
            "id": order.id,
            "out_trade_no": order.out_trade_no,
            "user_id": order.user_id,
            "total_cents": order.total_cents,
            "currency": order.currency,
            "status": order.status,
            "assigned_to": order.metadata_json.get("assigned_to") if order.metadata_json else None,
            "note": order.metadata_json.get("note") if order.metadata_json else None,
            "created_at": order.created_at.isoformat() if order.created_at else None,
            "updated_at": order.updated_at.isoformat() if order.updated_at else None,
        })

    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.get("/status-counts")
async def status_counts(
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin()),
):
    result = await db.execute(
        select(Order.status, func.count(Order.id)).group_by(Order.status)
    )
    counts = {row[0]: row[1] for row in result.all()}
    return counts


@router.get("/{order_id}")
async def get_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin()),
):
    result = await db.execute(
        select(Order)
        .options(
            joinedload(Order.items).joinedload(OrderItem.file),
            joinedload(Order.payments),
        )
        .where(Order.id == order_id)
    )
    order = result.unique().scalar_one_or_none()

    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    audit_result = await db.execute(
        select(AdminAuditLog)
        .where(
            AdminAuditLog.target_type == "order",
            AdminAuditLog.target_id == str(order_id),
        )
        .order_by(AdminAuditLog.created_at.desc())
    )
    audit_logs = audit_result.scalars().all()

    user_result = await db.execute(select(User).where(User.id == order.user_id))
    order_user = user_result.scalar_one_or_none()

    return {
        "id": order.id,
        "user": {
            "id": order_user.id,
            "display_name": order_user.display_name,
            "email": order_user.email,
        } if order_user else None,
        "out_trade_no": order.out_trade_no,
        "total_cents": order.total_cents,
        "currency": order.currency,
        "status": order.status,
        "payment_provider": order.payment_provider,
        "provider_payment_id": order.provider_payment_id,
        "paid_at": order.paid_at.isoformat() if order.paid_at else None,
        "address_id": order.address_id,
        "metadata": order.metadata_json,
        "assigned_to": order.metadata_json.get("assigned_to") if order.metadata_json else None,
        "note": order.metadata_json.get("note") if order.metadata_json else None,
        "created_at": order.created_at.isoformat() if order.created_at else None,
        "updated_at": order.updated_at.isoformat() if order.updated_at else None,
        "items": [
            {
                "id": item.id,
                "file_id": item.file_id,
                "description": item.description,
                "unit_price_cents": item.unit_price_cents,
                "quantity": item.quantity,
                "options": item.options,
                "created_at": item.created_at.isoformat() if item.created_at else None,
            }
            for item in order.items
        ],
        "payments": [
            {
                "id": p.id,
                "provider": p.provider,
                "provider_status": p.provider_status,
                "amount_cents": p.amount_cents,
                "created_at": p.created_at.isoformat() if p.created_at else None,
            }
            for p in order.payments
        ],
        "audit_logs": [
            {
                "id": log.id,
                "admin_user_id": log.admin_user_id,
                "action": log.action,
                "before": log.before,
                "after": log.after,
                "ip_address": log.ip_address,
                "created_at": log.created_at.isoformat() if log.created_at else None,
            }
            for log in audit_logs
        ],
    }


@router.patch("/{order_id}")
async def update_order(
    order_id: int,
    body: OrderUpdateRequest,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin()),
):
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()

    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    before = _order_to_dict(order)

    if body.status is not None:
        order.status = body.status

    if body.assigned_to is not None or body.note is not None:
        meta = dict(order.metadata_json) if order.metadata_json else {}
        if body.assigned_to is not None:
            meta["assigned_to"] = body.assigned_to
        if body.note is not None:
            meta["note"] = body.note
        order.metadata_json = meta

    await db.flush()
    await db.refresh(order)

    after = _order_to_dict(order)

    audit_entry = AdminAuditLog(
        admin_user_id=admin_user.id,
        action="update_order",
        target_type="order",
        target_id=str(order_id),
        before=before,
        after=after,
    )
    db.add(audit_entry)
    await db.flush()

    return _order_to_dict(order)


@router.post("/{order_id}/refund")
async def refund_order(
    order_id: int,
    body: RefundRequest,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin(allowed_roles=["finance", "admin"])),
):
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()

    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    max_id = (await db.execute(select(func.max(Payment.id)))).scalar() or 0

    refund = Payment(
        id=int(max_id) + 1,
        order_id=order.id,
        provider="manual",
        provider_status="refunded",
        amount_cents=body.amount_cents,
    )
    db.add(refund)

    audit_entry = AdminAuditLog(
        admin_user_id=admin_user.id,
        action="refund_order",
        target_type="order",
        target_id=str(order_id),
        before=_order_to_dict(order),
        after={
            "refund_amount_cents": body.amount_cents,
            "reason": body.reason,
        },
    )
    db.add(audit_entry)
    await db.flush()
    await db.refresh(refund)

    return {
        "id": refund.id,
        "order_id": refund.order_id,
        "amount_cents": refund.amount_cents,
        "provider": refund.provider,
        "provider_status": refund.provider_status,
        "created_at": refund.created_at.isoformat() if refund.created_at else None,
    }
