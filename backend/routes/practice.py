from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.schemas.practice import (
    DailyChallengeResponse,
    StreakResponse,
    SubmitSolutionRequest,
    SubmitSolutionResponse,
)
from backend.services.practice_service import (
    get_daily_challenge,
    get_streak,
    submit_solution,
)

router = APIRouter(tags=["practice"])


@router.get("/daily-challenge", response_model=DailyChallengeResponse)
def read_daily_challenge() -> DailyChallengeResponse:
    """Return the rotated daily debugging snippet (same for everyone on a given calendar day)."""
    c = get_daily_challenge()
    return DailyChallengeResponse(
        id=int(c["id"]),
        code=str(c["code"]),
        bug=str(c["bug"]),
    )


@router.post("/submit-solution", response_model=SubmitSolutionResponse)
def post_submit_solution(
    payload: SubmitSolutionRequest,
    db: Session = Depends(get_db),
) -> SubmitSolutionResponse:
    """
    Check the learner's fix against today's challenge; on success, refresh their streak.
    """
    correct, feedback = submit_solution(db=db, user_id=payload.user_id, code=payload.code)
    return SubmitSolutionResponse(correct=correct, feedback=feedback)


@router.get("/streak", response_model=StreakResponse)
def read_streak(
    user_id: str = Query(..., min_length=1, max_length=128),
    db: Session = Depends(get_db),
) -> StreakResponse:
    """Current consecutive-day practice streak for the user (0 if never recorded)."""
    return StreakResponse(current_streak=get_streak(db=db, user_id=user_id))
