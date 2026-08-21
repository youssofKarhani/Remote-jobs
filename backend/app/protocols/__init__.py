"""Protocols and gateway interfaces for AI services and external job sources."""

from app.protocols.ai_service import (
    AIService,
    CoverLetterResult,
    CVSelectionResult,
    ExtractedCertification,
    ExtractedEducation,
    ExtractedEvidenceBankDraft,
    ExtractedEvidenceBullet,
    ExtractedExperience,
    ExtractedProject,
    ExtractedSkill,
    JobAssessmentResult,
    PreScreenResult,
)
from app.protocols.job_source import JobSource, RawJobDTO

__all__ = [
    "AIService",
    "ExtractedEvidenceBullet",
    "ExtractedExperience",
    "ExtractedSkill",
    "ExtractedProject",
    "ExtractedCertification",
    "ExtractedEducation",
    "ExtractedEvidenceBankDraft",
    "PreScreenResult",
    "JobAssessmentResult",
    "CVSelectionResult",
    "CoverLetterResult",
    "JobSource",
    "RawJobDTO",
]
