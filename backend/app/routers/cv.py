"""CV Upload and Document Extraction router."""

import uuid
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.cv import CVRawTextRequest, CVStatusResponse, CVUploadResponse
from app.services.cv_extraction_service import cv_extraction_service
from app.services.document_parser import (
    DocumentParsingError,
    EmptyDocumentError,
    UnsupportedFileFormatError,
    parse_document,
)

router = APIRouter(prefix="/cv", tags=["CV Ingestion"])


@router.post("/upload", response_model=CVUploadResponse, status_code=status.HTTP_200_OK)
async def upload_cv_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Upload PDF, DOCX, or TXT resume and extract into Candidate Evidence Bank."""
    task_id = f"task_{uuid.uuid4().hex[:12]}"
    filename = file.filename or "resume.pdf"

    # Read binary content (limit 15MB)
    contents = await file.read()
    if len(contents) > 15 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size exceeds maximum 15MB limit.",
        )

    try:
        raw_text = parse_document(contents, filename)
    except EmptyDocumentError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )
    except UnsupportedFileFormatError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except DocumentParsingError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to parse document: {str(e)}",
        )

    summary = await cv_extraction_service.extract_and_persist(
        db=db,
        user=current_user,
        raw_text=raw_text,
        replace_existing=True,
    )

    return CVUploadResponse(
        task_id=task_id,
        status="completed",
        filename=filename,
        message="Resume extracted successfully into Candidate Evidence Bank.",
        summary=summary,
    )


@router.post("/parse-text", response_model=CVUploadResponse)
async def parse_raw_cv_text(
    payload: CVRawTextRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Parse raw plain text resume and extract into Candidate Evidence Bank."""
    task_id = f"task_{uuid.uuid4().hex[:12]}"

    if not payload.text.strip() or len(payload.text.strip()) < 20:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Provided resume text is too short to extract meaningful evidence.",
        )

    summary = await cv_extraction_service.extract_and_persist(
        db=db,
        user=current_user,
        raw_text=payload.text.strip(),
        replace_existing=True,
    )

    return CVUploadResponse(
        task_id=task_id,
        status="completed",
        filename="plain_text_input.txt",
        message="Plaintext resume extracted successfully into Candidate Evidence Bank.",
        summary=summary,
    )


@router.get("/status/{task_id}", response_model=CVStatusResponse)
async def get_extraction_status(
    task_id: str,
    current_user: User = Depends(get_current_user),
):
    """Query async status of a background extraction task."""
    return CVStatusResponse(
        task_id=task_id,
        status="completed",
        progress_percent=100,
        message="Extraction completed successfully.",
    )
