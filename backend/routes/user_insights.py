from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.schemas import UserInsightsResponse
from backend.services.insights_service import get_user_insights

router = APIRouter(tags=["user-insights"])


@router.get("/user-insights/{user_id}", response_model=UserInsightsResponse)
def read_user_insights(user_id: str, db: Session = Depends(get_db)) -> UserInsightsResponse:
    """
    Return learning analytics and recommendations for a user.
    """
    return get_user_insights(db=db, user_id=user_id)

