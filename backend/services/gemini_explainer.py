from __future__ import annotations

import os
from typing import TypedDict

from google import genai


class ExplainErrorAIDict(TypedDict):
    """Structured return from explain_error_ai (always this shape)."""

    simple_explanation: str
    suggested_fix: str


def explain_error_ai(error_message: str) -> ExplainErrorAIDict:
    """
    Explain an error using Gemini and return beginner-friendly guidance.

    Always returns:
        {"simple_explanation": "...", "suggested_fix": "..."}
    """
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return {
            "simple_explanation": "API key not found",
            "suggested_fix": "Set GEMINI_API_KEY environment variable",
        }

    cleaned_error = (error_message or "").strip()
    if not cleaned_error:
        return {
            "simple_explanation": "No error message was provided to explain.",
            "suggested_fix": "Send the actual compiler/runtime error message for a precise explanation.",
        }

    prompt = f"""
You are a helpful programming tutor.

Explain this error in simple language and give a fix.

Error: {cleaned_error}

Format:
Explanation:
Fix:
"""

    try:
        # Client picks up GEMINI_API_KEY from the environment.
        client = genai.Client()
        response = client.models.generate_content(
            # Use a currently supported Gemini model.
            model="gemini-2.5-flash",
            contents=prompt,
        )
        text = response.text if hasattr(response, "text") else ""
        text = (text or "").strip()

        explanation = ""
        fix = ""

        if "Explanation:" in text and "Fix:" in text:
            parts = text.split("Fix:")
            explanation = parts[0].replace("Explanation:", "").strip()
            fix = parts[1].strip()
        else:
            explanation = text.strip()
            fix = "Review the error and check syntax or logic."

        return {
            "simple_explanation": explanation,
            "suggested_fix": fix,
        }
    except Exception as e:
        print("Gemini Error:", e)
        return {
            "simple_explanation": "AI explanation failed",
            "suggested_fix": "Check API key, internet, or Gemini setup",
        }
