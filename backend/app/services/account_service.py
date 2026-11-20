"""Account data rights: export everything we hold about a user, and delete it (GDPR Art. 15/17/20)."""

import shutil
import uuid
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.base import Base
from app.models.user import User

# Columns never included in an export.
_EXCLUDED_COLUMNS = {"hashed_password", "file_bytes"}
_DOCUMENT_STORAGE_ROOT = Path(__file__).resolve().parent.parent.parent / "storage" / "documents"


def _jsonable(value: Any) -> Any:
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, uuid.UUID):
        return str(value)
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, bytes):
        return None
    return value


def _user_owned_tables():
    """Tables with a foreign key to users.id, discovered from the schema so new tables are included."""
    tables = []
    for table in Base.metadata.sorted_tables:
        for fk in table.foreign_keys:
            if fk.column.table.name == "users" and fk.column.name == "id":
                tables.append((table, fk.parent))
                break
    return tables


def _child_tables(parent_table) -> List:
    """Tables that hang off a user-owned table (e.g. application events, assessments)."""
    children = []
    for table in Base.metadata.sorted_tables:
        for fk in table.foreign_keys:
            if fk.column.table is parent_table:
                children.append((table, fk.parent, fk.column))
    return children


def _rows(db: Session, table, where) -> List[Dict[str, Any]]:
    result = db.execute(select(table).where(where)).mappings().all()
    return [
        {k: _jsonable(v) for k, v in row.items() if k not in _EXCLUDED_COLUMNS}
        for row in result
    ]


def export_user_data(db: Session, user: User) -> Dict[str, Any]:
    """Everything stored about the user, as plain JSON-serialisable data."""
    export: Dict[str, Any] = {
        "exported_at": datetime.utcnow().isoformat() + "Z",
        "account": {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "created_at": _jsonable(getattr(user, "created_at", None)),
        },
        "data": {},
    }
    for table, user_col in _user_owned_tables():
        export["data"][table.name] = _rows(db, table, user_col == user.id)
        # Rows that belong to the user only through a parent (application events, assessments).
        for child, child_fk_col, parent_col in _child_tables(table):
            if any(fk.column.table.name == "users" for fk in child.foreign_keys):
                continue  # exported on its own as a user-owned table
            owned_parents = select(parent_col).where(user_col == user.id)
            export["data"].setdefault(child.name, []).extend(
                _rows(db, child, child_fk_col.in_(owned_parents))
            )
    return export


def delete_user_account(db: Session, user: User) -> None:
    """Permanently delete the user and everything they own.

    Every foreign key to users.id is ON DELETE CASCADE, so deleting the user row removes
    profile, evidence, preferences, matches, documents, cover letters and applications.
    Generated files on disk are removed afterwards.
    """
    from app.models.document import GeneratedDocument

    user_id = user.id
    file_paths = [p for (p,) in db.execute(
        select(GeneratedDocument.file_path).where(GeneratedDocument.user_id == user_id)
    ).all() if p]

    db.expunge_all()
    db.execute(delete(User).where(User.id == user_id))
    db.commit()

    for path in file_paths:
        try:
            Path(path).unlink(missing_ok=True)
        except OSError:
            pass
    user_dir = _DOCUMENT_STORAGE_ROOT / str(user_id)
    if user_dir.is_dir():
        shutil.rmtree(user_dir, ignore_errors=True)
