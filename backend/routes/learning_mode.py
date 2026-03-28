from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from backend.schemas.learning import LearningModeRequest, LearningModeResponse
from backend.services.learning_service import learning_mode_explain

router = APIRouter(tags=["learning-mode"])


@router.post("/learning-mode", response_model=LearningModeResponse)
def post_learning_mode(payload: LearningModeRequest) -> LearningModeResponse:
    """
    Return quick fix, guided steps, root cause, and concept study link for code + error.
    """
    try:
        return learning_mode_explain(
            code=payload.code,
            error_message=payload.error_message,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
