from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import settings


router = Router()


@router.message(Command("start"))
async def start(message: Message):
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text="Открыть каталог",
        web_app={
            "url": settings.FRONTEND_ORIGIN,
        },
    )
    await message.answer(
        "Привет! Я бот-рекомендатель. Вот тебе моя рекомендация: \n"
        "открой приложение и посмотри на наши товары",
        reply_markup=keyboard.as_markup()
    )
