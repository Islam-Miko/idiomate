from typing import Protocol, abstractmethod

from src.tracking.domain.entities import Tracking, User


class ILocationRepository(Protocol):
    @abstractmethod
    def add(self, tracking: Tracking) -> Tracking:
        pass

    @abstractmethod
    async def commit(self) -> None:
        pass

    @abstractmethod
    async def get_last_tracking(self, user_id: str) -> Tracking | None:
        pass

    @abstractmethod
    async def get_locations(self, user_id: str) -> list[Tracking]:
        pass


class IUserRepository(Protocol):
    @abstractmethod
    async def get_by_user_id(self, user_id: str) -> User | None:
        """Get user by Telegram user_id"""
        pass

    @abstractmethod
    async def create(self, user: User) -> User:
        """Create a new user"""
        pass

    @abstractmethod
    async def commit(self) -> None:
        pass
