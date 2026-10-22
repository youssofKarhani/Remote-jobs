from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import init_db
from app.routers import (
    applications_router,
    auth_router,
    cover_letters_router,
    cv_router,
    jobs_router,
    matching_router,
    preferences_router,
    profile_router,
    tailoring_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure database schema is initialized on startup
    try:
        init_db()
    except Exception as e:
        print(f"Warning: Failed to auto-initialize DB on startup: {e}")
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Multi-user AI Job Application and Discovery Platform API",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API v1 Routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(cv_router, prefix="/api/v1")
app.include_router(profile_router, prefix="/api/v1")
app.include_router(preferences_router, prefix="/api/v1")
app.include_router(jobs_router, prefix="/api/v1")
app.include_router(matching_router, prefix="/api/v1")
app.include_router(tailoring_router, prefix="/api/v1")
app.include_router(cover_letters_router, prefix="/api/v1")
app.include_router(applications_router, prefix="/api/v1")


@app.get("/api/health", tags=["Health"])
async def health_check():
    """Health check probe endpoint."""
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "llm_provider": settings.LLM_PROVIDER,
    }


@app.get("/api/v1/ai/status", tags=["AI Gateway"])
async def get_ai_status():
    """Diagnostic endpoint to inspect AI Gateway connection, models, and liveliness."""
    from app.integrations.llm_ai_service import ai_service
    return await ai_service.check_health()


@app.post("/api/v1/ai/wake", tags=["AI Gateway"])
async def wake_ai_infrastructure():
    """Trigger the Serverless Wake endpoint to start scale-to-zero AWS infrastructure and refresh IP."""
    from app.integrations.llm_ai_service import ai_service
    wake_triggered = await ai_service.trigger_wake()
    health = await ai_service.check_health()
    return {
        "wake_triggered": wake_triggered,
        "wake_url_configured": bool(ai_service.wake_url),
        "orchestrator_url": ai_service.orchestrator_url,
        "ai_status": health,
    }


@app.get("/", tags=["Root"])
async def root():
    """Root landing endpoint."""
    return {
        "message": "Welcome to RemoteJobs Public Platform API",
        "docs": "/docs",
        "health": "/api/health",
    }
