from abc import ABC, abstractmethod
from typing import Any

from agent.main import client
from core.settings import get_settings

settings = get_settings()


class BaseAgentModel(ABC):
    @abstractmethod
    async def chat(self, messages: list[str]) -> Any:
        pass


class OpenAI35AgentModel(BaseAgentModel):
    async def chat(self, messages: list[dict]) -> Any:
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=150,
            temperature=0,
        )
        return response


class OpenAI4AgentModel(BaseAgentModel):
    async def chat(self, messages: list[dict]) -> Any:
        response = await client.chat.completions.create(
            model="gpt-4.1-nano",
            messages=messages,
            temperature=0,
        )
        return response


def get_model(model_name: str | None = None) -> BaseAgentModel:
    if model_name is None:
        model_name = settings.MODEL

    if model_name == "gpt-3.5-turbo":
        return OpenAI35AgentModel()
    elif model_name == "gpt-4.1-nano":
        return OpenAI4AgentModel()
    else:
        raise ValueError(f"Unsupported model name: {model_name}")
