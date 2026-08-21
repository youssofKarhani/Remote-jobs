import os
import tempfile
from pathlib import Path
from alembic.config import Config
from alembic import command
from sqlalchemy import create_engine, inspect


def test_alembic_upgrade_and_downgrade():
    """Verify that Alembic migrations run cleanly up to head and down to base."""
    # Create a temporary sqlite database file
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        tmp_db_path = tmp.name

    try:
        db_url = f"sqlite:///{tmp_db_path}"
        backend_dir = Path(__file__).resolve().parent.parent
        alembic_ini_path = backend_dir / "alembic.ini"

        alembic_cfg = Config(str(alembic_ini_path))
        alembic_cfg.set_main_option("sqlalchemy.url", db_url)
        alembic_cfg.set_main_option("script_location", str(backend_dir / "alembic"))

        # Run upgrade to head
        command.upgrade(alembic_cfg, "head")

        # Inspect created tables in database
        engine = create_engine(db_url)
        inspector = inspect(engine)
        tables = set(inspector.get_table_names())

        expected_tables = {
            "users",
            "candidate_profiles",
            "candidate_preferences",
            "experience_records",
            "evidence_items",
            "skills",
            "projects",
            "certifications",
            "education_records",
            "companies",
            "job_sources",
            "jobs",
            "job_source_records",
            "alembic_version",
        }

        assert expected_tables.issubset(tables), f"Missing tables: {expected_tables - tables}"

        # Verify columns on users table
        user_cols = {col["name"] for col in inspector.get_columns("users")}
        assert {"id", "email", "hashed_password", "full_name", "is_active", "is_superuser"}.issubset(user_cols)

        # Verify columns on evidence_items table
        evidence_cols = {col["name"] for col in inspector.get_columns("evidence_items")}
        assert {"id", "user_id", "experience_record_id", "stable_id", "raw_text", "category", "is_verified"}.issubset(evidence_cols)

        # Test downgrade back to base
        command.downgrade(alembic_cfg, "base")

        # Re-inspect to confirm all application tables dropped
        inspector_after = inspect(engine)
        remaining_tables = set(inspector_after.get_table_names())
        assert remaining_tables == {"alembic_version"}

        engine.dispose()

    finally:
        if os.path.exists(tmp_db_path):
            try:
                os.remove(tmp_db_path)
            except OSError:
                pass
