from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check() -> dict:
    """
    Simple endpoint to verify the API is up.
    """
    return {"status": "ok"}

