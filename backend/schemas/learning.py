from __future__ import annotations

from pydantic import BaseModel, Field


class LearningModeRequest(BaseModel):
    """Code snippet plus the error output to teach against."""

    code: str = Field(min_length=1, max_length=50_000)
    error_message: str = Field(min_length=1, max_length=10_000)


class LearningModeResponse(BaseModel):
    """Structured tutor-style guidance for debugging and concept study."""

    quick_fix: str
    step_by_step_debugging: list[str]
    why_error_occurred: str
    concept_to_learn: str
    concept_link: str
