from __future__ import annotations

from pydantic import BaseModel, Field


class DashboardResponse(BaseModel):
    """
    Chart-oriented analytics for the last seven calendar days (UTC) plus top weak spots.
    """

    weekly_errors: list[int] = Field(
        ...,
        description="Error counts per day, oldest day first (7 values).",
    )
    top_errors: list[str] = Field(default_factory=list)
    weak_topics: list[str] = Field(default_factory=list)
    progress: list[int] = Field(
        ...,
        description="Cumulative error count within the same 7-day window, oldest day first.",
    )
