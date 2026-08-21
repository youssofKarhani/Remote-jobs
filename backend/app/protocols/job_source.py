"""JobSource Protocol and RawJobDTO schema for external job platform integrations."""

from datetime import datetime
from typing import Any, Dict, List, Optional, Protocol
from pydantic import BaseModel, Field


class RawJobDTO(BaseModel):
    """Raw standardized job listing data transfer object from any external source."""
    source_name: str = Field(description="Name of the source platform (e.g. 'arbeitnow').")
    external_id: str = Field(description="Platform-specific identifier or slug.")
    external_url: str = Field(description="Direct URL to the external job listing.")
    title: str = Field(description="Raw job title.")
    company_name: str = Field(description="Company or employer name.")
    location: str = Field(description="Job location string.")
    remote: bool = Field(default=False, description="Whether the job is remote.")
    description: str = Field(description="Full job description (HTML or markdown).")
    tags: List[str] = Field(default_factory=list, description="Extracted technology/skill tags.")
    job_types: List[str] = Field(default_factory=list, description="e.g. ['Full Time', 'Working Student'].")
    published_at: datetime = Field(description="UTC publication datetime.")
    raw_data: Dict[str, Any] = Field(default_factory=dict, description="Untouched original payload.")


class JobSource(Protocol):
    """Protocol for external job board connectors."""
    name: str

    async def fetch_jobs(
        self,
        page: int = 1,
        since: Optional[datetime] = None,
    ) -> List[RawJobDTO]:
        """Fetch raw job postings from external source with pagination and rate limit handling."""
        ...
