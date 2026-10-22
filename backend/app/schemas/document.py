"""Generated Document Pydantic Schemas."""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict


class GeneratedDocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    job_id: Optional[uuid.UUID] = None
    document_type: str
    format: str
    verification_status: str = "unverified"
    selected_evidence_ids: Optional[List[str]] = None
    download_url: Optional[str] = None
    created_at: datetime


class TailorCVRequest(BaseModel):
    max_bullets_per_role: int = 4
    template_name: str = "modern"
    require_verified: bool = False
