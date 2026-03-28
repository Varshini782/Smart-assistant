from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ErrorExplanation:
    simple_explanation: str
    suggested_fix: str


def explain_error(
    *,
    language: str,
    error_type: str,
    error_message: str | None = None,
    concept: str | None = None,
) -> ErrorExplanation:
    """
    Return a simple (student-friendly) explanation + a suggested fix.

    This is a deterministic baseline. Later, you can:
    - enrich this mapping by concept
    - add language-specific patterns (line numbers, tokens, etc.)
    - fall back to an AI model when no match is found
    """

    lang = (language or "").strip().lower()
    et = (error_type or "").strip()
    msg = (error_message or "").strip()
    concept_norm = (concept or "").strip().lower()

    # Python common errors
    python_map: dict[str, ErrorExplanation] = {
        "SyntaxError": ErrorExplanation(
            simple_explanation=(
                "Python couldn't understand your code because it breaks the language rules "
                "(for example: missing a colon, unmatched parentheses, or a typo in a keyword)."
            ),
            suggested_fix=(
                "Look at the line mentioned in the error message and check punctuation: "
                "add missing `:` after `if/for/while/def/class`, and ensure parentheses/brackets/quotes match."
            ),
        ),
        "IndentationError": ErrorExplanation(
            simple_explanation=(
                "Python uses indentation (spaces) to know which lines belong inside blocks like `if` or `for`. "
                "This error means the indentation is missing or inconsistent."
            ),
            suggested_fix=(
                "Indent the block consistently (commonly 4 spaces). Avoid mixing tabs and spaces."
            ),
        ),
        "NameError": ErrorExplanation(
            simple_explanation=(
                "You used a variable or function name that Python doesn't recognize (it wasn't defined yet)."
            ),
            suggested_fix=(
                "Check spelling, define the variable before using it, and ensure you're in the correct scope."
            ),
        ),
        "TypeError": ErrorExplanation(
            simple_explanation=(
                "You used a value with the wrong type for an operation "
                "(for example adding a number to a string)."
            ),
            suggested_fix=(
                "Print or inspect the types (e.g., `type(x)`) and convert as needed "
                "(`int(...)`, `str(...)`, `float(...)`) or adjust the logic."
            ),
        ),
        "ZeroDivisionError": ErrorExplanation(
            simple_explanation="Your code tried to divide by zero, which is not allowed.",
            suggested_fix="Add a check before dividing (e.g., `if denominator != 0:`) or handle the zero case.",
        ),
        "IndexError": ErrorExplanation(
            simple_explanation=(
                "You tried to access a list/string index that doesn't exist (out of range)."
            ),
            suggested_fix=(
                "Check the length (`len(...)`) and ensure indices go from 0 to len-1. "
                "Fix loop boundaries and off-by-one errors."
            ),
        ),
        "KeyError": ErrorExplanation(
            simple_explanation=(
                "You tried to access a dictionary key that isn't present."
            ),
            suggested_fix=(
                "Use `dict.get(key)` with a default, check `if key in dict`, or make sure the key exists."
            ),
        ),
        "AttributeError": ErrorExplanation(
            simple_explanation=(
                "You tried to use an attribute or method that the object doesn't have."
            ),
            suggested_fix=(
                "Print the object and its type, verify the attribute name, and ensure the object is the expected type."
            ),
        ),
    }

    # Java common errors (simplified)
    java_map: dict[str, ErrorExplanation] = {
        "NullPointerException": ErrorExplanation(
            simple_explanation=(
                "Your code tried to use an object reference that is `null`."
            ),
            suggested_fix=(
                "Initialize the object before using it and add null checks "
                "(e.g., `if (obj != null) { ... }`)."
            ),
        ),
        "ArrayIndexOutOfBoundsException": ErrorExplanation(
            simple_explanation=(
                "You tried to access an array index that doesn't exist (out of range)."
            ),
            suggested_fix=(
                "Ensure indices stay between 0 and `array.length - 1`. Fix loop conditions."
            ),
        ),
    }

    # C common errors (simplified / heuristic)
    c_map: dict[str, ErrorExplanation] = {
        "Segmentation fault": ErrorExplanation(
            simple_explanation=(
                "Your program tried to access memory it shouldn't. This often happens with invalid pointers "
                "or array out-of-bounds access."
            ),
            suggested_fix=(
                "Check pointer initialization, array bounds, and make sure you allocate enough memory. "
                "If using `malloc`, verify it didn't return NULL."
            ),
        ),
    }

    # A few message-based fallbacks (when error_type is vague or inconsistent).
    msg_lower = msg.lower()
    if lang == "python" and "indentationerror" in msg_lower:
        return python_map["IndentationError"]
    if lang == "python" and "syntaxerror" in msg_lower:
        return python_map["SyntaxError"]
    if lang == "python" and "typeerror" in msg_lower:
        return python_map["TypeError"]
    if lang == "python" and ("indexerror" in msg_lower or "list index out of range" in msg_lower):
        return python_map["IndexError"]
    if lang == "python" and ("keyerror" in msg_lower or "key not found" in msg_lower):
        return python_map["KeyError"]
    if lang == "java" and "nullpointerexception" in msg_lower:
        return java_map["NullPointerException"]
    if lang == "c" and ("segmentation fault" in msg_lower or "segfault" in msg_lower):
        return c_map["Segmentation fault"]

    if lang == "python" and et in python_map:
        return python_map[et]
    if lang == "java" and et in java_map:
        return java_map[et]
    if lang == "c" and et in c_map:
        return c_map[et]

    # Concept-based tiny fallback
    if concept_norm in {"indentation", "loops", "variables", "types"}:
        return ErrorExplanation(
            simple_explanation=(
                f"This error is related to the concept: {concept}. Something in that area is inconsistent or missing."
            ),
            suggested_fix=(
                "Re-check the relevant lines, simplify the code into smaller steps, and print intermediate values "
                "to see where it goes wrong."
            ),
        )

    # Generic fallback
    return ErrorExplanation(
        simple_explanation=(
            "An error occurred, but I don't have a specific built-in explanation for this one yet."
        ),
        suggested_fix=(
            "Read the error message carefully, locate the referenced line, and try simplifying the code. "
            "If you share the full traceback/error output, we can pinpoint the exact cause."
        ),
    )

