"""Add document verification status, byte backup, and assessment evaluation mode

Revision ID: 0003_add_doc_verification_and_eval_mode
Revises: 0002_add_job_matching
Create Date: 2026-10-18 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0003_add_doc_verification_and_eval_mode"
down_revision: Union[str, None] = "0002_add_job_matching"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add verification_status and file_bytes to generated_documents
    op.add_column(
        "generated_documents",
        sa.Column("verification_status", sa.String(length=50), nullable=False, server_default="unverified"),
    )
    op.add_column(
        "generated_documents",
        sa.Column("file_bytes", sa.LargeBinary(), nullable=True),
    )

    # 2. Add evaluation_mode to job_assessments
    op.add_column(
        "job_assessments",
        sa.Column("evaluation_mode", sa.String(length=50), nullable=False, server_default="ai"),
    )


def downgrade() -> None:
    op.drop_column("job_assessments", "evaluation_mode")
    op.drop_column("generated_documents", "file_bytes")
    op.drop_column("generated_documents", "verification_status")
