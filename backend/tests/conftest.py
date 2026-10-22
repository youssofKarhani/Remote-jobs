import os
import socket
import sys
import uuid
from pathlib import Path
from typing import Generator
import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session

# Defensive guard against infinite hangs on Windows when loopback TCP is blocked in a sandbox:
# CPython's C-level _socket.socketpair() calls accept() on 127.0.0.1 with an infinite timeout.
# Probing loopback with a 0.5s timeout before asyncio starts ensures fast failure instead of hanging.
def _verify_windows_loopback_or_exit() -> None:
    lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    lsock.settimeout(0.5)
    try:
        lsock.bind(("127.0.0.1", 0))
        lsock.listen(1)
        csock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        csock.settimeout(0.5)
        try:
            csock.connect(lsock.getsockname())
            ssock, _ = lsock.accept()
            ssock.close()
        except Exception as exc:
            pytest.exit(
                f"Windows loopback TCP (127.0.0.1) is blocked in this environment ({exc}). "
                "Run pytest with BypassSandbox=True so asyncio socketpair() can connect.",
                returncode=2,
            )
        finally:
            csock.close()
    finally:
        lsock.close()


_verify_windows_loopback_or_exit()

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


@pytest.fixture(autouse=True)
def configure_test_ai(monkeypatch):
    """Ensure tests run lightning fast by default using mock/deterministic heuristic provider."""
    if not os.getenv("TEST_LIVE_AI"):
        from app.integrations.llm_ai_service import ai_service
        monkeypatch.setattr(ai_service, "provider", "mock")

