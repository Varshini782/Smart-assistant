from __future__ import annotations

from collections import Counter
from datetime import date, datetime, timedelta, timezone

from sqlalchemy.orm import Session

from models import ErrorLog
from schemas.dashboard import DashboardResponse


def _log_calendar_day(ts: datetime) -> date:
    """Normalize stored timestamp to a UTC calendar date for bucketing."""
    if ts.tzinfo is None:
        return ts.date()
    return ts.astimezone(timezone.utc).date()


def get_dashboard(db: Session, user_id: str) -> DashboardResponse:
    """
    Build dashboard metrics for charting: seven-day buckets, top errors, and topics.

    ``weekly_errors`` and ``progress`` always contain seven integers (UTC days, oldest first).
    ``progress`` is the cumulative sum of ``weekly_errors`` over that window.
    With no logs, counts are zero and top lists are empty.
    """
    uid = (user_id or "").strip()
    today_utc = datetime.now(timezone.utc).date()
    day_keys = [today_utc - timedelta(days=6 - i) for i in range(7)]

    if not uid:
        return DashboardResponse(
            weekly_errors=[0] * 7,
            top_errors=[],
            weak_topics=[],
            progress=[0] * 7,
        )

    logs = db.query(ErrorLog).filter(ErrorLog.user_id == uid).all()
    if not logs:
        return DashboardResponse(
            weekly_errors=[0] * 7,
            top_errors=[],
            weak_topics=[],
            progress=[0] * 7,
        )

    per_day: Counter[date] = Counter()
    for log in logs:
        if log.timestamp is None:
            continue
        per_day[_log_calendar_day(log.timestamp)] += 1

    weekly_errors = [per_day.get(d, 0) for d in day_keys]

    err_counter = Counter(
        str(log.error_type).strip() for log in logs if log.error_type and str(log.error_type).strip()
    )
    topic_counter = Counter(
        str(log.concept).strip() for log in logs if log.concept and str(log.concept).strip()
    )

    top_errors = [name for name, _ in err_counter.most_common(3)]
    weak_topics = [name for name, _ in topic_counter.most_common(3)]

    running = 0
    progress: list[int] = []
    for c in weekly_errors:
        running += c
        progress.append(running)

    return DashboardResponse(
        weekly_errors=weekly_errors,
        top_errors=top_errors,
        weak_topics=weak_topics,
        progress=progress,
    )
