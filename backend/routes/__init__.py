from .health import router as health_router
from .error_logs import router as error_logs_router
from .user_history import router as user_history_router
from .user_insights import router as user_insights_router
from .clustering import router as clustering_router
from .explain_error import router as explain_error_router
from .recommendations import router as recommendations_router
from .process_input import router as process_input_router
from .dashboard import router as dashboard_router
from .practice import router as practice_router
from .learning_mode import router as learning_mode_router

__all__ = [
    "health_router",
    "error_logs_router",
    "user_history_router",
    "user_insights_router",
    "clustering_router",
    "explain_error_router",
    "recommendations_router",
    "process_input_router",
    "dashboard_router",
    "practice_router",
    "learning_mode_router",
]

