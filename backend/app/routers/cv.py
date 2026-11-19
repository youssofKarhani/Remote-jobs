"""CV Upload and Document Extraction router."""

import time
import uuid
from collections import defaultdict, deque
from typing import Deque, Dict, Optional, Tuple

from fastapi import APIRouter, Depends, File, HTTPException, Query, Request, UploadFile, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database import get_db
from app.models.user import User
from app.protocols.ai_service import ExtractedEvidenceBankDraft
from app.schemas.cv import (
    CVPreview,
    CVPreviewCertification,
    CVPreviewCounts,
    CVPreviewEducation,
    CVPreviewExperience,
    CVPreviewProject,
    CVPreviewResponse,
    CVRawTextRequest,
    CVStatusResponse,
    CVUploadResponse,
)
from app.services.cv_extraction_service import cv_extraction_service
from app.services.document_parser import (
    DocumentParsingError,
    EmptyDocumentError,
    UnsupportedFileFormatError,
    parse_document,
    parse_document_detailed,
)

router = APIRouter(prefix="/cv", tags=["CV Ingestion"])


# In-memory registry for CV extraction task status tracking
_cv_task_store: dict[str, dict] = {}


@router.post("/upload", response_model=CVUploadResponse, status_code=status.HTTP_200_OK)
async def upload_cv_document(
    file: UploadFile = File(...),
    replace_existing: bool = Query(False, description="Whether to replace all existing candidate evidence"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Upload PDF, DOCX, or TXT resume and extract into Candidate Evidence Bank."""
    task_id = f"task_{uuid.uuid4().hex[:12]}"
    filename = file.filename or "resume.pdf"

    _cv_task_store[task_id] = {
        "status": "processing",
        "progress_percent": 25,
        "message": f"Parsing document {filename}...",
        "user_id": str(current_user.id),
    }

    # Read binary content (limit 15MB)
    contents = await file.read()
    if len(contents) > 15 * 1024 * 1024:
        _cv_task_store[task_id] = {
            "status": "failed",
            "progress_percent": 0,
            "message": "File size exceeds maximum 15MB limit.",
            "user_id": str(current_user.id),
        }
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size exceeds maximum 15MB limit.",
        )

    from app.config import settings

    if settings.CV_HARDENED_PIPELINE_ENABLED:
        try:
            summary = await cv_extraction_service.extract_hardened_document_and_persist(
                db=db,
                user=current_user,
                file_bytes=contents,
                filename=filename,
                replace_existing=replace_existing,
            )
        except EmptyDocumentError as e:
            _cv_task_store[task_id] = {"status": "failed", "progress_percent": 0, "message": str(e), "user_id": str(current_user.id)}
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(e),
            )
        except UnsupportedFileFormatError as e:
            _cv_task_store[task_id] = {"status": "failed", "progress_percent": 0, "message": str(e), "user_id": str(current_user.id)}
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )
        except DocumentParsingError as e:
            _cv_task_store[task_id] = {"status": "failed", "progress_percent": 0, "message": str(e), "user_id": str(current_user.id)}
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Failed to parse document: {str(e)}",
            )
    else:
        try:
            parsed_doc = parse_document_detailed(contents, filename)
            raw_text = parsed_doc.raw_text
            cleaned_text = parsed_doc.cleaned_text
        except EmptyDocumentError as e:
            _cv_task_store[task_id] = {"status": "failed", "progress_percent": 0, "message": str(e), "user_id": str(current_user.id)}
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(e),
            )
        except UnsupportedFileFormatError as e:
            _cv_task_store[task_id] = {"status": "failed", "progress_percent": 0, "message": str(e), "user_id": str(current_user.id)}
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )
        except DocumentParsingError as e:
            _cv_task_store[task_id] = {"status": "failed", "progress_percent": 0, "message": str(e), "user_id": str(current_user.id)}
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Failed to parse document: {str(e)}",
            )

        _cv_task_store[task_id]["progress_percent"] = 60
        _cv_task_store[task_id]["message"] = "Extracting evidence bank entities..."

        summary = await cv_extraction_service.extract_and_persist(
            db=db,
            user=current_user,
            raw_text=raw_text,
            replace_existing=replace_existing,
            cleaned_text=cleaned_text,
        )

    _cv_task_store[task_id] = {
        "status": "completed",
        "progress_percent": 100,
        "message": "Resume extracted successfully into Candidate Evidence Bank.",
        "user_id": str(current_user.id),
    }

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
    replace_existing: bool = Query(False, description="Whether to replace all existing candidate evidence"),
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

    _cv_task_store[task_id] = {
        "status": "processing",
        "progress_percent": 50,
        "message": "Parsing plaintext and extracting evidence...",
        "user_id": str(current_user.id),
    }

    effective_replace = payload.replace_existing if payload.replace_existing is not None else replace_existing
    from app.config import settings

    if settings.CV_HARDENED_PIPELINE_ENABLED:
        summary = await cv_extraction_service.extract_hardened_document_and_persist(
            db=db,
            user=current_user,
            file_bytes=payload.text.strip().encode("utf-8"),
            filename="plain_text_input.txt",
            replace_existing=effective_replace,
        )
    else:
        summary = await cv_extraction_service.extract_and_persist(
            db=db,
            user=current_user,
            raw_text=payload.text.strip(),
            replace_existing=effective_replace,
        )

    _cv_task_store[task_id] = {
        "status": "completed",
        "progress_percent": 100,
        "message": "Plaintext resume extracted successfully into Candidate Evidence Bank.",
        "user_id": str(current_user.id),
    }

    return CVUploadResponse(
        task_id=task_id,
        status="completed",
        filename="plain_text_input.txt",
        message="Plaintext resume extracted successfully into Candidate Evidence Bank.",
        summary=summary,
    )


# ---------------------------------------------------------------------------
# Anonymous preview: extract-only, nothing is persisted.
# Visitors can see what we extracted from their CV, but must sign in to save it.
# ---------------------------------------------------------------------------

MAX_CV_BYTES = 15 * 1024 * 1024
PREVIEW_RATE_LIMIT = 20  # previews per client IP per window
PREVIEW_RATE_WINDOW_SECONDS = 60 * 60

_preview_hits: Dict[str, Deque[float]] = defaultdict(deque)

# Placeholder values the deterministic pipeline fills in for NOT NULL DB columns.
# They are not facts from the CV, so the preview hides them.
_PLACEHOLDER_VALUES = {"issuing organization", "general", "undated", "candidate name"}


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _enforce_preview_rate_limit(request: Request) -> None:
    now = time.monotonic()
    hits = _preview_hits[_client_ip(request)]
    while hits and now - hits[0] > PREVIEW_RATE_WINDOW_SECONDS:
        hits.popleft()
    if len(hits) >= PREVIEW_RATE_LIMIT:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many CV previews from this network. Please sign in to continue.",
        )
    hits.append(now)


def _clean(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() in _PLACEHOLDER_VALUES:
        return None
    return text


def _draft_to_preview(draft: ExtractedEvidenceBankDraft) -> Tuple[CVPreview, CVPreviewCounts]:
    experiences = [
        CVPreviewExperience(
            company_name=_clean(e.company_name),
            role_title=_clean(e.role_title),
            start_date=_clean(e.start_date),
            end_date=_clean(e.end_date),
            is_current=bool(e.is_current),
            bullets=[b.text for b in e.bullets if b.text and b.text.strip()],
        )
        for e in draft.experiences
    ]
    preview = CVPreview(
        headline=_clean(draft.headline),
        summary=_clean(draft.summary),
        location=_clean(draft.location),
        phone=_clean(draft.phone),
        linkedin_url=_clean(draft.linkedin_url),
        github_url=_clean(draft.github_url),
        experiences=experiences,
        skills=[s.name for s in draft.skills if _clean(s.name)],
        projects=[
            CVPreviewProject(title=p.title, description=p.description)
            for p in draft.projects
            if _clean(p.title)
        ],
        education=[
            CVPreviewEducation(
                institution=_clean(e.institution),
                degree=_clean(e.degree),
                field_of_study=_clean(e.field_of_study),
                start_date=_clean(e.start_date),
                end_date=_clean(e.end_date),
            )
            for e in draft.education
        ],
        certifications=[
            CVPreviewCertification(
                name=c.name,
                issuing_organization=_clean(c.issuing_organization),
                issue_date=_clean(c.issue_date),
            )
            for c in draft.certifications
            if _clean(c.name)
        ],
        languages=[lang for lang in draft.languages if _clean(lang)],
    )
    counts = CVPreviewCounts(
        experiences=len(preview.experiences),
        bullets=sum(len(e.bullets) for e in preview.experiences),
        skills=len(preview.skills),
        projects=len(preview.projects),
        education=len(preview.education),
        certifications=len(preview.certifications),
        languages=len(preview.languages),
    )
    return preview, counts


async def _preview_from_bytes(contents: bytes, filename: str) -> CVPreviewResponse:
    from app.config import settings

    parser_mode = None
    degraded = None
    try:
        if settings.CV_HARDENED_PIPELINE_ENABLED:
            draft, _raw_text, audit = await cv_extraction_service.extract_hardened_draft(
                contents, filename=filename
            )
            parser_mode = audit.get("parser_mode")
            degraded = audit.get("degraded")
        else:
            parsed_doc = parse_document_detailed(contents, filename)
            draft = await cv_extraction_service.extract_legacy_draft(
                parsed_doc.raw_text, cleaned_text=parsed_doc.cleaned_text
            )
            parser_mode = draft.extraction_mode
    except EmptyDocumentError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except UnsupportedFileFormatError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except DocumentParsingError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to parse document: {str(e)}",
        )

    preview, counts = _draft_to_preview(draft)
    return CVPreviewResponse(
        filename=filename,
        persisted=False,
        preview=preview,
        counts=counts,
        parser_mode=parser_mode,
        degraded=degraded,
    )


@router.post("/preview", response_model=CVPreviewResponse)
async def preview_cv_document(request: Request, file: UploadFile = File(...)):
    """Extract a PDF/DOCX/TXT CV for an anonymous visitor. Nothing is stored."""
    _enforce_preview_rate_limit(request)
    contents = await file.read()
    if len(contents) > MAX_CV_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size exceeds maximum 15MB limit.",
        )
    return await _preview_from_bytes(contents, file.filename or "resume.pdf")


@router.post("/preview-text", response_model=CVPreviewResponse)
async def preview_cv_text(request: Request, payload: CVRawTextRequest):
    """Extract pasted CV text for an anonymous visitor. Nothing is stored."""
    _enforce_preview_rate_limit(request)
    text = payload.text.strip()
    if len(text) < 20:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Provided resume text is too short to extract meaningful evidence.",
        )
    if len(text.encode("utf-8")) > MAX_CV_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Resume text exceeds maximum 15MB limit.",
        )
    return await _preview_from_bytes(text.encode("utf-8"), "plain_text_input.txt")


@router.get("/status/{task_id}", response_model=CVStatusResponse)
async def get_extraction_status(
    task_id: str,
    current_user: User = Depends(get_current_user),
):
    """Query async status of a background extraction task."""
    task_info = _cv_task_store.get(task_id)
    if task_info:
        return CVStatusResponse(
            task_id=task_id,
            status=task_info.get("status", "completed"),
            progress_percent=task_info.get("progress_percent", 100),
            message=task_info.get("message", "Extraction task completed."),
        )

    return CVStatusResponse(
        task_id=task_id,
        status="completed",
        progress_percent=100,
        message="Extraction completed successfully.",
    )
