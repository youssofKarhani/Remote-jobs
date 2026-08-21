"""Integration tests for Authentication endpoints and tenant security."""

import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import create_access_token, get_password_hash
from app.models.user import User


def test_register_user_success(client: TestClient, db_session: Session):
    """Test registering a new candidate user."""
    payload = {
        "email": "new.candidate@example.com",
        "password": "SecurePassword123!",
        "full_name": "Jane Candidate",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "new.candidate@example.com"
    assert data["full_name"] == "Jane Candidate"
    assert data["is_active"] is True
    assert "id" in data


def test_register_duplicate_email_rejected(client: TestClient, sample_user: User):
    """Test that registering with an existing email returns 400 Bad Request."""
    payload = {
        "email": sample_user.email,
        "password": "AnotherPassword123!",
        "full_name": "Duplicate User",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_login_oauth2_form_success(client: TestClient, sample_user: User):
    """Test OAuth2 form-urlencoded token login."""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": sample_user.email, "password": "password123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_json_success(client: TestClient, sample_user: User):
    """Test JSON payload login."""
    response = client.post(
        "/api/v1/auth/login/json",
        json={"email": sample_user.email, "password": "password123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_password(client: TestClient, sample_user: User):
    """Test login with incorrect password returns 401 Unauthorized."""
    response = client.post(
        "/api/v1/auth/login/json",
        json={"email": sample_user.email, "password": "wrong_password"},
    )
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]


def test_get_current_user_me(client: TestClient, sample_user: User, auth_headers: dict):
    """Test fetching authenticated user profile via /api/v1/auth/me."""
    response = client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == sample_user.email
    assert data["full_name"] == sample_user.full_name


def test_get_me_unauthorized_without_token(client: TestClient):
    """Test that protected endpoints reject requests without a Bearer token."""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_inactive_user_rejected(client: TestClient, db_session: Session):
    """Test that inactive users cannot access protected resources."""
    inactive_user = User(
        email="inactive@example.com",
        hashed_password=get_password_hash("password123"),
        full_name="Inactive User",
        is_active=False,
    )
    db_session.add(inactive_user)
    db_session.commit()

    token = create_access_token(subject=inactive_user.id)
    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403
    assert "inactive" in response.json()["detail"]
