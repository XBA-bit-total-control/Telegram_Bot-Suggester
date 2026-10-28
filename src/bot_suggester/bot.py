from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import (
    RedisEventIsolation,
    RedisStorage,
)

from config import settings


bot = Bot(token=settings.BOT_TOKEN)

if settings.BOT_MODE == "webhook":
    dp = Dispatcher(
        storage=RedisStorage.from_url(settings.REDIS_URL),
        events_isolation=RedisEventIsolation.from_url(
            settings.REDIS_URL
        ),
    )
else:
    dp = Dispatcher()

