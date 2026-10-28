from fastapi import APIRouter, Depends, HTTPException
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from database import get_async_session
from dependencies import verify_bot_api_secret_key
from schemas.admin_bootstrap import AdminBootstrapRequest
from services.user import promote_or_create_admin


router = APIRouter()


@router.post(
    "/bootstrap-admin",
    dependencies=[Depends(verify_bot_api_secret_key)],
)
async def bootstrap_admin(
        payload: AdminBootstrapRequest,
        session: AsyncSession = Depends(
            get_async_session,
            scope="function",
        ),
):
    if not settings.ADMIN_BOOTSTRAP_ENABLED:
        raise HTTPException(
            status_code=404,
            detail="Admin bootstrap is disabled",
        )

    async with Redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
    ) as redis:
        claim_key = "bot_suggester:admin_bootstrap:claimed"

        claimed = await redis.set(
            claim_key,
            "used",
            nx=True,
        )

        if not claimed:
            raise HTTPException(
                status_code=409,
                detail="Admin bootstrap has already been used",
            )

        try:
            user = await promote_or_create_admin(
                session,
                payload.telegram_id,
            )

            await session.commit()

        except Exception:
            await session.rollback()
            await redis.delete(claim_key)
            raise

    return {
        "status": "ok",
        "message": "Administrator role granted",
        "telegram_id": user.telegram_id,
        "role": user.role,
    }
