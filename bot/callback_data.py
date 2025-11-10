from aiogram.filters.callback_data import CallbackData


class QuizCallbackData(CallbackData, prefix="quiz"):
    question: int
    is_correct: bool
    quiz_id: int
