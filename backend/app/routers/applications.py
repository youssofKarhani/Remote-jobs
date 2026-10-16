"""Application Tracking System (ATS) Router."""

from datetime import datetime, timezone
from typing import List, Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database import get_db
from app.models.application import Application, ApplicationEvent
from app.models.job import Job
from app.models.user import User
from app.schemas.application import (
    ApplicationRead,
    CreateApplicationRequest,
    UpdateApplicationRequest,
    UpdateApplicationStatusRequest,
)

router = APIRouter(prefix="/applications", tags=["Application Tracking System (ATS)"])

VALID_STAGES = {"Saved", "Applying", "Applied", "Interview", "Offer", "Rejected"}


@router.post("", response_model=ApplicationRead, status_code=status.HTTP_201_CREATED)
async def create_or_track_application(
    payload: CreateApplicationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Track a job in candidate ATS pipeline."""
    job = db.query(Job).filter(Job.id == payload.job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job '{payload.job_id}' not found.",
        )

    # Check if already tracked
    app = db.query(Application).filter(
        Application.user_id == current_user.id,
        Application.job_id == payload.job_id,
    ).first()

    if app:
        # Update existing
        if payload.status:
            app.status = payload.status
        if payload.notes:
            app.notes = payload.notes
        if payload.tailored_cv_id:
            app.tailored_cv_id = payload.tailored_cv_id
        if payload.cover_letter_id:
            app.cover_letter_id = payload.cover_letter_id
        if payload.salary_offered is not None:
            app.salary_offered = payload.salary_offered
    else:
        app = Application(
            user_id=current_user.id,
            job_id=payload.job_id,
            status=payload.status if payload.status in VALID_STAGES else "Saved",
            notes=payload.notes,
            tailored_cv_id=payload.tailored_cv_id,
            cover_letter_id=payload.cover_letter_id,
            salary_offered=payload.salary_offered,
            applied_at=datetime.now(timezone.utc) if payload.status == "Applied" else None,
        )
        db.add(app)
        db.flush()

        # Audit event
        event = ApplicationEvent(
            application_id=app.id,
            event_type="created",
            description=f"Tracked application in '{app.status}' status.",
        )
        db.add(event)

    db.commit()
    db.refresh(app)
    return ApplicationRead.model_validate(app)


@router.get("", response_model=List[ApplicationRead])
async def list_applications(
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by stage"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all candidate applications grouped or filtered by stage."""
    query = db.query(Application).filter(Application.user_id == current_user.id)

    if status_filter:
        query = query.filter(Application.status == status_filter)

    query = query.order_by(Application.updated_at.desc())
    apps = query.all()

    return [ApplicationRead.model_validate(a) for a in apps]


@router.get("/{application_id}", response_model=ApplicationRead)
async def get_application(
    application_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve full details of a specific tracked application."""
    app = db.query(Application).filter(
        Application.id == application_id,
        Application.user_id == current_user.id,
    ).first()

    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application '{application_id}' not found.",
        )

    return ApplicationRead.model_validate(app)


@router.patch("/{application_id}/status", response_model=ApplicationRead)
async def update_application_status(
    application_id: uuid.UUID,
    payload: UpdateApplicationStatusRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Transition application to a new ATS stage with an audit event."""
    app = db.query(Application).filter(
        Application.id == application_id,
        Application.user_id == current_user.id,
    ).first()

    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application '{application_id}' not found.",
        )

    new_stage = payload.status
    old_stage = app.status

    app.status = new_stage
    if new_stage == "Applied" and not app.applied_at:
        app.applied_at = datetime.now(timezone.utc)

    # Record status change event
    event = ApplicationEvent(
        application_id=app.id,
        event_type="status_changed",
        description=f"Stage changed from '{old_stage}' to '{new_stage}'.",
    )
    db.add(event)

    db.commit()
    db.refresh(app)
    return ApplicationRead.model_validate(app)


@router.put("/{application_id}", response_model=ApplicationRead)
async def update_application(
    application_id: uuid.UUID,
    payload: UpdateApplicationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Edit notes, salary, or attached document links for a tracked application."""
    app = db.query(Application).filter(
        Application.id == application_id,
        Application.user_id == current_user.id,
    ).first()

    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application '{application_id}' not found.",
        )

    if payload.status is not None and payload.status != app.status:
        old_status = app.status
        app.status = payload.status
        db.add(
            ApplicationEvent(
                application_id=app.id,
                event_type="status_changed",
                description=f"Stage changed from '{old_status}' to '{payload.status}'.",
            )
        )

    if payload.notes is not None:
        app.notes = payload.notes
    if payload.tailored_cv_id is not None:
        app.tailored_cv_id = payload.tailored_cv_id
    if payload.cover_letter_id is not None:
        app.cover_letter_id = payload.cover_letter_id
    if payload.salary_offered is not None:
        app.salary_offered = payload.salary_offered

    db.commit()
    db.refresh(app)
    return ApplicationRead.model_validate(app)


@router.delete("/{application_id}")
async def delete_application(
    application_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Remove a job from candidate ATS tracker."""
    app = db.query(Application).filter(
        Application.id == application_id,
        Application.user_id == current_user.id,
    ).first()

    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application '{application_id}' not found.",
        )

    db.delete(app)
    db.commit()
    return {"status": "deleted", "id": str(application_id)}
