from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import ErrorLog
from backend.schemas import LogErrorResponse, ErrorLogCreate
from backend.services import explain_error_ai

router = APIRouter(tags=["error-logging"])


@router.post(
    "/log-error",
    response_model=LogErrorResponse,
    status_code=status.HTTP_201_CREATED,
)
def log_error(payload: ErrorLogCreate, db: Session = Depends(get_db)) -> dict:
    """
    Save an error event into the database.
    """
    try:
        row = ErrorLog(
            user_id=payload.user_id,
            language=payload.language,
            error_type=payload.error_type,
            concept=payload.concept,
            error_message=payload.error_message,
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        teaching = explain_error_ai(row.error_message or "")
        return {
            "logged": row,
            "explanation": {
                "simple_explanation": teaching["simple_explanation"],
                "suggested_fix": teaching["suggested_fix"],
            },
        }
    except Exception as exc:
        # Keep error handling beginner-friendly: return a clean API error.
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to log error",
        ) from exc

