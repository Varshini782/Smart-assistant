from __future__ import annotations

import json
import os
import re
from typing import Any

from google import genai


def _fallback_explanations() -> dict[str, str]:
    return {
        "beginner": "I could not generate an explanation right now. Please try again with a clearer error message.",
        "intermediate": "The AI explanation service is unavailable or returned an invalid format.",
        "advanced": "Retry with full stack trace and surrounding code context to improve explanation quality.",
    }


def _clean_and_parse_json(raw_text: str) -> dict[str, Any] | None:
    """
    Parse model output as JSON, tolerating markdown wrappers.
    """
    text = (raw_text or "").strip()
    if not text:
        return None

    # Remove common fenced blocks: ```json ... ``` or ``` ... ```
    fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, flags=re.IGNORECASE)
    if fence_match:
        text = fence_match.group(1).strip()

    # First attempt: parse whole text.
    try:
        data = json.loads(text)
        return data if isinstance(data, dict) else None
    except Exception:
        pass

    # Second attempt: parse first JSON object in mixed text.
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        candidate = text[start : end + 1]
        try:
            data = json.loads(candidate)
            return data if isinstance(data, dict) else None
        except Exception:
            return None
    return None


def _parse_labeled_response(raw_text: str) -> dict[str, str] | None:
    """
    Parse non-JSON responses like:
    Beginner: ...
    Intermediate: ...
    Advanced: ...
    """
    text = (raw_text or "").strip()
    if not text:
        return None

    pattern = (
        r"Beginner\s*:\s*(?P<beginner>[\s\S]*?)"
        r"Intermediate\s*:\s*(?P<intermediate>[\s\S]*?)"
        r"Advanced\s*:\s*(?P<advanced>[\s\S]*)"
    )
    match = re.search(pattern, text, flags=re.IGNORECASE)
    if not match:
        return None

    beginner = match.group("beginner").strip(" \n\r-*:")
    intermediate = match.group("intermediate").strip(" \n\r-*:")
    advanced = match.group("advanced").strip(" \n\r-*:")
    if not (beginner and intermediate and advanced):
        return None

    return {
        "beginner": beginner,
        "intermediate": intermediate,
        "advanced": advanced,
    }


def explain_error_multi(code: str, error_message: str) -> dict[str, str]:
    """
    Return beginner, intermediate, and advanced explanations for an error.
    """
    cleaned_code = (code or "").strip()
    cleaned_error = (error_message or "").strip()

    if not cleaned_code and not cleaned_error:
        return {
            "beginner": "Please provide code and an error message so I can explain the issue.",
            "intermediate": "No input detected. Submit code plus the related error output.",
            "advanced": "Insufficient context: provide source snippet, runtime/compiler error, and expected behavior.",
        }

    if not os.getenv("GEMINI_API_KEY"):
        return _fallback_explanations()

    prompt = f"""
You are an expert programming tutor.
Analyze the given code and error.
Prefer valid JSON with this exact shape:
{{
  "beginner": "...",
  "intermediate": "...",
  "advanced": "..."
}}
If you cannot output JSON, output this plain text format:
Beginner: ...
Intermediate: ...
Advanced: ...

Rules:
- beginner: simple, non-technical explanation
- intermediate: technical root cause and practical fix path
- advanced: deep reasoning (runtime behavior, edge cases, debugging strategy)
- Keep each field concise but educational

Code:
{cleaned_code if cleaned_code else "<no code provided>"}

Error message:
{cleaned_error if cleaned_error else "<no error message provided>"}
"""

    try:
        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        text = response.text if hasattr(response, "text") else ""
        parsed = _clean_and_parse_json(text)
        if parsed:
            beginner = str(parsed.get("beginner", "")).strip()
            intermediate = str(parsed.get("intermediate", "")).strip()
            advanced = str(parsed.get("advanced", "")).strip()
            if beginner and intermediate and advanced:
                return {
                    "beginner": beginner,
                    "intermediate": intermediate,
                    "advanced": advanced,
                }

        labeled = _parse_labeled_response(text)
        if labeled:
            return labeled

        # Last non-error fallback: still use model text to avoid empty output.
        text = (text or "").strip()
        if text:
            return {
                "beginner": text,
                "intermediate": "Parseable JSON was not returned. This is the raw AI explanation.",
                "advanced": "Ask the model to format output as Beginner/Intermediate/Advanced for more structure.",
            }
        return _fallback_explanations()
    except Exception as e:
        print("Multi explainer Gemini error:", e)
        return _fallback_explanations()

