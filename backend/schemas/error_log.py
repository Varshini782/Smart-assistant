from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


Language = Literal["python", "java", "c"]


class ErrorLogCreate(BaseModel):
    """
    Request body for logging an error event.

    Keep this minimal and stable: you can always add optional fields later.
    """

    user_id: str = Field(min_length=1, max_length=128, examples=["student_123"])
    language: Language = Field(examples=["python"])
    error_type: str = Field(min_length=1, max_length=128, examples=["SyntaxError"])
    concept: str = Field(min_length=1, max_length=128, examples=["Indentation"])
    error_message: str = Field(
        max_length=10_000,
        examples=["IndentationError: expected an indented block"],
    )


class ErrorLogOut(BaseModel):
    """
    Response model for a logged error event.
    """

    id: int
    user_id: str
    language: str
    error_type: str
    concept: str
    error_message: str | None
    timestamp: datetime

    class Config:
        from_attributes = True


class ExplainErrorOut(BaseModel):
    simple_explanation: str
    suggested_fix: str


class ErrorLogResponse(BaseModel):
    """
    Public response model for an ErrorLog record.
    """

    id: int
    user_id: str
    language: str
    error_type: str
    concept: str
    error_message: str | None
    timestamp: datetime

    class Config:
        from_attributes = True


class UserInsightsResponse(BaseModel):
    """
    Personalized learning analytics derived from a user's history.
    """

    most_common_errors: list[str]
    weak_concepts: list[str]
    total_errors: int
    recommendation: str


class ExplainErrorRequest(BaseModel):
    """
    Request body for the multi-layer explanation endpoint.

    ``level`` selects which depth of explanation to return (only one is returned).
    """

    code: str = Field(default="")
    error_message: str = Field(default="")
    level: str = Field(
        ...,
        min_length=1,
        description='One of: "beginner", "intermediate", "advanced"',
        examples=["beginner"],
    )


class MultiLayerExplanationResponse(BaseModel):
    beginner: str
    intermediate: str
    advanced: str


class ExplainErrorSingleResponse(BaseModel):
    """
    Single-level explanation chosen by the client.
    """

    level: str
    title: str
    explanation: str


class LogErrorResponse(BaseModel):
    """
    Response for POST /log-error.

    Includes the saved DB row + teaching-friendly explanation and fix.
    """

    logged: ErrorLogOut
    explanation: ExplainErrorOut


class RecommendationsResponse(BaseModel):
    """
    Personalized learning suggestions for debugging, tied to an error type and user history.
    """

    debugging_tips: list[str]
    concepts_to_revise: list[str]
    practice_suggestions: list[str]

