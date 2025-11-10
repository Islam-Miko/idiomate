from sqlalchemy import select

from core.db.models import QuizModel

from .base import BaseRepository


class QuizRepository(BaseRepository[QuizModel]):
    model = QuizModel

    async def get_active_quiz(self, chat_id: int) -> QuizModel:
        result = await self.session.execute(
            select(self.model).where(
                self.model.user_id == chat_id, self.model.is_active
            )
        )
        return result.scalar_one_or_none()
