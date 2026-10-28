from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_async_session
from dependencies import CurrentUser
from schemas.basket import BasketResponse
from services import basket as basket_service


router = APIRouter()


@router.get(
    "",
    response_model=BasketResponse,
    summary="Получить корзину текущего пользователя",
)
async def get_my_basket(
        current_user: CurrentUser,
        session: AsyncSession = Depends(get_async_session),
):
    basket = await basket_service.get_basket(
        session,
        current_user.id,
    )

    if basket is None:
        return BasketResponse(products=[])

    return basket


@router.post(
    "/items/{product_id}",
    response_model=BasketResponse,
    summary="Добавить товар в корзину",
)
async def add_item_to_basket(
        product_id: UUID,
        current_user: CurrentUser,
        session: AsyncSession = Depends(
            get_async_session,
            scope="function"),
):
    basket = await basket_service.add_product_to_basket(
        session,
        current_user.id,
        product_id,
    )

    if basket is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    return basket


@router.delete(
    "/items/{product_id}",
    status_code=204,
    summary="Удалить товар из корзины",
)
async def remove_item_from_basket(
        product_id: UUID,
        current_user: CurrentUser,
        session: AsyncSession = Depends(get_async_session),
):
    removed = await basket_service.remove_product_from_basket(
        session,
        current_user.id,
        product_id,
    )

    if not removed:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    return Response(status_code=204)
