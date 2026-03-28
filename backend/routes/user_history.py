from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.schemas import ErrorLogResponse
from backend.services.history_service import get_user_history

router = APIRouter(tags=["user-history"])


@router.get("/user-history/{user_id}", response_model=list[ErrorLogResponse])
def read_user_history(user_id: str, db: Session = Depends(get_db)) -> list[ErrorLogResponse]:
    """
    Return the latest error logs for a specific user (up to 50).
    """
    return get_user_history(db=db, user_id=user_id, limit=50)

