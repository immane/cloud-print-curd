from src.app.services.pricing import DEFAULT_RULES, calculate_price, get_price_tip


def test_calculate_price_default_rules():
    result = calculate_price(
        [{"file_id": 1, "options": {"size": "A4", "color": "black_white", "duplex": False, "copies": 2, "pages": 10}}],
        DEFAULT_RULES,
    )
    assert result["total_cents"] == 400
    assert result["items_detail"][0]["unit_price_cents"] == 20


def test_calculate_price_fallback_default():
    result = calculate_price(
        [{"file_id": 2, "options": {"size": "UNKNOWN", "copies": 1, "pages": 3}}],
        DEFAULT_RULES,
    )
    assert result["total_cents"] == 90


def test_get_price_tip():
    tip = get_price_tip()
    assert "Prices are per page" in tip["text"]
