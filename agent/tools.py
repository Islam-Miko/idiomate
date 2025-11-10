# flake8: noqa: E501
import json
import logging
from abc import ABC, abstractmethod

from agent.models import get_model
from core.db.session import SessionFactory
from core.repository.setting_repository import SettingRepository

logger = logging.getLogger(__name__)


class ABCTool(ABC):
    """Abstract base class for tools used by AI agents."""

    @classmethod
    @abstractmethod
    async def run(cls, input_data: dict) -> dict:
        """Executes the tool's main functionality."""
        pass


class GenerateEnTestTool(ABCTool):
    @staticmethod
    def get_prompt() -> str:
        prompt = """
        You are an intelligent English tutor who creates realistic vocabulary and idiom quizzes for pre-intermediate and intermediate learners.

        The user provides a list of target words or idioms (between ----- lines).
        Your task is to generate a **quiz in JSON format**, containing **exactly one question per provided word or idiom**, in the same order as they appear in the list.

        ### Your goals:
        - Create **natural, story-like, or conversational situations** that clearly express when the target word or idiom would be used.
        - Make learners understand the *meaning in context*, not just grammar.
        - Use short but emotionally expressive sentences — e.g., surprise, regret, excitement, humor.

        ### Rules for each question:
        1. Write a **short scenario (1–3 sentences)** that sounds like a real situation or dialogue, where the blank ("____") fits naturally with the target word or idiom.
        Example: “After running for an hour, Mike said, ‘Let’s ____ and rest for a bit.’”
        2. The blank must **clearly imply** the meaning of the correct answer.
        3. Provide **4 options**:
        - The **first option** is always the **correct answer** (the target word or idiom).
        - The remaining **three options** should:
            - Be believable distractors (similar tone or grammatical structure).
            - Fit grammatically but not semantically.
            - NOT come from the provided list.
        4. Vary tone, context, and emotion between questions (friendly chat, work, family, travel, etc.).
        5. Avoid generic patterns like “He said ____.” — each sentence should sound natural and alive.
        6. Output **only valid JSON**, no comments, markdown, or explanations.
        ### Output format:
        [
        {{
            "q": "<natural sentence or situation with a blank>",
            "options": ["<correct_answer>", "<distractor1>", "<distractor2>", "<distractor3>"]
        }},
        ...
        ]
        -----
        {}
        -----
        """
        return prompt

    @classmethod
    async def run(cls, input_data: dict) -> dict:
        prompt = cls.get_prompt()
        messages = [
            {
                "role": "system",
                "content": prompt.format(input_data["input_data"]),
            },
        ]
        logger.debug(f"Messages for AddLessonTool: {messages}")

        model = get_model()
        logger.debug(f"Using model: {model}")
        response = await model.chat(messages=messages)

        context = response.choices[0].message.content
        import pprint

        pprint.pprint(context)
        context = json.loads(context)
        logger.debug(f"Extracted context for AddLessonTool: {context}")

        return {"result": context}


class GenerateRuTestTool(GenerateEnTestTool):
    @staticmethod
    def get_prompt() -> str:
        prompt = """
        Ты — умный преподаватель английского языка, который создает тесты по словарю и идиомам для студентов уровня pre-intermediate и intermediate.
        Пользователь присылает список слов или идиом (между линиями -----).
        Твоя задача — создать тест в формате JSON, где для каждого слова ты пишешь короткое описание или подсказку, которая помогает понять значение этого слова, не используя само слово.

        Правила:
        Для каждого слова или идиомы нужно создать один вопрос.
        Вопрос — это описание или объяснение, написанное естественным языком.
        Описание должно быть понятным, коротким (1-3 предложения).
        Можно описывать значение, ситуацию, эмоцию или типичное использование.
        Пример:
        Какое слово используется, когда вы прощаетесь или желаете кому-то не переживать слишком сильно?
        Ответы:
        Всего 4 варианта.
        Первый вариант — всегда правильный (то самое слово из списка).
        Остальные 3 варианта — правдоподобные, но неправильные.
        Они должны быть похожи по стилю или типу слова (фраза, идиома, глагол и т. п.),
        но не совпадать по смыслу.
        Формат вывода — строго JSON, без комментариев и без markdown.

        [
            {{
                "q": "Какое выражение говорят, когда прощаются с другом, но хотят звучать спокойно и доброжелательно?",
                "options": ["take it easy", "go ahead", "hold on", "come on"]
            }},
        ]
        -----
        {}
        -----
        """
        return prompt


async def get_tool() -> ABCTool:
    async with SessionFactory() as session:
        mode = await SettingRepository(session).get_by_key("MODE")

    mode = json.loads(mode.value)
    mode = mode.get("lang")
    if mode == "RU":
        return GenerateRuTestTool
    else:
        return GenerateEnTestTool
