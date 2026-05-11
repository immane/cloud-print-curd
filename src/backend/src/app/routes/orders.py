from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.app.db import get_db
from src.app.dependencies.auth import ADMIN_ROLES, get_current_user, require_admin
from src.app.models import File, LibraryResource, Order, OrderItem, Payment
from src.app.models.user import User
from src.app.services.pricing import calculate_price, get_current_price_rules
from src.app.services.wechat import create_jsapi_order

router = APIRouter(prefix="/v1/orders", tags=["orders"])


class OrderItemInput(BaseModel):
    file_id: int
    options: dict[str, Any] = Field(default_factory=dict)


class CreateOrderRequest(BaseModel):
    items: list[OrderItemInput]
    address_id: int | None = None


class CreateFromResourceRequest(BaseModel):
    resource_id: int
    options: dict[str, Any] = Field(default_factory=dict)
    address_id: int | None = None


class RefundRequest(BaseModel):
    amount_cents: int
    reason: str


def _order_dict(order: Order) -> dict[str, Any]:
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
        "created_at": order.created_at.isoformat() if order.created_at else None,
        "updated_at": order.updated_at.isoformat() if order.updated_at else None,
    }


async def _build_payment_params(openid: str, out_trade_no: str, total_cents: int) -> dict[str, Any]:
    payment = await create_jsapi_order(
        openid=openid,
        out_trade_no=out_trade_no,
        total_fee=total_cents,
        description="Cloud Print Order",
    )
    return payment


@router.post("/create")
async def create_order(
    body: CreateOrderRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not body.items:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="items is required")

    file_ids = [item.file_id for item in body.items]
    files = (
        await db.execute(
            select(File).where(File.id.in_(file_ids), File.user_id == current_user.id, File.status != "deleted")
        )
    ).scalars().all()

    file_map = {f.id: f for f in files}
    for item in body.items:
        if item.file_id not in file_map:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"file_id {item.file_id} is invalid or inaccessible",
            )

    calc_items = []
    for item in body.items:
        options = dict(item.options)
        if "pages" not in options:
            options["pages"] = int(file_map[item.file_id].page_count or 1)
        calc_items.append({"file_id": item.file_id, "options": options})

    rules = await get_current_price_rules(db)
    pricing = calculate_price(calc_items, rules)

    out_trade_no = f"CP{uuid.uuid4().hex[:24].upper()}"
    order = Order(
        user_id=current_user.id,
        out_trade_no=out_trade_no,
        total_cents=pricing["total_cents"],
        currency="CNY",
        status="CREATED",
        payment_provider="wechat",
        address_id=body.address_id,
        metadata={"source": "user_upload"},
    )
    db.add(order)
    await db.flush()

    for idx, item in enumerate(body.items):
        detail = pricing["items_detail"][idx]
        db.add(
            OrderItem(
                order_id=order.id,
                file_id=item.file_id,
                description=file_map[item.file_id].filename,
                unit_price_cents=detail["unit_price_cents"],
                quantity=detail["quantity"],
                options=item.options,
            )
        )

    payment = await _build_payment_params(
        openid=current_user.openid or f"mock-openid-{current_user.id}",
        out_trade_no=out_trade_no,
        total_cents=order.total_cents,
    )

    await db.flush()
    return {
        "order_id": order.id,
        "total_cents": order.total_cents,
        "status": order.status,
        "payment": payment,
    }


@router.post("/create-from-resource")
async def create_from_resource(
    body: CreateFromResourceRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    resource = (
        await db.execute(
            select(LibraryResource)
            .options(joinedload(LibraryResource.file))
            .where(LibraryResource.id == body.resource_id, LibraryResource.is_public.is_(True))
        )
    ).unique().scalar_one_or_none()

    if resource is None or resource.file_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found")

    pages = int(resource.page_count or 1)
    rules = await get_current_price_rules(db)
    pricing = calculate_price([{"file_id": resource.file_id, "options": {**body.options, "pages": pages}}], rules)

    if resource.price_override_cents is not None:
        pricing["total_cents"] = int(resource.price_override_cents) * int(body.options.get("copies", 1) or 1)
        pricing["items_detail"][0]["unit_price_cents"] = int(resource.price_override_cents)

    out_trade_no = f"CP{uuid.uuid4().hex[:24].upper()}"
    order = Order(
        user_id=current_user.id,
        out_trade_no=out_trade_no,
        total_cents=pricing["total_cents"],
        currency="CNY",
        status="CREATED",
        payment_provider="wechat",
        address_id=body.address_id,
        metadata={"source": "library", "resource_id": resource.id},
    )
    db.add(order)
    await db.flush()

    detail = pricing["items_detail"][0]
    db.add(
        OrderItem(
            order_id=order.id,
            file_id=resource.file_id,
            description=resource.title,
            unit_price_cents=detail["unit_price_cents"],
            quantity=detail["quantity"],
            options=body.options,
        )
    )

    payment = await _build_payment_params(
        openid=current_user.openid or f"mock-openid-{current_user.id}",
        out_trade_no=out_trade_no,
        total_cents=order.total_cents,
    )

    await db.flush()
    return {
        "order_id": order.id,
        "total_cents": order.total_cents,
        "status": order.status,
        "payment": payment,
    }


@router.get("")
async def list_orders(
    status_filter: str | None = Query(default=None, alias="status"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    base = select(Order).where(Order.user_id == current_user.id)
    if status_filter:
        base = base.where(Order.status == status_filter)

    total = (await db.execute(select(func.count()).select_from(base.subquery()))).scalar() or 0
    items = (
        await db.execute(
            base.order_by(Order.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
    ).scalars().all()

    return {
        "items": [_order_dict(item) for item in items],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/{order_id}")
async def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    order = (
        await db.execute(
            select(Order)
            .options(joinedload(Order.items), joinedload(Order.payments))
            .where(Order.id == order_id)
        )
    ).unique().scalar_one_or_none()

    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    if order.user_id != current_user.id and current_user.role not in ADMIN_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return {
        **_order_dict(order),
        "items": [
            {
                "id": item.id,
                "file_id": item.file_id,
                "description": item.description,
                "unit_price_cents": item.unit_price_cents,
                "quantity": item.quantity,
                "options": item.options,
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
    }


@router.post("/{order_id}/refund")
async def user_refund(
    order_id: int,
    body: RefundRequest,
    _: User = Depends(require_admin(["finance", "admin"])),
    db: AsyncSession = Depends(get_db),
):
    order = (await db.execute(select(Order).where(Order.id == order_id))).scalar_one_or_none()
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    max_id = (await db.execute(select(func.max(Payment.id)))).scalar() or 0

    payment = Payment(
        id=int(max_id) + 1,
        order_id=order.id,
        provider="manual",
        provider_status="refunded",
        amount_cents=body.amount_cents,
        provider_payload={"reason": body.reason, "at": datetime.now(timezone.utc).isoformat()},
    )
    db.add(payment)
    order.status = "REFUNDED"
    await db.flush()
    return {"refund_id": payment.id, "status": "refunded"}
