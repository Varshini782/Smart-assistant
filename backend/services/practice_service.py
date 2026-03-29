from __future__ import annotations

import ast
import re
from collections.abc import Callable
from datetime import date, timedelta

from sqlalchemy.orm import Session

from models import Streak

DAILY_CHALLENGES: list[dict[str, str | int]] = [
    {
        "id": 1,
        "code": "my_list = [1, 2, 3]\nprint(my_list[5])",
        "bug": "IndexError",
    },
    {
        "id": 2,
        "code": 'label = "Total: "\nprint(label + 10)',
        "bug": "TypeError",
    },
    {
        "id": 3,
        "code": "print(undefined_name)",
        "bug": "NameError",
    },
    {
        "id": 4,
        "code": 'if True\n    print("ok")',
        "bug": "SyntaxError",
    },
    {
        "id": 5,
        "code": "items = []\nprint(items[0])",
        "bug": "IndexError",
    },
    {
        "id": 6,
        "code": "value = 42\nprint(len(value))",
        "bug": "TypeError",
    },
    {
        "id": 7,
        "code": "x = 10\ny = \"5\"\nprint(x + y)",
        "bug": "TypeError",
    },
]


def _challenge_index_for_date(d: date) -> int:
    """Stable daily rotation over the static challenge list."""
    return d.toordinal() % len(DAILY_CHALLENGES)


def get_daily_challenge() -> dict[str, str | int]:
    """
    Return the challenge for the current calendar day (local date).
    """
    return dict(DAILY_CHALLENGES[_challenge_index_for_date(date.today())])


def _syntax_feedback(code: str) -> str | None:
    """Return a user-facing message if ``code`` is not valid Python."""
    try:
        ast.parse(code)
        return None
    except SyntaxError as exc:
        return f"Syntax issue near line {exc.lineno or '?'}: {exc.msg}. Fix structure before re-running logic checks."


def _check_c1_index_list(code: str) -> tuple[bool, str]:
    if re.search(r"\[\s*5\s*\]", code):
        return False, "Index 5 is out of range for a 3-item list. Use 0–2 or another safe pattern."
    if "print" not in code:
        return False, "Add a print so you can see a valid element from the list."
    return True, "Good job! You fixed the indexing issue."


def _check_c2_str_plus_int(code: str) -> tuple[bool, str]:
    if re.search(r"\+\s*10\b", code):
        if "str(10)" not in code and "f\"" not in code and "f'" not in code:
            return (
                False,
                "You are still adding an int to a str. Use str(10), an f-string, or similar.",
            )
    if "print" not in code:
        return False, "Use print so the combined value is visible."
    return True, "Nice—you handled the string/number mix correctly."


def _check_c3_name_error(code: str) -> tuple[bool, str]:
    if re.search(r"\bundefined_name\b", code):
        if not re.search(r"\bundefined_name\s*=", code):
            return False, "Define `undefined_name` before printing it, or print a variable that exists."
    if "print" not in code:
        return False, "Include a print statement."
    return True, "Great—you resolved the name error."


def _check_c4_syntax_challenge(code: str) -> tuple[bool, str]:
    if not re.search(r"if\s+True\s*:", code):
        return False, "The `if` line still needs a colon before the indented block."
    return True, "Good—valid `if` syntax with a colon."


def _check_c5_empty_list(code: str) -> tuple[bool, str]:
    if re.search(r"items\[\s*0\s*\]", code):
        has_guard = bool(
            re.search(r"len\s*\(\s*items\s*\)", code)
            or re.search(r"items\.append", code)
            or re.search(r"if\s+items", code)
        )
        if not has_guard:
            return (
                False,
                "Printing `items[0]` on an empty list still crashes. Guard with len/items or add data first.",
            )
    if "print" not in code:
        return False, "Keep a print to show your safe result."
    return True, "Well done—you avoided indexing an empty list unsafely."


def _check_c6_len_int(code: str) -> tuple[bool, str]:
    if re.search(r"len\s*\(\s*value\s*\)", code):
        return False, "`len()` does not apply to integers. Remove it or use a string/list instead."
    if "print" not in code:
        return False, "Use print to display the outcome."
    return True, "Correct—no invalid len() on an int."


def _check_c7_mixed_add(code: str) -> tuple[bool, str]:
    compact = re.sub(r"\s+", "", code)
    if "x+y" in compact or "y+x" in compact:
        has_fix = bool(
            re.search(r"str\s*\(\s*x\s*\)", code)
            or re.search(r"str\s*\(\s*y\s*\)", code)
            or re.search(r"int\s*\(\s*x\s*\)", code)
            or re.search(r"int\s*\(\s*y\s*\)", code)
            or "f\"" in code
            or "f'" in code
        )
        if not has_fix:
            return False, "Still mixing int and str with `+`. Convert with str()/int() or use an f-string."
    if "print" not in code:
        return False, "Include print to show the result."
    return True, "Good fix for the type mismatch."


_CHALLENGE_VALIDATORS: dict[int, Callable[[str], tuple[bool, str]]] = {
    1: _check_c1_index_list,
    2: _check_c2_str_plus_int,
    3: _check_c3_name_error,
    4: _check_c4_syntax_challenge,
    5: _check_c5_empty_list,
    6: _check_c6_len_int,
    7: _check_c7_mixed_add,
}


def submit_solution(db: Session, user_id: str, code: str) -> tuple[bool, str]:
    """
    Validate submitted code against today's challenge using simple static rules.

    Returns:
        (correct, feedback) — feedback is mentor-style text either way.
    """
    uid = (user_id or "").strip()
    if not uid:
        return False, "user_id is required."

    challenge = get_daily_challenge()
    cid = int(challenge["id"])
    body = (code or "").strip()
    if not body:
        return False, "Submit non-empty code."

    syn = _syntax_feedback(body)
    if syn:
        return False, syn

    validator = _CHALLENGE_VALIDATORS.get(cid)
    if validator is None:
        return False, "Unknown challenge configuration."

    ok, msg = validator(body)
    if ok:
        update_streak(db, uid)
    else:
        msg = msg or "Not quite—compare your fix to the bug type and try again."
    return ok, msg


def _get_or_create_streak(db: Session, user_id: str) -> Streak:
    row = db.query(Streak).filter(Streak.user_id == user_id).one_or_none()
    if row is None:
        row = Streak(user_id=user_id, current_streak=0, last_active_date=None)
        db.add(row)
        db.flush()
    return row


def update_streak(db: Session, user_id: str) -> Streak:
    """
    Increment or reset streak based on calendar-day gaps (local date).

    Call only when the learner successfully completed today's challenge.
    """
    uid = (user_id or "").strip()
    row = _get_or_create_streak(db, uid)
    today = date.today()
    last = row.last_active_date

    if last == today:
        db.commit()
        db.refresh(row)
        return row

    if last is None:
        row.current_streak = 1
    elif last == today - timedelta(days=1):
        row.current_streak += 1
    else:
        row.current_streak = 1

    row.last_active_date = today
    db.commit()
    db.refresh(row)
    return row


def get_streak(db: Session, user_id: str) -> int:
    """Return stored streak for the user, or 0 when no row exists yet."""
    uid = (user_id or "").strip()
    if not uid:
        return 0
    row = db.query(Streak).filter(Streak.user_id == uid).one_or_none()
    if row is None:
        return 0
    return int(row.current_streak)
