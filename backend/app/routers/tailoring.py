"""CV Tailoring and Document Streaming Router."""

import os
from pathlib import Path
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.config import settings
from app.database import get_db
from app.models.document import GeneratedDocument
from app.models.job import Job
from app.models.user import User
from app.schemas.document import GeneratedDocumentRead, TailorCVRequest
from app.services.cv_tailoring_service import cv_tailoring_service

router = APIRouter(tags=["CV Tailoring & Documents"])


@router.post("/jobs/{job_id}/tailor-cv", response_model=GeneratedDocumentRead)
async def tailor_cv_for_job(
    job_id: uuid.UUID,
    payload: TailorCVRequest = TailorCVRequest(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Generate tailored .docx CV strictly from verified candidate evidence."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job '{job_id}' not found.",
        )

    try:
        gen_doc = await cv_tailoring_service.generate_tailored_cv(
            db=db,
            user=current_user,
            job=job,
            max_bullets_per_role=payload.max_bullets_per_role,
            require_verified=payload.require_verified if settings.FEATURE_EVIDENCE_VERIFICATION else False,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    doc_read = GeneratedDocumentRead(
        id=gen_doc.id,
        user_id=gen_doc.user_id,
        job_id=gen_doc.job_id,
        document_type=gen_doc.document_type,
        format=gen_doc.format,
        verification_status=gen_doc.verification_status or "unverified",
        selected_evidence_ids=gen_doc.selected_evidence_ids,
        download_url=f"/api/v1/documents/{gen_doc.id}/download",
        created_at=gen_doc.created_at,
    )
    return doc_read


@router.get("/documents/{document_id}", response_model=GeneratedDocumentRead)
async def get_document_info(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve metadata for a generated document."""
    doc = db.query(GeneratedDocument).filter(
        GeneratedDocument.id == document_id,
        GeneratedDocument.user_id == current_user.id,
    ).first()

    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document '{document_id}' not found.",
        )

    return GeneratedDocumentRead(
        id=doc.id,
        user_id=doc.user_id,
        job_id=doc.job_id,
        document_type=doc.document_type,
        format=doc.format,
        verification_status=doc.verification_status or "unverified",
        selected_evidence_ids=doc.selected_evidence_ids,
        download_url=f"/api/v1/documents/{doc.id}/download",
        created_at=doc.created_at,
    )


@router.get("/documents/{document_id}/download")
async def download_generated_document(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Download the generated .docx file attachment."""
    doc = db.query(GeneratedDocument).filter(
        GeneratedDocument.id == document_id,
        GeneratedDocument.user_id == current_user.id,
    ).first()

    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document '{document_id}' not found.",
        )

    filename = f"CV_Tailored_{doc.id.hex[:8]}.docx"

    if os.path.exists(doc.file_path):
        return FileResponse(
            path=doc.file_path,
            filename=filename,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )

    # Cloud/Railway container resilience: stream from database bytes if disk file was wiped
    if doc.file_bytes:
        from fastapi.responses import Response
        return Response(
            content=doc.file_bytes,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Document file not found on disk.",
    )
