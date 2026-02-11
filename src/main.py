# src/main.py
import asyncio
import logging

from src.infrastructure.database.setup import db_helper
from src.infrastructure.logging import setup_logging
from src.infrastructure.settings import get_settings
from src.tracking.presentation.bot.loader import start_bot

logger = logging.getLogger(__name__)


async def main():
    settings = get_settings()

    # Setup logging first
    setup_logging(level=settings.LOG_LEVEL, log_file=None)

    logger.info(f"Starting application in {settings.ENVIRONMENT} environment")

    db_helper.setup()
    logger.info("Database helper configured")

    await start_bot(
        token=settings.BOT_TOKEN,
        db_handler=db_helper,
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Application stopped by user")
        print("Бот остановлен")
