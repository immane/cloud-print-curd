from src.app.services.auth import create_access_token, create_refresh_token, verify_token


def test_access_token_contains_role():
    token = create_access_token(1, "admin")
    payload = verify_token(token)
    assert payload["sub"] == "1"
    assert payload["role"] == "admin"
    assert payload["type"] == "access"


def test_refresh_token_type():
    token = create_refresh_token(2)
    payload = verify_token(token)
    assert payload["sub"] == "2"
    assert payload["type"] == "refresh"
