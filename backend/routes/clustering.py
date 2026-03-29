from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database import get_db
from models import ErrorLog
from services.clustering_service import find_similar_errors

router = APIRouter(tags=["clustering"])


@router.get("/similar-errors")
def get_similar_errors(
    error: str = Query(..., description="Input error message to compare"),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """
    Return similar historical errors and a simple common-mistake insight.
    """
    rows = (
        db.query(ErrorLog.error_message)
        .filter(ErrorLog.error_message.isnot(None))
        .all()
    )
    error_list = [row[0] for row in rows if row and row[0]]

    result = find_similar_errors(input_error=error, error_list=error_list)
    return {
        "input_error": error,
        "similar_errors": result["similar_errors"],
        "common_mistake": result["common_mistake"],
    }

