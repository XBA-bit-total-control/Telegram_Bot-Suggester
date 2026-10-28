from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.basket import Basket
from models.product import BasketProduct, Product


async def get_basket(
        db: AsyncSession,
        user_id: UUID,
) -> Basket | None:
    result = await db.execute(
        select(Basket)
        .options(selectinload(Basket.products))
        .where(Basket.user_id == user_id)
        .execution_options(populate_existing=True)
    )
    return result.scalar_one_or_none()


async def get_or_create_basket(
        db: AsyncSession,
        user_id: UUID,
) -> Basket:
    statement = (
        pg_insert(Basket)
        .values(user_id=user_id)
        .on_conflict_do_nothing(
            index_elements=[Basket.user_id]
        )
    )
    await db.execute(statement)

    basket = await get_basket(db, user_id)

    if basket is None:
        raise RuntimeError("Failed to get or create basket")

    return basket


async def add_product_to_basket(
        db: AsyncSession,
        user_id: UUID,
        product_id: UUID,
) -> Basket | None:
    product = await db.get(Product, product_id)

    if product is None:
        return None

    basket = await get_or_create_basket(db, user_id)

    statement = (
        pg_insert(BasketProduct)
        .values(
            basket_id=basket.id,
            product_id=product.id,
        )
        .on_conflict_do_nothing(
            index_elements=[
                BasketProduct.basket_id,
                BasketProduct.product_id,
            ]
        )
    )
    await db.execute(statement)

    return await get_basket(db, user_id)


async def remove_product_from_basket(
        db: AsyncSession,
        user_id: UUID,
        product_id: UUID,
) -> bool:
    product = await db.get(Product, product_id)

    if product is None:
        return False

    basket = await get_basket(db, user_id)

    if basket is None:
        return True

    statement = delete(BasketProduct).where(
        BasketProduct.basket_id == basket.id,
        BasketProduct.product_id == product.id,
    )
    await db.execute(statement)

    return True
