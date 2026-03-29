from __future__ import annotations

from collections import Counter
from copy import deepcopy

from sqlalchemy.orm import Session

from models import ErrorLog
from schemas import RecommendationsResponse

# Rule bundles keyed by normalized error type (lowercase).
_ERROR_RULES: dict[str, dict[str, list[str]]] = {
    "indexerror": {
        "debugging_tips": [
            "Print len(sequence) right before the line that indexes - confirm the index is in range.",
            "Check off-by-one: last valid index is len - 1, and empty sequences cannot be indexed at 0.",
            "If the index comes from user input or a variable, log or assert its value before use.",
        ],
        "concepts_to_revise": [
            "Sequence indexing and slicing",
            "Loops vs direct indexing",
            "Empty collections and guards",
        ],
        "practice_suggestions": [
            "Rewrite a loop that uses range(len(x)) to iterate values safely without raw indices.",
            "Fix three snippets that raise IndexError by adding bounds checks or try/except.",
            "Trace a nested list access (e.g. matrix[i][j]) and validate each dimension first.",
        ],
    },
    "typeerror": {
        "debugging_tips": [
            "Read the full traceback: note which operation failed and the types of both operands.",
            "Use type() or isinstance() at the failing line to confirm what you actually have.",
            "Watch for None where an object was expected, or mixing str with int in arithmetic.",
        ],
        "concepts_to_revise": [
            "Dynamic typing vs runtime type checks",
            "Function arguments and return types",
            "Implicit conversions (strings, numbers, collections)",
        ],
        "practice_suggestions": [
            "Write small functions that validate inputs with clear error messages before use.",
            "Refactor code that concatenates str + int using explicit str() or formatting.",
            "Complete exercises on callables: ensure you invoke functions with (), not pass references by mistake.",
        ],
    },
    "syntaxerror": {
        "debugging_tips": [
            "The caret in the traceback points near the issue - check the previous line for unclosed brackets or quotes.",
            "Balance (), [], {}, and string quotes; use an editor with bracket matching.",
            "Invalid indentation in Python often follows a missing colon after if/for/def.",
        ],
        "concepts_to_revise": [
            "Python indentation and block structure",
            "Colons after compound statements",
            "String literals and escape characters",
        ],
        "practice_suggestions": [
            "Parse a broken file line-by-line and fix one syntax issue at a time.",
            "Use python -m py_compile on small files to catch syntax errors quickly.",
            "Rewrite snippets using only valid statement order (imports, defs, then top-level code).",
        ],
    },
}

_DEFAULT_RULE: dict[str, list[str]] = {
    "debugging_tips": [
        "Reproduce the error with the smallest possible input or test case.",
        "Read the traceback from bottom upward: innermost frame is where the exception originated.",
        "Add temporary prints or a debugger breakpoint at the line before the failure.",
        "Compare your assumptions to actual values (types, lengths, None checks).",
    ],
    "concepts_to_revise": [
        "Reading and interpreting tracebacks",
        "Minimal reproducible examples",
        "Defensive checks and error handling basics",
    ],
    "practice_suggestions": [
        "Log five different errors in this app and review the patterns you see.",
        "Pair each error with one documentation page you read end-to-end.",
        "Time-box debugging: 10 minutes of hypothesis, then narrow with one new fact.",
    ],
}


def _normalize_error_type(error_type: str) -> str:
    """
    Normalize an error type string for dictionary lookup.

    Args:
        error_type: Raw query or stored value (e.g. ``\"IndexError\"``).

    Returns:
        Lowercase, stripped key suitable for ``_ERROR_RULES``.
    """
    return error_type.strip().casefold()


def _bundle_for_error(error_type: str) -> dict[str, list[str]]:
    """
    Return a deep copy of the rule bundle for the given error, or the default bundle.

    Args:
        error_type: Requested error type (may be unknown).

    Returns:
        Mapping with keys ``debugging_tips``, ``concepts_to_revise``, ``practice_suggestions``.
    """
    key = _normalize_error_type(error_type)
    raw = _ERROR_RULES.get(key, _DEFAULT_RULE)
    return deepcopy(raw)


def fetch_user_history(db: Session, user_id: str) -> list[ErrorLog]:
    """
    Load all error logs for a user from the database.

    Args:
        db: SQLAlchemy session.
        user_id: Learner identifier.

    Returns:
        List of ``ErrorLog`` rows (possibly empty). Empty list is safe for callers.
    """
    if not (user_id or "").strip():
        return []
    return db.query(ErrorLog).filter(ErrorLog.user_id == user_id.strip()).all()


def analyze_history(logs: list[ErrorLog]) -> tuple[Counter[str], Counter[str]]:
    """
    Count most frequent error types and concepts in history.

    Args:
        logs: Error log rows (may be empty).

    Returns:
        Tuple of (error_type_counter, concept_counter). Empty counters if no usable fields.
    """
    error_counter: Counter[str] = Counter()
    concept_counter: Counter[str] = Counter()
    for log in logs:
        if log.error_type and str(log.error_type).strip():
            error_counter[str(log.error_type).strip()] += 1
        if log.concept and str(log.concept).strip():
            concept_counter[str(log.concept).strip()] += 1
    return error_counter, concept_counter


def _merge_unique_preserve_order(*sequences: list[str]) -> list[str]:
    """
    Concatenate string lists and drop duplicates while preserving first-seen order.

    Args:
        *sequences: One or more lists of strings.

    Returns:
        Deduplicated list in stable order.
    """
    seen: set[str] = set()
    out: list[str] = []
    for seq in sequences:
        for item in seq:
            s = str(item).strip()
            if not s or s in seen:
                continue
            seen.add(s)
            out.append(s)
    return out


def _history_personalization_lines(
    error_counter: Counter[str],
    concept_counter: Counter[str],
    current_key: str,
) -> tuple[list[str], list[str], list[str]]:
    """
    Build extra tips, concepts, and practice lines from history frequency.

    Args:
        error_counter: Counts of error types for the user.
        concept_counter: Counts of concepts for the user.
        current_key: Normalized error type for the current request (lowercase).

    Returns:
        Three lists: extra debugging tips, extra concepts, extra practice suggestions.
    """
    extra_tips: list[str] = []
    extra_concepts: list[str] = []
    extra_practice: list[str] = []

    if concept_counter:
        top_concepts = [c for c, _ in concept_counter.most_common(5)]
        extra_concepts.extend(
            f"History: revisit '{c}' - it appears often in your logs." for c in top_concepts[:3]
        )

    if error_counter:
        for err_name, count in error_counter.most_common(3):
            if count < 2:
                continue
            ek = _normalize_error_type(err_name)
            if ek == current_key:
                continue
            extra_tips.append(
                f"You've hit {err_name} multiple times - compare this session with those patterns."
            )
            if ek in _ERROR_RULES:
                sample = _ERROR_RULES[ek]["practice_suggestions"][:1]
                extra_practice.extend(sample)

    return extra_tips, extra_concepts, extra_practice


def build_recommendations(db: Session, user_id: str, error_type: str) -> RecommendationsResponse:
    """
    Produce personalized debugging tips, concepts, and practice ideas.

    Combines rule-based guidance for the requested ``error_type`` with weak spots
    inferred from the user's stored history. No history yields rule-only (or default)
    content - still useful and fast.

    Args:
        db: SQLAlchemy session.
        user_id: Learner identifier.
        error_type: Focus error type (e.g. ``IndexError``); unknown types use defaults.

    Returns:
        ``RecommendationsResponse`` with three list fields, all safe when empty.
    """
    safe_user = (user_id or "").strip()
    safe_error = (error_type or "").strip() or "Unknown"
    bundle = _bundle_for_error(safe_error)
    current_key = _normalize_error_type(safe_error)

    logs = fetch_user_history(db, safe_user) if safe_user else []
    if not logs:
        return RecommendationsResponse(
            debugging_tips=list(bundle["debugging_tips"]),
            concepts_to_revise=list(bundle["concepts_to_revise"]),
            practice_suggestions=list(bundle["practice_suggestions"]),
        )

    err_c, conc_c = analyze_history(logs)
    tip_extras, concept_extras, practice_extras = _history_personalization_lines(
        err_c, conc_c, current_key
    )

    weak_from_history = [c for c, _ in conc_c.most_common(5)]

    tips = _merge_unique_preserve_order(bundle["debugging_tips"], tip_extras)
    concepts = _merge_unique_preserve_order(
        bundle["concepts_to_revise"],
        weak_from_history,
        concept_extras,
    )
    practice = _merge_unique_preserve_order(bundle["practice_suggestions"], practice_extras)

    return RecommendationsResponse(
        debugging_tips=tips,
        concepts_to_revise=concepts,
        practice_suggestions=practice,
    )
