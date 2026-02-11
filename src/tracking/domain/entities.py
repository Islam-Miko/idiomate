from dataclasses import dataclass
from datetime import datetime
from math import asin, cos, radians, sin, sqrt
from typing import Optional


@dataclass(frozen=True)
class Coordinates:
    latitude: float
    longitude: float

    def distance_to(self, other: "Coordinates") -> float:
        """Считает расстояние в метрах (Haversine formula)"""
        R = 6371000  # Радиус Земли
        d_lat = radians(other.latitude - self.latitude)
        d_lon = radians(other.longitude - self.longitude)

        a = sin(d_lat / 2) ** 2 + cos(radians(self.latitude)) * cos(radians(other.latitude)) * sin(d_lon / 2) ** 2
        c = 2 * asin(sqrt(a))
        return R * c

    def __str__(self):
        return f"Coordinates(latitude={self.latitude}, longitude={self.longitude})"


@dataclass
class Tracking:
    user_id: str
    location: Coordinates
    recorded_at: datetime

    def __str__(self):
        return f"Tracking(location={self.location}, recorded_at={self.recorded_at}, user_id={self.user_id})"


@dataclass
class User:
    user_id: str  # Telegram user id
    username: str
    link: Optional[str] = None

    def __str__(self):
        return f"User(user_id={self.user_id}, username={self.username}, link={self.link})"
