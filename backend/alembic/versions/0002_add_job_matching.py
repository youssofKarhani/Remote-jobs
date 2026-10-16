"""Add job matching, documents, cover letters, and applications schema

Revision ID: 0002_add_job_matching
Revises: 0001_initial_schema
Create Date: 2026-10-16 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from app.models.types import GUID

# revision identifiers, used by Alembic.
revision: str = "0002_add_job_matching"
down_revision: Union[str, None] = "0001_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. job_matches
    op.create_table(
        "job_matches",
        sa.Column("id", GUID(), nullable=False),
        sa.Column("user_id", GUID(), nullable=False),
        sa.Column("job_id", GUID(), nullable=False),
        sa.Column("overall_score", sa.Integer(), nullable=False),
        sa.Column("recommendation", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="new"),
        sa.Column("matched_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "job_id", name="uq_job_matches_user_job"),
    )
    op.create_index("idx_job_matches_user_id", "job_matches", ["user_id"])
    op.create_index("idx_job_matches_job_id", "job_matches", ["job_id"])

    # 2. job_assessments
    op.create_table(
        "job_assessments",
        sa.Column("id", GUID(), nullable=False),
        sa.Column("job_match_id", GUID(), nullable=False),
        sa.Column("skills_score", sa.Integer(), nullable=False),
        sa.Column("experience_score", sa.Integer(), nullable=False),
        sa.Column("seniority_score", sa.Integer(), nullable=False),
        sa.Column("location_score", sa.Integer(), nullable=False),
        sa.Column("language_score", sa.Integer(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("strengths", sa.JSON().with_variant(postgresql.JSONB(), "postgresql"), nullable=False),
        sa.Column("missing_requirements", sa.JSON().with_variant(postgresql.JSONB(), "postgresql"), nullable=False),
        sa.Column("matching_evidence_ids", sa.JSON().with_variant(postgresql.JSONB(), "postgresql"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["job_match_id"], ["job_matches.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("job_match_id", name="uq_job_assessments_match_id"),
    )
    op.create_index("idx_job_assessments_match_id", "job_assessments", ["job_match_id"])

    # 3. prescreen_results
    op.create_table(
        "prescreen_results",
        sa.Column("id", GUID(), nullable=False),
        sa.Column("user_id", GUID(), nullable=False),
        sa.Column("job_id", GUID(), nullable=False),
        sa.Column("relevant", sa.Boolean(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("reason_codes", sa.JSON().with_variant(postgresql.JSONB(), "postgresql"), nullable=False),
        sa.Column("reasoning", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "job_id", name="uq_prescreen_results_user_job"),
    )
    op.create_index("idx_prescreen_results_user_id", "prescreen_results", ["user_id"])
    op.create_index("idx_prescreen_results_job_id", "prescreen_results", ["job_id"])

    # 4. generated_documents
    op.create_table(
        "generated_documents",
        sa.Column("id", GUID(), nullable=False),
        sa.Column("user_id", GUID(), nullable=False),
        sa.Column("job_id", GUID(), nullable=True),
        sa.Column("document_type", sa.String(length=50), nullable=False),
        sa.Column("format", sa.String(length=20), nullable=False, server_default="docx"),
        sa.Column("file_path", sa.String(length=1024), nullable=False),
        sa.Column("selected_evidence_ids", sa.JSON().with_variant(postgresql.JSONB(), "postgresql"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_generated_docs_user_id", "generated_documents", ["user_id"])
    op.create_index("idx_generated_docs_job_id", "generated_documents", ["job_id"])

    # 5. cover_letters
    op.create_table(
        "cover_letters",
        sa.Column("id", GUID(), nullable=False),
        sa.Column("user_id", GUID(), nullable=False),
        sa.Column("job_id", GUID(), nullable=False),
        sa.Column("strategy", sa.String(length=100), nullable=False, server_default="Technical Depth"),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("referenced_evidence_ids", sa.JSON().with_variant(postgresql.JSONB(), "postgresql"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "job_id", name="uq_cover_letters_user_job"),
    )
    op.create_index("idx_cover_letters_user_id", "cover_letters", ["user_id"])
    op.create_index("idx_cover_letters_job_id", "cover_letters", ["job_id"])

    # 6. applications
    op.create_table(
        "applications",
        sa.Column("id", GUID(), nullable=False),
        sa.Column("user_id", GUID(), nullable=False),
        sa.Column("job_id", GUID(), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="Saved"),
        sa.Column("tailored_cv_id", GUID(), nullable=True),
        sa.Column("cover_letter_id", GUID(), nullable=True),
        sa.Column("applied_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("salary_offered", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tailored_cv_id"], ["generated_documents.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["cover_letter_id"], ["cover_letters.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "job_id", name="uq_applications_user_job"),
    )
    op.create_index("idx_applications_user_id", "applications", ["user_id"])
    op.create_index("idx_applications_job_id", "applications", ["job_id"])
    op.create_index("idx_applications_status", "applications", ["status"])

    # 7. application_events
    op.create_table(
        "application_events",
        sa.Column("id", GUID(), nullable=False),
        sa.Column("application_id", GUID(), nullable=False),
        sa.Column("event_type", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["application_id"], ["applications.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_application_events_app_id", "application_events", ["application_id"])


def downgrade() -> None:
    op.drop_table("application_events")
    op.drop_table("applications")
    op.drop_table("cover_letters")
    op.drop_table("generated_documents")
    op.drop_table("prescreen_results")
    op.drop_table("job_assessments")
    op.drop_table("job_matches")
