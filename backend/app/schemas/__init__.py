"""Pydantic request and response schemas."""

from app.schemas.auth import Token, TokenData, UserCreate, UserLogin, UserRead
from app.schemas.cv import CVRawTextRequest, CVStatusResponse, CVUploadResponse
from app.schemas.job import (
    JobRead,
    JobSyncRequest,
    JobSyncResponse,
    PaginatedJobsResponse,
    PaginationMeta,
)
from app.schemas.preference import (
    CandidatePreferenceCreate,
    CandidatePreferenceRead,
    CandidatePreferenceUpdate,
)
from app.schemas.profile import (
    CandidateProfileRead,
    CandidateProfileUpdate,
    CertificationRead,
    EducationRecordRead,
    EvidenceBankRead,
    EvidenceItemRead,
    EvidenceItemUpdate,
    EvidenceVerificationRequest,
    EvidenceVerificationResponse,
    ExperienceRecordRead,
    ProjectRead,
    SkillRead,
)

__all__ = [
    "UserCreate",
    "UserLogin",
    "UserRead",
    "Token",
    "TokenData",
    "CandidateProfileRead",
    "CandidateProfileUpdate",
    "EvidenceBankRead",
    "ExperienceRecordRead",
    "EvidenceItemRead",
    "SkillRead",
    "ProjectRead",
    "CertificationRead",
    "EducationRecordRead",
    "EvidenceVerificationRequest",
    "EvidenceVerificationResponse",
    "EvidenceItemUpdate",
    "CandidatePreferenceCreate",
    "CandidatePreferenceRead",
    "CandidatePreferenceUpdate",
    "JobRead",
    "PaginationMeta",
    "PaginatedJobsResponse",
    "JobSyncRequest",
    "JobSyncResponse",
    "CVUploadResponse",
    "CVStatusResponse",
    "CVRawTextRequest",
]
