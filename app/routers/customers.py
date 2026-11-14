"""Customer management route skeleton."""

from fastapi import APIRouter


router = APIRouter(prefix="/api/customers", tags=["customers"])


@router.get("")
def customers_index() -> dict[str, str]:
    """Expose the customer module readiness state."""

    return {"module": "customers", "status": "ready"}
