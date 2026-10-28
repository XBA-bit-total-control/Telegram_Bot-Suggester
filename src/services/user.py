from uuid import UUID

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User


async def get_user_by_telegram_id(
        db: AsyncSession,
        telegram_id: int
) -> User | None:
    result = await db.execute(select(User).where(User.telegram_id == telegram_id))
    return result.scalar_one_or_none()


async def get_user_by_inside_id(
        db: AsyncSession,
        id: UUID
) -> User | None:
    result = await db.execute(select(User).where(User.id == id))
    return result.scalar_one_or_none()


async def create_user(
        db: AsyncSession,
        telegram_id: int,
        role: str = 'user'
) -> User:
    user = User(telegram_id=telegram_id, role=role)
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


async def get_or_create_user(
        db: AsyncSession,
        telegram_id: int,
) -> User:
    statement = (
        insert(User)
        .values(
            telegram_id=telegram_id,
            role="user",
        )
        .on_conflict_do_nothing(
            index_elements=[User.telegram_id]
        )
    )

    await db.execute(statement)

    result = await db.execute(
        select(User).where(
            User.telegram_id == telegram_id
        )
    )

    return result.scalar_one()


async def promote_or_create_admin(
        session: AsyncSession,
        telegram_id: int,
) -> User:
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    user = result.scalar_one_or_none()

    if user is None:
        user = User(
            telegram_id=telegram_id,
            role="admin",
        )
        session.add(user)
    else:
        user.role = "admin"

    await session.flush()

    return user
