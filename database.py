"""SQLite engine, session factory, and database initialization entry point."""

from collections.abc import Generator

from pathlib import Path

from sqlalchemy import create_engine, event, inspect
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from models import Base


PROJECT_DIR = Path(__file__).resolve().parent
DATABASE_PATH = PROJECT_DIR / "customer.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH.as_posix()}"

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


@event.listens_for(Engine, "connect")
def enable_sqlite_foreign_keys(dbapi_connection, _connection_record) -> None:
    """Enable SQLite foreign-key enforcement for every connection."""

    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def init_db() -> list[str]:
    """Create all model tables and return their names."""

    Base.metadata.create_all(bind=engine)
    return sorted(inspect(engine).get_table_names())


def get_db() -> Generator[Session, None, None]:
    """Provide one SQLAlchemy session per FastAPI request."""

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


if __name__ == "__main__":
    table_names = init_db()
    print(f"Database created: {DATABASE_PATH}")
    print(f"Tables created ({len(table_names)}): {', '.join(table_names)}")
