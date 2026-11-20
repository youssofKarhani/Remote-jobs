"""Password policy, brute-force throttling, and GDPR export/delete."""

import json

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.user import User
from app.routers import auth as auth_router
from app.services.account_service import _user_owned_tables

GOOD_PASSWORD = "correct horse battery"


def _register(client: TestClient, email: str, password: str = GOOD_PASSWORD, ip: str = "203.0.113.10"):
    return client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "full_name": "Test Person"},
        headers={"X-Forwarded-For": ip},
    )


def _login(client: TestClient, email: str, password: str, ip: str = "203.0.113.20"):
    return client.post(
        "/api/v1/auth/login/json",
        json={"email": email, "password": password},
        headers={"X-Forwarded-For": ip},
    )


# --- Password policy -------------------------------------------------------------------

@pytest.mark.parametrize(
    "password",
    ["short-pw", "aaaaaaaaaaaaaaaa", "password1234", "jane.doe-2026-pass"],
)
def test_weak_passwords_rejected(client: TestClient, password: str):
    assert _register(client, "jane.doe@example.com", password).status_code == 422


def test_strong_password_accepted(client: TestClient):
    assert _register(client, "jane.doe@example.com").status_code == 201


# --- Throttling ------------------------------------------------------------------------

def test_account_locked_after_repeated_failures(client: TestClient):
    _register(client, "victim@example.com")
    limit = auth_router.login_account_limiter.limit
    for i in range(limit):
        assert _login(client, "victim@example.com", "wrong", ip=f"198.51.100.{i}").status_code == 401
    # Even the right password is refused while locked, from any IP.
    res = _login(client, "victim@example.com", GOOD_PASSWORD, ip="198.51.100.250")
    assert res.status_code == 429
    assert int(res.headers["Retry-After"]) > 0
    # Other accounts are unaffected.
    _register(client, "bystander@example.com", ip="203.0.113.11")
    assert _login(client, "bystander@example.com", GOOD_PASSWORD).status_code == 200


def test_successful_login_resets_failure_count(client: TestClient):
    _register(client, "forgetful@example.com")
    for _ in range(auth_router.login_account_limiter.limit - 1):
        _login(client, "forgetful@example.com", "wrong")
    assert _login(client, "forgetful@example.com", GOOD_PASSWORD).status_code == 200
    assert _login(client, "forgetful@example.com", "wrong").status_code == 401  # count restarted


def test_ip_limited_across_accounts(client: TestClient, monkeypatch):
    monkeypatch.setattr(auth_router.login_ip_limiter, "limit", 3)
    for i in range(3):
        assert _login(client, f"spray{i}@example.com", "guess", ip="192.0.2.99").status_code == 401
    assert _login(client, "spray9@example.com", "guess", ip="192.0.2.99").status_code == 429


def test_registration_rate_limited_per_ip(client: TestClient, monkeypatch):
    monkeypatch.setattr(auth_router.register_ip_limiter, "limit", 2)
    assert _register(client, "a1@example.com", ip="192.0.2.50").status_code == 201
    assert _register(client, "a2@example.com", ip="192.0.2.50").status_code == 201
    assert _register(client, "a3@example.com", ip="192.0.2.50").status_code == 429


# --- Export ----------------------------------------------------------------------------

def _signed_in_with_cv(client: TestClient, email: str = "owner@example.com") -> dict:
    _register(client, email)
    token = _login(client, email, GOOD_PASSWORD).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    cv = (
        "Sam Example\nData Engineer\n\nEXPERIENCE\nAcme GmbH - Data Engineer (2020 - Present)\n"
        "- Built nightly ETL in Python moving 2 TB per day.\n\nSKILLS\nPython, SQL, Airflow\n"
    )
    assert client.post("/api/v1/cv/parse-text", json={"text": cv}, headers=headers).status_code == 200
    return headers


def test_export_contains_my_data_and_no_secrets(client: TestClient):
    headers = _signed_in_with_cv(client)
    res = client.get("/api/v1/auth/me/export", headers=headers)
    assert res.status_code == 200
    assert "attachment" in res.headers["content-disposition"]
    data = res.json()
    assert data["account"]["email"] == "owner@example.com"
    assert data["data"]["candidate_profiles"], "profile missing from export"
    assert data["data"]["skills"], "skills missing from export"
    assert "hashed_password" not in json.dumps(data)


def test_export_requires_auth(client: TestClient):
    assert client.get("/api/v1/auth/me/export").status_code == 401


def test_export_only_contains_own_data(client: TestClient):
    _signed_in_with_cv(client, "other@example.com")
    headers = _signed_in_with_cv(client, "me@example.com")
    blob = json.dumps(client.get("/api/v1/auth/me/export", headers=headers).json())
    assert "other@example.com" not in blob


# --- Delete ----------------------------------------------------------------------------

def test_delete_requires_correct_password(client: TestClient):
    headers = _signed_in_with_cv(client)
    res = client.request("DELETE", "/api/v1/auth/me", json={"password": "nope"}, headers=headers)
    assert res.status_code == 403
    assert client.get("/api/v1/auth/me", headers=headers).status_code == 200


def test_delete_removes_every_user_row(client: TestClient, db_session: Session):
    keep_headers = _signed_in_with_cv(client, "keeper@example.com")
    headers = _signed_in_with_cv(client, "leaver@example.com")
    leaver_id = db_session.query(User).filter(User.email == "leaver@example.com").one().id

    res = client.request("DELETE", "/api/v1/auth/me", json={"password": GOOD_PASSWORD}, headers=headers)
    assert res.status_code == 204

    db_session.expire_all()
    assert db_session.query(User).filter(User.id == leaver_id).count() == 0
    for table, user_col in _user_owned_tables():
        remaining = db_session.execute(select(func.count()).select_from(table).where(user_col == leaver_id)).scalar()
        assert remaining == 0, f"{table.name} still has rows for the deleted user"

    # The old token no longer works; the other account is untouched.
    assert client.get("/api/v1/auth/me", headers=headers).status_code == 401
    assert client.get("/api/v1/auth/me", headers=keep_headers).status_code == 200
