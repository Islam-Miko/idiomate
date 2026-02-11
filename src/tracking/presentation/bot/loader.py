import logging

from aiogram import Bot, Dispatcher

from src.infrastructure.database.setup import DatabaseHelper
from src.tracking.presentation.bot.handlers import router as tracking_router
from src.tracking.presentation.bot.middlewares import DependencyInjectionMiddleware

logger = logging.getLogger(__name__)


# Функция принимает зависимости, а не создает их!
async def start_bot(token: str, db_handler: DatabaseHelper):
    logger.info("Initializing bot...")

    bot = Bot(token=token)
    dp = Dispatcher()

    # Регистрация middleware, роутеров
    dp.message.middleware(DependencyInjectionMiddleware(db_handler))
    dp.edited_message.middleware(DependencyInjectionMiddleware(db_handler))
    dp.include_router(tracking_router)

    logger.info("Bot configured, starting polling...")
    await dp.start_polling(bot)
