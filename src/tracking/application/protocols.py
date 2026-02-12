from typing import Protocol, abstractmethod


class INotifier(Protocol):
    @abstractmethod
    async def notify(self, user_id: str, message: str) -> None:
        """Send a notification to the user"""
        pass


class IGeoService(Protocol):
    @abstractmethod
    async def get_address(self, lat: float, lon: float) -> str:
        pass
