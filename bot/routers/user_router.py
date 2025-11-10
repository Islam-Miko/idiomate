import json
import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from bot.buttons import create_quiz_options_button
from bot.callback_data import QuizCallbackData
from bot.exceptions import HasActiveQuizError
from bot.services import IdiomService
from bot.views import create_final_result_view

logger = logging.getLogger(__name__)
router = Router(name=__name__)


class QuizState(StatesGroup):
    quiz = State()


@router.message(Command("idomify"))
async def start_idomification(
    message: Message,
):
    logger.debug(f"Starting idiomification for chat_id: {message.chat.id}")
    try:
        quiz = await IdiomService.init_idiomification(chat_id=message.chat.id)
    except HasActiveQuizError:
        await message.answer("You have active quiz!")
        return

    questions = json.loads(quiz.questions)
    logger.debug(questions)
    question = questions[quiz.current_question]
    logger.debug(f"question: {type(question)}")
    keyboard = create_quiz_options_button(
        quiz_id=quiz.id,
        question=quiz.current_question,
        quiz_options=question["options"],
    )
    await message.answer(
        "Let's start the idiomification quiz! Here's your first question:"
    )
    await message.answer(question["q"], reply_markup=keyboard)


@router.callback_query(QuizCallbackData.filter())
async def list_groups_for_student_create(
    callback: CallbackQuery,
    callback_data: QuizCallbackData,
):
    await callback.answer()
    logger.debug(f"Received callback data: {callback_data}")
    quiz = await IdiomService.process_answer(
        callback_data.quiz_id,
        callback_data.is_correct,
    )

    questions = json.loads(quiz.questions)
    if quiz.current_question < len(questions):
        question = questions[quiz.current_question]
        keyboard = create_quiz_options_button(
            quiz_id=quiz.id,
            question=quiz.current_question,
            quiz_options=question["options"],
        )
        await callback.message.edit_text(
            question["q"],
            reply_markup=keyboard,
        )
    else:
        text = create_final_result_view(questions, quiz.correct_answers)
        await IdiomService.close_quiz(callback_data.quiz_id)
        await callback.message.edit_text(text, reply_markup=None)


@router.message(Command("start"))
async def start_command(
    message: Message,
):
    await message.answer(
        "Welcome to the Idiomate Bot! Use /idomify to start an idiom quiz."
    )
