from __future__ import annotations

from fastapi import APIRouter, Query

router = APIRouter(prefix="/v1/support", tags=["support"])


@router.get("/session-info")
async def session_info(order_id: int | None = Query(default=None)):
    session_from = {"type": "order", "id": order_id} if order_id else {"type": "general"}
    return {
        "sessionFrom": str(session_from),
        "sendMessageTitle": "Cloud Print Customer Service",
        "sendMessagePath": f"/pages/orders/detail?id={order_id}" if order_id else "/pages/index/index",
    }
