from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Integer,
    SmallInteger,
    Text,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class QuizModel(Base):
    __tablename__ = "quizes"

    id: Mapped[int] = mapped_column(
        Integer, autoincrement=True, primary_key=True
    )
    current_question: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=0
    )
    correct_answers: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=0
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(), default=datetime.now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(), default=datetime.now, onupdate=datetime.now
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger, index=True, nullable=False
    )
    questions: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default=text("false")
    )
