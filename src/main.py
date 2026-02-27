import asyncio
import logging

from aiohttp import web

from src.infrastructure.database.setup import db_helper
from src.infrastructure.logging import setup_logging
from src.infrastructure.settings import get_settings
from src.tracking.presentation.api.loader import start_web_server
from src.tracking.presentation.bot.loader import start_bot

logger = logging.getLogger(__name__)


async def main():
    settings = get_settings()

    # Setup logging first
    setup_logging(level=settings.LOG_LEVEL, log_file=None)

    logger.info(f"Starting application in {settings.ENVIRONMENT} environment")

    db_helper.setup()
    logger.info("Database helper configured")

    app = web.Application()

    await start_web_server(app, host="127.0.0.1", port=8080)

    await start_bot(
        token=settings.BOT_TOKEN,
        db_handler=db_helper,
    )
    await db_helper.dispose()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Application stopped by user")
        print("Бот остановлен")
