from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.db import get_db
from src.app.models import User
from src.app.services.auth import create_access_token, create_refresh_token
from src.app.services.wechat import exchange_code

router = APIRouter(prefix="/v1/auth/wechat", tags=["auth-wechat"])


class WeChatLoginRequest(BaseModel):
    code: str


class WeChatLoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    user: dict


@router.post("/login", response_model=WeChatLoginResponse)
async def wechat_login(
    body: WeChatLoginRequest,
    db: AsyncSession = Depends(get_db),
):
    wx_data = await exchange_code(body.code)

    openid = wx_data.get("openid")
    if not openid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to exchange WeChat code",
        )

    unionid = wx_data.get("unionid")
    result = await db.execute(select(User).where(User.openid == openid))
    user = result.scalar_one_or_none()

    if user is None:
        user = User(
            openid=openid,
            unionid=unionid,
            display_name="",
            role="user",
        )
        db.add(user)
        await db.flush()
        await db.refresh(user)

    access_token = create_access_token(user.id, user.role)
    refresh_token = create_refresh_token(user.id)

    return WeChatLoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user={
            "id": user.id,
            "display_name": user.display_name,
            "avatar_url": user.avatar_url,
        },
    )
