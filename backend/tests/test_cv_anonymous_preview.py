"""Anonymous CV preview: visitors can extract their CV without an account, but nothing is saved."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.evidence import ExperienceRecord, Skill
from app.models.profile import CandidateProfile
from app.routers import cv as cv_router

SAMPLE_CV = """Maria Schmidt
Data Analyst
Hamburg, Germany | maria.schmidt@example.org

WORK EXPERIENCE
Otto Group - Senior Data Analyst (2021 - Present)
- Built Power BI dashboards used by 120 store managers.
- Automated weekly sales reporting in Python, saving 6 hours per week.

SKILLS
SQL, Python, Power BI, Excel, Tableau

EDUCATION
M.Sc. Economics
University of Hamburg

CERTIFICATIONS
Google Data Analytics Certificate
"""


@pytest.fixture(autouse=True)
def _reset_rate_limit():
    cv_router._preview_hits.clear()
    yield
    cv_router._preview_hits.clear()


def test_preview_text_works_without_auth_and_persists_nothing(client: TestClient, db_session: Session):
    res = client.post("/api/v1/cv/preview-text", json={"text": SAMPLE_CV})
    assert res.status_code == 200, res.text
    data = res.json()

    assert data["persisted"] is False
    assert data["counts"]["skills"] >= 3
    assert "Python" in data["preview"]["skills"]
    assert data["counts"]["experiences"] >= 1

    # Name / title / location / contact lines from the CV header are not skills.
    for not_a_skill in ("Maria Schmidt", "Data Analyst", "Hamburg", "maria.schmidt@example.org"):
        assert not_a_skill not in data["preview"]["skills"]

    # Placeholders the pipeline uses for NOT NULL columns must not reach the visitor.
    for cert in data["preview"]["certifications"]:
        assert cert["issuing_organization"] != "Issuing Organization"
    for edu in data["preview"]["education"]:
        assert edu["field_of_study"] != "General"

    assert db_session.query(CandidateProfile).count() == 0
    assert db_session.query(ExperienceRecord).count() == 0
    assert db_session.query(Skill).count() == 0


def test_preview_file_works_without_auth(client: TestClient, db_session: Session):
    files = {"file": ("cv.txt", SAMPLE_CV.encode("utf-8"), "text/plain")}
    res = client.post("/api/v1/cv/preview", files=files)
    assert res.status_code == 200, res.text
    assert res.json()["filename"] == "cv.txt"
    assert db_session.query(CandidateProfile).count() == 0


def test_saving_still_requires_auth(client: TestClient):
    assert client.post("/api/v1/cv/parse-text", json={"text": SAMPLE_CV}).status_code == 401
    files = {"file": ("cv.txt", SAMPLE_CV.encode("utf-8"), "text/plain")}
    assert client.post("/api/v1/cv/upload", files=files).status_code == 401


def test_preview_rejects_too_short_text(client: TestClient):
    res = client.post("/api/v1/cv/preview-text", json={"text": "hello there!"})
    assert res.status_code == 422


def test_preview_is_rate_limited_per_ip(client: TestClient, monkeypatch):
    monkeypatch.setattr(cv_router, "PREVIEW_RATE_LIMIT", 2)
    headers = {"X-Forwarded-For": "203.0.113.7"}
    for _ in range(2):
        assert client.post("/api/v1/cv/preview-text", json={"text": SAMPLE_CV}, headers=headers).status_code == 200
    res = client.post("/api/v1/cv/preview-text", json={"text": SAMPLE_CV}, headers=headers)
    assert res.status_code == 429

    # A different client is unaffected.
    other = {"X-Forwarded-For": "198.51.100.9"}
    assert client.post("/api/v1/cv/preview-text", json={"text": SAMPLE_CV}, headers=other).status_code == 200
