"""Production configuration must fail fast instead of running with unsafe defaults."""

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.config import DEFAULT_DEV_SECRET_KEY, Settings

STRONG_KEY = "x" * 64


def _settings(**overrides) -> Settings:
    # _env_file=None: don't let the developer's local .env leak into these assertions.
    return Settings(_env_file=None, **overrides)


def test_development_allows_defaults():
    s = _settings(ENVIRONMENT="development")
    assert s.SECRET_KEY == DEFAULT_DEV_SECRET_KEY
    assert s.is_production is False


def test_debug_is_off_by_default():
    assert _settings().DEBUG is False


@pytest.mark.parametrize("env", ["production", "prod", "Production"])
def test_production_rejects_default_secret_key(env):
    with pytest.raises(ValidationError, match="SECRET_KEY"):
        _settings(ENVIRONMENT=env)


def test_production_rejects_short_secret_key():
    with pytest.raises(ValidationError, match="SECRET_KEY"):
        _settings(ENVIRONMENT="production", SECRET_KEY="too-short")


def test_production_rejects_debug():
    with pytest.raises(ValidationError, match="DEBUG"):
        _settings(ENVIRONMENT="production", SECRET_KEY=STRONG_KEY, DEBUG=True)


def test_production_drops_localhost_cors_origins():
    s = _settings(
        ENVIRONMENT="production",
        SECRET_KEY=STRONG_KEY,
        CORS_ORIGINS="https://findjobfit.de,http://localhost:3000,http://127.0.0.1:3000",
    )
    assert s.CORS_ORIGINS == ["https://findjobfit.de"]


def test_ai_diagnostics_require_superuser(client: TestClient, auth_headers: dict):
    for method, path in (("get", "/api/v1/ai/status"), ("post", "/api/v1/ai/wake")):
        assert getattr(client, method)(path).status_code == 401
        assert getattr(client, method)(path, headers=auth_headers).status_code == 403
