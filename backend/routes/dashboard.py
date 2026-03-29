from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database import get_db
from schemas.dashboard import DashboardResponse
from services.dashboard_service import get_dashboard

router = APIRouter(tags=["dashboard"])


@router.get("/dashboard", response_model=DashboardResponse)
def read_dashboard(
    user_id: str = Query(..., min_length=1, max_length=128),
    db: Session = Depends(get_db),
) -> DashboardResponse:
    """
    Learning analytics for charts: seven-day error counts, cumulative progress, top weaknesses.
    """
    return get_dashboard(db=db, user_id=user_id)
