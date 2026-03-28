from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class ErrorLog(Base):
    """
    Stores a student's debugging events over time.

    This table is intentionally simple at first:
    - you can later add relationships (e.g., to a User table),
      session IDs, assignment/course metadata, etc.
    """

    __tablename__ = "error_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # In many student projects, "user_id" can just be an ID from your frontend auth.
    user_id: Mapped[str] = mapped_column(String(128), index=True)

    language: Mapped[str] = mapped_column(String(32), index=True)  # python/java/c
    error_type: Mapped[str] = mapped_column(String(128), index=True)
    concept: Mapped[str] = mapped_column(String(128), index=True)

    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Use database time (func.now()) so it works even if app server time differs.
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True,
    )

