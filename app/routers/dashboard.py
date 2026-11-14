"""Sales dashboard route skeleton."""

from fastapi import APIRouter


router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("")
def dashboard_index() -> dict[str, str]:
    """Expose the dashboard module readiness state."""

    return {"module": "dashboard", "status": "ready"}
