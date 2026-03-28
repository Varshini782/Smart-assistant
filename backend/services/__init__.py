"""
Business logic lives in services.
Routes should stay thin and just orchestrate request/response.
"""

from .explain import ErrorExplanation, explain_error
from .gemini_explainer import ExplainErrorAIDict, explain_error_ai
from .clustering_service import cluster_errors, find_similar_errors
from .history_service import get_user_history
from .insights_service import get_user_insights
from .multi_explainer import explain_error_multi

__all__ = [
    "ErrorExplanation",
    "explain_error",
    "ExplainErrorAIDict",
    "explain_error_ai",
    "cluster_errors",
    "find_similar_errors",
    "get_user_history",
    "get_user_insights",
    "explain_error_multi",
]

