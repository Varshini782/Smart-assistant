from __future__ import annotations

from datetime import date

from sqlalchemy import Date, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Streak(Base):
    """
    Tracks consecutive days the learner completed the daily practice challenge.
    """

    __tablename__ = "streaks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    current_streak: Mapped[int] = mapped_column(Integer, default=0)
    last_active_date: Mapped[date | None] = mapped_column(Date, nullable=True)
