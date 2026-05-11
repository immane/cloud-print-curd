from src.app.services.pricing import calculate_price


def test_calculate_price_uses_default_when_rules_invalid():
    result = calculate_price(
        [{"file_id": 1, "options": {"size": "A9", "color": "none", "pages": 2, "copies": 1}}],
        {"default": 30},
    )
    assert result["total_cents"] == 60
    assert result["items_detail"][0]["unit_price_cents"] == 30


def test_calculate_price_force_minimum_quantity_one():
    result = calculate_price(
        [{"file_id": 1, "options": {"size": "A4", "color": "black_white", "pages": 0, "copies": 0}}],
        {"A4": {"black_white": {"single": 20, "duplex": 30}}, "default": 30},
    )
    assert result["items_detail"][0]["quantity"] == 1
    assert result["total_cents"] == 20
