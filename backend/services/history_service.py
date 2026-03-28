from __future__ import annotations

from sqlalchemy.orm import Session

from backend.models import ErrorLog


def get_user_history(db: Session, user_id: str, limit: int = 50) -> list[ErrorLog]:
    """
    Return a user's recent error logs (latest first).

    Args:
        db: SQLAlchemy session.
        user_id: The learner identifier.
        limit: Maximum number of records to return.
    """
    safe_limit = max(1, min(limit, 200))
    return (
        db.query(ErrorLog)
        .filter(ErrorLog.user_id == user_id)
        .order_by(ErrorLog.timestamp.desc())
        .limit(safe_limit)
        .all()
    )

