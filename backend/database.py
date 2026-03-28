from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# SQLite database file stored inside the backend folder.
# For production, you can swap this to Postgres/MySQL without changing model code.
DB_PATH = Path(__file__).resolve().parent / "app.db"
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH.as_posix()}"

# check_same_thread=False is required for SQLite when using FastAPI (multiple threads).
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that yields a DB session.
    Always closes the session after the request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def db_session() -> Generator[Session, None, None]:
    """
    Convenience context manager for scripts/tests.
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

