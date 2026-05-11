from datetime import datetime, timedelta, timezone
import base64
import hashlib
import hmac
import json
import bcrypt

from src.app.config import settings

def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode((data + padding).encode())


def _jwt_encode(payload: dict) -> str:
    header = {"alg": settings.jwt_algorithm, "typ": "JWT"}
    header_part = _b64url_encode(json.dumps(header, separators=(",", ":")).encode())
    payload_part = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode())
    signing_input = f"{header_part}.{payload_part}".encode()
    sig = hmac.new(settings.jwt_secret.encode(), signing_input, hashlib.sha256).digest()
    return f"{header_part}.{payload_part}.{_b64url_encode(sig)}"


def _jwt_decode(token: str, verify_exp: bool = True) -> dict:
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("Invalid token format")

    header_part, payload_part, sig_part = parts
    signing_input = f"{header_part}.{payload_part}".encode()
    expected_sig = hmac.new(settings.jwt_secret.encode(), signing_input, hashlib.sha256).digest()
    actual_sig = _b64url_decode(sig_part)
    if not hmac.compare_digest(expected_sig, actual_sig):
        raise ValueError("Invalid token signature")

    header = json.loads(_b64url_decode(header_part))
    if header.get("alg") != settings.jwt_algorithm:
        raise ValueError("Invalid token algorithm")

    payload = json.loads(_b64url_decode(payload_part))
    if verify_exp and "exp" in payload:
        now = int(datetime.now(timezone.utc).timestamp())
        if int(payload["exp"]) < now:
            raise ValueError("Token expired")
    return payload


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())


def create_access_token(user_id: int, user_role: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "role": user_role,
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=settings.jwt_expire_minutes)).timestamp()),
    }
    return _jwt_encode(payload)


def create_refresh_token(user_id: int) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(days=settings.jwt_refresh_expire_days)).timestamp()),
    }
    return _jwt_encode(payload)


def verify_token(token: str) -> dict:
    return _jwt_decode(token, verify_exp=True)


def decode_token(token: str) -> dict:
    return _jwt_decode(token, verify_exp=False)
