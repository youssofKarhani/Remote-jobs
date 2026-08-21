"""FastAPI application routers."""

from app.routers.auth import router as auth_router
from app.routers.cv import router as cv_router
from app.routers.jobs import router as jobs_router
from app.routers.preferences import router as preferences_router
from app.routers.profile import router as profile_router

__all__ = [
    "auth_router",
    "cv_router",
    "profile_router",
    "preferences_router",
    "jobs_router",
]
