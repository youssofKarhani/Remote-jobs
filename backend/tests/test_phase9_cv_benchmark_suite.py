"""Test Suite for Phase 9 — CV Benchmark and Regression Suite.

Verifies the entire hardened CV ingestion pipeline across all 7 corpus archetypes:
1. Two-Column Sidebar Regression (Youssof Layout)
2. Single-Column Modern Chronological
3. Multi-Page Continuous Layout
4. Multilingual / German European Format
5. Adversarial / Typo-Laden / Unknown Sections
6. Scanned Raster Image with OCR Fallback Driver
7. Plain Text Markdown Resume

Quality Gates Verified:
- Reading Order Accuracy (100% - No horizontal column interleaving)
- Strict Block Provenance (100% of extracted claims anchored to valid source blocks)
- Raw Text Preservation (100% of raw_values preserved without overwrite)
- Unknown Section Retention (0% silent dropping)
- Evidence Bank Safety (0% auto-verification)
- Quantitative Performance (Sub-50ms execution latency per document)
"""

import pytest

from app.services.cv_benchmark_runner import (
    CVBenchmarkRunner,
    get_standard_benchmark_corpus,
)


@pytest.fixture
def runner() -> CVBenchmarkRunner:
    return CVBenchmarkRunner()


@pytest.fixture
def corpus():
    return get_standard_benchmark_corpus()


# ============================================================================
# 1. Corpus Archetype Execution Tests
# ============================================================================

def test_benchmark_youssof_twocolumn_regression(runner, corpus):
    item = next(c for c in corpus if c.archetype == "two_column_sidebar")
    res = runner.run_item(item)

    assert res.success is True
    assert res.reading_order_correct is True
    assert res.provenance_coverage_pct == 100.0
    assert res.raw_preservation_pct == 100.0
    assert res.is_verified_guarded is True
    assert res.extracted_skills_count >= 4
    assert res.source_blocks_count >= 10


def test_benchmark_single_column_modern(runner, corpus):
    item = next(c for c in corpus if c.archetype == "single_column")
    res = runner.run_item(item)

    assert res.success is True
    assert res.reading_order_correct is True
    assert res.provenance_coverage_pct == 100.0
    assert res.raw_preservation_pct == 100.0
    assert res.extracted_skills_count >= 6
    assert res.quality_score > 0.0


def test_benchmark_multipage_continuous(runner, corpus):
    item = next(c for c in corpus if c.archetype == "multi_page")
    res = runner.run_item(item)

    assert res.success is True
    assert res.total_pages == 2
    assert res.reading_order_correct is True
    assert res.provenance_coverage_pct == 100.0
    assert res.extracted_skills_count >= 4


def test_benchmark_german_multilingual(runner, corpus):
    item = next(c for c in corpus if c.archetype == "multilingual_german")
    res = runner.run_item(item)

    assert res.success is True
    assert res.reading_order_correct is True
    assert res.provenance_coverage_pct == 100.0
    assert res.extracted_skills_count >= 4


def test_benchmark_adversarial_typo_and_unknown_sections(runner, corpus):
    item = next(c for c in corpus if c.archetype == "adversarial_typo")
    res = runner.run_item(item)

    assert res.success is True
    assert res.reading_order_correct is True
    assert res.provenance_coverage_pct == 100.0
    assert res.raw_preservation_pct == 100.0
    # Verifies unknown section was not dropped
    assert res.extracted_unknown_sections_count >= 1


def test_benchmark_scanned_ocr_fallback(runner, corpus):
    item = next(c for c in corpus if c.archetype == "scanned_ocr")
    res = runner.run_item(item)

    assert res.success is True
    assert res.reading_order_correct is True
    assert res.provenance_coverage_pct == 100.0
    assert res.raw_preservation_pct == 100.0
    assert res.extracted_skills_count >= 3


def test_benchmark_plain_text(runner, corpus):
    item = next(c for c in corpus if c.archetype == "plain_text")
    res = runner.run_item(item)

    assert res.success is True
    assert res.reading_order_correct is True
    assert res.provenance_coverage_pct == 100.0
    assert res.extracted_skills_count >= 4


# ============================================================================
# 2. Benchmark Suite Aggregation & Quality Gate Tests
# ============================================================================

def test_full_benchmark_suite_quality_gates(runner):
    summary = runner.run_suite()

    assert summary.total_benchmarks == 7
    assert summary.passed_benchmarks == 7
    assert summary.failed_benchmarks == 0

    # Strict quality thresholds
    assert summary.overall_reading_order_accuracy_pct == 100.0
    assert summary.overall_provenance_coverage_pct == 100.0
    assert summary.overall_raw_preservation_pct == 100.0

    # Sub-50ms average execution latency
    assert summary.average_latency_ms < 50.0

    for r in summary.results:
        assert r.is_verified_guarded is True, f"Evidence Bank invariant violated in {r.name}"
        assert r.error is None
