from datetime import datetime

from pydantic import BaseModel


class UpdateLocationDTO(BaseModel):
    user_id: str
    lat: float
    lon: float
    recorded_at: datetime


class CreateUserDTO(BaseModel):
    user_id: str
    username: str
    link: str | None = None
