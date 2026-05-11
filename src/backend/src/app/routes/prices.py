from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.db import get_db
from src.app.services.pricing import get_current_price_rules, get_price_tip

router = APIRouter(prefix="/v1/prices", tags=["prices"])


@router.get("")
async def list_prices(
    paper_type: str | None = Query(default=None),
    size: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    rules = await get_current_price_rules(db)
    items: list[dict] = []

    for entry_size, entry_val in rules.items():
        if entry_size == "default" or not isinstance(entry_val, dict):
            continue
        for color, mode_map in entry_val.items():
            if not isinstance(mode_map, dict):
                continue
            for side, unit in mode_map.items():
                item = {
                    "paper_type": color,
                    "size": entry_size,
                    "unit_price_cents": int(unit),
                    "description": f"{entry_size} {color} {side}",
                    "currency": "CNY",
                    "duplex": side == "duplex",
                }
                items.append(item)

    if paper_type:
        items = [it for it in items if it["paper_type"] == paper_type]
    if size:
        items = [it for it in items if it["size"] == size]

    return items


@router.get("/tip")
async def price_tip():
    return get_price_tip()
