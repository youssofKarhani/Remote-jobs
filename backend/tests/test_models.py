import uuid
from datetime import datetime, timezone
from decimal import Decimal
import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

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


class TestIdentityAndProfileModels:
    """Test suite for User, CandidateProfile, and CandidatePreference entities."""

    def test_create_user_success(self, db_session: Session):
        user = User(
            email="dev@example.com",
            hashed_password="secret_hash_value",
            full_name="Jane Doe",
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        assert user.id is not None
        assert isinstance(user.id, uuid.UUID)
        assert user.email == "dev@example.com"
        assert user.is_active is True
        assert user.is_superuser is False
        assert user.created_at is not None
        assert user.updated_at is not None

    def test_user_email_unique_constraint(self, db_session: Session, sample_user: User):
        duplicate_user = User(
            email=sample_user.email,
            hashed_password="another_hash",
            full_name="Duplicate Name",
        )
        db_session.add(duplicate_user)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_create_candidate_profile(self, db_session: Session, sample_user: User):
        profile = CandidateProfile(
            user_id=sample_user.id,
            headline="Lead AI & Platform Engineer",
            summary="10+ years engineering scalable AI systems.",
            phone="+49 151 12345678",
            location="Munich, Germany",
            linkedin_url="https://linkedin.com/in/alexmorgan",
            github_url="https://github.com/alexmorgan",
            portfolio_url="https://alexmorgan.dev",
            raw_cv_text="Experienced Software Engineer with deep AI background.",
            is_verified=True,
        )
        db_session.add(profile)
        db_session.commit()
        db_session.refresh(profile)

        assert profile.id is not None
        assert profile.user_id == sample_user.id
        assert profile.headline == "Lead AI & Platform Engineer"
        assert profile.is_verified is True
        assert profile.user.email == sample_user.email

    def test_candidate_profile_unique_per_user(self, db_session: Session, sample_user: User):
        profile1 = CandidateProfile(user_id=sample_user.id, headline="Engineer 1")
        db_session.add(profile1)
        db_session.commit()

        profile2 = CandidateProfile(user_id=sample_user.id, headline="Engineer 2")
        db_session.add(profile2)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_create_candidate_preference(self, db_session: Session, sample_user: User):
        pref = CandidatePreference(
            user_id=sample_user.id,
            target_roles=["AI Engineer", "Backend Architect"],
            locations=["Germany", "Remote"],
            remote_only=False,
            hybrid_allowed=True,
            onsite_allowed=False,
            job_types=["Full Time", "Part Time"],
            min_salary=Decimal("95000.00"),
            salary_currency="EUR",
            max_seniority="Lead",
            languages=["English", "German"],
            excluded_companies=["Spam Corp", "LowBall Ltd"],
            excluded_keywords=["legacy", "cobol"],
            preferred_industries=["AI/ML", "FinTech"],
        )
        db_session.add(pref)
        db_session.commit()
        db_session.refresh(pref)

        assert pref.id is not None
        assert pref.user_id == sample_user.id
        assert "AI Engineer" in pref.target_roles
        assert pref.min_salary == Decimal("95000.00")
        assert pref.hybrid_allowed is True
        assert pref.onsite_allowed is False


class TestEvidenceBankModels:
    """Test suite for Candidate Evidence Bank entities with stable IDs."""

    def test_create_experience_and_evidence_items(self, db_session: Session, sample_user: User):
        exp = ExperienceRecord(
            user_id=sample_user.id,
            company_name="TechCorp AI",
            role_title="Senior Systems Architect",
            location="Berlin, Germany",
            start_date="2022-03",
            end_date="2024-05",
            is_current=False,
            description="Led distributed machine learning platform development.",
            display_order=1,
        )
        db_session.add(exp)
        db_session.commit()
        db_session.refresh(exp)

        item1 = EvidenceItem(
            user_id=sample_user.id,
            experience_record_id=exp.id,
            stable_id="EXP_001",
            raw_text="Reduced 24 TB ML data export duration from 3 hours to 30 minutes.",
            category="achievement",
            variants={
                "EXP_001_FULL": "Optimized export pipeline for 24TB datasets reducing time by 83%.",
                "EXP_001_SHORT": "Cut ML data export duration from 3h to 30m.",
            },
            is_verified=True,
            display_order=1,
        )
        item2 = EvidenceItem(
            user_id=sample_user.id,
            experience_record_id=exp.id,
            stable_id="EXP_002",
            raw_text="Built asyncio WebSocket client handling 9 real-time feeds.",
            category="experience",
            is_verified=True,
            display_order=2,
        )
        db_session.add_all([item1, item2])
        db_session.commit()

        assert len(exp.evidence_items) == 2
        assert exp.evidence_items[0].stable_id == "EXP_001"
        assert exp.evidence_items[0].variants["EXP_001_SHORT"] == "Cut ML data export duration from 3h to 30m."

    def test_evidence_item_stable_id_uniqueness_per_user(self, db_session: Session, sample_user: User):
        item1 = EvidenceItem(
            user_id=sample_user.id,
            stable_id="EXP_001",
            raw_text="First achievement statement.",
        )
        db_session.add(item1)
        db_session.commit()

        duplicate_item = EvidenceItem(
            user_id=sample_user.id,
            stable_id="EXP_001",
            raw_text="Duplicate stable ID for same user.",
        )
        db_session.add(duplicate_item)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_create_skill_and_unique_stable_id(self, db_session: Session, sample_user: User):
        skill = Skill(
            user_id=sample_user.id,
            stable_id="SKILL_001",
            name="FastAPI",
            category="backend",
            proficiency="expert",
            years_of_experience=Decimal("4.5"),
            is_verified=True,
            display_order=1,
        )
        db_session.add(skill)
        db_session.commit()
        db_session.refresh(skill)

        assert skill.id is not None
        assert skill.stable_id == "SKILL_001"
        assert skill.name == "FastAPI"
        assert skill.years_of_experience == Decimal("4.5")

        # Attempt duplicate stable_id
        duplicate_skill = Skill(
            user_id=sample_user.id,
            stable_id="SKILL_001",
            name="Python",
            category="programming",
        )
        db_session.add(duplicate_skill)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_create_project_and_unique_stable_id(self, db_session: Session, sample_user: User):
        proj = Project(
            user_id=sample_user.id,
            stable_id="PROJ_001",
            title="Reddit Intelligence Pipeline",
            category="Data Engineering",
            description="Automated crawler and sentiment analysis engine processing 150+ posts per run.",
            technologies=["Python", "FastAPI", "PostgreSQL", "Redis"],
            url="https://reddit-intel.example.com",
            github_url="https://github.com/alex/reddit-intel",
            start_date="2023-01",
            end_date="2023-06",
            is_verified=True,
        )
        db_session.add(proj)
        db_session.commit()
        db_session.refresh(proj)

        assert proj.id is not None
        assert proj.stable_id == "PROJ_001"
        assert "FastAPI" in proj.technologies

    def test_create_certification_and_education(self, db_session: Session, sample_user: User):
        cert = Certification(
            user_id=sample_user.id,
            stable_id="CERT_001",
            name="Model Context Protocol (MCP) Specialist",
            issuing_organization="Anthropic / Community",
            issue_date="2024-01",
            credential_id="MCP-987654",
            is_verified=True,
        )
        edu = EducationRecord(
            user_id=sample_user.id,
            stable_id="EDU_001",
            institution="Technical University of Munich",
            degree="Master of Science",
            field_of_study="Computer Science & AI",
            start_date="2018-10",
            end_date="2020-09",
            grade="1.3",
            is_verified=True,
        )
        db_session.add_all([cert, edu])
        db_session.commit()

        assert cert.stable_id == "CERT_001"
        assert edu.stable_id == "EDU_001"
        assert edu.degree == "Master of Science"


class TestJobDiscoveryModels:
    """Test suite for Company, JobSource, Job, and JobSourceRecord entities."""

    def test_create_company(self, db_session: Session):
        company = Company(
            name="OpenAI Tech Services",
            normalized_name="openai tech services",
            website="https://openai.com",
            description="Pioneering AI research and deployment.",
            engineering_focus="Large language models, distributed training.",
        )
        db_session.add(company)
        db_session.commit()
        db_session.refresh(company)

        assert company.id is not None
        assert company.normalized_name == "openai tech services"

    def test_company_normalized_name_unique(self, db_session: Session):
        c1 = Company(name="Acme Inc", normalized_name="acme inc")
        db_session.add(c1)
        db_session.commit()

        c2 = Company(name="Acme Incorporated", normalized_name="acme inc")
        db_session.add(c2)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_create_job_and_source_record(self, db_session: Session):
        company = Company(name="Arbeitnow Partner", normalized_name="arbeitnow partner")
        source = JobSource(
            name="arbeitnow",
            base_url="https://arbeitnow.com/api/job-board-api",
            is_active=True,
        )
        db_session.add_all([company, source])
        db_session.commit()

        published_time = datetime.now(timezone.utc)
        job = Job(
            company_id=company.id,
            slug="senior-python-engineer-berlin-12345",
            title="Senior Python Engineer (m/w/d)",
            sanitized_title="Senior Python Engineer",
            company_name=company.name,
            location="Berlin, Germany",
            remote=True,
            url="https://arbeitnow.com/jobs/senior-python-engineer-12345",
            description="We are seeking an experienced Python/FastAPI engineer...",
            tags=["Python", "FastAPI", "PostgreSQL", "Docker"],
            job_types=["Full Time", "Remote"],
            salary_min=Decimal("80000.00"),
            salary_max=Decimal("100000.00"),
            salary_currency="EUR",
            published_at=published_time,
            content_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        )
        db_session.add(job)
        db_session.commit()
        db_session.refresh(job)

        source_record = JobSourceRecord(
            job_id=job.id,
            source_id=source.id,
            external_id="12345",
            external_url=job.url,
            raw_payload={"id": "12345", "title": job.title, "company": company.name},
        )
        db_session.add(source_record)
        db_session.commit()
        db_session.refresh(source_record)

        assert job.id is not None
        assert job.company.name == "Arbeitnow Partner"
        assert len(job.source_records) == 1
        assert job.source_records[0].external_id == "12345"

    def test_job_content_hash_uniqueness(self, db_session: Session):
        published_time = datetime.now(timezone.utc)
        job1 = Job(
            slug="job-one-slug",
            title="Backend Dev",
            company_name="Corp A",
            location="Remote",
            url="https://example.com/job-1",
            description="Job desc",
            published_at=published_time,
            content_hash="unique_hash_111",
        )
        db_session.add(job1)
        db_session.commit()

        job2 = Job(
            slug="job-two-slug",
            title="Backend Dev 2",
            company_name="Corp A",
            location="Remote",
            url="https://example.com/job-2",
            description="Job desc",
            published_at=published_time,
            content_hash="unique_hash_111",  # duplicate hash
        )
        db_session.add(job2)
        with pytest.raises(IntegrityError):
            db_session.commit()


class TestCascadeDeletions:
    """Test suite ensuring foreign key cascade deletions clean up dependent data."""

    def test_delete_user_cascades_all_candidate_entities(self, db_session: Session):
        user = User(
            email="cascade.test@example.com",
            hashed_password="password_hash",
            full_name="Cascade User",
        )
        db_session.add(user)
        db_session.commit()

        profile = CandidateProfile(user_id=user.id, headline="Test Engineer")
        pref = CandidatePreference(user_id=user.id)
        exp = ExperienceRecord(
            user_id=user.id,
            company_name="Company X",
            role_title="Lead Dev",
            start_date="2020-01",
        )
        db_session.add_all([profile, pref, exp])
        db_session.commit()

        item = EvidenceItem(
            user_id=user.id,
            experience_record_id=exp.id,
            stable_id="EXP_001",
            raw_text="Bullet point text",
        )
        skill = Skill(user_id=user.id, stable_id="SKILL_001", name="Python")
        proj = Project(user_id=user.id, stable_id="PROJ_001", title="Project X", description="Desc")
        cert = Certification(user_id=user.id, stable_id="CERT_001", name="Cert X", issuing_organization="Org X")
        edu = EducationRecord(user_id=user.id, stable_id="EDU_001", institution="Uni X", degree="BS", field_of_study="CS")
        db_session.add_all([item, skill, proj, cert, edu])
        db_session.commit()

        # Delete user
        db_session.delete(user)
        db_session.commit()

        # Check all child records were cascade deleted
        assert db_session.query(CandidateProfile).filter_by(user_id=user.id).first() is None
        assert db_session.query(CandidatePreference).filter_by(user_id=user.id).first() is None
        assert db_session.query(ExperienceRecord).filter_by(user_id=user.id).first() is None
        assert db_session.query(EvidenceItem).filter_by(user_id=user.id).first() is None
        assert db_session.query(Skill).filter_by(user_id=user.id).first() is None
        assert db_session.query(Project).filter_by(user_id=user.id).first() is None
        assert db_session.query(Certification).filter_by(user_id=user.id).first() is None
        assert db_session.query(EducationRecord).filter_by(user_id=user.id).first() is None
