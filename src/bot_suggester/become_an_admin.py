import httpx
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from config import settings


router = Router()

if settings.ADMIN_COMMAND:

    @router.message(Command(settings.ADMIN_COMMAND))
    async def become_an_admin(message: Message):
        if message.chat.type != "private":
            await message.answer(
                "Первоначальная настройка доступна только в личном чате."
            )
            return

        if message.from_user is None:
            await message.answer(
                "Не удалось определить пользователя Telegram."
            )
            return

        if not settings.BOT_API_SECRET_KEY:
            await message.answer(
                "Первоначальная настройка временно недоступна."
            )
            return

        url = (
            f"{settings.BACKEND_INTERNAL_URL.rstrip('/')}"
            "/internal/bootstrap-admin"
        )

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    url,
                    headers={
                        "X-Internal-API-Key": settings.BOT_API_SECRET_KEY,
                    },
                    json={
                        "telegram_id": message.from_user.id,
                    },
                )

                response.raise_for_status()

        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 409:
                text = (
                    "Первоначальная настройка администратора "
                    "уже была использована."
                )
            elif exc.response.status_code == 401:
                text = "Не удалось подтвердить внутренние полномочия."
            elif exc.response.status_code == 404:
                text = "Первоначальная настройка отключена."
            else:
                text = (
                    "Не удалось назначить администратора. "
                    f"HTTP {exc.response.status_code}."
                )

            await message.answer(text)
            return

        except httpx.RequestError:
            await message.answer(
                "Backend недоступен. Попробуйте позже."
            )
            return

        await message.answer(
            "Профиль администратора создан или обновлён. "
            "Теперь доступна команда /add_product."
        )
