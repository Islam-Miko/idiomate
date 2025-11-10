import json
import logging

from aiogram import Bot
from aiogram.types import BotCommandScopeChat
from sqlalchemy.ext.asyncio import AsyncSession

from agent.tools import get_tool
from bot.constants import ADMIN_COMMANDS
from bot.exceptions import HasActiveQuizError
from bot.schemas import QuizModelSchema
from core.db.session import SessionFactory
from core.repository.idiom_repository import IdiomModel, IdiomRepository
from core.repository.quiz_repository import QuizModel, QuizRepository
from core.settings import get_settings

logger = logging.getLogger(__name__)


class StartupService:
    @classmethod
    async def set_admin_commands(self, bot: Bot) -> None:
        admins = [get_settings().ADMIN_ID]
        for chat_id in admins:
            await bot.delete_my_commands(
                scope=BotCommandScopeChat(chat_id=chat_id)
            )
            await bot.set_my_commands(
                ADMIN_COMMANDS, scope=BotCommandScopeChat(chat_id=chat_id)
            )
            logger.info(f"Set admin commands for chats: {chat_id}")


class AdminService:
    @classmethod
    async def save_file(cls, file_id: str, bot: Bot):
        file_info = await bot.get_file(file_id)
        downloaded_file = await bot.download_file(file_info.file_path)
        file_content = downloaded_file.read().decode("utf-8")

        async with SessionFactory() as session:
            repo = IdiomRepository(session)
            for line in file_content.splitlines():
                if clean_line := line.strip():
                    repo.add(IdiomModel(text=clean_line))
            await session.commit()


class IdiomService:
    @classmethod
    async def init_idiomification(cls, chat_id: int) -> QuizModelSchema:
        async with SessionFactory() as session:
            repo = QuizRepository(session)
            quiz = await repo.get_active_quiz(chat_id)
            if quiz:
                raise HasActiveQuizError()

            repo = IdiomRepository(session)
            questions = await repo.get_random_idioms(10)

        question_for_prompt = "\n".join(
            [f"{i}) {text.text}" for i, text in enumerate(questions, start=1)]
        )
        tool = await get_tool()
        test_questions = await tool.run({"input_data": question_for_prompt})

        quiz = QuizModel(
            user_id=chat_id,
            questions=json.dumps(test_questions.get("result")),
        )

        async with SessionFactory() as session:
            session: AsyncSession
            repo = QuizRepository(session)
            repo.add(quiz)
            await session.flush()
            await session.commit()

        return QuizModelSchema.model_validate(quiz)

    @classmethod
    async def process_answer(
        cls,
        quiz_id: int,
        is_correct: int,
    ) -> QuizModelSchema:
        async with SessionFactory() as session:
            repo = QuizRepository(session)
            quiz = await repo.get_by_id(quiz_id)
            if is_correct:
                quiz.correct_answers += 1
            quiz.current_question += 1
            repo.add(quiz)
            await session.flush([quiz])
            await session.commit()
            return QuizModelSchema.model_construct(**quiz.to_dict())

    @classmethod
    async def close_quiz(self, quiz_id: int) -> None:
        async with SessionFactory() as session:
            repo = QuizRepository(session)
            quiz = await repo.get_by_id(quiz_id)
            quiz.is_active = False
            repo.add(quiz)
            await session.commit()
