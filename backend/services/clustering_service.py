from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any

from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer


def _infer_common_mistake(errors: list[str]) -> str:
    """
    Produce a simple human-readable pattern summary.
    """
    if not errors:
        return "Not enough data yet. Log more errors to discover patterns."

    text = " ".join(errors).lower()
    if "indexerror" in text:
        return "List indexing issue"
    if "typeerror" in text:
        return "Data type mismatch"
    if "syntaxerror" in text or "indentationerror" in text:
        return "Syntax/indentation issue"
    return "General debugging pattern detected. Review recurring traceback lines."


def cluster_errors(error_list: list[str], n_clusters: int = 3) -> dict[int, list[str]]:
    """
    Group error messages by semantic similarity using TF-IDF + KMeans.
    """
    cleaned = [e.strip() for e in error_list if e and e.strip()]
    if not cleaned:
        return {}

    if len(cleaned) < 3:
        return {0: cleaned}

    try:
        vectorizer = TfidfVectorizer(stop_words="english")
        vectors = vectorizer.fit_transform(cleaned)

        safe_clusters = max(1, min(n_clusters, len(cleaned)))
        model = KMeans(n_clusters=safe_clusters, random_state=42, n_init=10)
        labels = model.fit_predict(vectors)

        grouped: dict[int, list[str]] = defaultdict(list)
        for label, msg in zip(labels, cleaned):
            grouped[int(label)].append(msg)
        return dict(grouped)
    except Exception:
        # Safety fallback: if ML fails, return one bucket.
        return {0: cleaned}


def find_similar_errors(input_error: str, error_list: list[str]) -> dict[str, Any]:
    """
    Find errors most related to the input error and summarize likely mistake.
    """
    seed = (input_error or "").strip()
    historical = [e.strip() for e in error_list if e and e.strip()]

    if not seed:
        return {
            "similar_errors": historical[:5],
            "common_mistake": _infer_common_mistake(historical),
        }

    if not historical:
        return {
            "similar_errors": [],
            "common_mistake": "No past errors found yet for clustering.",
        }

    # For very small sets, clustering is noisy. Return a simple basic list.
    if len(historical) < 3:
        small = historical[:5]
        if seed not in small:
            small = [seed] + small
        return {
            "similar_errors": small,
            "common_mistake": _infer_common_mistake(small),
        }

    try:
        all_errors = historical + [seed]
        vectorizer = TfidfVectorizer(stop_words="english")
        vectors = vectorizer.fit_transform(all_errors)

        safe_clusters = max(2, min(3, len(all_errors)))
        model = KMeans(n_clusters=safe_clusters, random_state=42, n_init=10)
        labels = model.fit_predict(vectors)

        input_label = int(labels[-1])
        similar = [
            msg
            for idx, msg in enumerate(all_errors[:-1])
            if int(labels[idx]) == input_label
        ]

        # Keep top frequent first when duplicates exist in history.
        freq = Counter(similar)
        ranked = [msg for msg, _ in freq.most_common(10)]

        return {
            "similar_errors": ranked,
            "common_mistake": _infer_common_mistake(ranked or [seed]),
        }
    except Exception:
        # If clustering fails, degrade gracefully.
        fallback = historical[:5]
        return {
            "similar_errors": fallback,
            "common_mistake": _infer_common_mistake(fallback or [seed]),
        }

