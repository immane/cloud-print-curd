from src.app.services.pricing import calculate_price


def test_calculate_price_zero_or_negative_inputs():
    rules = {"default": 30}
    result = calculate_price(
        [{"file_id": 1, "options": {"pages": 0, "copies": 0, "size": "A4", "color": "black_white"}}],
        rules,
    )
    assert result["total_cents"] >= 30


def test_calculate_price_multiple_items():
    rules = {
        "A4": {"black_white": {"single": 20, "duplex": 30}, "color": {"single": 50, "duplex": 80}},
        "default": 30,
    }
    result = calculate_price(
        [
            {"file_id": 1, "options": {"size": "A4", "color": "black_white", "duplex": False, "copies": 1, "pages": 10}},
            {"file_id": 2, "options": {"size": "A4", "color": "color", "duplex": True, "copies": 2, "pages": 5}},
        ],
        rules,
    )
    assert result["total_cents"] == 1000
