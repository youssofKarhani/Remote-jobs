import os
import sys
import uuid
from pathlib import Path
from typing import Generator
import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session

# Add backend dir to sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.models.base import Base
from app.models.user import User
from app.models.profile import CandidateProfile
from app.models.preference import CandidatePreference
from app.models.evidence import (
    ExperienceRecord,
    EvidenceItem,
    Skill,
    Project,
    Certification,
    EducationRecord,
)
from app.models.job import Company, JobSource, Job, JobSourceRecord


from sqlalchemy.pool import StaticPool


@pytest.fixture(scope="function")
def db_engine():
    """Create an in-memory SQLite engine with foreign key enforcement enabled and StaticPool."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()



@pytest.fixture(scope="function")
def db_session(db_engine) -> Generator[Session, None, None]:
    """Provide a transactional SQLAlchemy session for testing."""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def sample_user(db_session: Session) -> User:
    """Create and persist a sample User fixture."""
    from app.core.security import get_password_hash
    user = User(
        email="test.engineer@example.com",
        hashed_password=get_password_hash("password123"),
        full_name="Alex Morgan",
        is_active=True,
        is_superuser=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(sample_user: User) -> dict:
    """Provide valid JWT bearer authentication headers for sample_user."""
    from app.core.security import create_access_token
    token = create_access_token(subject=sample_user.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def client(db_session: Session) -> Generator:
    """FastAPI TestClient with overridden get_db dependency."""
    from fastapi.testclient import TestClient
    from app.main import app
    from app.database import get_db

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

