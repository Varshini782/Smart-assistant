from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from database import engine
from models import Base
from routes import (
    clustering_router,
    dashboard_router,
    explain_error_router,
    error_logs_router,
    health_router,
    practice_router,
    process_input_router,
    recommendations_router,
    user_history_router,
    user_insights_router,
    learning_mode_router,
)


def create_app() -> FastAPI:
    """
    FastAPI application factory.

    Using a factory makes testing easier and keeps startup logic tidy.
    """
    app = FastAPI(
        title="Smart Debugging Assistant (Backend)",
        version="0.1.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Create DB tables on startup (SQLite-friendly).
    Base.metadata.create_all(bind=engine)

    # Routes
    app.include_router(health_router)
    app.include_router(error_logs_router)
    app.include_router(user_history_router)
    app.include_router(user_insights_router)
    app.include_router(recommendations_router)
    app.include_router(process_input_router)
    app.include_router(dashboard_router)
    app.include_router(practice_router)
    app.include_router(clustering_router)
    app.include_router(explain_error_router)
    app.include_router(learning_mode_router)

    return app


app = create_app()

