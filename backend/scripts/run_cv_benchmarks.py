"""CLI Tool: Run CV Ingestion Hardening Benchmark & Regression Suite (Phase 9).

Executes across all 7 corpus archetypes:
1. Two-Column Sidebar (Youssof regression layout)
2. Single-Column Modern Chronological
3. Multi-Page Continuous
4. Multilingual / German European Format
5. Adversarial / Typo-Laden / Unknown Sections
6. Scanned Raster Image (with OCR Fallback)
7. Plain Text / DOCX Non-PDF Documents

Usage:
    uv run python scripts/run_cv_benchmarks.py
"""

import sys
from pathlib import Path

# Ensure backend root is on sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.services.cv_benchmark_runner import CVBenchmarkRunner, BenchmarkSuiteSummary


def print_header(title: str) -> None:
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80)


def main() -> int:
    print_header("REMOTEJOBS CV INGESTION HARDENING: PHASE 9 BENCHMARK SUITE")
    print("Executing end-to-end benchmark across 7 document archetypes...\n")

    runner = CVBenchmarkRunner()
    summary: BenchmarkSuiteSummary = runner.run_suite()

    header_fmt = "{:<32} {:<10} {:<8} {:<8} {:<8} {:<10} {:<10}"
    row_fmt = "{:<32} {:<10} {:<8} {:<8} {:<8} {:<10.1f} {:<10.2f}"

    print("-" * 92)
    print(header_fmt.format("Benchmark Name", "Status", "Blocks", "Skills", "Reading", "Prov %", "Time (ms)"))
    print("-" * 92)

    for r in summary.results:
        status_str = "[PASS]" if r.success and r.reading_order_correct and r.provenance_coverage_pct == 100.0 else "[FAIL]"
        ro_str = "OK" if r.reading_order_correct else "ERR"
        print(row_fmt.format(
            r.name[:32],
            status_str,
            r.source_blocks_count,
            r.extracted_skills_count,
            ro_str,
            r.provenance_coverage_pct,
            r.total_time_ms,
        ))
        if r.error:
            print(f"   └─ ERROR: {r.error}")

    print("-" * 92)
    print("\nBenchmark Suite Aggregate Metrics:")
    print(f"  Total Benchmarks Evaluated      : {summary.total_benchmarks}")
    print(f"  Passed Benchmarks                : {summary.passed_benchmarks} / {summary.total_benchmarks}")
    print(f"  Overall Reading Order Accuracy   : {summary.overall_reading_order_accuracy_pct}%")
    print(f"  Overall Provenance Coverage      : {summary.overall_provenance_coverage_pct}%")
    print(f"  Overall Raw Preservation Rate    : {summary.overall_raw_preservation_pct}%")
    print(f"  Average End-to-End Latency       : {summary.average_latency_ms} ms")

    all_passed = summary.failed_benchmarks == 0
    if all_passed:
        print("\n[SUCCESS] ALL BENCHMARK QUALITY GATES PASSED! Ready for Manual Quality Review.")
        return 0
    else:
        print("\n[FAILURE] Some benchmark quality gates failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
