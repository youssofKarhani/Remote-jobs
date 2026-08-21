from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import (
    auth_router,
    cv_router,
    jobs_router,
    preferences_router,
    profile_router,
)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Multi-user AI Job Application and Discovery Platform API",
    docs_url="/docs",
    redoc_url="/redoc",
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


@app.get("/api/health", tags=["Health"])
async def health_check():
    """Health check probe endpoint."""
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }


@app.get("/", tags=["Root"])
async def root():
    """Root landing endpoint."""
    return {
        "message": "Welcome to RemoteJobs Public Platform API",
        "docs": "/docs",
        "health": "/api/health",
    }

