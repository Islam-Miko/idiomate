from io import BytesIO
from typing import Protocol, abstractmethod

from src.tracking.domain.entities import Tracking


class INotifier(Protocol):
    @abstractmethod
    async def notify(self, user_id: str, message: str) -> None:
        """Send a notification to the user"""
        pass


class IGeoService(Protocol):
    @abstractmethod
    async def get_address(self, lat: float, lon: float) -> str:
        pass


class IMapGenerator(Protocol):
    @abstractmethod
    def generate_map(self, trackings: list[Tracking]) -> BytesIO:
        pass
