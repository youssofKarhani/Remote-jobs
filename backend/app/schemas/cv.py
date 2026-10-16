"""CV Ingestion and Status Pydantic schemas."""

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class CVUploadResponse(BaseModel):
    task_id: str
    status: str
    filename: str
    message: str
    summary: Optional[Dict[str, Any]] = None


class CVStatusResponse(BaseModel):
    task_id: str
    status: str
    progress_percent: int
    message: str
    summary: Optional[Dict[str, Any]] = None


class CVRawTextRequest(BaseModel):
    text: str = Field(min_length=10, description="Raw plaintext resume content")
    replace_existing: Optional[bool] = Field(default=None, description="Whether to replace all existing candidate evidence")

