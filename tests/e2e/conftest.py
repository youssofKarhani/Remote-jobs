"""Pytest fixtures and test environment configuration for E2E Test Suite.
Provides SQLite in-memory database with foreign keys enabled, SQLAlchemy session lifecycle,
domain object factories, mock authentication, mock AI gateway, and mock Arbeitnow source.
"""

import hashlib
import json
import re
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, Generator, List, Optional, Set

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

# Import canonical models from app
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
from app.models.job import (
    Company,
    JobSource,
    Job,
    JobSourceRecord,
)


# ============================================================================
# Database Engine and Session Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def db_engine() -> Engine:
    """Create an in-memory SQLite engine with PRAGMA foreign_keys enabled."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        echo=False,
    )

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    # Create all tables defined in Base.metadata
    Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture(scope="function")
def db(db_engine: Engine) -> Generator[Session, None, None]:
    """Provide a transactional SQLAlchemy session rolled back after every test."""
    connection = db_engine.connect()
    transaction = connection.begin()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=connection)
    session = SessionLocal()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


# ============================================================================
# Canonical Algorithms & Protocol Implementations for Testing
# ============================================================================

class EvidenceValidationError(ValueError):
    """Raised when an LLM or caller provides invalid or unauthorized evidence IDs."""
    pass


def validate_selected_evidence_ids(
    selected_ids: List[str],
    allowed_ids: Set[str],
    max_bullets: Optional[int] = None,
) -> None:
    """Strict validation rule: selected_ids ⊆ allowed_ids.
    Enforces in code that the LLM has not hallucinated an ID or chosen an unauthorized item.
    """
    if not selected_ids:
        return

    selected_set = set(selected_ids)
    invalid_ids = selected_set - allowed_ids
    if invalid_ids:
        raise EvidenceValidationError(
            f"Validation Failed: The following evidence IDs are invalid or unauthorized: {sorted(list(invalid_ids))}"
        )

    if max_bullets is not None and len(selected_ids) > max_bullets:
        raise EvidenceValidationError(
            f"Validation Failed: Selected {len(selected_ids)} bullets exceeds maximum allowed ({max_bullets})"
        )


def compute_content_hash(url: str, title: str, company: str, location: str) -> str:
    """Computes a deterministic SHA-256 hash for job deduplication.
    1. Primary canonical source: Canonical URL (lowercase stripped).
    2. Fallback / Cross-source: Normalized title + company + location.
    """
    # Clean and sanitize title from gender markers & recruitment fluff
    norm_title = re.sub(r'\(.*?\)|\[.*?\]', '', title).lower().strip()
    norm_title = re.sub(r'\s+', ' ', norm_title)
    norm_company = company.lower().strip()
    norm_loc = location.lower().strip()
    norm_url = url.split('?')[0].lower().strip()

    payload = f"{norm_url}|{norm_title}|{norm_company}|{norm_loc}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


JOB_TYPE_MAPPING = {
    "Full Time": ["vollzeit", "full-time", "full time", "festanstellung"],
    "Part Time": ["teilzeit", "part-time", "part time"],
    "Internship": ["praktikum", "internship", "intern", "praktikant"],
    "Working Student": ["werkstudent", "working student", "studentische aushilfe", "werkstudententätigkeit"],
}


class DeterministicFilterService:
    """Zero-cost in-memory filtering of jobs against candidate preferences."""

    @staticmethod
    def _make_word_pattern(term: str) -> str:
        """Create word boundary pattern resilient to symbols like C++, C#, .NET."""
        escaped = re.escape(term.strip().lower())
        return rf"(?<!\w){escaped}(?!\w)"

    @classmethod
    def is_job_eligible(cls, job: Job, pref: CandidatePreference) -> bool:
        # 1. Excluded Companies Check (case-insensitive substring)
        if pref.excluded_companies:
            job_comp = job.company_name.lower().strip()
            for exc in pref.excluded_companies:
                if exc.strip() and exc.lower().strip() in job_comp:
                    return False

        # 2. Excluded Keywords Check (word boundary regex)
        if pref.excluded_keywords:
            for kw in pref.excluded_keywords:
                if kw.strip():
                    pattern = cls._make_word_pattern(kw)
                    if re.search(pattern, job.title.lower()) or re.search(pattern, job.description.lower()):
                        return False

        # 3. Remote Policy Check
        if pref.remote_only and not job.remote:
            return False

        # 4. Location Match Check (if not remote_only and locations specified)
        if pref.locations and len(pref.locations) > 0 and not job.remote:
            loc_matched = False
            for loc in pref.locations:
                if loc.strip():
                    pattern = cls._make_word_pattern(loc)
                    if re.search(pattern, job.location.lower()):
                        loc_matched = True
                        break
            if not loc_matched:
                return False

        # 5. Job Type Match Check
        if pref.job_types and len(pref.job_types) > 0:
            type_matched = False
            target_keywords = []
            for jt in pref.job_types:
                target_keywords.extend(JOB_TYPE_MAPPING.get(jt, [jt.lower()]))

            for kw in target_keywords:
                pattern = cls._make_word_pattern(kw)
                if re.search(pattern, job.title.lower()):
                    type_matched = True
                    break
                if job.job_types and any(re.search(pattern, str(t).lower()) for t in job.job_types):
                    type_matched = True
                    break
            if not type_matched:
                return False

        # 6. Target Role Keyword Matching (if specified)
        if pref.target_roles and len(pref.target_roles) > 0:
            role_matched = False
            for role in pref.target_roles:
                if role.strip():
                    pattern = cls._make_word_pattern(role)
                    if re.search(pattern, job.title.lower()):
                        role_matched = True
                        break
            if not role_matched:
                return False

        # 7. Minimum Salary Check (if specified and job has salary info)
        if pref.min_salary is not None and job.salary_max is not None:
            if Decimal(str(job.salary_max)) < Decimal(str(pref.min_salary)):
                return False

        return True


# ============================================================================
# Domain Object Factories
# ============================================================================

@pytest.fixture
def make_user(db: Session):
    """Factory fixture to create a User."""
    def _make(
        email: Optional[str] = None,
        full_name: str = "Test Candidate",
        password: str = "securepassword123",
        is_active: bool = True,
        is_superuser: bool = False,
    ) -> User:
        user = User(
            id=uuid.uuid4(),
            email=email or f"user_{uuid.uuid4().hex[:8]}@example.com",
            hashed_password=f"hashed_{password}",
            full_name=full_name,
            is_active=is_active,
            is_superuser=is_superuser,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    return _make


@pytest.fixture
def make_profile(db: Session):
    """Factory fixture to create a CandidateProfile."""
    def _make(
        user: User,
        headline: str = "Senior AI & Data Engineer",
        summary: str = "Experienced Python and ML systems architect.",
        phone: str = "+49 151 12345678",
        location: str = "Berlin, Germany",
        is_verified: bool = True,
        raw_cv_text: Optional[str] = None,
    ) -> CandidateProfile:
        profile = CandidateProfile(
            id=uuid.uuid4(),
            user_id=user.id,
            headline=headline,
            summary=summary,
            phone=phone,
            location=location,
            is_verified=is_verified,
            raw_cv_text=raw_cv_text or "Sample CV raw text content.",
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
        return profile
    return _make


@pytest.fixture
def make_preference(db: Session):
    """Factory fixture to create CandidatePreference."""
    def _make(
        user: User,
        target_roles: Optional[List[str]] = None,
        locations: Optional[List[str]] = None,
        remote_only: bool = False,
        job_types: Optional[List[str]] = None,
        min_salary: Optional[float] = None,
        excluded_companies: Optional[List[str]] = None,
        excluded_keywords: Optional[List[str]] = None,
    ) -> CandidatePreference:
        pref = CandidatePreference(
            id=uuid.uuid4(),
            user_id=user.id,
            target_roles=target_roles if target_roles is not None else [],
            locations=locations if locations is not None else [],
            remote_only=remote_only,
            job_types=job_types if job_types is not None else [],
            min_salary=Decimal(str(min_salary)) if min_salary is not None else None,
            salary_currency="EUR",
            excluded_companies=excluded_companies or [],
            excluded_keywords=excluded_keywords or [],
            languages=["English", "German"],
        )
        db.add(pref)
        db.commit()
        db.refresh(pref)
        return pref
    return _make


@pytest.fixture
def make_experience(db: Session):
    """Factory fixture to create an ExperienceRecord."""
    def _make(
        user: User,
        company_name: str = "Ruya Advisory",
        role_title: str = "AI & Automation Lead",
        start_date: str = "2023-01",
        end_date: Optional[str] = None,
        is_current: bool = True,
        location: str = "Berlin, Germany",
    ) -> ExperienceRecord:
        exp = ExperienceRecord(
            id=uuid.uuid4(),
            user_id=user.id,
            company_name=company_name,
            role_title=role_title,
            start_date=start_date,
            end_date=end_date,
            is_current=is_current,
            location=location,
            description="Leading AI and data infrastructure projects.",
        )
        db.add(exp)
        db.commit()
        db.refresh(exp)
        return exp
    return _make


@pytest.fixture
def make_evidence_item(db: Session):
    """Factory fixture to create an EvidenceItem with stable_id."""
    def _make(
        user: User,
        stable_id: str = "EXP_001",
        raw_text: str = "Reduced ML data export time from 3 hours to 30 minutes.",
        category: str = "experience",
        is_verified: bool = True,
        experience_record: Optional[ExperienceRecord] = None,
        variants: Optional[Dict[str, str]] = None,
    ) -> EvidenceItem:
        item = EvidenceItem(
            id=uuid.uuid4(),
            user_id=user.id,
            experience_record_id=experience_record.id if experience_record else None,
            stable_id=stable_id,
            raw_text=raw_text,
            category=category,
            is_verified=is_verified,
            variants=variants,
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        return item
    return _make


@pytest.fixture
def make_skill(db: Session):
    """Factory fixture to create a Skill with stable_id."""
    def _make(
        user: User,
        stable_id: str = "SKILL_001",
        name: str = "Python",
        category: str = "programming",
        proficiency: str = "expert",
        years_of_experience: float = 5.0,
        is_verified: bool = True,
    ) -> Skill:
        skill = Skill(
            id=uuid.uuid4(),
            user_id=user.id,
            stable_id=stable_id,
            name=name,
            category=category,
            proficiency=proficiency,
            years_of_experience=Decimal(str(years_of_experience)),
            is_verified=is_verified,
        )
        db.add(skill)
        db.commit()
        db.refresh(skill)
        return skill
    return _make


@pytest.fixture
def make_project(db: Session):
    """Factory fixture to create a Project with stable_id."""
    def _make(
        user: User,
        stable_id: str = "PROJ_001",
        title: str = "Automated Job Intelligence Engine",
        description: str = "Built multi-agent platform for real-time job discovery.",
        technologies: Optional[List[str]] = None,
        is_verified: bool = True,
    ) -> Project:
        proj = Project(
            id=uuid.uuid4(),
            user_id=user.id,
            stable_id=stable_id,
            title=title,
            description=description,
            technologies=technologies or ["Python", "FastAPI", "PostgreSQL", "Docker"],
            is_verified=is_verified,
        )
        db.add(proj)
        db.commit()
        db.refresh(proj)
        return proj
    return _make


@pytest.fixture
def make_certification(db: Session):
    """Factory fixture to create a Certification with stable_id."""
    def _make(
        user: User,
        stable_id: str = "CERT_001",
        name: str = "Model Context Protocol Applied Certification",
        issuing_organization: str = "Anthropic Community",
        is_verified: bool = True,
    ) -> Certification:
        cert = Certification(
            id=uuid.uuid4(),
            user_id=user.id,
            stable_id=stable_id,
            name=name,
            issuing_organization=issuing_organization,
            is_verified=is_verified,
        )
        db.add(cert)
        db.commit()
        db.refresh(cert)
        return cert
    return _make


@pytest.fixture
def make_education(db: Session):
    """Factory fixture to create an EducationRecord with stable_id."""
    def _make(
        user: User,
        stable_id: str = "EDU_001",
        institution: str = "Technical University of Munich",
        degree: str = "Master of Science",
        field_of_study: str = "Computer Science",
        is_verified: bool = True,
    ) -> EducationRecord:
        edu = EducationRecord(
            id=uuid.uuid4(),
            user_id=user.id,
            stable_id=stable_id,
            institution=institution,
            degree=degree,
            field_of_study=field_of_study,
            is_verified=is_verified,
        )
        db.add(edu)
        db.commit()
        db.refresh(edu)
        return edu
    return _make


@pytest.fixture
def make_company(db: Session):
    """Factory fixture to create a Company."""
    def _make(
        name: str = "TechCorp Global",
        website: Optional[str] = "https://techcorp.example.com",
    ) -> Company:
        normalized = name.lower().strip()
        comp = Company(
            id=uuid.uuid4(),
            name=name,
            normalized_name=normalized,
            website=website,
        )
        db.add(comp)
        db.commit()
        db.refresh(comp)
        return comp
    return _make


@pytest.fixture
def make_job_source(db: Session):
    """Factory fixture to create a JobSource."""
    def _make(
        name: str = "arbeitnow",
        base_url: str = "https://arbeitnow.com/api/job-board-api",
    ) -> JobSource:
        source = JobSource(
            id=uuid.uuid4(),
            name=name,
            base_url=base_url,
            is_active=True,
            config={"rate_limit_per_minute": 60},
        )
        db.add(source)
        db.commit()
        db.refresh(source)
        return source
    return _make


@pytest.fixture
def make_job(db: Session, make_company):
    """Factory fixture to create a canonical Job."""
    def _make(
        title: str = "Senior AI Engineer (m/w/d)",
        company_name: str = "TechCorp Global",
        location: str = "Berlin, Germany",
        remote: bool = True,
        url: Optional[str] = None,
        job_types: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        description: str = "We are seeking a senior AI engineer to build LLM pipelines.",
        salary_min: Optional[float] = None,
        salary_max: Optional[float] = None,
        company: Optional[Company] = None,
    ) -> Job:
        resolved_url = url or f"https://jobs.example.com/view/{uuid.uuid4().hex[:12]}"
        chash = compute_content_hash(resolved_url, title, company_name, location)
        
        job = Job(
            id=uuid.uuid4(),
            company_id=company.id if company else None,
            slug=f"job-{uuid.uuid4().hex[:8]}",
            title=title,
            sanitized_title=re.sub(r'\(.*?\)|\[.*?\]', '', title).strip(),
            company_name=company_name,
            location=location,
            remote=remote,
            url=resolved_url,
            description=description,
            tags=tags or ["Python", "AI", "FastAPI"],
            job_types=job_types or ["Full Time"],
            salary_min=Decimal(str(salary_min)) if salary_min is not None else None,
            salary_max=Decimal(str(salary_max)) if salary_max is not None else None,
            salary_currency="EUR",
            published_at=datetime.now(timezone.utc),
            content_hash=chash,
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        return job
    return _make
