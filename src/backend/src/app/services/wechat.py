import json
import hashlib
import time
import hmac
from typing import Optional

import httpx

from src.app.config import settings

WECHAT_CODE2SESSION_URL = "https://api.weixin.qq.com/sns/jscode2session"


async def exchange_code(code: str) -> dict:
    if not settings.wechat_app_id or not settings.wechat_app_secret:
        return {
            "openid": f"mock_openid_{code[:8]}",
            "unionid": f"mock_unionid_{code[:8]}",
        }

    async with httpx.AsyncClient() as client:
        response = await client.get(
            WECHAT_CODE2SESSION_URL,
            params={
                "appid": settings.wechat_app_id,
                "secret": settings.wechat_app_secret,
                "js_code": code,
                "grant_type": "authorization_code",
            },
        )
        response.raise_for_status()
        data = response.json()
        if "errcode" in data and data.get("errcode") != 0:
            raise ValueError(f"WeChat API error: {data.get('errmsg', 'unknown')}")
        return data


async def create_jsapi_order(
    openid: str,
    out_trade_no: str,
    total_fee: int,
    description: str,
    attach: Optional[str] = None,
    notify_url: Optional[str] = None,
) -> dict:
    now = str(int(time.time()))
    nonce = hashlib.sha256(f"{out_trade_no}:{now}".encode()).hexdigest()[:16]
    # Current implementation returns deterministic signed stub for local/testing.
    # Replace this block with real v3 JSAPI integration when merchant infra is wired.
    return {
        "provider": "wechat",
        "mock": not (settings.wechat_mch_id and settings.wechat_mch_api_v3_key),
        "params": {
            "appId": settings.wechat_app_id or "mock-app-id",
            "timeStamp": now,
            "nonceStr": nonce,
            "package": f"prepay_id=mock_{out_trade_no}",
            "signType": "RSA",
            "paySign": hashlib.sha256(
                f"{openid}:{out_trade_no}:{total_fee}:{settings.wechat_mch_id or 'mock'}".encode()
            ).hexdigest(),
        },
    }


def verify_webhook_signature(
    timestamp: str,
    nonce: str,
    body: str,
    signature_header: str,
) -> bool:
    if not settings.wechat_mch_api_v3_key:
        return True

    message = f"{timestamp}\n{nonce}\n{body}\n"
    expected = hmac.new(
        settings.wechat_mch_api_v3_key.encode(),
        message.encode(),
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature_header)
