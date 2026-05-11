import pytest

from src.app.services.auth import create_access_token, verify_token


def test_verify_token_rejects_invalid_signature():
    token = create_access_token(1, "user")
    header, payload, _sig = token.split(".")
    tampered = f"{header}.{payload}.invalidsig"
    with pytest.raises(ValueError):
        verify_token(tampered)


def test_verify_token_rejects_invalid_format():
    with pytest.raises(ValueError):
        verify_token("not-a-jwt")
