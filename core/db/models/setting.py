from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class SettingModel(Base):
    __tablename__ = "settings"

    key: Mapped[str] = mapped_column(
        String(256), nullable=False, autoincrement=False, primary_key=True
    )
    value: Mapped[str] = mapped_column(Text, nullable=False)
