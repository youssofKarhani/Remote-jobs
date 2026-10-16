"""FastAPI application routers."""

from app.routers.auth import router as auth_router
from app.routers.cv import router as cv_router
from app.routers.jobs import router as jobs_router
from app.routers.preferences import router as preferences_router
from app.routers.profile import router as profile_router
from app.routers.matching import router as matching_router
from app.routers.tailoring import router as tailoring_router
from app.routers.cover_letters import router as cover_letters_router
from app.routers.applications import router as applications_router

__all__ = [
    "auth_router",
    "cv_router",
    "profile_router",
    "preferences_router",
    "jobs_router",
    "matching_router",
    "tailoring_router",
    "cover_letters_router",
    "applications_router",
]

