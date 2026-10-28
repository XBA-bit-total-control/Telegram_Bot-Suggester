import io

import httpx
from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from config import settings


router = Router()


class ProductUpload(StatesGroup):
    waiting_for_product = State()


@router.message(Command("add_product"))
async def add_product_command(
        message: Message,
        state: FSMContext,
):
    await state.set_state(ProductUpload.waiting_for_product)
    await message.answer(
        "Для добавления товара пришлите в одном сообщении "
        "фотографию товара и его название"
    )


@router.message(ProductUpload.waiting_for_product)
async def receive_product(
        message: Message,
        state: FSMContext,
):
    if not message.photo:
        await message.answer(
            "Неудача: Фото не было отправлено или отправлено в формате файла"
        )
        return

    title = (message.caption or "").strip()

    if not title:
        await message.answer(
            "Нехватает названия, добавьте его и отправьте фото ещё раз"
        )
        return

    if message.from_user is None:
        await message.answer("Не пойму кто вы - в доступе отказано")
        await state.clear()
        return

    await state.clear()

    photo = message.photo[-1]
    image_buffer = io.BytesIO()

    try:
        await message.bot.download(
            file=photo,
            destination=image_buffer,
        )
    except Exception:
        await message.answer(
            "Не получилось скачать фотографию."
            "Попробуйте ещё раз - вызовите /add_product"
        )
        return

    image_data = image_buffer.getvalue()

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{settings.BACKEND_INTERNAL_URL.rstrip('/')}/api/product",
                headers={
                    "X-Internal-API-Key": settings.BOT_API_SECRET_KEY,
                },
                data={
                    "telegram_id": str(message.from_user.id),
                    "title": title,
                },
                files={
                    "image": (
                        "product.jpg",
                        image_data,
                        "image/jpeg",
                    ),
                },
            )

            response.raise_for_status()

    except httpx.HTTPStatusError as exc:
        status_code = exc.response.status_code

        try:
            detail = exc.response.json().get(
                "detail",
                "Неизвестная внутренняя ошибка",
            )
        except ValueError:
            detail = "Описание ошибки отсутствует"

        if status_code == 401:
            text = (
                "Неудача: Недействительное значение X-Internal-API-Key"
            )
        elif status_code == 403:
            text = "Недостаточно прав: добавлять товары может только админ"
        elif status_code == 404:
            text = (
                f"Неудача: Требуется регистрация"
            )
        else:
            text = (
                f"Ошибка добавления товара: "
                f"(HTTP {status_code}): {detail}"
            )

        await message.answer(text)
        return

    except httpx.RequestError:
        await message.answer(
            "Не удалось добавить товар. "
            "Повторите запрос повторно"
        )
        return

    await message.answer(
        f"Товар «{title}» был успешно добавлен"
    )
