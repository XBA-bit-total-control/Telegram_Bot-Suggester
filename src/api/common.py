from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from database import get_async_session
from services.user import get_or_create_user
from utilities.jwt_handler import create_access_token
from utilities.telegram_auth import validate_telegram_init_data


router = APIRouter()


class TelegramInitDataRequest(BaseModel):
    init_data: str = Field(min_length=1)


@router.get(
    "/health",
    status_code=200,
    summary="Проверка работоспособности"
)
async def check():
    return {"status": "ok"}


@router.post(
    "/validate",
    status_code=200,
    summary="Валидация initData через POST",
)
async def validate_user_from_tma(
        payload: TelegramInitDataRequest,
        session: AsyncSession = Depends(get_async_session)
):
    try:
        data = validate_telegram_init_data(
            payload.init_data,
            settings.BOT_TOKEN,
        )
    except ValueError as err:
        raise HTTPException(
            status_code=401,
            detail="Invalid Telegram initData",
        ) from err

    if not data:
        raise HTTPException(
            status_code=401,
            detail="Invalid Telegram initData",
        )

    telegram_id = data["user"]["id"]
    user = await get_or_create_user(session, telegram_id)
    token = create_access_token(str(user.id))

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user.to_dict(),
    }
