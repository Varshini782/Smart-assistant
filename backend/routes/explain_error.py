from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from schemas import ExplainErrorRequest, ExplainErrorSingleResponse
from services.multi_explainer import explain_error_multi

router = APIRouter(tags=["multi-explainer"])

ALLOWED_LEVELS = frozenset({"beginner", "intermediate", "advanced"})


@router.post(
    "/explain-error",
    response_model=ExplainErrorSingleResponse,
    responses={
        400: {
            "description": "Invalid explanation level",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Invalid level. Choose beginner, intermediate, or advanced."
                    }
                }
            },
        }
    },
)
def explain_error(payload: ExplainErrorRequest) -> ExplainErrorSingleResponse | JSONResponse:
    """
    Return one explanation at the depth chosen by ``level`` (beginner, intermediate, or advanced).

    Calls ``explain_error_multi`` internally, then returns only the selected field.
    """
    result = explain_error_multi(code=payload.code, error_message=payload.error_message)
    level = payload.level.lower()

    if level not in ALLOWED_LEVELS:
        return JSONResponse(
            status_code=400,
            content={
                "error": "Invalid level. Choose beginner, intermediate, or advanced."
            },
        )

    explanation = result.get(level, "Explanation not available")
    title = f"{level.capitalize()} Explanation"

    return ExplainErrorSingleResponse(level=level, title=title, explanation=explanation)
