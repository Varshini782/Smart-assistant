from __future__ import annotations

from pydantic import BaseModel, Field


class DailyChallengeResponse(BaseModel):
    id: int
    code: str
    bug: str


class SubmitSolutionRequest(BaseModel):
    user_id: str = Field(min_length=1, max_length=128)
    code: str = Field(min_length=1, max_length=50_000)


class SubmitSolutionResponse(BaseModel):
    correct: bool
    feedback: str


class StreakResponse(BaseModel):
    current_streak: int
