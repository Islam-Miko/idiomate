from aiogram import Bot

from core.settings import get_settings

bot = Bot(
    token=get_settings().BOT_TOKEN,
)
