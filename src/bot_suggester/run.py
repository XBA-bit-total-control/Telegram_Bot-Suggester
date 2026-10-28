import asyncio
import logging

from aiogram import Bot
from aiogram.webhook.aiohttp_server import (
    SimpleRequestHandler,
    setup_application,
)
from aiohttp import web

from bot_suggester.bot import bot, dp
from bot_suggester.product import router as product_router
from bot_suggester.become_an_admin import router as admin_router
from bot_suggester.start import router as start_router
from config import settings


def include_routers() -> None:
    dp.include_router(start_router)
    dp.include_router(admin_router)
    dp.include_router(product_router)


async def on_startup(bot: Bot) -> None:
    if not settings.BOT_WEBHOOK_URL:
        raise RuntimeError(
            "Не задан BOT_WEBHOOK_URL"
        )

    if not settings.BOT_WEBHOOK_SECRET:
        raise RuntimeError(
            "Не задан BOT_WEBHOOK_SECRET"
        )

    await bot.set_webhook(
        url=settings.BOT_WEBHOOK_URL,
        secret_token=settings.BOT_WEBHOOK_SECRET,
        allowed_updates=dp.resolve_used_update_types(),
    )


async def run_polling() -> None:
    include_routers()
    await dp.start_polling(bot)


def create_webhook_app() -> web.Application:
    include_routers()

    dp.startup.register(on_startup)

    app = web.Application()

    SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        handle_in_background=False,
        secret_token=settings.BOT_WEBHOOK_SECRET,
    ).register(
        app,
        path=settings.BOT_WEBHOOK_PATH,
    )

    setup_application(app, dp, bot=bot)

    return app


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    if settings.BOT_MODE == "polling":
        asyncio.run(run_polling())

    elif settings.BOT_MODE == "webhook":
        web.run_app(
            create_webhook_app(),
            host=settings.BOT_WEBHOOK_HOST,
            port=settings.BOT_WEBHOOK_PORT,
        )

    else:
        raise ValueError(
            f"Неизвестный BOT_MODE: {settings.BOT_MODE}"
        )
