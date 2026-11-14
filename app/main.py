"""FastAPI entry point for Customer Manager."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.routers import auth, customers, dashboard, health
from database import init_db


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Create only missing tables while preserving the existing database."""

    init_db()
    yield


app = FastAPI(
    title="Customer Manager",
    description="고객·주문·상품·직원 데이터를 관리하는 웹 서비스",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(customers.router)
app.include_router(dashboard.router)


@app.get("/", tags=["service"])
def read_root() -> dict[str, str]:
    """Return basic service metadata."""

    return {
        "service": "Customer Manager",
        "status": "ok",
        "docs": "/docs",
    }
