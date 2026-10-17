from typing import List, Optional, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application runtime configuration settings."""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_NAME: str = "RemoteJobs Public Platform API"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Database Settings - PostgreSQL default with SQLite fallback for local test/dev
    DATABASE_URL: str = "sqlite:///./remotejobs_dev.db"

    # Security & Auth Settings
    SECRET_KEY: str = "dev-secret-key-change-in-production-0987654321"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # AI Gateway / Model Settings (Supports LiteLLM, AWS deployment, Ollama, OpenAI)
    LLM_PROVIDER: str = "litellm"  # "litellm", "openai", "ollama", "mock"
    LLM_BASE_URL: str = "http://localhost:4000/v1"
    LLM_API_KEY: Optional[str] = "sk-dev-litellm-key"
    LLM_MODEL_PRESCREEN: str = "fast"
    LLM_MODEL_ASSESSMENT: str = "reasoning"
    LLM_MODEL_EXTRACTION: str = "fast"
    LLM_MODEL_TAILORING: str = "reasoning"
    LLM_MODEL_COVER_LETTER: str = "fast"
    LLM_TIMEOUT_SECONDS: float = 15.0
    LLM_MAX_RETRIES: int = 2
    LLM_FALLBACK_TO_HEURISTICS: bool = True

    # Orchestrator / AWS Control Plane Infrastructure
    ORCHESTRATOR_URL: str = "http://localhost:8000"
    AWS_INFERENCE_ENDPOINT: Optional[str] = None

    # CORS Settings
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    @field_validator("CORS_ORIGINS")
    @classmethod
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            v_trimmed = v.strip()
            if v_trimmed.startswith("[") and v_trimmed.endswith("]"):
                import json
                try:
                    parsed = json.loads(v_trimmed)
                    if isinstance(parsed, list):
                        return [str(x).strip() for x in parsed]
                except Exception:
                    pass
            return [origin.strip() for origin in v_trimmed.split(",") if origin.strip()]
        return v


settings = Settings()
