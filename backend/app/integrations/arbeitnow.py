"""Arbeitnow external job board integration implementing JobSource protocol."""

import asyncio
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import httpx

from app.protocols.job_source import JobSource, RawJobDTO


class ArbeitnowSource:
    """Connector for Arbeitnow public job board API (https://arbeitnow.com/api/job-board-api)."""

    name: str = "arbeitnow"
    base_url: str = "https://arbeitnow.com/api/job-board-api"

    def __init__(self, base_url: Optional[str] = None, timeout_seconds: float = 10.0):
        if base_url:
            self.base_url = base_url
        self.timeout = timeout_seconds

    async def fetch_jobs(
        self,
        page: int = 1,
        since: Optional[datetime] = None,
        max_retries: int = 3,
    ) -> List[RawJobDTO]:
        """Fetch a page of job postings from Arbeitnow with exponential backoff on HTTP 429."""
        url = f"{self.base_url}?page={page}"
        headers = {
            "User-Agent": "RemoteJobsPublicPlatform/1.0",
            "Accept": "application/json",
        }

        retries = 0
        backoff = 1.0

        while retries <= max_retries:
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.get(url, headers=headers)

                    if response.status_code == 429:
                        # Rate limited: check Retry-After header or use exponential backoff
                        retry_after = response.headers.get("Retry-After")
                        wait_seconds = float(retry_after) if retry_after else backoff
                        await asyncio.sleep(min(wait_seconds, 10.0))
                        backoff *= 2.0
                        retries += 1
                        continue

                    response.raise_for_status()
                    data = response.json()
                    raw_items = data.get("data", [])
                    return self._parse_items(raw_items, since=since)

            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429 and retries < max_retries:
                    retries += 1
                    await asyncio.sleep(backoff)
                    backoff *= 2.0
                    continue
                raise
            except (httpx.RequestError, httpx.TimeoutException):
                if retries < max_retries:
                    retries += 1
                    await asyncio.sleep(backoff)
                    backoff *= 2.0
                    continue
                raise

        return []

    def _parse_items(
        self,
        raw_items: List[Dict[str, Any]],
        since: Optional[datetime] = None,
    ) -> List[RawJobDTO]:
        """Transform raw JSON items into standardized RawJobDTO objects."""
        jobs: List[RawJobDTO] = []

        for item in raw_items:
            # Parse published timestamp from unix epoch or ISO string
            created_at_val = item.get("created_at")
            if isinstance(created_at_val, (int, float)):
                published_at = datetime.fromtimestamp(created_at_val, tz=timezone.utc)
            elif isinstance(created_at_val, str):
                try:
                    published_at = datetime.fromisoformat(created_at_val)
                    if published_at.tzinfo is None:
                        published_at = published_at.replace(tzinfo=timezone.utc)
                except ValueError:
                    published_at = datetime.now(timezone.utc)
            else:
                published_at = datetime.now(timezone.utc)

            # Check since filter if provided
            if since and published_at < since:
                continue

            slug = item.get("slug") or f"job-{item.get('title', 'job')}"
            title = item.get("title", "Untitled Job")
            company_name = item.get("company_name", "Unknown Company")
            location = item.get("location", "Remote")
            remote = bool(item.get("remote", False))
            url = item.get("url") or f"https://arbeitnow.com/jobs/companies/{slug}"
            description = item.get("description", "")
            tags = item.get("tags") or []
            job_types = item.get("job_types") or []

            jobs.append(
                RawJobDTO(
                    source_name=self.name,
                    external_id=slug,
                    external_url=url,
                    title=title,
                    company_name=company_name,
                    location=location,
                    remote=remote,
                    description=description,
                    tags=tags,
                    job_types=job_types,
                    published_at=published_at,
                    raw_data=item,
                )
            )

        return jobs
