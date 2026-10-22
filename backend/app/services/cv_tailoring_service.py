"""CV Tailoring and Document Generation Pipeline Service.

Connects:
select_cv_evidence -> validate_selected_evidence_ids -> resolve_verified_evidence_text -> docxtpl
"""

import os
from pathlib import Path
import uuid
from typing import Any, Dict, List, Optional
from docxtpl import DocxTemplate
from sqlalchemy.orm import Session

from app.integrations.llm_ai_service import ai_service
from app.models.document import GeneratedDocument
from app.models.evidence import (
    Certification,
    EducationRecord,
    EvidenceItem,
    ExperienceRecord,
    Project,
    Skill,
)
from app.models.job import Job
from app.models.profile import CandidateProfile
from app.models.user import User
from app.protocols.ai_service import AIService, CVSelectionResult
from app.services.evidence_validation import (
    compute_evidence_verification_status,
    get_user_allowed_evidence_ids,
    resolve_verified_evidence_text,
    validate_selected_evidence_ids,
)


class CVTailoringService:
    """Orchestrates static CV tailoring from verified evidence bank using docxtpl."""

    def __init__(self, ai_gateway: Optional[AIService] = None):
        self.ai = ai_gateway or ai_service
        self.template_path = Path(__file__).resolve().parent.parent / "templates" / "cv" / "modern_template.docx"
        self.output_dir = Path(__file__).resolve().parent.parent.parent / "storage" / "documents"

    async def generate_tailored_cv(
        self,
        db: Session,
        user: User,
        job: Job,
        max_bullets_per_role: int = 4,
        require_verified: bool = False,
    ) -> GeneratedDocument:
        """Tailor and render a .docx CV strictly from candidate evidence.
        
        If require_verified=True, restricts selection to verified evidence (partner-ready).
        If require_verified=False, selects across all candidate evidence without modifying DB flags.
        """
        # 1. Retrieve CandidateProfile (auto-create default if not present)
        profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == user.id).first()
        if not profile:
            profile = CandidateProfile(
                user_id=user.id,
                headline="Software Professional",
                is_verified=False,
            )
            db.add(profile)
            db.commit()
            db.refresh(profile)

        # 2. Get allowed evidence IDs scoped strictly to candidate
        allowed_ids = get_user_allowed_evidence_ids(db, user.id, verified_only=require_verified)
        if not allowed_ids:
            if require_verified:
                has_any = get_user_allowed_evidence_ids(db, user.id, verified_only=False)
                if has_any:
                    raise ValueError("No verified candidate evidence items found. Please verify your evidence or generate with require_verified=False.")
            raise ValueError("No candidate evidence items found. Please upload a CV first.")

        grouped_allowed: Dict[str, List[str]] = {
            "experience_bullets": [sid for sid in allowed_ids if sid.startswith("EXP")],
            "skills": [sid for sid in allowed_ids if sid.startswith("SKILL")],
            "projects": [sid for sid in allowed_ids if sid.startswith("PROJ")],
            "certifications": [sid for sid in allowed_ids if sid.startswith("CERT")],
            "education": [sid for sid in allowed_ids if sid.startswith("EDU")],
        }

        job_details = {
            "id": str(job.id),
            "title": job.title,
            "company_name": job.company_name,
            "location": job.location,
            "tags": job.tags or [],
            "description": job.description,
        }

        # 3. LLM Evidence Selection (IDs only)
        selection: CVSelectionResult = await self.ai.select_cv_evidence(
            job_details=job_details,
            allowed_evidence_ids=grouped_allowed,
            max_bullets_per_role=max_bullets_per_role,
        )

        # Fallback if selection was empty
        if not selection.experience_bullet_ids:
            selection.experience_bullet_ids = grouped_allowed["experience_bullets"][:6]
        if not selection.skill_ids:
            selection.skill_ids = grouped_allowed["skills"][:10]
        if not selection.project_ids:
            selection.project_ids = grouped_allowed["projects"][:3]
        if not selection.certification_ids:
            selection.certification_ids = grouped_allowed["certifications"][:3]

        # Ensure experiences with evidence have representation
        experiences_db = (
            db.query(ExperienceRecord)
            .filter(ExperienceRecord.user_id == user.id)
            .order_by(ExperienceRecord.display_order)
            .all()
        )

        selected_bullet_id_set = set(selection.experience_bullet_ids)
        for exp in experiences_db:
            exp_q = (
                db.query(EvidenceItem)
                .filter(
                    EvidenceItem.user_id == user.id,
                    EvidenceItem.experience_record_id == exp.id,
                )
            )
            if require_verified:
                exp_q = exp_q.filter(EvidenceItem.is_verified.is_(True))
            exp_bullets = exp_q.order_by(EvidenceItem.display_order).all()

            has_selected = any(b.stable_id in selected_bullet_id_set for b in exp_bullets)
            if not has_selected and exp_bullets:
                fallback_sid = exp_bullets[0].stable_id
                if fallback_sid in allowed_ids:
                    selection.experience_bullet_ids.append(fallback_sid)
                    selected_bullet_id_set.add(fallback_sid)

        all_selected = (
            selection.experience_bullet_ids
            + selection.skill_ids
            + selection.project_ids
            + selection.certification_ids
        )

        # 4. Strict Non-Negotiable Validation
        validate_selected_evidence_ids(all_selected, allowed_ids)

        # 5. Resolve verified/allowed text from database
        resolved_items = resolve_verified_evidence_text(
            db,
            user.id,
            all_selected,
            verified_only=require_verified,
        )

        # 6. Build document context strictly from resolved verified items
        exp_bullets_map: Dict[uuid.UUID, List[str]] = {}
        for item in resolved_items:
            if item.get("type") == "experience_bullet":
                exp_rec_id = item.get("experience_record_id")
                if exp_rec_id:
                    exp_bullets_map.setdefault(exp_rec_id, []).append(item["text"])

        experiences_context = []
        for exp in experiences_db:
            bullets = exp_bullets_map.get(exp.id, [])
            if bullets:
                experiences_context.append({
                    "role_title": exp.role_title,
                    "company_name": exp.company_name,
                    "location": exp.location or "Remote",
                    "start_date": exp.start_date,
                    "end_date": exp.end_date or ("Present" if exp.is_current else ""),
                    "bullets": bullets,
                })

        skills_context = [
            {"name": item.get("name", "")}
            for item in resolved_items
            if item.get("type") == "skill"
        ]

        projects_context = [
            {
                "title": item.get("title", ""),
                "technologies": ", ".join(item.get("technologies", [])),
                "description": item.get("description", ""),
            }
            for item in resolved_items
            if item.get("type") == "project"
        ]

        certifications_context = [
            {
                "name": item.get("name", ""),
                "issuing_organization": item.get("issuing_organization", ""),
                "issue_date": item.get("issue_date", ""),
            }
            for item in resolved_items
            if item.get("type") == "certification"
        ]

        education_db = (
            db.query(EducationRecord)
            .filter(EducationRecord.user_id == user.id)
            .order_by(EducationRecord.display_order)
            .all()
        )
        education_context = [
            {
                "degree": edu.degree,
                "field_of_study": edu.field_of_study,
                "institution": edu.institution,
                "start_date": edu.start_date or "",
                "end_date": edu.end_date or "",
            }
            for edu in education_db
        ]

        context = {
            "candidate_name": user.full_name or "Candidate",
            "headline": profile.headline or "Software Professional",
            "email": user.email,
            "phone": profile.phone or "",
            "location": profile.location or "Remote",
            "linkedin_url": profile.linkedin_url or "",
            "github_url": profile.github_url or "",
            "portfolio_url": profile.portfolio_url or "",
            "summary": profile.summary or "Dedicated and experienced engineer.",
            "skills": skills_context,
            "experiences": experiences_context,
            "projects": projects_context,
            "certifications": certifications_context,
            "education": education_context,
        }

        # 7. Render document via docxtpl
        doc_id = uuid.uuid4()
        user_out_dir = self.output_dir / str(user.id)
        user_out_dir.mkdir(parents=True, exist_ok=True)
        file_path = user_out_dir / f"tailored_cv_{doc_id}.docx"

        doc = DocxTemplate(str(self.template_path))
        doc.render(context)
        doc.save(str(file_path))

        # Read binary file for persistent cloud/Railway storage resilience
        file_bytes = file_path.read_bytes() if file_path.exists() else None

        # Determine verification trust status
        verification_status = compute_evidence_verification_status(db, user.id, all_selected)

        # 8. Persist GeneratedDocument in database with backup bytes and verification tier
        gen_doc = GeneratedDocument(
            id=doc_id,
            user_id=user.id,
            job_id=job.id,
            document_type="cv",
            format="docx",
            file_path=str(file_path),
            file_bytes=file_bytes,
            verification_status=verification_status,
            selected_evidence_ids=all_selected,
        )
        db.add(gen_doc)
        db.commit()
        db.refresh(gen_doc)

        return gen_doc


cv_tailoring_service = CVTailoringService()
