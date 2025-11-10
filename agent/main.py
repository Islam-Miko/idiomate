from openai import AsyncOpenAI

from core.settings import get_settings

settings = get_settings()


client = AsyncOpenAI(api_key=settings.OPENAPI_TOKEN)
