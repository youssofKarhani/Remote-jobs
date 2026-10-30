"""Phase 1 Regression Tests — Harden the Existing CV Text Extraction Path.

Covers:
1. PDF layout extraction mode ('layout') with per-page fallback to plain extract_text()
2. Page boundary preservation and raw vs cleaned text separation
3. Valid phone number extraction (+961-76-071579, +49 170 1234567, 01573 9622426)
4. Date ranges (2019-2022, 2020 - 2024) never misclassified as phone numbers
5. Wrapped LinkedIn / GitHub URL reconstruction across line breaks & two-column layouts (user-specific)
6. Languages section recognition (Language, Languages, Languages Spoken, Spoken Languages) without leaking into Projects/Certifications
7. Logical separation of Projects and Certifications (even under layout corruption)
8. Wrapped multi-line skills continuation (Reinforcement\\nLearning -> Reinforcement Learning)
9. Footer / boilerplate noise filtering ("For more information on my Education / Certificates / Project visit my LinkedIn profile.")
10. Raw candidate claim preservation (e.g. 'MangoDB' is NOT silently normalized to 'MongoDB')
11. Two-column Youssof CV full regression test
"""

from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.integrations.llm_ai_service import DefaultAIService
from app.models.profile import CandidateProfile
from app.models.user import User
from app.services.document_parser import (
    ParsedDocument,
    clean_extracted_cv_text,
    extract_pdf_pages,
    extract_text_from_pdf,
    parse_document,
    parse_document_detailed,
    reconstruct_broken_urls,
)


# ============================================================================
# 1. PDF Extraction (Layout Mode First + Per-Page Fallback + Page Boundaries)
# ============================================================================

class TestPhase1PDFExtractionAndRawPreservation:
    """Verify PDF layout-mode extraction, safe fallback, page boundaries, and raw text retention."""

    def test_pdf_attempts_layout_mode_first_and_preserves_page_boundaries(self):
        """Native PDFs must first call page.extract_text(extraction_mode='layout') and preserve page boundaries."""
        mock_page_1 = MagicMock()
        mock_page_1.extract_text.side_effect = lambda **kwargs: (
            "Youssof El Karhani          Email: youssof.k0@gmail.com\nExperience\nRUYA Advisory"
            if kwargs.get("extraction_mode") == "layout"
            else "Plain page 1"
        )
        mock_page_2 = MagicMock()
        mock_page_2.extract_text.side_effect = lambda **kwargs: (
            "Projects\nSentimental Chatbot\nLanguages\nEnglish: C1"
            if kwargs.get("extraction_mode") == "layout"
            else "Plain page 2"
        )

        mock_reader = MagicMock()
        mock_reader.pages = [mock_page_1, mock_page_2]

        with patch("app.services.document_parser.PdfReader", return_value=mock_reader):
            pages = extract_pdf_pages(b"%PDF-1.4 mock bytes")
            assert len(pages) == 2
            assert pages[0].page_number == 1
            assert pages[0].extraction_mode == "layout"
            assert pages[1].page_number == 2
            assert pages[1].extraction_mode == "layout"
            mock_page_1.extract_text.assert_called_once_with(extraction_mode="layout")
            mock_page_2.extract_text.assert_called_once_with(extraction_mode="layout")

            full_text = extract_text_from_pdf(b"%PDF-1.4 mock bytes")
            # Page boundary delimiter (\f) preserved between page 1 and page 2
            assert "\f" in full_text
            page_splits = full_text.split("\f")
            assert len(page_splits) == 2
            assert "RUYA Advisory" in page_splits[0]
            assert "Sentimental Chatbot" in page_splits[1]

    def test_pdf_layout_failure_safely_falls_back_per_page_to_plain_extract_text(self):
        """If page.extract_text(extraction_mode='layout') raises or returns empty on a page, fall back to page.extract_text()."""
        mock_page_1 = MagicMock()

        def page1_side_effect(**kwargs):
            if kwargs.get("extraction_mode") == "layout":
                raise RuntimeError("Layout font matrix error on page 1")
            return "Page 1 recovered via plain extract_text()"

        mock_page_1.extract_text.side_effect = page1_side_effect

        mock_page_2 = MagicMock()
        mock_page_2.extract_text.side_effect = lambda **kwargs: (
            "Page 2 extracted via layout mode"
            if kwargs.get("extraction_mode") == "layout"
            else "Page 2 plain"
        )

        mock_reader = MagicMock()
        mock_reader.pages = [mock_page_1, mock_page_2]

        with patch("app.services.document_parser.PdfReader", return_value=mock_reader):
            doc: ParsedDocument = parse_document_detailed(b"%PDF-1.4 mock", "sample.pdf")
            assert len(doc.pages) == 2
            assert doc.pages[0].extraction_mode == "plain_fallback"
            assert "Page 1 recovered via plain extract_text()" in doc.pages[0].raw_text
            assert doc.pages[1].extraction_mode == "layout"
            assert "Page 2 extracted via layout mode" in doc.pages[1].raw_text

    def test_raw_and_cleaned_text_preserved_separately_without_overwriting_raw(self):
        """Raw extracted text must remain untouched while cleaned_text holds reconstructed URLs/spacing."""
        raw_input = (
            "Youssof El Karhani\n"
            "https://www.linkedin.com/in\n"
            "/youssof-el-karhani\n"
            "Skills:\n"
            "Python, scikit                 -learn, MangoDB\n"
        )
        doc = parse_document_detailed(raw_input.encode("utf-8"), "cv.txt")

        # Raw text preserves exact original line break inside URL and exact spacing
        assert "https://www.linkedin.com/in\n/youssof-el-karhani" in doc.raw_text
        assert "scikit                 -learn" in doc.raw_text
        assert "MangoDB" in doc.raw_text

        # Cleaned text reconstructs the URL and fixes layout hyphen gap, but NEVER mutates MangoDB -> MongoDB
        assert "https://www.linkedin.com/in/youssof-el-karhani" in doc.cleaned_text
        assert "scikit-learn" in doc.cleaned_text
        assert "MangoDB" in doc.cleaned_text
        assert "MongoDB" not in doc.cleaned_text


# ============================================================================
# 2. Phone Number Hardening vs Date Ranges
# ============================================================================

class TestPhase1PhoneAndDateRanges:
    """Verify phone number extraction supports international formats and rejects date ranges."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "valid_phone",
        [
            "+961-76-071579",
            "+49 170 1234567",
            "01573 9622426",
            "+1 (555) 234-5678",
        ],
    )
    async def test_valid_phone_numbers_extracted_accurately(self, valid_phone: str):
        """Valid international and local phone numbers must be extracted even when date ranges exist."""
        cv_text = f"""
Youssof El Karhani
Education
BS Software Engineer - 2019-2022
MSc Computer Science - 2020 - 2024
Phone: {valid_phone}
Skills
Python, FastAPI
"""
        service = DefaultAIService(provider="mock")
        draft = await service.extract_cv_to_evidence_bank(cv_text)
        assert draft.phone == valid_phone

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "date_range_text",
        [
            "2019-2022",
            "2020 - 2024",
            "2019 – 2022",
            "04/2024 - 01/2025",
            "2024 to est. 2026",
        ],
    )
    async def test_date_ranges_never_classified_as_phone_number(self, date_range_text: str):
        """Date ranges such as 2019-2022 or 2020 - 2024 must never be interpreted as telephone numbers."""
        cv_text = f"""
Youssof El Karhani
AI & Data Engineer
Education
University of Balamand ({date_range_text})
Experience
RUYA Advisory ({date_range_text})
- Built automated backend pipelines in Python.
Skills
Python, SQL
"""
        service = DefaultAIService(provider="mock")
        draft = await service.extract_cv_to_evidence_bank(cv_text)
        assert draft.phone is None


# ============================================================================
# 3. Wrapped LinkedIn / URL Reconstruction (User-Specific)
# ============================================================================

class TestPhase1WrappedURLReconstruction:
    """Verify URLs broken by layout extraction are safely reconstructed for any user."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "broken_url,expected_url",
        [
            (
                "https://www.linkedin.com/in\n/youssof-el-karhani",
                "https://www.linkedin.com/in/youssof-el-karhani",
            ),
            (
                "https://www.linkedin.com/in/\nelena-rodriguez-99",
                "https://www.linkedin.com/in/elena-rodriguez-99",
            ),
            (
                "https://linkedin.com/in\n   /marcus-chen-dev",
                "https://linkedin.com/in/marcus-chen-dev",
            ),
            (
                "https://www.linkedin.com/in/youssof-el-\nkarhani",
                "https://www.linkedin.com/in/youssof-el-karhani",
            ),
        ],
    )
    async def test_wrapped_linkedin_urls_reconstructed_for_any_user(
        self, broken_url: str, expected_url: str
    ):
        """Broken LinkedIn URLs must be reconstructed dynamically from source text (never hardcoded)."""
        cv_text = f"""
Candidate Name
Senior AI Engineer
{broken_url}
Experience
Acme Corp - AI Engineer
- Developed production ML pipelines.
Skills
Python, PyTorch
"""
        service = DefaultAIService(provider="mock")
        draft = await service.extract_cv_to_evidence_bank(cv_text)
        assert draft.linkedin_url == expected_url
        # Raw CV text must still preserve the original un-reconstructed text
        assert broken_url in (draft.raw_cv_text or "")


# ============================================================================
# 4. Languages Section Recognition & No Section Leakage
# ============================================================================

class TestPhase1LanguagesSection:
    """Verify Language/Languages/Languages Spoken/Spoken Languages headings and prevent section leakage."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "heading",
        [
            "Language",
            "Languages",
            "Languages Spoken",
            "Spoken Languages",
            "Languages:",
            "Spoken Languages:",
        ],
    )
    async def test_language_section_headings_recognized_and_do_not_leak(self, heading: str):
        """Languages under any supported heading must be extracted into draft.languages and never leak into Projects or Certifications."""
        cv_text = f"""
Youssof El Karhani
AI Engineer

Projects
Sentimental Chatbot - Senior Project (link)
Machine Learning & Software Engineering
- Developed a Discord chatbot integrating GPT-3 for dialogue. — Technologies used: GPT (DaVinci), MySQL, NumPy, Pandas

Courses & Certifications
• Build & Deploy AI Messenger Chatbot using IBM Watson — Coursera Project Network

{heading}
English: (C1) - IELTS
German: B1
Arabic : Native
French: B2 - DELF
"""
        service = DefaultAIService(provider="mock")
        draft = await service.extract_cv_to_evidence_bank(cv_text)

        assert len(draft.languages) == 4
        assert any("English" in lang for lang in draft.languages)
        assert any("German" in lang for lang in draft.languages)
        assert any("Arabic" in lang for lang in draft.languages)
        assert any("French" in lang for lang in draft.languages)

        # Ensure languages did NOT leak into projects or certifications
        project_titles_and_descs = " ".join(f"{p.title} {p.description}" for p in draft.projects)
        cert_names = " ".join(c.name for c in draft.certifications)
        for lang_kw in ["IELTS", "German: B1", "Arabic : Native", "DELF"]:
            assert lang_kw not in project_titles_and_descs
            assert lang_kw not in cert_names


# ============================================================================
# 5. Certifications and Projects Separation
# ============================================================================

class TestPhase1ProjectsAndCertificationsSeparation:
    """Verify Certifications and Projects remain logically separate even under layout corruption."""

    @pytest.mark.asyncio
    async def test_projects_and_certifications_logically_separate(self):
        """Multi-line projects and certifications with words like 'Project-Based' or 'Certificate' must not cross-contaminate."""
        cv_text = """
Youssof El Karhani
AI & Data Engineer

Projects
Sentimental Chatbot - Senior Project (link)
Machine Learning & Software Engineering
- Developed a Discord chatbot integrating GPT-3 for dialogue and a Bi-GRU sentiment analysis model. — Technologies used: GPT (DaVinci), MySQL, NumPy, Pandas

AI in Business Sales Data Analysis (link)
Business Analytics & Machine Learning
- Analyzed sales data for customer segmentation, forecasting, and association mining. — Technologies used: Prophet, Mlxtend, Matplotlib, Seaborn

Courses & Certifications
• Build & Deploy AI Messenger Chatbot using IBM Watson — Coursera Project Network
• Build a Data Science Web App (Project-Based) — Coursera Project Network
• Distinguished Trainee Certificate (Enterprise Development Program) — Arab Planning Institute, Kuwait
"""
        service = DefaultAIService(provider="mock")
        draft = await service.extract_cv_to_evidence_bank(cv_text)

        assert len(draft.projects) == 2
        assert "Sentimental Chatbot" in draft.projects[0].title
        assert draft.projects[0].category == "Machine Learning & Software Engineering"
        assert "MySQL" in draft.projects[0].technologies
        assert "AI in Business Sales Data Analysis" in draft.projects[1].title
        assert "Prophet" in draft.projects[1].technologies

        assert len(draft.certifications) == 3
        cert_titles = [c.name for c in draft.certifications]
        assert any("IBM Watson" in t for t in cert_titles)
        assert any("Build a Data Science Web App (Project-Based)" in t for t in cert_titles)
        assert any("Distinguished Trainee Certificate" in t for t in cert_titles)

        # Ensure no project became a certification and no certification became a project
        assert not any("Sentimental Chatbot" in t for t in cert_titles)
        assert not any("Coursera Project Network" in p.title for p in draft.projects)

    @pytest.mark.asyncio
    async def test_portfolio_project_not_classified_as_certification_under_layout_corruption(self):
        """Even if layout corruption places a portfolio project after a Certifications header, it must be classified as a Project."""
        corrupted_cv = """
Youssof El Karhani
AI Engineer

Certifications
• Model Context Protocol (MCP) — Udemy
Sentimental Chatbot - Senior Project (link)
Machine Learning & Software Engineering
- Developed a Discord chatbot integrating GPT-3 for dialogue and sentiment analysis. — Technologies used: GPT (DaVinci), MySQL, NumPy, Pandas
"""
        service = DefaultAIService(provider="mock")
        draft = await service.extract_cv_to_evidence_bank(corrupted_cv)

        assert len(draft.certifications) == 1
        assert "Model Context Protocol" in draft.certifications[0].name
        assert len(draft.projects) == 1
        assert "Sentimental Chatbot" in draft.projects[0].title
        assert "MySQL" in draft.projects[0].technologies


# ============================================================================
# 6. Wrapped Skills Continuation & Raw Claim Preservation ('MangoDB')
# ============================================================================

class TestPhase1WrappedSkillsAndRawClaims:
    """Verify wrapped skills (Reinforcement\\nLearning) join cleanly while candidate claims (MangoDB) are never altered."""

    @pytest.mark.asyncio
    async def test_wrapped_skills_joined_and_mangodb_not_silently_normalized(self):
        """'Reinforcement\\nLearning' becomes 'Reinforcement Learning', while 'MangoDB' remains 'MangoDB'."""
        cv_text = """
Youssof El Karhani
AI & Data Engineer

Skills
Python
Reinforcement
Learning
Natural Language
Processing
MangoDB
FastAPI
"""
        service = DefaultAIService(provider="mock")
        draft = await service.extract_cv_to_evidence_bank(cv_text)

        skill_names = [s.name for s in draft.skills]
        assert "Reinforcement Learning" in skill_names
        assert "Natural Language Processing" in skill_names
        assert "Reinforcement" not in skill_names
        assert "Learning" not in skill_names

        # Candidate claim preservation rule: MangoDB must NOT be mutated to MongoDB
        assert "MangoDB" in skill_names
        assert "MongoDB" not in skill_names


# ============================================================================
# 7. Footer / Noise Filtering
# ============================================================================

class TestPhase1FooterNoiseFiltering:
    """Verify obvious footer or guidance text never becomes evidence."""

    @pytest.mark.asyncio
    async def test_linkedin_footer_guidance_filtered_out(self):
        """'For more information on my Education / Certificates / Project visit my LinkedIn profile.' must be ignored."""
        footer_line = "For more information on my Education / Certificates / Project visit my LinkedIn profile."
        cv_text = f"""
Youssof El Karhani
AI & Data Engineer

Experience
RUYA Advisory - AI & Automation Lead
- Engineered automated data pipelines in Python.

Projects
Sentimental Chatbot - Senior Project (link)
Machine Learning & Software Engineering
- Developed a Discord chatbot integrating GPT-3. — Technologies used: Python, MySQL

Certifications
• Model Context Protocol (MCP) — Udemy

Languages
English: (C1) - IELTS

{footer_line}
"""
        service = DefaultAIService(provider="mock")
        draft = await service.extract_cv_to_evidence_bank(cv_text)

        all_bullets = [b.text for e in draft.experiences for b in e.bullets]
        all_projects = [f"{p.title} {p.description}" for p in draft.projects]
        all_certs = [c.name for c in draft.certifications]
        all_edu = [e.institution for e in draft.education]

        for collection in (all_bullets, all_projects, all_certs, all_edu, draft.languages):
            for item in collection:
                assert "for more information" not in item.lower()
                assert "visit my linkedin" not in item.lower()


# ============================================================================
# 8. Current Two-Column Youssof CV End-to-End Regression Test
# ============================================================================

class TestPhase1TwoColumnYoussofCV:
    """End-to-end regression test on two-column Youssof CV layout and real PDF fixture."""

    @pytest.mark.asyncio
    async def test_two_column_youssof_cv_layout_extraction(
        self, client: TestClient, sample_user: User, auth_headers: dict, db_session: Session
    ):
        """Verify two-column Youssof CV with side-by-side columns, wrapped URL, phone, date ranges, wrapped skills, MangoDB, and footer."""
        two_column_cv = (
            "Youssof El Karhani                                  Phone: +961-76-071579\n"
            "AI & Data Engineer                                  Email: youssof.k0@gmail.com\n"
            "Kirchhain, Germany                                  https://www.linkedin.com/in\n"
            "                                                    /youssof-el-karhani\n"
            "\n"
            "Experience                                          Skills\n"
            "RUYA Advisory — Beirut, Lebanon (Remote)            Python, FastAPI, SQL\n"
            "- AI & Automation Lead, 01/2025 to Present          Reinforcement\n"
            "• Engineered 100% automated PSP data pipeline.      Learning\n"
            "• Connected Kajabi and Folk CRM via Zapier.         MangoDB, TensorFlow\n"
            "\n"
            "Education                                           Courses & Certifications\n"
            "• BS Software Engineer – 2019-2022                  • Model Context Protocol (MCP) — Udemy\n"
            "  University of Balamand, Lebanon                   • Build a Data Science Web App (Project-Based) — Coursera\n"
            "• MSc Computer Science – 2020 - 2024\n"
            "  Philips University of Marburg, Germany            Languages Spoken\n"
            "                                                    English: (C1) - IELTS\n"
            "Projects                                            German: B1\n"
            "Sentimental Chatbot - Senior Project (link)         Arabic : Native\n"
            "Machine Learning & Software Engineering             French: B2 - DELF\n"
            "- Developed a Discord chatbot integrating GPT-3. — Technologies used: GPT (DaVinci), MySQL, NumPy, Pandas\n"
            "\n"
            "For more information on my Education / Certificates / Project visit my LinkedIn profile.\n"
        )

        service = DefaultAIService(provider="mock")
        draft = await service.extract_cv_to_evidence_bank(two_column_cv)

        # 1. Phone vs date ranges
        assert draft.phone == "+961-76-071579"

        # 2. Wrapped LinkedIn URL reconstructed
        assert draft.linkedin_url == "https://www.linkedin.com/in/youssof-el-karhani"

        # 3. Wrapped skills & raw MangoDB preserved
        skill_names = [s.name for s in draft.skills]
        assert "Reinforcement Learning" in skill_names
        assert "MangoDB" in skill_names
        assert "MongoDB" not in skill_names

        # 4. Certifications and Projects separated
        assert len(draft.projects) == 1
        assert "Sentimental Chatbot" in draft.projects[0].title
        assert "MySQL" in draft.projects[0].technologies
        assert len(draft.certifications) == 2
        assert any("Model Context Protocol" in c.name for c in draft.certifications)

        # 5. Languages extracted and not leaked into Projects or Certifications
        assert len(draft.languages) == 4
        assert any("English" in l for l in draft.languages)
        assert not any("English" in p.title or "English" in p.description for p in draft.projects)

        # 6. Footer filtered out
        assert not any("visit my linkedin" in p.description.lower() for p in draft.projects)
        assert not any("visit my linkedin" in c.name.lower() for c in draft.certifications)

        # 7. Raw text preserved in DB via endpoint without overwriting with normalized values
        resp = client.post(
            "/api/v1/cv/parse-text",
            json={"text": two_column_cv, "replace_existing": True},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        profile = db_session.query(CandidateProfile).filter(CandidateProfile.user_id == sample_user.id).first()
        assert profile is not None
        assert profile.phone == "+961-76-071579"
        assert profile.linkedin_url == "https://www.linkedin.com/in/youssof-el-karhani"
        assert "https://www.linkedin.com/in\n" in (profile.raw_cv_text or "")
        assert "MangoDB" in (profile.raw_cv_text or "")

    @pytest.mark.asyncio
    async def test_real_youssof_pdf_extraction_if_present(self):
        """If the local Youssof PDF fixture is present in sibling remotejobs-cli repo, verify layout extraction."""
        pdf_path = (
            Path(__file__).resolve().parents[3]
            / "remotejobs-cli"
            / "data"
            / "CV"
            / "Information"
            / "Base_CVs"
            / "Youssof_El_Karhani_2026_CV (AI & Data egineer).pdf"
        )
        if not pdf_path.exists():
            pytest.skip("Local Youssof PDF fixture not present in environment")

        pdf_bytes = pdf_path.read_bytes()
        doc = parse_document_detailed(pdf_bytes, pdf_path.name)
        assert len(doc.pages) == 2
        assert all(p.extraction_mode == "layout" for p in doc.pages)
        assert "\f" in doc.raw_text

        service = DefaultAIService(provider="mock")
        draft = await service.extract_cv_to_evidence_bank(doc.raw_text)
        assert draft.phone == "01573 9622426"
        assert len(draft.experiences) >= 2
        assert len(draft.projects) == 3
        assert len(draft.certifications) == 5
        assert len(draft.languages) == 4
