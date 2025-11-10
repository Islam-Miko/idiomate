from sqlalchemy import Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class IdiomModel(Base):
    __tablename__ = "idioms"

    id: Mapped[int] = mapped_column(
        Integer, autoincrement=True, primary_key=True
    )
    text: Mapped[str] = mapped_column(Text, nullable=False)
