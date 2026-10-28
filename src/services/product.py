import asyncio
import io
import mimetypes
from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from models.product import Product
from storage.minio import minio_client


ALLOWED_IMAGE_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}

MAX_IMAGE_SIZE = 5242880


async def get_product_by_id(
        db: AsyncSession,
        product_id: str
) -> Product | None:
    result = await db.execute(
        select(Product).where(Product.id == product_id)
    )
    return result.scalar_one_or_none()


async def get_list_all_products(db: AsyncSession) -> list[Product]:
    result = await db.execute(select(Product))
    return list(result.scalars().all())


async def create_product(
        db: AsyncSession,
        title: str,
        image: UploadFile,
) -> Product:
    content_type = image.content_type

    if content_type not in ALLOWED_IMAGE_TYPES:
        raise ValueError("Unsupported image type")

    image_data = await image.read(MAX_IMAGE_SIZE + 1)

    if not image_data:
        raise ValueError("Image is empty")

    if len(image_data) > MAX_IMAGE_SIZE:
        raise ValueError("Image is too large")

    object_name = (
        f"products/{uuid4()}"
        f"{ALLOWED_IMAGE_TYPES[content_type]}"
    )

    await asyncio.to_thread(
        minio_client.put_object,
        settings.MINIO_BUCKET,
        object_name=object_name,
        data=io.BytesIO(image_data),
        length=len(image_data),
        content_type=content_type,
    )

    try:
        product = Product(
            title=title,
            image_key=object_name,
        )
        db.add(product)

        await db.flush()
        await db.refresh(product)
        return product

    except Exception:
        await asyncio.to_thread(
            minio_client.remove_object,
            settings.MINIO_BUCKET,
            object_name,
        )
        raise


def _read_image_from_minio(image_key: str) -> bytes:
    response = minio_client.get_object(
        settings.MINIO_BUCKET,
        image_key,
    )

    try:
        return response.read()
    finally:
        response.close()
        response.release_conn()


async def get_product_image(
        db: AsyncSession,
        product_id,
) -> tuple[bytes, str] | None:
    product_obj = await get_product_by_id(db, product_id)

    if product_obj is None:
        return None

    image_data = await asyncio.to_thread(
        _read_image_from_minio,
        product_obj.image_key,
    )

    content_type = (
            mimetypes.guess_type(product_obj.image_key)[0]
            or "application/octet-stream"
    )

    return image_data, content_type
