from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database import get_db
from schemas import RecommendationsResponse
from services.recommendation_service import build_recommendations

router = APIRouter(tags=["recommendations"])


@router.get("/recommendations", response_model=RecommendationsResponse)
def read_recommendations(
    user_id: str = Query(
        ...,
        min_length=1,
        max_length=128,
        description="Learner identifier used in error logs.",
    ),
    error_type: str = Query(
        ...,
        min_length=1,
        max_length=128,
        description="Focus error type, e.g. IndexError, TypeError, SyntaxError.",
    ),
    db: Session = Depends(get_db),
) -> RecommendationsResponse:
    """
    Return mentor-style tips, concepts to revise, and practice ideas.

    Rule-based guidance is merged with weak spots from the user's stored history when available.
    """
    return build_recommendations(db=db, user_id=user_id, error_type=error_type)
