"""Empirical Adversarial Test Suite for Milestone 1 (M1).
Tests edge cases, foreign key cascading, stable_id uniqueness across multi-tenant boundaries,
Alembic migration multi-cycle stability, GUID resilience, and complex data constraints.
"""

import os
import tempfile
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Generator

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, event, inspect, text
from sqlalchemy.exc import IntegrityError, StatementError
from sqlalchemy.orm import Session, sessionmaker

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


# ============================================================================
# Test Fixtures for Adversarial Scenarios
# ============================================================================

@pytest.fixture(scope="function")
def sqlite_adv_engine():
    """Create a clean in-memory SQLite engine with PRAGMA foreign_keys=ON."""
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

    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def adv_session(sqlite_adv_engine) -> Generator[Session, None, None]:
    """Provide a transactional session for adversarial test cases."""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sqlite_adv_engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def two_users(adv_session: Session) -> tuple[User, User]:
    """Create two distinct users for multi-tenant isolation testing."""
    user1 = User(
        email="alice@company-a.com",
        hashed_password="hashed_pwd_alice_123",
        full_name="Alice Developer",
    )
    user2 = User(
        email="bob@company-b.com",
        hashed_password="hashed_pwd_bob_456",
        full_name="Bob Engineer",
    )
    adv_session.add_all([user1, user2])
    adv_session.commit()
    adv_session.refresh(user1)
    adv_session.refresh(user2)
    return user1, user2


# ============================================================================
# 1. Multi-Tenant Stable ID Uniqueness Tests
# ============================================================================

class TestStableIdUniquenessAdversarial:
    """Stress-test unique constraints on (user_id, stable_id) across all 5 evidence tables."""

    def test_evidence_item_duplicate_same_user_fails(self, adv_session: Session, two_users: tuple[User, User]):
        u1, _ = two_users
        item1 = EvidenceItem(user_id=u1.id, stable_id="EXP_001", raw_text="Bullet 1")
        adv_session.add(item1)
        adv_session.commit()

        # Duplicate for same user
        item2 = EvidenceItem(user_id=u1.id, stable_id="EXP_001", raw_text="Duplicate bullet")
        adv_session.add(item2)
        with pytest.raises(IntegrityError):
            adv_session.commit()
        adv_session.rollback()

    def test_evidence_item_same_stable_id_different_users_succeeds(
        self, adv_session: Session, two_users: tuple[User, User]
    ):
        u1, u2 = two_users
        item1 = EvidenceItem(user_id=u1.id, stable_id="EXP_001", raw_text="Alice bullet")
        item2 = EvidenceItem(user_id=u2.id, stable_id="EXP_001", raw_text="Bob bullet")
        adv_session.add_all([item1, item2])
        adv_session.commit()

        assert item1.id != item2.id
        assert item1.stable_id == item2.stable_id == "EXP_001"
        assert item1.user_id == u1.id
        assert item2.user_id == u2.id

    def test_skill_duplicate_same_user_fails(self, adv_session: Session, two_users: tuple[User, User]):
        u1, _ = two_users
        s1 = Skill(user_id=u1.id, stable_id="SKILL_001", name="Python")
        adv_session.add(s1)
        adv_session.commit()

        s2 = Skill(user_id=u1.id, stable_id="SKILL_001", name="Rust")
        adv_session.add(s2)
        with pytest.raises(IntegrityError):
            adv_session.commit()
        adv_session.rollback()

    def test_skill_same_stable_id_different_users_succeeds(
        self, adv_session: Session, two_users: tuple[User, User]
    ):
        u1, u2 = two_users
        s1 = Skill(user_id=u1.id, stable_id="SKILL_001", name="Python")
        s2 = Skill(user_id=u2.id, stable_id="SKILL_001", name="Python")
        adv_session.add_all([s1, s2])
        adv_session.commit()

        assert s1.id != s2.id
        assert s1.stable_id == s2.stable_id == "SKILL_001"

    def test_project_duplicate_same_user_fails(self, adv_session: Session, two_users: tuple[User, User]):
        u1, _ = two_users
        p1 = Project(user_id=u1.id, stable_id="PROJ_001", title="Crawler", description="Crawler desc")
        adv_session.add(p1)
        adv_session.commit()

        p2 = Project(user_id=u1.id, stable_id="PROJ_001", title="Search Engine", description="Search desc")
        adv_session.add(p2)
        with pytest.raises(IntegrityError):
            adv_session.commit()
        adv_session.rollback()

    def test_project_same_stable_id_different_users_succeeds(
        self, adv_session: Session, two_users: tuple[User, User]
    ):
        u1, u2 = two_users
        p1 = Project(user_id=u1.id, stable_id="PROJ_001", title="Crawler Alice", description="A desc")
        p2 = Project(user_id=u2.id, stable_id="PROJ_001", title="Crawler Bob", description="B desc")
        adv_session.add_all([p1, p2])
        adv_session.commit()
        assert p1.id != p2.id

    def test_certification_duplicate_same_user_fails(self, adv_session: Session, two_users: tuple[User, User]):
        u1, _ = two_users
        c1 = Certification(user_id=u1.id, stable_id="CERT_001", name="AWS SAA", issuing_organization="AWS")
        adv_session.add(c1)
        adv_session.commit()

        c2 = Certification(user_id=u1.id, stable_id="CERT_001", name="AWS SAP", issuing_organization="AWS")
        adv_session.add(c2)
        with pytest.raises(IntegrityError):
            adv_session.commit()
        adv_session.rollback()

    def test_education_duplicate_same_user_fails(self, adv_session: Session, two_users: tuple[User, User]):
        u1, _ = two_users
        e1 = EducationRecord(user_id=u1.id, stable_id="EDU_001", institution="TUM", degree="B.Sc.", field_of_study="CS")
        adv_session.add(e1)
        adv_session.commit()

        e2 = EducationRecord(user_id=u1.id, stable_id="EDU_001", institution="LMU", degree="M.Sc.", field_of_study="AI")
        adv_session.add(e2)
        with pytest.raises(IntegrityError):
            adv_session.commit()
        adv_session.rollback()


# ============================================================================
# 2. Foreign Key Cascade & Set Null Verification
# ============================================================================

class TestCascadeAndOrphanAdversarial:
    """Stress-test FK cascading on User, Job, Company, and JobSource."""

    def test_cascade_delete_all_child_entities(self, adv_session: Session):
        user = User(
            email="victim@cascade.com",
            hashed_password="hash",
            full_name="Victim User",
        )
        adv_session.add(user)
        adv_session.commit()

        # Add 1 of every user-dependent entity
        profile = CandidateProfile(user_id=user.id, headline="Victim Profile")
        pref = CandidatePreference(user_id=user.id)
        exp = ExperienceRecord(user_id=user.id, company_name="Co", role_title="Dev", start_date="2021-01")
        adv_session.add_all([profile, pref, exp])
        adv_session.commit()

        item = EvidenceItem(user_id=user.id, experience_record_id=exp.id, stable_id="EXP_001", raw_text="Bullet")
        skill = Skill(user_id=user.id, stable_id="SKILL_001", name="Go")
        proj = Project(user_id=user.id, stable_id="PROJ_001", title="P", description="D")
        cert = Certification(user_id=user.id, stable_id="CERT_001", name="C", issuing_organization="O")
        edu = EducationRecord(user_id=user.id, stable_id="EDU_001", institution="I", degree="D", field_of_study="F")
        adv_session.add_all([item, skill, proj, cert, edu])
        adv_session.commit()

        # Delete user
        adv_session.delete(user)
        adv_session.commit()

        # Verify all children are gone
        assert adv_session.query(CandidateProfile).filter_by(user_id=user.id).count() == 0
        assert adv_session.query(CandidatePreference).filter_by(user_id=user.id).count() == 0
        assert adv_session.query(ExperienceRecord).filter_by(user_id=user.id).count() == 0
        assert adv_session.query(EvidenceItem).filter_by(user_id=user.id).count() == 0
        assert adv_session.query(Skill).filter_by(user_id=user.id).count() == 0
        assert adv_session.query(Project).filter_by(user_id=user.id).count() == 0
        assert adv_session.query(Certification).filter_by(user_id=user.id).count() == 0
        assert adv_session.query(EducationRecord).filter_by(user_id=user.id).count() == 0

    def test_delete_company_sets_job_company_id_null(self, adv_session: Session):
        company = Company(name="Orphan Company", normalized_name="orphan company")
        adv_session.add(company)
        adv_session.commit()

        job = Job(
            company_id=company.id,
            slug="orphan-test-job-1",
            title="Software Developer",
            company_name=company.name,
            location="Remote",
            url="https://example.com/job/orphan-1",
            description="Desc",
            published_at=datetime.now(timezone.utc),
            content_hash="hash_orphan_1",
        )
        adv_session.add(job)
        adv_session.commit()
        adv_session.refresh(job)

        assert job.company_id == company.id

        # Delete company
        adv_session.delete(company)
        adv_session.commit()
        adv_session.refresh(job)

        # Job must still exist with company_id set to None
        assert job.company_id is None
        assert adv_session.query(Job).filter_by(id=job.id).first() is not None

    def test_delete_job_cascades_to_source_records(self, adv_session: Session):
        source = JobSource(name="source_x", base_url="https://source-x.com")
        adv_session.add(source)
        adv_session.commit()

        job = Job(
            slug="job-to-delete-123",
            title="Backend Lead",
            company_name="Corp Z",
            location="Berlin",
            url="https://source-x.com/jobs/123",
            description="Desc",
            published_at=datetime.now(timezone.utc),
            content_hash="hash_source_rec_test",
        )
        adv_session.add(job)
        adv_session.commit()

        sr = JobSourceRecord(
            job_id=job.id,
            source_id=source.id,
            external_id="ext_123",
            external_url=job.url,
            raw_payload={"id": "ext_123"},
        )
        adv_session.add(sr)
        adv_session.commit()

        sr_id = sr.id
        assert adv_session.query(JobSourceRecord).filter_by(id=sr_id).count() == 1

        # Delete Job
        adv_session.delete(job)
        adv_session.commit()

        assert adv_session.query(JobSourceRecord).filter_by(id=sr_id).count() == 0

    def test_delete_job_source_cascades_to_source_records(self, adv_session: Session):
        source = JobSource(name="source_to_kill", base_url="https://kill.com")
        adv_session.add(source)
        adv_session.commit()

        job = Job(
            slug="job-persist-123",
            title="DevOps Engineer",
            company_name="Corp Y",
            location="Munich",
            url="https://kill.com/jobs/999",
            description="Desc",
            published_at=datetime.now(timezone.utc),
            content_hash="hash_kill_source_test",
        )
        adv_session.add(job)
        adv_session.commit()

        sr = JobSourceRecord(
            job_id=job.id,
            source_id=source.id,
            external_id="kill_999",
            external_url=job.url,
            raw_payload={"id": "999"},
        )
        adv_session.add(sr)
        adv_session.commit()

        sr_id = sr.id

        # Delete JobSource
        adv_session.delete(source)
        adv_session.commit()

        assert adv_session.query(JobSourceRecord).filter_by(id=sr_id).count() == 0
        # Job itself remains intact
        assert adv_session.query(Job).filter_by(id=job.id).count() == 1


# ============================================================================
# 3. UUID & GUID Type Edge Cases & String Queries
# ============================================================================

class TestGUIDTypeAdversarial:
    """Stress-test GUID type handling with string UUIDs, object UUIDs, invalid formats."""

    def test_guid_accepts_uuid_instance_and_string_uuid(self, adv_session: Session):
        custom_uuid = uuid.uuid4()
        user1 = User(
            id=custom_uuid,
            email="custom.uuid@example.com",
            hashed_password="hash",
            full_name="Custom UUID",
        )
        adv_session.add(user1)
        adv_session.commit()

        # Query using uuid.UUID object
        found_by_obj = adv_session.query(User).filter(User.id == custom_uuid).first()
        assert found_by_obj is not None
        assert found_by_obj.id == custom_uuid

        # Query using string representation
        found_by_str = adv_session.query(User).filter(User.id == str(custom_uuid)).first()
        assert found_by_str is not None
        assert found_by_str.id == custom_uuid

    def test_guid_rejects_invalid_uuid_string(self, adv_session: Session):
        with pytest.raises((ValueError, StatementError)):
            user = User(
                id="not-a-valid-uuid-string",
                email="invalid.uuid@example.com",
                hashed_password="hash",
                full_name="Invalid UUID",
            )
            adv_session.add(user)
            adv_session.commit()
        adv_session.rollback()


# ============================================================================
# 4. Alembic Migration Multi-Cycle Stress Test
# ============================================================================

class TestAlembicMigrationsCycle:
    """Run multiple complete upgrade -> downgrade -> upgrade cycles to guarantee idempotent migrations."""

    def test_alembic_multi_cycle_upgrade_downgrade(self):
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            tmp_db_path = tmp.name

        try:
            db_url = f"sqlite:///{tmp_db_path}"
            backend_dir = Path(__file__).resolve().parent.parent
            alembic_ini_path = backend_dir / "alembic.ini"

            alembic_cfg = Config(str(alembic_ini_path))
            alembic_cfg.set_main_option("sqlalchemy.url", db_url)
            alembic_cfg.set_main_option("script_location", str(backend_dir / "alembic"))

            engine = create_engine(db_url)

            # Perform 3 full cycles
            for cycle in range(3):
                # Upgrade to head
                command.upgrade(alembic_cfg, "head")
                inspector = inspect(engine)
                tables = set(inspector.get_table_names())
                assert "users" in tables
                assert "evidence_items" in tables
                assert "jobs" in tables

                # Downgrade to base
                command.downgrade(alembic_cfg, "base")
                inspector_after = inspect(engine)
                remaining = set(inspector_after.get_table_names())
                assert remaining == {"alembic_version"}

            # Final upgrade to verify clean state
            command.upgrade(alembic_cfg, "head")
            inspector_final = inspect(engine)
            assert len(inspector_final.get_table_names()) == 14  # 13 application tables + alembic_version

            engine.dispose()

        finally:
            if os.path.exists(tmp_db_path):
                try:
                    os.remove(tmp_db_path)
                except OSError:
                    pass


# ============================================================================
# 5. Complex JSON Data & Numeric Precision Stress
# ============================================================================

class TestComplexTypesAndNumericStress:
    """Stress-test JSON structures, German characters, emojis, and high-precision numeric values."""

    def test_candidate_preference_complex_json_and_special_chars(
        self, adv_session: Session, two_users: tuple[User, User]
    ):
        u1, _ = two_users
        pref = CandidatePreference(
            user_id=u1.id,
            target_roles=["Senior AI Engineer 🚀", "KI-Entwickler (m/w/d)", "Softwarearchitekt"],
            locations=["München, Bayern", "Köln", "Zürich", "Berlin (Remote)"],
            remote_only=False,
            hybrid_allowed=True,
            onsite_allowed=False,
            job_types=["Vollzeit", "Working Student", "Teilzeit"],
            min_salary=Decimal("125000.50"),
            salary_currency="EUR",
            max_seniority="Staff / Principal",
            languages=["Deutsch (Muttersprache)", "Englisch (Fließend)"],
            excluded_companies=["Spam & Co. KG", "LowPay GmbH & Co. KG"],
            excluded_keywords=["Legacy Cobol", "Unbezahltes Praktikum", "Callcenter"],
            preferred_industries=["Künstliche Intelligenz", "FinTech", "HealthTech"],
        )
        adv_session.add(pref)
        adv_session.commit()
        adv_session.refresh(pref)

        assert pref.min_salary == Decimal("125000.50")
        assert "Senior AI Engineer 🚀" in pref.target_roles
        assert "München, Bayern" in pref.locations
        assert "Künstliche Intelligenz" in pref.preferred_industries

    def test_evidence_item_rich_variants_json(
        self, adv_session: Session, two_users: tuple[User, User]
    ):
        u1, _ = two_users
        variants_dict = {
            "EXP_001_FULL": "Optimierte Datenpipeline für 24 TB Datensätze um 83 % (von 3h auf 30min).",
            "EXP_001_SHORT": "24 TB ML-Export von 3h auf 30min reduziert.",
            "EXP_001_TECH": "Refactored Celery task queue into async asyncio worker pool.",
            "EXP_001_EMOJI": "⚡ 6x speedup on 24TB ML pipeline 🚀",
        }
        item = EvidenceItem(
            user_id=u1.id,
            stable_id="EXP_001",
            raw_text="24 TB export reduced from 3 hours to 30 mins.",
            category="achievement",
            variants=variants_dict,
            is_verified=True,
        )
        adv_session.add(item)
        adv_session.commit()
        adv_session.refresh(item)

        assert item.variants == variants_dict
        assert item.variants["EXP_001_EMOJI"] == "⚡ 6x speedup on 24TB ML pipeline 🚀"

    def test_numeric_precision_boundary_values(
        self, adv_session: Session, two_users: tuple[User, User]
    ):
        u1, _ = two_users
        skill = Skill(
            user_id=u1.id,
            stable_id="SKILL_001",
            name="Python Architecture",
            years_of_experience=Decimal("15.5"),
        )
        adv_session.add(skill)
        adv_session.commit()
        adv_session.refresh(skill)

        assert skill.years_of_experience == Decimal("15.5")


# ============================================================================
# 6. Job Deduplication Constraints Stress
# ============================================================================

class TestJobDeduplicationConstraints:
    """Stress-test unique constraints on slug, url, and content_hash."""

    def test_job_slug_uniqueness(self, adv_session: Session):
        pub_time = datetime.now(timezone.utc)
        j1 = Job(
            slug="duplicate-slug-test",
            title="Job 1",
            company_name="Corp A",
            location="Remote",
            url="https://jobs.com/1",
            description="Desc 1",
            published_at=pub_time,
            content_hash="hash_111",
        )
        adv_session.add(j1)
        adv_session.commit()

        j2 = Job(
            slug="duplicate-slug-test",  # Duplicate slug
            title="Job 2",
            company_name="Corp B",
            location="Berlin",
            url="https://jobs.com/2",
            description="Desc 2",
            published_at=pub_time,
            content_hash="hash_222",
        )
        adv_session.add(j2)
        with pytest.raises(IntegrityError):
            adv_session.commit()
        adv_session.rollback()

    def test_job_url_uniqueness(self, adv_session: Session):
        pub_time = datetime.now(timezone.utc)
        j1 = Job(
            slug="job-slug-url-1",
            title="Job 1",
            company_name="Corp A",
            location="Remote",
            url="https://jobs.com/unique-url",
            description="Desc 1",
            published_at=pub_time,
            content_hash="hash_333",
        )
        adv_session.add(j1)
        adv_session.commit()

        j2 = Job(
            slug="job-slug-url-2",
            title="Job 2",
            company_name="Corp A",
            location="Remote",
            url="https://jobs.com/unique-url",  # Duplicate URL
            description="Desc 2",
            published_at=pub_time,
            content_hash="hash_444",
        )
        adv_session.add(j2)
        with pytest.raises(IntegrityError):
            adv_session.commit()
        adv_session.rollback()

    def test_job_source_record_external_id_uniqueness_per_source(self, adv_session: Session):
        s1 = JobSource(name="source_alpha", base_url="https://alpha.com")
        s2 = JobSource(name="source_beta", base_url="https://beta.com")
        adv_session.add_all([s1, s2])
        adv_session.commit()

        pub_time = datetime.now(timezone.utc)
        j1 = Job(
            slug="job-j1",
            title="Job 1",
            company_name="Corp A",
            location="Remote",
            url="https://alpha.com/job/1",
            description="Desc",
            published_at=pub_time,
            content_hash="hash_j1",
        )
        j2 = Job(
            slug="job-j2",
            title="Job 2",
            company_name="Corp B",
            location="Remote",
            url="https://beta.com/job/1",
            description="Desc",
            published_at=pub_time,
            content_hash="hash_j2",
        )
        adv_session.add_all([j1, j2])
        adv_session.commit()

        # Insert record for s1 with external_id 'EXT_100'
        sr1 = JobSourceRecord(
            job_id=j1.id,
            source_id=s1.id,
            external_id="EXT_100",
            external_url=j1.url,
            raw_payload={"id": "100"},
        )
        adv_session.add(sr1)
        adv_session.commit()

        # Same external_id for s2 -> SUCCEEDS (different sources can have same external id)
        sr2 = JobSourceRecord(
            job_id=j2.id,
            source_id=s2.id,
            external_id="EXT_100",
            external_url=j2.url,
            raw_payload={"id": "100"},
        )
        adv_session.add(sr2)
        adv_session.commit()

        # Duplicate external_id for s1 -> FAILS
        sr_dup = JobSourceRecord(
            job_id=j2.id,
            source_id=s1.id,
            external_id="EXT_100",
            external_url=j2.url,
            raw_payload={"id": "100"},
        )
        adv_session.add(sr_dup)
        with pytest.raises(IntegrityError):
            adv_session.commit()
        adv_session.rollback()
