"""Authentication router for user registration, login, and profile retrieval."""

import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.rate_limit import SlidingWindowLimiter, client_ip
from app.core.security import create_access_token, get_current_user, get_password_hash, verify_password
from app.database import get_db
from app.models.preference import CandidatePreference
from app.models.profile import CandidateProfile
from app.models.user import User
from app.schemas.auth import AccountDeleteRequest, Token, UserCreate, UserLogin, UserRead
from app.services.account_service import delete_user_account, export_user_data

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Brute-force protection. Per-IP counts every attempt; per-account counts only failures,
# so a forgotten password locks out the guesser, not the whole network.
login_ip_limiter = SlidingWindowLimiter(limit=30, window_seconds=15 * 60)
login_account_limiter = SlidingWindowLimiter(limit=8, window_seconds=15 * 60)
register_ip_limiter = SlidingWindowLimiter(limit=10, window_seconds=60 * 60)

_TOO_MANY_LOGINS = "Too many sign-in attempts. Please wait a few minutes and try again."


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register_user(
    request: Request,
    user_in: UserCreate,
    db: Session = Depends(get_db),
):
    """Register a new user account."""
    ip = client_ip(request)
    register_ip_limiter.check(ip, "Too many accounts created from this network. Please try again later.")
    register_ip_limiter.hit(ip)

    existing_user = db.query(User).filter(User.email == user_in.email.lower().strip()).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists.",
        )

    hashed_pw = get_password_hash(user_in.password)
    new_user = User(
        email=user_in.email.lower().strip(),
        hashed_password=hashed_pw,
        full_name=user_in.full_name.strip(),
        is_active=True,
    )
    db.add(new_user)
    db.flush()

    # Initialize default candidate profile
    profile = CandidateProfile(
        user_id=new_user.id,
        headline="Software Professional",
        is_verified=False,
    )
    db.add(profile)

    # Initialize default candidate preferences
    preferences = CandidatePreference(
        user_id=new_user.id,
        target_roles=[],
        locations=["Germany"],
        remote_only=False,
        job_types=["Full Time"],
    )
    db.add(preferences)

    db.commit()
    db.refresh(new_user)
    return new_user


def _authenticate(request: Request, raw_email: str, password: str, db: Session) -> Token:
    """Shared, throttled credential check for both login endpoints."""
    email = raw_email.lower().strip()
    ip = client_ip(request)
    login_ip_limiter.check(ip, _TOO_MANY_LOGINS)
    login_account_limiter.check(email, _TOO_MANY_LOGINS)
    login_ip_limiter.hit(ip)

    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        login_account_limiter.hit(email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    login_account_limiter.reset(email)
    access_token = create_access_token(subject=user.id)
    return Token(access_token=access_token, token_type="bearer")


@router.post("/login", response_model=Token)
async def login_for_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """OAuth2 compatible token login, getting an access token for future requests."""
    return _authenticate(request, form_data.username, form_data.password, db)


@router.post("/login/json", response_model=Token)
async def login_json(
    request: Request,
    credentials: UserLogin,
    db: Session = Depends(get_db),
):
    """JSON-based login endpoint for frontend client flexibility."""
    return _authenticate(request, credentials.email, credentials.password, db)


@router.get("/me", response_model=UserRead)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
):
    """Get current authenticated user info."""
    return current_user


@router.get("/me/export")
async def export_my_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Download everything stored about the signed-in user as JSON (GDPR Art. 15 and 20)."""
    data = export_user_data(db, current_user)
    filename = f"findjobfit-data-{datetime.utcnow():%Y%m%d}.json"
    return Response(
        content=json.dumps(data, ensure_ascii=False, indent=2),
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="{filename}"', "Cache-Control": "no-store"},
    )


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_my_account(
    payload: AccountDeleteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Permanently delete the signed-in user's account and all their data (GDPR Art. 17)."""
    if not verify_password(payload.password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Password is incorrect. Your account was not deleted.",
        )
    delete_user_account(db, current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
