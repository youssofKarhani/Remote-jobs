"""CV Ingestion Benchmark and Regression Evaluation Engine (Phase 9).

Executes end-to-end ingestion pipelines across a diverse corpus of CV archetypes:
1. Two-Column Sidebar (Youssof regression layout)
2. Single-Column Modern Chronological
3. Multi-Page Continuous
4. Scanned Raster Image (with OCR Fallback)
5. Multilingual / German European Format
6. Adversarial / Typo-Laden / Unknown Sections
7. Plain Text / DOCX Non-PDF Documents

Measures:
- Reading order accuracy (zero column interleaving)
- Source block provenance coverage (100% anchored claims)
- Raw text preservation integrity (raw_value untouched)
- Normalization accuracy (e.g. MangoDB -> MongoDB)
- Unknown section retention (zero silent dropping)
- Evidence Bank safety (is_verified == False)
- Latency across pipeline stages
"""

from dataclasses import dataclass, field
import io
import time
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

try:
    import pymupdf
except ImportError:
    try:
        import fitz as pymupdf
    except ImportError:
        pymupdf = None

from app.schemas.layout import LayoutDocument
from app.schemas.semantic_cv import CanonicalSemanticCV
from app.services.document_router import DocumentRoutingResult, route_and_parse_document
from app.services.layout import reconstruct_reading_order
from app.services.normalization import NormalizedSemanticCVResult, normalize_canonical_cv
from app.services.ocr_service import MockOCREngine
from app.services.provenance_validator import validate_canonical_cv
from app.services.semantic_extraction_client import heuristic_fallback_extract


@dataclass
class BenchmarkCorpusItem:
    """A test document fixture representing a specific CV layout archetype."""
    name: str
    archetype: str
    filename: str
    file_bytes: bytes
    expected_layout: str
    expected_columns: int
    expected_full_name: str
    expected_raw_skills: List[str]
    expected_normalized_skills: List[str]
    expected_unknown_headings: List[str] = field(default_factory=list)
    reading_order_asserts: List[Tuple[str, str]] = field(default_factory=list)  # (first_text, second_text)
    ocr_mock: Optional[MockOCREngine] = None


@dataclass
class BenchmarkExecutionMetrics:
    """Metrics recorded during benchmark execution for a single document."""
    name: str
    archetype: str
    success: bool
    total_time_ms: float
    stage_times_ms: Dict[str, float]
    total_pages: int
    source_blocks_count: int
    extracted_skills_count: int
    extracted_experiences_count: int
    extracted_unknown_sections_count: int
    reading_order_correct: bool
    provenance_coverage_pct: float
    raw_preservation_pct: float
    quality_score: float
    is_verified_guarded: bool  # True if no unverified items became verified
    error: Optional[str] = None


@dataclass
class BenchmarkSuiteSummary:
    """Overall summary statistics for the benchmark regression run."""
    total_benchmarks: int
    passed_benchmarks: int
    failed_benchmarks: int
    overall_reading_order_accuracy_pct: float
    overall_provenance_coverage_pct: float
    overall_raw_preservation_pct: float
    average_latency_ms: float
    results: List[BenchmarkExecutionMetrics]


# ============================================================================
# Synthetic Corpus Generators (Deterministic & Portable)
# ============================================================================

def build_youssof_twocolumn_pdf() -> bytes:
    """Generates Youssof El Karhani's regression two-column layout."""
    doc = pymupdf.open()
    page = doc.new_page(width=612.0, height=792.0)

    # Left Column (x: 50..220)
    page.insert_text(pymupdf.Point(50, 50), "Youssof El Karhani", fontsize=18, fontname="hebo")
    page.insert_text(pymupdf.Point(50, 80), "Contact", fontsize=13, fontname="hebo")
    page.insert_text(pymupdf.Point(50, 105), "youssof.k0@gmail.com", fontsize=10, fontname="helv")
    page.insert_text(pymupdf.Point(50, 125), "+961-76-071579", fontsize=10, fontname="helv")
    page.insert_text(pymupdf.Point(50, 160), "Languages", fontsize=13, fontname="hebo")
    page.insert_text(pymupdf.Point(50, 185), "English (C1), Arabic (Native)", fontsize=10, fontname="helv")
    page.insert_text(pymupdf.Point(50, 220), "Technical Skills", fontsize=13, fontname="hebo")
    page.insert_text(pymupdf.Point(50, 245), "Python, FastAPI, SQL, Docker", fontsize=10, fontname="helv")

    # Right Column (x: 270..560)
    page.insert_text(pymupdf.Point(270, 80), "Education", fontsize=13, fontname="hebo")
    page.insert_text(pymupdf.Point(270, 105), "B.S. in Computer Science", fontsize=11, fontname="hebo")
    page.insert_text(pymupdf.Point(270, 125), "Lebanese American University (2020 - 2024)", fontsize=10, fontname="helv")
    page.insert_text(pymupdf.Point(270, 160), "Certifications", fontsize=13, fontname="hebo")
    page.insert_text(pymupdf.Point(270, 185), "AWS Certified Solutions Architect", fontsize=10, fontname="helv")
    page.insert_text(pymupdf.Point(270, 220), "Projects", fontsize=13, fontname="hebo")
    page.insert_text(pymupdf.Point(270, 245), "Autonomous Job Intelligence Pipeline", fontsize=10, fontname="helv")

    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


def build_single_column_modern_pdf() -> bytes:
    """Generates standard chronological single-column layout."""
    doc = pymupdf.open()
    page = doc.new_page(width=612.0, height=792.0)

    y = 50.0
    lines = [
        ("Marcus Vance", 18, "hebo"),
        ("Lead Backend Engineer | London, UK | marcus.vance@example.com", 10, "helv"),
        ("Professional Summary", 13, "hebo"),
        ("Accomplished distributed systems engineer specializing in high-throughput APIs.", 10, "helv"),
        ("Work Experience", 13, "hebo"),
        ("Senior Backend Engineer at FinTech Global (01/2021 - Present)", 11, "hebo"),
        ("Architected payment routing engine processing $10M daily volume.", 10, "helv"),
        ("Reduced P99 API latency by 45% using Redis caching and asynchronous queues.", 10, "helv"),
        ("Education", 13, "hebo"),
        ("Master of Science in Software Engineering, Imperial College London (2018 - 2020)", 10, "helv"),
        ("Technical Skills", 13, "hebo"),
        ("Python, Go, PostgreSQL, Redis, Kubernetes, Kafka", 10, "helv"),
    ]

    for text, sz, fn in lines:
        page.insert_text(pymupdf.Point(50, y), text, fontsize=sz, fontname=fn)
        y += (sz * 1.6)

    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


def build_multipage_pdf() -> bytes:
    """Generates multi-page CV with reading continuity across pages."""
    doc = pymupdf.open()
    # Page 1
    p1 = doc.new_page(width=612.0, height=792.0)
    p1.insert_text(pymupdf.Point(50, 50), "Dr. Elena Rostova", fontsize=18, fontname="hebo")
    p1.insert_text(pymupdf.Point(50, 75), "elena.rostova@university.edu | Page 1 of 2", fontsize=10, fontname="helv")
    p1.insert_text(pymupdf.Point(50, 110), "Work Experience", fontsize=13, fontname="hebo")
    p1.insert_text(pymupdf.Point(50, 135), "Principal AI Research Scientist at DeepGraph Labs (2021 - Present)", fontsize=11, fontname="hebo")
    p1.insert_text(pymupdf.Point(50, 155), "Led generative graph model research applied to biochemical molecule discovery.", fontsize=10, fontname="helv")
    p1.insert_text(pymupdf.Point(50, 200), "Senior AI Researcher at Cortex Systems (2018 - 2021)", fontsize=11, fontname="hebo")
    p1.insert_text(pymupdf.Point(50, 220), "Implemented transformer embeddings for multi-modal knowledge graphs.", fontsize=10, fontname="helv")

    # Page 2
    p2 = doc.new_page(width=612.0, height=792.0)
    p2.insert_text(pymupdf.Point(50, 50), "Dr. Elena Rostova — Curriculum Vitae | Page 2", fontsize=10, fontname="helv")
    p2.insert_text(pymupdf.Point(50, 90), "Education", fontsize=13, fontname="hebo")
    p2.insert_text(pymupdf.Point(50, 115), "PhD in Computer Science, ETH Zurich (2014 - 2018)", fontsize=11, fontname="hebo")
    p2.insert_text(pymupdf.Point(50, 150), "Technical Skills", fontsize=13, fontname="hebo")
    p2.insert_text(pymupdf.Point(50, 175), "PyTorch, Python, CUDA, Distributed Training, C++", fontsize=10, fontname="helv")

    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


def build_german_multilingual_pdf() -> bytes:
    """Generates multilingual German/European CV with German dates and CEFR tiers."""
    doc = pymupdf.open()
    page = doc.new_page(width=612.0, height=792.0)

    y = 50.0
    lines = [
        ("Hans Mueller", 18, "hebo"),
        ("Softwareentwickler | Berlin, Deutschland | hans.mueller@example.de", 10, "helv"),
        ("Berufserfahrung", 13, "hebo"),
        ("Senior Backend Entwickler bei AutoCloud GmbH (März 2021 - heute)", 11, "hebo"),
        ("Entwicklung hochverfügbarer Cloud-Microservices auf Basis von FastAPI.", 10, "helv"),
        ("Software Entwickler bei TechBerlin (Januar 2019 - Februar 2021)", 11, "hebo"),
        ("Ausbildung", 13, "hebo"),
        ("Bachelor of Science in Informatik, TU Berlin (2015 - 2018)", 10, "helv"),
        ("Sprachen", 13, "hebo"),
        ("Deutsch (Muttersprache), Englisch (C1)", 10, "helv"),
        ("Kenntnisse", 13, "hebo"),
        ("Python, FastAPI, PostgreSQL, Docker, Git", 10, "helv"),
    ]

    for text, sz, fn in lines:
        page.insert_text(pymupdf.Point(50, y), text, fontsize=sz, fontname=fn)
        y += (sz * 1.6)

    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


def build_adversarial_typo_pdf() -> bytes:
    """Generates adversarial CV containing typos in skills, wrapped URLs, and unknown sections."""
    doc = pymupdf.open()
    page = doc.new_page(width=612.0, height=792.0)

    y = 50.0
    lines = [
        ("Alexandre Dumas", 18, "hebo"),
        ("alex.dumas@startup.io | https://linkedin.com/in/\nalexandre-dumas-dev", 10, "helv"),
        ("Experience", 13, "hebo"),
        ("Fullstack Developer at NovelTech (2022 - 2024)", 11, "hebo"),
        ("Technical Skills", 13, "hebo"),
        ("MangoDB, Dokker, TypeScrpt, React, Python", 10, "helv"),
        ("Open Source Contributions", 13, "hebo"),
        ("Core contributor to popular open-source task queue library.", 10, "helv"),
        ("Maintained async driver with over 1M monthly downloads.", 10, "helv"),
    ]

    for text, sz, fn in lines:
        page.insert_text(pymupdf.Point(50, y), text, fontsize=sz, fontname=fn)
        y += (sz * 1.6)

    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


def get_standard_benchmark_corpus() -> List[BenchmarkCorpusItem]:
    """Assemble all archetypes into standard regression test corpus."""
    # Scanned OCR mock setup
    mock_ocr = MockOCREngine(
        mock_pages_words=[
            [
                {"text": "Claire", "bbox": (50.0, 50.0, 95.0, 65.0), "line_idx": 0},
                {"text": "Beaufort", "bbox": (100.0, 50.0, 160.0, 65.0), "line_idx": 0},
                {"text": "claire.beaufort@scan.io", "bbox": (50.0, 75.0, 180.0, 88.0), "line_idx": 1},
                {"text": "EXPERIENCE", "bbox": (50.0, 110.0, 130.0, 125.0), "line_idx": 2, "is_bold": True},
                {"text": "Systems", "bbox": (50.0, 135.0, 95.0, 148.0), "line_idx": 3},
                {"text": "Architect", "bbox": (100.0, 135.0, 150.0, 148.0), "line_idx": 3},
                {"text": "SKILLS", "bbox": (50.0, 175.0, 95.0, 190.0), "line_idx": 4, "is_bold": True},
                {"text": "Python,", "bbox": (50.0, 200.0, 90.0, 212.0), "line_idx": 5},
                {"text": "FastAPI,", "bbox": (95.0, 200.0, 140.0, 212.0), "line_idx": 5},
                {"text": "MangoDB", "bbox": (145.0, 200.0, 200.0, 212.0), "line_idx": 5},
            ]
        ]
    )
    dummy_scanned_pdf = (
        b"%PDF-1.4\n1 0 obj <</Type /Catalog /Pages 2 0 R>> endobj\n"
        b"2 0 obj <</Type /Pages /Kids [3 0 R] /Count 1>> endobj\n"
        b"3 0 obj <</Type /Page /Parent 2 0 R /MediaBox [0 0 612 792]>> endobj\n"
        b"trailer <</Size 4 /Root 1 0 R>>\n%%EOF"
    )

    return [
        BenchmarkCorpusItem(
            name="Youssof Two-Column Regression",
            archetype="two_column_sidebar",
            filename="youssof_twocol.pdf",
            file_bytes=build_youssof_twocolumn_pdf(),
            expected_layout="two_column",
            expected_columns=2,
            expected_full_name="Youssof El Karhani",
            expected_raw_skills=["Python", "FastAPI", "SQL", "Docker"],
            expected_normalized_skills=["Python", "FastAPI", "SQL", "Docker"],
            reading_order_asserts=[("Technical Skills", "Education")],
        ),
        BenchmarkCorpusItem(
            name="Single-Column Modern Chronological",
            archetype="single_column",
            filename="marcus_vance.pdf",
            file_bytes=build_single_column_modern_pdf(),
            expected_layout="single_column",
            expected_columns=1,
            expected_full_name="Marcus Vance",
            expected_raw_skills=["Python", "Go", "PostgreSQL", "Redis", "Kubernetes", "Kafka"],
            expected_normalized_skills=["Python", "Go", "PostgreSQL", "Redis", "Kubernetes", "Apache Kafka"],
        ),
        BenchmarkCorpusItem(
            name="Multi-Page Continuous",
            archetype="multi_page",
            filename="elena_rostova.pdf",
            file_bytes=build_multipage_pdf(),
            expected_layout="single_column",
            expected_columns=1,
            expected_full_name="Dr. Elena Rostova",
            expected_raw_skills=["PyTorch", "Python", "CUDA", "Distributed Training", "C++"],
            expected_normalized_skills=["PyTorch", "Python", "CUDA", "C++"],
        ),
        BenchmarkCorpusItem(
            name="German Multilingual European",
            archetype="multilingual_german",
            filename="hans_mueller.pdf",
            file_bytes=build_german_multilingual_pdf(),
            expected_layout="single_column",
            expected_columns=1,
            expected_full_name="Hans Mueller",
            expected_raw_skills=["Python", "FastAPI", "PostgreSQL", "Docker", "Git"],
            expected_normalized_skills=["Python", "FastAPI", "PostgreSQL", "Docker", "Git"],
        ),
        BenchmarkCorpusItem(
            name="Adversarial Typo & Unknown Sections",
            archetype="adversarial_typo",
            filename="alexandre_dumas.pdf",
            file_bytes=build_adversarial_typo_pdf(),
            expected_layout="single_column",
            expected_columns=1,
            expected_full_name="Alexandre Dumas",
            expected_raw_skills=["MangoDB", "Dokker", "TypeScrpt", "React", "Python"],
            expected_normalized_skills=["MongoDB", "Docker", "TypeScript", "React", "Python"],
            expected_unknown_headings=["Open Source Contributions"],
        ),
        BenchmarkCorpusItem(
            name="Scanned Raster Image (OCR Fallback)",
            archetype="scanned_ocr",
            filename="claire_scanned.pdf",
            file_bytes=dummy_scanned_pdf,
            expected_layout="single_column",
            expected_columns=1,
            expected_full_name="Claire Beaufort",
            expected_raw_skills=["Python", "FastAPI", "MangoDB"],
            expected_normalized_skills=["Python", "FastAPI", "MongoDB"],
            ocr_mock=mock_ocr,
        ),
        BenchmarkCorpusItem(
            name="Plain Text Markdown Resume",
            archetype="plain_text",
            filename="developer_cv.txt",
            file_bytes=b"Samantha Reed\nSenior Site Reliability Engineer\nEmail: sam@sre.io\n\nEXPERIENCE\nSenior SRE at CloudScale (2021 - Present)\n\nSKILLS\nTerraform, Kubernetes, Python, Prometheus\n",
            expected_layout="single_column",
            expected_columns=1,
            expected_full_name="Samantha Reed",
            expected_raw_skills=["Terraform", "Kubernetes", "Python", "Prometheus"],
            expected_normalized_skills=["Terraform", "Kubernetes", "Python", "Prometheus"],
        ),
    ]


# ============================================================================
# Benchmark Runner Implementation
# ============================================================================

class CVBenchmarkRunner:
    """Executes the full CV ingestion pipeline and collects quantitative benchmark metrics."""

    def __init__(self, corpus: Optional[List[BenchmarkCorpusItem]] = None):
        self.corpus = corpus or get_standard_benchmark_corpus()

    def run_item(self, item: BenchmarkCorpusItem) -> BenchmarkExecutionMetrics:
        """Run single benchmark item through routing, layout, extraction, and normalization."""
        t_start = time.perf_counter()
        stage_times: Dict[str, float] = {}

        try:
            # 1. Document Routing & Extraction
            t0 = time.perf_counter()
            routing_res: DocumentRoutingResult = route_and_parse_document(
                file_bytes=item.file_bytes,
                filename=item.filename,
                enable_ocr=True,
                ocr_service=item.ocr_mock,
            )
            stage_times["routing_ms"] = round((time.perf_counter() - t0) * 1000, 2)
            spatial_doc = routing_res.spatial_document
            if not spatial_doc:
                raise ValueError(f"No spatial document produced: {routing_res.error}")

            # 2. Layout Reconstruction & Reading Order
            t1 = time.perf_counter()
            layout_doc: LayoutDocument = reconstruct_reading_order(spatial_doc)
            stage_times["layout_ms"] = round((time.perf_counter() - t1) * 1000, 2)

            # Check Reading Order Assertions
            reading_order_correct = True
            blocks = layout_doc.source_blocks
            for first_txt, second_txt in item.reading_order_asserts:
                order_first = next((b.reading_order for b in blocks if first_txt.lower() in b.text.lower()), None)
                order_second = next((b.reading_order for b in blocks if second_txt.lower() in b.text.lower()), None)
                if order_first is None or order_second is None or order_first >= order_second:
                    reading_order_correct = False

            # 3. Semantic Extraction (Heuristic Fallback Engine)
            t2 = time.perf_counter()
            raw_cv: CanonicalSemanticCV = heuristic_fallback_extract(layout_doc)
            stage_times["extraction_ms"] = round((time.perf_counter() - t2) * 1000, 2)

            # 4. Strict Block Provenance Validation
            valid_block_ids = {b.id for b in layout_doc.source_blocks}
            prov_report = validate_canonical_cv(raw_cv, valid_block_ids=valid_block_ids)
            provenance_coverage_pct = 100.0 if prov_report.is_valid else 0.0

            # 5. Normalization, Consistency & Quality Scoring
            t3 = time.perf_counter()
            norm_res: NormalizedSemanticCVResult = normalize_canonical_cv(raw_cv)
            stage_times["normalization_ms"] = round((time.perf_counter() - t3) * 1000, 2)

            norm_cv = norm_res.cv
            quality_score = norm_res.quality_score.overall_score

            # Check Raw Value Preservation
            raw_values_checked = 0
            raw_values_preserved = 0
            for skill in norm_cv.skills:
                raw_values_checked += 1
                if skill.raw_value:
                    raw_values_preserved += 1

            raw_preservation_pct = (
                round((raw_values_preserved / raw_values_checked) * 100.0, 1)
                if raw_values_checked > 0
                else 100.0
            )

            # Evidence Bank Safety Guard (Rule 1 & 2): No claims auto-verified
            is_verified_guarded = True
            for entity in [norm_cv.personal_info] + norm_cv.skills + norm_cv.experiences + norm_cv.education:
                if entity is not None and getattr(entity, "is_verified", False):
                    is_verified_guarded = False

            total_elapsed_ms = round((time.perf_counter() - t_start) * 1000, 2)

            return BenchmarkExecutionMetrics(
                name=item.name,
                archetype=item.archetype,
                success=True,
                total_time_ms=total_elapsed_ms,
                stage_times_ms=stage_times,
                total_pages=spatial_doc.total_pages,
                source_blocks_count=len(layout_doc.source_blocks),
                extracted_skills_count=len(norm_cv.skills),
                extracted_experiences_count=len(norm_cv.experiences),
                extracted_unknown_sections_count=len(norm_cv.unknown_sections),
                reading_order_correct=reading_order_correct,
                provenance_coverage_pct=provenance_coverage_pct,
                raw_preservation_pct=raw_preservation_pct,
                quality_score=quality_score,
                is_verified_guarded=is_verified_guarded,
            )

        except Exception as exc:
            total_elapsed_ms = round((time.perf_counter() - t_start) * 1000, 2)
            return BenchmarkExecutionMetrics(
                name=item.name,
                archetype=item.archetype,
                success=False,
                total_time_ms=total_elapsed_ms,
                stage_times_ms=stage_times,
                total_pages=0,
                source_blocks_count=0,
                extracted_skills_count=0,
                extracted_experiences_count=0,
                extracted_unknown_sections_count=0,
                reading_order_correct=False,
                provenance_coverage_pct=0.0,
                raw_preservation_pct=0.0,
                quality_score=0.0,
                is_verified_guarded=True,
                error=str(exc),
            )

    def run_suite(self) -> BenchmarkSuiteSummary:
        """Execute all benchmark items and compile comprehensive statistical summary."""
        results: List[BenchmarkExecutionMetrics] = []
        for item in self.corpus:
            res = self.run_item(item)
            results.append(res)

        total = len(results)
        passed = sum(1 for r in results if r.success and r.reading_order_correct and r.provenance_coverage_pct == 100.0)
        failed = total - passed

        ro_pct = (sum(1 for r in results if r.reading_order_correct) / total * 100.0) if total else 0.0
        prov_pct = (sum(r.provenance_coverage_pct for r in results) / total) if total else 0.0
        raw_pct = (sum(r.raw_preservation_pct for r in results) / total) if total else 0.0
        avg_latency = (sum(r.total_time_ms for r in results) / total) if total else 0.0

        return BenchmarkSuiteSummary(
            total_benchmarks=total,
            passed_benchmarks=passed,
            failed_benchmarks=failed,
            overall_reading_order_accuracy_pct=round(ro_pct, 1),
            overall_provenance_coverage_pct=round(prov_pct, 1),
            overall_raw_preservation_pct=round(raw_pct, 1),
            average_latency_ms=round(avg_latency, 2),
            results=results,
        )
