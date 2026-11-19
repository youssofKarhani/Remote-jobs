"""The old shared demo account is retired: no registration, no login, no use of old tokens."""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import create_access_token, get_password_hash
from app.models.user import User

DEMO_EMAIL = "demo@remotejobs.com"
DEMO_PASSWORD = "DemoPassword123!"  # the password that shipped in the old frontend bundle


def _create_demo_user(db_session: Session) -> User:
    user = User(
        email=DEMO_EMAIL,
        hashed_password=get_password_hash(DEMO_PASSWORD),
        full_name="Demo Candidate",
        is_active=True,
        is_superuser=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def test_demo_account_cannot_register(client: TestClient):
    res = client.post(
        "/api/v1/auth/register",
        json={"email": DEMO_EMAIL, "password": DEMO_PASSWORD, "full_name": "Demo Candidate"},
    )
    assert res.status_code == 400


def test_demo_account_cannot_log_in(client: TestClient, db_session: Session):
    _create_demo_user(db_session)
    res = client.post("/api/v1/auth/login/json", json={"email": DEMO_EMAIL, "password": DEMO_PASSWORD})
    assert res.status_code == 403
    res = client.post("/api/v1/auth/login", data={"username": DEMO_EMAIL, "password": DEMO_PASSWORD})
    assert res.status_code == 403


def test_existing_demo_tokens_are_rejected(client: TestClient, db_session: Session):
    user = _create_demo_user(db_session)
    headers = {"Authorization": f"Bearer {create_access_token(subject=user.id)}"}
    assert client.get("/api/v1/auth/me", headers=headers).status_code == 403
    assert client.get("/api/v1/profile", headers=headers).status_code == 403


def test_regular_accounts_still_work(client: TestClient, auth_headers: dict):
    assert client.get("/api/v1/auth/me", headers=auth_headers).status_code == 200
