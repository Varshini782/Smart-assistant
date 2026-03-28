from __future__ import annotations

import json
import os
import re
from typing import Any
from urllib.parse import quote_plus

from google import genai

from backend.schemas.learning import LearningModeResponse

CONCEPT_LINKS: dict[str, str] = {
    "Lists": "https://www.w3schools.com/python/python_lists.asp",
    "Indexing": "https://www.geeksforgeeks.org/python-list/",
    "Data Types": "https://www.w3schools.com/python/python_datatypes.asp",
    "Loops": "https://www.w3schools.com/python/python_for_loops.asp",
}

_DEFAULT_SEARCH = "https://www.google.com/search?q=programming+concept"


def _build_learning_prompt(code: str, error_message: str) -> str:
    """
    Build the fixed tutor prompt that asks for JSON-only output.
    """
    return f"""You are an expert programming tutor.

Analyze the following code and error.

Code:
{code}

Error:
{error_message}

Provide structured learning guidance:

1. Quick Fix:
Give a short and direct fix.

2. Step-by-Step Debugging:
Provide 3–5 simple steps to debug this error.

3. Why Error Occurred:
Explain root cause clearly.

4. Concept to Learn:
Suggest what topic the student should study.

Return ONLY valid JSON:

{{
  "quick_fix": "...",
  "step_by_step_debugging": ["...", "..."],
  "why_error_occurred": "...",
  "concept_to_learn": "..."
}}
"""


def _extract_json_text(raw: str) -> str:
    """
    Strip markdown fences and isolate a JSON object from model output.
    """
    text = (raw or "").strip()
    if not text:
        return ""

    fenced = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
    if fenced:
        return fenced.group(1).strip()

    brace = re.search(r"\{[\s\S]*\}", text)
    if brace:
        return brace.group(0).strip()

    return text


def _safe_parse_learning_json(text: str) -> dict[str, Any] | None:
    """
    Parse JSON from cleaned text; return None if parsing fails or structure is unusable.
    """
    cleaned = _extract_json_text(text)
    if not cleaned:
        return None
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        return None
    if not isinstance(data, dict):
        return None
    return data


def _normalize_steps(value: Any) -> list[str]:
    """Coerce step list from JSON into a clean list of strings."""
    if value is None:
        return []
    if isinstance(value, str):
        lines = [ln.strip() for ln in re.split(r"[\n;]", value) if ln.strip()]
        out: list[str] = []
        for ln in lines:
            ln = re.sub(r"^\d+[\).\s]+", "", ln).strip()
            if ln:
                out.append(ln)
        return out[:10]
    if isinstance(value, list):
        return [str(x).strip() for x in value if str(x).strip()][:10]
    return []


def _concept_link_for(concept: str) -> str:
    """
    Map ``concept_to_learn`` to a known resource URL or a search fallback.
    """
    c = (concept or "").strip()
    if not c:
        return _DEFAULT_SEARCH
    if c in CONCEPT_LINKS:
        return CONCEPT_LINKS[c]
    c_lower = c.lower()
    for key, url in CONCEPT_LINKS.items():
        if key.lower() == c_lower:
            return url
    return f"https://www.google.com/search?q={quote_plus(c + ' programming tutorial')}"


def _learning_dict_to_response(data: dict[str, Any]) -> LearningModeResponse:
    """Build a response model, filling gaps when keys are missing."""
    quick = str(data.get("quick_fix", "") or "").strip()
    why = str(data.get("why_error_occurred", "") or "").strip()
    concept = str(data.get("concept_to_learn", "") or "").strip()
    steps = _normalize_steps(data.get("step_by_step_debugging"))

    if not quick:
        quick = "Review the traceback and align types, bounds, and names with what the runtime expects."
    if not steps:
        steps = [
            "Re-read the error line and the line above it.",
            "Print or log the values involved right before the failure.",
            "Reduce the program to the smallest snippet that still fails.",
            "Check documentation for the operation that raised the error.",
        ]
    if not why:
        why = "The runtime reported a condition your code did not satisfy (types, bounds, syntax, or state)."
    if not concept:
        concept = "Debugging workflow and reading error messages"

    return LearningModeResponse(
        quick_fix=quick,
        step_by_step_debugging=steps,
        why_error_occurred=why,
        concept_to_learn=concept,
        concept_link=_concept_link_for(concept),
    )


def _fallback_response(reason: str) -> LearningModeResponse:
    """
    Deterministic tutor-style content when the model or parsing is unavailable.
    """
    return LearningModeResponse(
        quick_fix=(
            "Compare the failing line to the error text, then change one variable or "
            "expression at a time until the error changes."
        ),
        step_by_step_debugging=[
            "Locate the file and line number from the traceback.",
            "Write down what you believe each name and value is at that line.",
            "Form a hypothesis (wrong type, wrong index, typo, etc.) and test a tiny change.",
            "If stuck, comment out lines until the error moves, then narrow the cause.",
            f"(System note: {reason})",
        ],
        why_error_occurred=(
            "Without a successful model response, the exact root cause could not be inferred. "
            "Most errors come from a mismatch between what your code assumes and what the "
            "language or runtime allows."
        ),
        concept_to_learn="Reading tracebacks and minimal reproduction",
        concept_link=_concept_link_for("Data Types"),
    )


def learning_mode_explain(code: str, error_message: str) -> LearningModeResponse:
    """
    Call Gemini with a structured prompt and return parsed learning guidance.

    Handles missing API keys, network failures, and malformed JSON with safe fallbacks.
    """
    code_clean = (code or "").strip()
    err_clean = (error_message or "").strip()
    if not code_clean or not err_clean:
        raise ValueError("Both `code` and `error_message` must be non-empty.")

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return _fallback_response("GEMINI_API_KEY is not set.")

    prompt = _build_learning_prompt(code_clean, err_clean)

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt,
        )
        raw_text = response.text if hasattr(response, "text") else ""
        raw_text = (raw_text or "").strip()
        if not raw_text:
            return _fallback_response("The model returned an empty response.")

        parsed = _safe_parse_learning_json(raw_text)
        if not parsed:
            return _fallback_response("Could not parse JSON from the model output.")

        return _learning_dict_to_response(parsed)
    except Exception as exc:
        return _fallback_response(f"Gemini request failed: {exc}")
