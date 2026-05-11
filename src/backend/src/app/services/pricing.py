from __future__ import annotations

from typing import Any

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.models import PriceTable


DEFAULT_RULES: dict[str, Any] = {
    "A4": {
        "black_white": {"single": 20, "duplex": 30},
        "color": {"single": 50, "duplex": 80},
    },
    "A3": {
        "black_white": {"single": 30, "duplex": 45},
        "color": {"single": 75, "duplex": 120},
    },
    "default": 30,
}


async def get_current_price_rules(db: AsyncSession) -> dict[str, Any]:
    result = await db.execute(
        select(PriceTable).where(PriceTable.published.is_(True)).order_by(desc(PriceTable.version)).limit(1)
    )
    table = result.scalar_one_or_none()
    if table and isinstance(table.rules, dict):
        return table.rules
    return DEFAULT_RULES


def calculate_price(items: list[dict[str, Any]], rules: dict[str, Any]) -> dict[str, Any]:
    total_cents = 0
    items_detail: list[dict[str, Any]] = []

    for item in items:
        options = item.get("options") or {}
        size = options.get("size", "A4")
        color = options.get("color", "black_white")
        duplex_flag = bool(options.get("duplex", False))
        side_key = "duplex" if duplex_flag else "single"
        copies = int(options.get("copies", 1) or 1)
        pages = int(options.get("pages", 1) or 1)
        quantity = max(copies * pages, 1)

        size_rule = rules.get(size, {}) if isinstance(rules, dict) else {}
        base_price = (
            size_rule.get(color, {}).get(side_key)
            if isinstance(size_rule, dict)
            else None
        )

        if base_price is None:
            base_price = rules.get("default", 30) if isinstance(rules, dict) else 30

        unit_price_cents = int(base_price)
        subtotal = unit_price_cents * quantity
        total_cents += subtotal

        items_detail.append(
            {
                "unit_price_cents": unit_price_cents,
                "quantity": quantity,
                "subtotal": subtotal,
                "size": size,
                "color": color,
                "duplex": duplex_flag,
                "copies": copies,
                "pages": pages,
            }
        )

    return {"total_cents": total_cents, "items_detail": items_detail}


def get_price_tip() -> dict[str, str]:
    return {
        "text": "Prices are per page. Color printing costs extra. Duplex is double-sided."
    }
