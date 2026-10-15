"""FastAPI dependencies shared across the API."""
from __future__ import annotations

from typing import Generator

from sqlalchemy.orm import Session

from app.db.base import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """Yield a request-scoped database session and close it afterwards."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
