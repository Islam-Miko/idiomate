from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from bot.bot import bot
from bot.routers.admin_router import router as admin_router
from bot.routers.user_router import router as user_router
from bot.services import StartupService

dp = Dispatcher(storage=MemoryStorage())
dp.include_router(admin_router)
dp.include_router(user_router)


async def main() -> None:
    print("Starting")

    await StartupService.set_admin_commands(bot)

    await dp.start_polling(
        bot, allowed_updates=["message", "edited_message", "callback_query"]
    )
    print("Ending")
