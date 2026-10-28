from secrets import compare_digest
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException
from fastapi.security import (
    APIKeyHeader,
    HTTPBearer,
    HTTPAuthorizationCredentials,
)
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from database import get_async_session
from models.user import User
from services.user import get_user_by_inside_id
from utilities.jwt_handler import decode_access_token


bot_api_secret_key_header = APIKeyHeader(
    name="X-Internal-API-Key",
    auto_error=False,
)

bearer_scheme = HTTPBearer(auto_error=False)


async def verify_bot_api_secret_key(
        api_key: str | None = Depends(bot_api_secret_key_header),
) -> None:
    expected_key = settings.BOT_API_SECRET_KEY

    if (
            not expected_key
            or not api_key
            or not compare_digest(api_key, expected_key)
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid API credentials",
        )


async def jwt_authorization(
        credentials: HTTPAuthorizationCredentials | None = Depends(
            bearer_scheme
        ),
        session: AsyncSession = Depends(
            get_async_session,
            scope="function"),
) -> User:
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Missing access token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = decode_access_token(credentials.credentials)

    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        parsed_user_id = UUID(user_id)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=401,
            detail="Invalid access token subject",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None

    user = await get_user_by_inside_id(
        session,
        parsed_user_id,
    )

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User associated with token not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


CurrentUser = Annotated[User, Depends(jwt_authorization)]


async def admin_authorization(
        current_user: CurrentUser,
) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Administrator access required",
        )

    return current_user


AdminUser = Annotated[User, Depends(admin_authorization)]
