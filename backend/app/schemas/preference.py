"""Candidate Preference Pydantic schemas."""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class CandidatePreferenceBase(BaseModel):
    target_roles: List[str] = Field(default_factory=list, description="Target job titles (e.g. ['AI Engineer'])")
    locations: List[str] = Field(default_factory=list, description="Target countries or cities (e.g. ['Germany'])")
    remote_only: bool = Field(default=False, description="Enforce 100% remote listings only")
    hybrid_allowed: bool = Field(default=True, description="Allow hybrid workplace roles")
    onsite_allowed: bool = Field(default=True, description="Allow onsite workplace roles")
    job_types: List[str] = Field(default_factory=lambda: ["Full Time"], description="e.g. ['Full Time', 'Working Student']")
    min_salary: Optional[Decimal] = Field(default=None, description="Minimum acceptable annual salary")
    salary_currency: Optional[str] = Field(default="EUR", description="Salary currency code")
    max_seniority: Optional[str] = Field(default=None, description="Max target seniority (e.g. 'Senior')")
    languages: List[str] = Field(default_factory=lambda: ["English"], description="Spoken languages")
    excluded_companies: List[str] = Field(default_factory=list, description="Companies to exclude")
    excluded_keywords: List[str] = Field(default_factory=list, description="Keywords to exclude via word boundary regex")
    preferred_industries: List[str] = Field(default_factory=list, description="Preferred industry domains")


class CandidatePreferenceCreate(CandidatePreferenceBase):
    pass


class CandidatePreferenceUpdate(BaseModel):
    target_roles: Optional[List[str]] = None
    locations: Optional[List[str]] = None
    remote_only: Optional[bool] = None
    hybrid_allowed: Optional[bool] = None
    onsite_allowed: Optional[bool] = None
    job_types: Optional[List[str]] = None
    min_salary: Optional[Decimal] = None
    salary_currency: Optional[str] = None
    max_seniority: Optional[str] = None
    languages: Optional[List[str]] = None
    excluded_companies: Optional[List[str]] = None
    excluded_keywords: Optional[List[str]] = None
    preferred_industries: Optional[List[str]] = None


class CandidatePreferenceRead(CandidatePreferenceBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
