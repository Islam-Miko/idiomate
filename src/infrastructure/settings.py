from enum import Enum
from functools import cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(str, Enum):
    LOCAL = "LOCAL"
    TESTING = "TESTING"
    STAGING = "STAGING"
    PRODUCTION = "PRODUCTION"

    @property
    def is_debug(self):
        return self in (self.LOCAL, self.STAGING, self.TESTING)

    @property
    def is_testing(self):
        return self == self.TESTING

    @property
    def is_deployed(self) -> bool:
        return self in (self.STAGING, self.PRODUCTION)


class Settings(BaseSettings):
    DATABASE_URL: str
    BOT_TOKEN: str
    ADMIN_ONE: str
    ADMIN_TWO: str
    ENVIRONMENT: Environment = Environment.PRODUCTION
    LOG_LEVEL: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    STRICT_DISTANCE_METERS: float = 50.0
    RELAXED_DISTANCE_METERS: float = 15.0
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@cache
def get_settings() -> Settings:
    return Settings()
