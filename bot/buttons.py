import random

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.callback_data import QuizCallbackData


def create_quiz_options_button(
    quiz_id: int,
    question: int,
    quiz_options: list[dict],
) -> InlineKeyboardMarkup:
    """
    Creates a dynamic inline keyboard for student list.
    """
    builder = InlineKeyboardBuilder()

    buttons = list()

    for idx, option in enumerate(quiz_options):
        is_correct = idx == 0
        button = InlineKeyboardButton(
            text=option,
            callback_data=QuizCallbackData(
                quiz_id=quiz_id, question=question, is_correct=is_correct
            ).pack(),
        )
        buttons.append(button)
    random.shuffle(buttons)
    builder.add(*buttons)
    builder.adjust(1)
    keyboard = builder.as_markup()
    return keyboard
