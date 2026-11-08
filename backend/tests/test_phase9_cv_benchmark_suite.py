"""Test Suite for Phase 9 — CV Benchmark and Regression Suite.

Verifies the entire hardened CV ingestion pipeline across all 16 corpus archetypes:
 1. Simple Single-Column CV
 2. Two-Column CV (Youssof Layout)
 3. Sidebar CV (Asymmetric layout)
 4. Three-Column Layout
 5. Canva-Style CV (Grid and visual cards)
 6. Scanned PDF (with OCR Fallback)
 7. Icon-Heavy CV (Glyph-annotated text)
 8. Table-Based CV (Tabular grid cells)
 9. Europass-Style CV (European timeline standard)
10. Academic CV (Multi-page scholarly layout)
11. CV Without Explicit Section Headings (Implicit typography)
12. CV With Headers/Footers (Running page metadata)
13. German Lebenslauf (German sections and date formatting)
14. Multilingual CV (Bilingual parallel sections)
15. DOCX CV (OpenXML structured document)
16. Unusual / Custom Section Names (Non-standard categories)

Quality Gates Verified:
- Reading Order Accuracy (100% - No column interleaving)
- Strict Block Provenance (100% of claims anchored to valid source blocks)
- Raw Text Preservation (100% of raw_values preserved without overwrite)
- Fabricated Facts Safety (Approaches 0.0% - zero hallucinations)
- Invalid Provenance Rate (0.0%)
- Evidence Bank Safety (0% auto-verification - is_verified == False)
"""

import pytest

from app.services.cv_benchmark_runner import (
    CVBenchmarkRunner,
    get_full_16_corpus,
)


@pytest.fixture
def runner() -> CVBenchmarkRunner:
    return CVBenchmarkRunner()


@pytest.fixture
def corpus():
    return get_full_16_corpus()


# ============================================================================
# 1. Corpus Archetype Execution Tests
# ============================================================================

def test_benchmark_simple_single_column(runner, corpus):
    item = next(c for c in corpus if c.archetype == "simple_single_column")
    res = runner.run_item(item)
    assert res.success is True
    assert res.reading_order_correct is True
    assert res.provenance_coverage_pct == 100.0
    assert res.fabricated_fact_rate_pct == 0.0
    assert res.extracted_skills_count >= 5


def test_benchmark_two_column_youssof(runner, corpus):
    item = next(c for c in corpus if c.archetype == "two_column")
    res = runner.run_item(item)
    assert res.success is True
    assert res.reading_order_correct is True
    assert res.provenance_coverage_pct == 100.0
    assert res.raw_preservation_pct == 100.0
    assert res.is_verified_guarded is True
    assert res.extracted_skills_count >= 4
    assert res.source_blocks_count >= 10


def test_benchmark_sidebar_cv(runner, corpus):
    item = next(c for c in corpus if c.archetype == "sidebar_cv")
    res = runner.run_item(item)
    assert res.success is True
    assert res.reading_order_correct is True
    assert res.provenance_coverage_pct == 100.0
    assert res.fabricated_fact_rate_pct == 0.0


def test_benchmark_three_column_layout(runner, corpus):
    item = next(c for c in corpus if c.archetype == "three_column")
    res = runner.run_item(item)
    assert res.success is True
    assert res.reading_order_correct is True
    assert res.provenance_coverage_pct == 100.0
    assert res.source_blocks_count >= 5


def test_benchmark_canva_style_cv(runner, corpus):
    item = next(c for c in corpus if c.archetype == "canva_style")
    res = runner.run_item(item)
    assert res.success is True
    assert res.reading_order_correct is True
    assert res.provenance_coverage_pct == 100.0
    assert res.source_blocks_count >= 3


def test_benchmark_scanned_ocr_fallback(runner, corpus):
    item = next(c for c in corpus if c.archetype == "scanned_pdf")
    res = runner.run_item(item)
    assert res.success is True
    assert res.reading_order_correct is True
    assert res.provenance_coverage_pct == 100.0
    assert res.extracted_skills_count >= 3


def test_benchmark_icon_heavy_cv(runner, corpus):
    item = next(c for c in corpus if c.archetype == "icon_heavy")
    res = runner.run_item(item)
    assert res.success is True
    assert res.reading_order_correct is True
    assert res.provenance_coverage_pct == 100.0
    assert res.extracted_skills_count >= 4


def test_benchmark_table_based_cv(runner, corpus):
    item = next(c for c in corpus if c.archetype == "table_based")
    res = runner.run_item(item)
    assert res.success is True
    assert res.reading_order_correct is True
    assert res.provenance_coverage_pct == 100.0
    assert res.extracted_skills_count >= 3


def test_benchmark_europass_style_cv(runner, corpus):
    item = next(c for c in corpus if c.archetype == "europass_style")
    res = runner.run_item(item)
    assert res.success is True
    assert res.reading_order_correct is True
    assert res.provenance_coverage_pct == 100.0
    assert res.fabricated_fact_rate_pct == 0.0


def test_benchmark_academic_cv(runner, corpus):
    item = next(c for c in corpus if c.archetype == "academic_cv")
    res = runner.run_item(item)
    assert res.success is True
    assert res.reading_order_correct is True
    assert res.provenance_coverage_pct == 100.0
    assert res.total_pages == 2


def test_benchmark_no_explicit_headings(runner, corpus):
    item = next(c for c in corpus if c.archetype == "no_explicit_headings")
    res = runner.run_item(item)
    assert res.success is True
    assert res.reading_order_correct is True
    assert res.provenance_coverage_pct == 100.0
    assert res.extracted_skills_count >= 4


def test_benchmark_headers_footers(runner, corpus):
    item = next(c for c in corpus if c.archetype == "headers_footers")
    res = runner.run_item(item)
    assert res.success is True
    assert res.reading_order_correct is True
    assert res.provenance_coverage_pct == 100.0
    assert res.total_pages == 2


def test_benchmark_german_lebenslauf(runner, corpus):
    item = next(c for c in corpus if c.archetype == "german_lebenslauf")
    res = runner.run_item(item)
    assert res.success is True
    assert res.reading_order_correct is True
    assert res.provenance_coverage_pct == 100.0
    assert res.extracted_skills_count >= 4


def test_benchmark_multilingual_cv(runner, corpus):
    item = next(c for c in corpus if c.archetype == "multilingual_cv")
    res = runner.run_item(item)
    assert res.success is True
    assert res.reading_order_correct is True
    assert res.provenance_coverage_pct == 100.0
    assert res.extracted_skills_count >= 3


def test_benchmark_docx_cv(runner, corpus):
    item = next(c for c in corpus if c.archetype == "docx_cv")
    res = runner.run_item(item)
    assert res.success is True
    assert res.reading_order_correct is True
    assert res.provenance_coverage_pct == 100.0
    assert res.extracted_skills_count >= 3


def test_benchmark_unusual_custom_sections(runner, corpus):
    item = next(c for c in corpus if c.archetype == "unusual_custom_sections")
    res = runner.run_item(item)
    assert res.success is True
    assert res.reading_order_correct is True
    assert res.provenance_coverage_pct == 100.0
    assert res.extracted_unknown_sections_count >= 1


# ============================================================================
# 2. Benchmark Suite Aggregation & Quality Gate Tests
# ============================================================================

def test_full_benchmark_suite_quality_gates(runner):
    summary = runner.run_suite()

    assert summary.total_benchmarks == 16
    assert summary.passed_benchmarks == 16
    assert summary.failed_benchmarks == 0

    # Strict quality thresholds
    assert summary.overall_reading_order_accuracy_pct == 100.0
    assert summary.overall_provenance_coverage_pct == 100.0
    assert summary.overall_raw_preservation_pct == 100.0

    # Safety metrics
    assert summary.average_fabricated_fact_rate_pct == 0.0, "Fabricated facts must approach 0.0%"
    assert summary.average_invalid_provenance_rate_pct == 0.0, "Invalid provenance must be 0.0%"
    assert summary.total_layout_failures == 0

    # Latency threshold
    assert summary.average_latency_ms < 150.0

    for r in summary.results:
        assert r.is_verified_guarded is True, f"Evidence Bank invariant violated in {r.name}"
        assert r.error is None
