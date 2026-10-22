from typing import Generator
from sqlalchemy import create_engine, event, inspect, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session
from app.config import settings
from app.models.base import Base


def create_db_engine(db_url: str = settings.DATABASE_URL) -> Engine:
    """Create a SQLAlchemy engine configured for PostgreSQL or SQLite."""
    if db_url.startswith("sqlite"):
        engine = create_engine(
            db_url,
            connect_args={"check_same_thread": False},
            echo=settings.DEBUG,
        )

        # Enable foreign key constraint enforcement in SQLite
        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

        return engine
    else:
        return create_engine(
            db_url,
            pool_pre_ping=True,
            echo=settings.DEBUG,
        )


engine = create_db_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency yielding database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _ensure_incremental_columns(target_engine: Engine) -> None:
    """Ensure columns added in migration 0003 exist on pre-existing databases."""
    inspector = inspect(target_engine)
    table_names = set(inspector.get_table_names())
    binary_type = "BYTEA" if target_engine.dialect.name == "postgresql" else "BLOB"

    with target_engine.begin() as conn:
        if "generated_documents" in table_names:
            doc_cols = {c["name"] for c in inspector.get_columns("generated_documents")}
            if "verification_status" not in doc_cols:
                conn.execute(
                    text(
                        "ALTER TABLE generated_documents "
                        "ADD COLUMN verification_status VARCHAR(50) NOT NULL DEFAULT 'unverified'"
                    )
                )
            if "file_bytes" not in doc_cols:
                conn.execute(
                    text(
                        f"ALTER TABLE generated_documents ADD COLUMN file_bytes {binary_type}"
                    )
                )

        if "job_assessments" in table_names:
            assess_cols = {c["name"] for c in inspector.get_columns("job_assessments")}
            if "evaluation_mode" not in assess_cols:
                conn.execute(
                    text(
                        "ALTER TABLE job_assessments "
                        "ADD COLUMN evaluation_mode VARCHAR(50) NOT NULL DEFAULT 'ai'"
                    )
                )


def init_db() -> None:
    """Initialize database tables directly and apply incremental column migrations."""
    Base.metadata.create_all(bind=engine)
    _ensure_incremental_columns(engine)
