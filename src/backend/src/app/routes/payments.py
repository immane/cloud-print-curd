from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.db import get_db
from src.app.models import Order, Payment
from src.app.services.wechat import verify_webhook_signature

router = APIRouter(prefix="/v1/payments", tags=["payments"])


class WebhookTestPayload(BaseModel):
    out_trade_no: str
    amount_cents: int
    provider_status: str = "SUCCESS"
    provider: str = "wechat"


async def _process_payment_event(payload: dict[str, Any], db: AsyncSession) -> dict[str, Any]:
    out_trade_no = payload.get("out_trade_no")
    if not out_trade_no:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing out_trade_no")

    result = await db.execute(select(Order).where(Order.out_trade_no == out_trade_no))
    order = result.scalar_one_or_none()
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    order.status = "PAID"
    order.paid_at = datetime.now(timezone.utc)

    max_id = (await db.execute(select(func.max(Payment.id)))).scalar() or 0
    payment = Payment(
        id=int(max_id) + 1,
        order_id=order.id,
        provider=payload.get("provider", "wechat"),
        provider_payload=payload,
        provider_status=payload.get("provider_status", "SUCCESS"),
        amount_cents=int(payload.get("amount_cents", order.total_cents or 0)),
    )
    db.add(payment)
    await db.flush()

    return {"status": "processed", "order_id": order.id, "payment_id": payment.id}


@router.post("/webhook")
async def payments_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
    wechatpay_timestamp: str | None = Header(default=None, alias="Wechatpay-Timestamp"),
    wechatpay_nonce: str | None = Header(default=None, alias="Wechatpay-Nonce"),
    wechatpay_signature: str | None = Header(default=None, alias="Wechatpay-Signature"),
):
    body_bytes = await request.body()
    body_text = body_bytes.decode("utf-8") if body_bytes else "{}"

    if wechatpay_timestamp and wechatpay_nonce and wechatpay_signature:
        if not verify_webhook_signature(
            timestamp=wechatpay_timestamp,
            nonce=wechatpay_nonce,
            body=body_text,
            signature_header=wechatpay_signature,
        ):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid webhook signature")

    payload = await request.json()
    result = await _process_payment_event(payload, db)
    return result


@router.post("/webhook/test")
async def webhook_test(payload: WebhookTestPayload, db: AsyncSession = Depends(get_db)):
    result = await _process_payment_event(payload.model_dump(), db)
    return result
