"""Authentication route skeleton."""

from fastapi import APIRouter


router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.get("/status")
def auth_status() -> dict[str, str]:
    """Expose the authentication module readiness state."""

    return {"module": "auth", "status": "ready"}
