"""Small in-process sliding-window rate limiter.

Good enough for a single backend instance. Before scaling out to several instances,
move the counters to Redis or Postgres so limits are shared.
"""

import time
from collections import defaultdict, deque
from typing import Deque, Dict, Optional

from fastapi import HTTPException, Request, status


def client_ip(request: Request) -> str:
    """Best-effort client IP behind Railway/Cloudflare proxies."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


class SlidingWindowLimiter:
    def __init__(self, limit: int, window_seconds: float):
        self.limit = limit
        self.window = window_seconds
        self._hits: Dict[str, Deque[float]] = defaultdict(deque)

    def _prune(self, key: str, now: float) -> Deque[float]:
        hits = self._hits[key]
        while hits and now - hits[0] > self.window:
            hits.popleft()
        return hits

    def retry_after(self, key: str) -> Optional[int]:
        """Seconds until the key may try again, or None if it is under the limit."""
        now = time.monotonic()
        hits = self._prune(key, now)
        if len(hits) < self.limit:
            return None
        return max(1, int(self.window - (now - hits[0])) + 1)

    def hit(self, key: str) -> None:
        now = time.monotonic()
        self._prune(key, now).append(now)

    def reset(self, key: Optional[str] = None) -> None:
        if key is None:
            self._hits.clear()
        else:
            self._hits.pop(key, None)

    def check(self, key: str, message: str) -> None:
        """Raise 429 if the key is over the limit."""
        wait = self.retry_after(key)
        if wait is not None:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=message,
                headers={"Retry-After": str(wait)},
            )
