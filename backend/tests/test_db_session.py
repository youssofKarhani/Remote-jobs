import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database import get_db, SessionLocal


@pytest.mark.asyncio
async def test_health_check_endpoint():
    """Verify that the FastAPI /api/health endpoint returns 200 OK."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data


def test_get_db_session_dependency():
    """Verify that get_db yields an active session and closes properly."""
    gen = get_db()
    session = next(gen)
    assert session is not None
    assert session.is_active
    try:
        next(gen)
    except StopIteration:
        pass
