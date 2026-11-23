from pathlib import Path
from typing import List, Optional, Union
from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_BACKEND_ENV_FILE = Path(__file__).resolve().parent.parent / ".env"

# Public, committed default for local development only. Production must override it.
DEFAULT_DEV_SECRET_KEY = "dev-secret-key-change-in-production-0987654321"
_PRODUCTION_NAMES = {"production", "prod"}
_LOCAL_ORIGIN_PREFIXES = ("http://localhost", "http://127.0.0.1", "http://0.0.0.0")


class Settings(BaseSettings):
    """Application runtime configuration settings."""
    model_config = SettingsConfigDict(
        env_file=(str(_BACKEND_ENV_FILE), ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_NAME: str = "RemoteJobs Public Platform API"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    # Off by default: DEBUG turns on SQL echo, which writes every query (including CV text) to logs.
    DEBUG: bool = False

    # Database Settings - PostgreSQL default with SQLite fallback for local test/dev
    DATABASE_URL: str = "sqlite:///./remotejobs_dev.db"

    # Security & Auth Settings
    SECRET_KEY: str = DEFAULT_DEV_SECRET_KEY
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # AI Gateway / Model Settings (Supports LiteLLM, Orchestrator, AWS deployment, Ollama, OpenAI)
    LLM_PROVIDER: str = "orchestrator"  # "litellm", "orchestrator", "aws", "openai", "ollama", "mock"
    LLM_BASE_URL: str = "http://localhost:4000/v1"
    LLM_API_KEY: Optional[str] = "sk-dev-litellm-key"
    LLM_MODEL_PRESCREEN: str = "fast"
    LLM_MODEL_ASSESSMENT: str = "reasoning"
    LLM_MODEL_EXTRACTION: str = "fast"
    LLM_MODEL_TAILORING: str = "reasoning"
    LLM_MODEL_COVER_LETTER: str = "writing"
    LLM_TIMEOUT_SECONDS: float = 60.0
    LLM_MAX_RETRIES: int = 2
    LLM_FALLBACK_TO_HEURISTICS: bool = True

    # Dedicated CV Extraction LLM Service (Phase 5/6: Isolated Ollama Qwen Service)
    CV_EXTRACTION_LLM_BASE_URL: str = "http://localhost:11434"
    CV_EXTRACTION_LLM_MODEL: str = "qwen3:1.7b"
    CV_EXTRACTION_LLM_ENABLED: bool = False
    CV_EXTRACTION_LLM_TIMEOUT_SECONDS: float = 90.0
    CV_EXTRACTION_LLM_MAX_RETRIES: int = 2
    CV_HARDENED_PIPELINE_ENABLED: bool = True

    # Orchestrator / AWS Control Plane Infrastructure (Port 8000 exposed on EC2 Control Plane in eu-north-1)
    ORCHESTRATOR_URL: str = "http://13.60.213.205:8000"
    ORCHESTRATOR_POLL_INTERVAL_SECONDS: float = 0.5
    AWS_INFERENCE_ENDPOINT: Optional[str] = None
    AWS_WAKE_ENDPOINT: Optional[str] = "https://rc2npu70vc.execute-api.eu-north-1.amazonaws.com/wake"

    # [HIDDEN:EVIDENCE_VERIFICATION] Dormant until verification partner is integrated.
    FEATURE_EVIDENCE_VERIFICATION: bool = False

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

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.strip().lower() in _PRODUCTION_NAMES

    @model_validator(mode="after")
    def enforce_production_safety(self) -> "Settings":
        """Fail fast on unsafe production configuration instead of running with it."""
        if not self.is_production:
            return self
        if self.SECRET_KEY == DEFAULT_DEV_SECRET_KEY or len(self.SECRET_KEY) < 32:
            raise ValueError(
                "ENVIRONMENT=production requires SECRET_KEY to be set to a random value of at least "
                "32 characters (the committed development default is public)."
            )
        if self.DEBUG:
            raise ValueError("DEBUG must be false when ENVIRONMENT=production (it logs SQL including CV text).")
        if isinstance(self.CORS_ORIGINS, list):
            self.CORS_ORIGINS = [o for o in self.CORS_ORIGINS if not o.startswith(_LOCAL_ORIGIN_PREFIXES)]
        return self


settings = Settings()
