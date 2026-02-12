import logging

from aiogram import Bot

from src.tracking.application.protocols import INotifier

logger = logging.getLogger(__name__)


class TelegramNotifier(INotifier):
    def __init__(self, bot: Bot):
        self.bot = bot

    async def notify(self, user_id: str, message: str):
        try:
            await self.bot.send_message(chat_id=user_id, text=message)
        except Exception as e:
            logger.error(f"Failed to send notification to {user_id}: {e}")
