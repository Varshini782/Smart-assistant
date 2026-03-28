from __future__ import annotations

from collections import Counter

from sqlalchemy.orm import Session

from backend.models import ErrorLog
from backend.schemas import UserInsightsResponse


def get_user_insights(db: Session, user_id: str) -> UserInsightsResponse:
    """
    Analyze a user's debugging history and return personalized insights.

    Advanced logic:
    - If one error type is > 40% of all errors, mark as major weakness.
    - If one concept repeats frequently, mark as needs revision.
    """
    logs = db.query(ErrorLog).filter(ErrorLog.user_id == user_id).all()
    total_errors = len(logs)

    if total_errors == 0:
        return UserInsightsResponse(
            most_common_errors=[],
            weak_concepts=[],
            total_errors=0,
            recommendation="No history yet. Start by logging a few debugging attempts.",
        )

    error_counter = Counter(log.error_type for log in logs if log.error_type)
    concept_counter = Counter(log.concept for log in logs if log.concept)

    most_common_errors = [item for item, _ in error_counter.most_common(3)]
    weak_concepts = [item for item, _ in concept_counter.most_common(3)]

    recommendation_parts: list[str] = []

    if most_common_errors:
        top_error, top_error_count = error_counter.most_common(1)[0]
        if (top_error_count / total_errors) > 0.4:
            recommendation_parts.append(
                f"Major weakness detected: {top_error} appears frequently."
            )

    if weak_concepts:
        top_concept, top_concept_count = concept_counter.most_common(1)[0]
        # A simple threshold: repeated at least 3 times or >40% overall.
        if top_concept_count >= 3 or (top_concept_count / total_errors) > 0.4:
            recommendation_parts.append(f"{top_concept} needs revision.")

    if weak_concepts:
        recommendation_parts.append(
            f"Focus on {', '.join(weak_concepts)} concepts."
        )
    elif most_common_errors:
        recommendation_parts.append(
            f"Practice handling {', '.join(most_common_errors)} errors."
        )

    recommendation = " ".join(recommendation_parts).strip()
    if not recommendation:
        recommendation = (
            "Good progress. Keep practicing mixed debugging problems to improve speed and accuracy."
        )

    return UserInsightsResponse(
        most_common_errors=most_common_errors,
        weak_concepts=weak_concepts,
        total_errors=total_errors,
        recommendation=recommendation,
    )

