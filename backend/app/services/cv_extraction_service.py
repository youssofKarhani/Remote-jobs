"""CV Extraction and Evidence Bank Ingestion Pipeline.

Parses raw CV text through the AIService Gateway, assigns immutable stable IDs
(EXP_001, SKILL_001, PROJ_001, CERT_001, EDU_001) scoped per user, and persists
structured entities to PostgreSQL.
"""

import re
import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from app.integrations.llm_ai_service import ai_service
from app.models.evidence import (
    Certification,
    EducationRecord,
    EvidenceItem,
    ExperienceRecord,
    Project,
    Skill,
)
from app.models.profile import CandidateProfile
from app.models.user import User
from app.protocols.ai_service import AIService, ExtractedEvidenceBankDraft


class CVExtractionService:
    """Service to orchestrate document parsing, LLM schema extraction, stable ID assignment, and persistence."""

    def __init__(self, ai_gateway: Optional[AIService] = None):
        self.ai = ai_gateway or ai_service

    def _get_next_index(self, existing_ids: List[str], prefix: str) -> int:
        """Find the next sequential index for a given prefix for a user."""
        max_idx = 0
        pattern = re.compile(rf"^{re.escape(prefix)}_(\d+)$")
        for sid in existing_ids:
            m = pattern.match(sid)
            if m:
                try:
                    val = int(m.group(1))
                    if val > max_idx:
                        max_idx = val
                except ValueError:
                    pass
        return max_idx + 1

    async def extract_and_persist(
        self,
        db: Session,
        user: User,
        raw_text: str,
        replace_existing: bool = False,
        cleaned_text: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Extract entities from raw CV text and persist into candidate's Evidence Bank."""
        draft: ExtractedEvidenceBankDraft = await self.ai.extract_cv_to_evidence_bank(raw_text)
        if cleaned_text and not draft.cleaned_cv_text:
            draft.cleaned_cv_text = cleaned_text

        # 1. Update or create CandidateProfile
        profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == user.id).first()
        if not profile:
            profile = CandidateProfile(
                user_id=user.id,
                headline=draft.headline or "Professional",
                summary=draft.summary,
                phone=draft.phone,
                location=draft.location or "Remote",
                linkedin_url=draft.linkedin_url,
                github_url=draft.github_url,
                portfolio_url=draft.portfolio_url,
                raw_cv_text=raw_text,
                is_verified=False,
            )
            db.add(profile)
        else:
            if draft.headline:
                profile.headline = draft.headline
            if draft.summary:
                profile.summary = draft.summary
            if draft.phone:
                profile.phone = draft.phone
            if draft.location:
                profile.location = draft.location
            if draft.linkedin_url:
                profile.linkedin_url = draft.linkedin_url
            if draft.github_url:
                profile.github_url = draft.github_url
            if draft.portfolio_url:
                profile.portfolio_url = draft.portfolio_url
            profile.raw_cv_text = raw_text

        if replace_existing:
            # Delete old evidence records for a clean import
            db.query(EvidenceItem).filter(EvidenceItem.user_id == user.id).delete()
            db.query(ExperienceRecord).filter(ExperienceRecord.user_id == user.id).delete()
            db.query(Skill).filter(Skill.user_id == user.id).delete()
            db.query(Project).filter(Project.user_id == user.id).delete()
            db.query(Certification).filter(Certification.user_id == user.id).delete()
            db.query(EducationRecord).filter(EducationRecord.user_id == user.id).delete()
            db.flush()

        # Fetch existing IDs for incremental sequencing if not replacing
        existing_exp_ids = [
            sid for (sid,) in db.query(EvidenceItem.stable_id).filter(EvidenceItem.user_id == user.id).all() if sid
        ]
        existing_skill_ids = [
            sid for (sid,) in db.query(Skill.stable_id).filter(Skill.user_id == user.id).all() if sid
        ]
        existing_proj_ids = [
            sid for (sid,) in db.query(Project.stable_id).filter(Project.user_id == user.id).all() if sid
        ]
        existing_cert_ids = [
            sid for (sid,) in db.query(Certification.stable_id).filter(Certification.user_id == user.id).all() if sid
        ]
        existing_edu_ids = [
            sid for (sid,) in db.query(EducationRecord.stable_id).filter(EducationRecord.user_id == user.id).all() if sid
        ]

        bullet_idx = self._get_next_index(existing_exp_ids, "EXP")
        skill_idx = self._get_next_index(existing_skill_ids, "SKILL")
        proj_idx = self._get_next_index(existing_proj_ids, "PROJ")
        cert_idx = self._get_next_index(existing_cert_ids, "CERT")
        edu_idx = self._get_next_index(existing_edu_ids, "EDU")

        bullets_created = 0
        exp_records_created = 0

        # Existing maps for non-destructive deduplication
        existing_exps = db.query(ExperienceRecord).filter(ExperienceRecord.user_id == user.id).all()
        exp_map = {
            (e.company_name.strip().lower(), e.role_title.strip().lower()): e
            for e in existing_exps
        }

        # 2. Persist Experience Records and Atomic Bullets
        for exp_order, exp_draft in enumerate(draft.experiences):
            exp_key = (exp_draft.company_name.strip().lower(), exp_draft.role_title.strip().lower())
            exp_rec = exp_map.get(exp_key)
            if exp_rec is None:
                exp_rec = ExperienceRecord(
                    user_id=user.id,
                    company_name=exp_draft.company_name,
                    role_title=exp_draft.role_title,
                    location=exp_draft.location,
                    start_date=exp_draft.start_date,
                    end_date=exp_draft.end_date,
                    is_current=exp_draft.is_current,
                    description=exp_draft.description,
                    display_order=exp_order,
                )
                db.add(exp_rec)
                db.flush()  # populate exp_rec.id
                exp_map[exp_key] = exp_rec
                exp_records_created += 1
            else:
                if exp_draft.location and not exp_rec.location:
                    exp_rec.location = exp_draft.location
                if exp_draft.start_date and not exp_rec.start_date:
                    exp_rec.start_date = exp_draft.start_date
                if exp_draft.end_date and not exp_rec.end_date:
                    exp_rec.end_date = exp_draft.end_date
                if exp_draft.description and not exp_rec.description:
                    exp_rec.description = exp_draft.description

            # Existing bullets for this experience record
            existing_bullets = db.query(EvidenceItem).filter(
                EvidenceItem.user_id == user.id,
                EvidenceItem.experience_record_id == exp_rec.id,
            ).all()
            bullet_map = {b.raw_text.strip().lower(): b for b in existing_bullets}

            for b_order, b_draft in enumerate(exp_draft.bullets):
                b_text_key = b_draft.text.strip().lower()
                if b_text_key in bullet_map:
                    # Bullet already exists, keep preserved
                    continue

                stable_id = f"EXP_{bullet_idx:03d}"
                bullet_idx += 1
                ev_item = EvidenceItem(
                    user_id=user.id,
                    experience_record_id=exp_rec.id,
                    stable_id=stable_id,
                    raw_text=b_draft.text,
                    category=b_draft.category or "experience",
                    variants=b_draft.variants,
                    is_verified=False,
                    display_order=b_order,
                )
                db.add(ev_item)
                bullet_map[b_text_key] = ev_item
                bullets_created += 1

        # 3. Persist Skills
        existing_skills = db.query(Skill).filter(Skill.user_id == user.id).all()
        skill_map = {s.name.strip().lower(): s for s in existing_skills}
        skills_created = 0
        for s_order, s_draft in enumerate(draft.skills):
            s_key = s_draft.name.strip().lower()
            if s_key in skill_map:
                continue

            stable_id = f"SKILL_{skill_idx:03d}"
            skill_idx += 1
            skill_item = Skill(
                user_id=user.id,
                stable_id=stable_id,
                name=s_draft.name,
                category=s_draft.category or "programming",
                proficiency=s_draft.proficiency,
                years_of_experience=s_draft.years_of_experience,
                is_verified=False,
                display_order=s_order,
            )
            db.add(skill_item)
            skill_map[s_key] = skill_item
            skills_created += 1

        # 4. Persist Projects
        existing_projects = db.query(Project).filter(Project.user_id == user.id).all()
        proj_map = {p.title.strip().lower(): p for p in existing_projects}
        projects_created = 0
        for p_order, p_draft in enumerate(draft.projects):
            p_key = p_draft.title.strip().lower()
            if p_key in proj_map:
                continue

            stable_id = f"PROJ_{proj_idx:03d}"
            proj_idx += 1
            proj_item = Project(
                user_id=user.id,
                stable_id=stable_id,
                title=p_draft.title,
                category=p_draft.category,
                description=p_draft.description,
                technologies=p_draft.technologies or [],
                url=p_draft.url,
                github_url=p_draft.github_url,
                is_verified=False,
                display_order=p_order,
            )
            db.add(proj_item)
            proj_map[p_key] = proj_item
            projects_created += 1

        # 5. Persist Certifications
        existing_certs = db.query(Certification).filter(Certification.user_id == user.id).all()
        cert_map = {c.name.strip().lower(): c for c in existing_certs}
        certs_created = 0
        for c_order, c_draft in enumerate(draft.certifications):
            c_key = c_draft.name.strip().lower()
            if c_key in cert_map:
                continue

            stable_id = f"CERT_{cert_idx:03d}"
            cert_idx += 1
            cert_item = Certification(
                user_id=user.id,
                stable_id=stable_id,
                name=c_draft.name,
                issuing_organization=c_draft.issuing_organization,
                issue_date=c_draft.issue_date,
                expiration_date=c_draft.expiration_date,
                credential_id=c_draft.credential_id,
                credential_url=c_draft.credential_url,
                is_verified=False,
                display_order=c_order,
            )
            db.add(cert_item)
            cert_map[c_key] = cert_item
            certs_created += 1

        # 6. Persist Education Records
        existing_edus = db.query(EducationRecord).filter(EducationRecord.user_id == user.id).all()
        edu_map = {(e.institution.strip().lower(), e.degree.strip().lower()): e for e in existing_edus}
        edu_created = 0
        for e_order, e_draft in enumerate(draft.education):
            e_key = (e_draft.institution.strip().lower(), e_draft.degree.strip().lower())
            if e_key in edu_map:
                continue

            stable_id = f"EDU_{edu_idx:03d}"
            edu_idx += 1
            edu_item = EducationRecord(
                user_id=user.id,
                stable_id=stable_id,
                institution=e_draft.institution,
                degree=e_draft.degree,
                field_of_study=e_draft.field_of_study,
                start_date=e_draft.start_date,
                end_date=e_draft.end_date,
                grade=e_draft.grade,
                activities=e_draft.activities,
                is_verified=False,
                display_order=e_order,
            )
            db.add(edu_item)
            edu_map[e_key] = edu_item
            edu_created += 1

        db.commit()

        # Count total in evidence bank for reporting
        total_exps = db.query(ExperienceRecord).filter(ExperienceRecord.user_id == user.id).count()
        total_bullets = db.query(EvidenceItem).filter(EvidenceItem.user_id == user.id).count()
        total_skills = db.query(Skill).filter(Skill.user_id == user.id).count()
        total_projects = db.query(Project).filter(Project.user_id == user.id).count()
        total_certs = db.query(Certification).filter(Certification.user_id == user.id).count()
        total_edus = db.query(EducationRecord).filter(EducationRecord.user_id == user.id).count()

        return {
            "profile_id": str(profile.id),
            "experiences_extracted": total_exps,
            "bullets_extracted": total_bullets,
            "skills_extracted": total_skills,
            "projects_extracted": total_projects,
            "certifications_extracted": total_certs,
            "education_extracted": total_edus,
            "languages_extracted": len(draft.languages),
            "extraction_mode": draft.extraction_mode,
            "new_experiences_added": exp_records_created,
            "new_bullets_added": bullets_created,
            "new_skills_added": skills_created,
        }


# Global CV extraction service instance
cv_extraction_service = CVExtractionService()

