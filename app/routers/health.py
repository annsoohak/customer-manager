"""Service and database health endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from database import get_db


router = APIRouter(tags=["health"])


@router.get("/health")
def health_check(db: Session = Depends(get_db)) -> dict[str, str]:
    """Verify that the API and SQLite connection are available."""

    db.execute(text("SELECT 1"))
    return {"status": "ok", "database": "connected"}
