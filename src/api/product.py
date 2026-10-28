from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import Response
from minio.error import S3Error
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_async_session
from dependencies import verify_bot_api_secret_key
from schemas.product import ProductResponse
from services import product, user


router = APIRouter()

ALLOWED_IMAGE_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}

MAX_IMAGE_SIZE = 5242880


@router.get(
    "/product/{product_id}",
    status_code=200,
    summary="Получить продукт по id",
    response_model=ProductResponse
)
async def get_product_by_id(
        product_id: str,
        session: AsyncSession = Depends(get_async_session)
):
    try:
        result = await product.get_product_by_id(session, product_id)
        if result is None:
            raise HTTPException(status_code=404, detail="Product not found")
        return result
    except DBAPIError:
        raise HTTPException(status_code=400, detail="Invalid product_id")


@router.get(
    "/product",
    status_code=200,
    summary="Получить все продукты",
    response_model=list[ProductResponse]
)
async def get_all_products(
        session: AsyncSession = Depends(get_async_session)
):
    return await product.get_list_all_products(session)


@router.post(
    "/product",
    status_code=201,
    response_model=ProductResponse,
    summary="Добавить продукт",
)
async def add_product(
        telegram_id: int = Form(...),
        title: str = Form(...),
        image: UploadFile = File(...),
        session: AsyncSession = Depends(
            get_async_session,
            scope="function"),
        check_from_a_bot: str = Depends(verify_bot_api_secret_key)
):
    user_obj = await user.get_user_by_telegram_id(session, telegram_id)
    if user_obj is None:
        raise HTTPException(status_code=404, detail="User not found")
    if user_obj.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    try:
        return await product.create_product(
            db=session,
            title=title,
            image=image,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc


@router.get(
    "/product/{product_id}/image",
    status_code=200,
    summary="Получить изображение товара",
)
async def get_product_image(
        product_id: UUID,
        session: AsyncSession = Depends(get_async_session),
):
    try:
        result = await product.get_product_image(
            db=session,
            product_id=product_id,
        )
    except S3Error as exc:
        if exc.code in {"NoSuchKey", "NoSuchObject"}:
            raise HTTPException(
                status_code=404,
                detail="Product image not found",
            ) from exc

        raise HTTPException(
            status_code=502,
            detail="Unable to retrieve image from storage",
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail="Unable to retrieve image from storage",
        ) from exc

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    image_data, content_type = result

    return Response(
        content=image_data,
        media_type=content_type,
        headers={"Cache-Control": "no-store"},
    )
