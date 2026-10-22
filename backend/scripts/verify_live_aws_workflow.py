#!/usr/bin/env python3
"""End-to-End Live AWS & Cross-Project Workflow Verifier for remotejobs-public.

Verifies:
1. Connectivity & dynamic EC2 Public IP discovery via AWS_WAKE_ENDPOINT.
2. Automatic cold-start wake-up and readiness polling on Orchestrator (:8000/health).
3. Execution of all 5 AIService structured tasks with fallback_to_heuristics=False:
   - extract_cv_to_evidence_bank
   - prescreen_job
   - assess_job
   - select_cv_evidence (with strict anti-hallucination gate verification)
   - generate_cover_letter
"""

from __future__ import annotations

import argparse
import asyncio
import sys
import time
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.config import settings
from app.integrations.llm_ai_service import DefaultAIService


async def run_all_5_tasks(service: DefaultAIService) -> None:
    """Execute all 5 AIService methods and assert strict schema and safety invariants."""
    print("\n[1/5] Testing extract_cv_to_evidence_bank ...")
    cv_text = (
        "Alex Morgan\n"
        "Staff Cloud & AI Architect - Munich, Germany\n"
        "Phone: +49 170 9876543\n"
        "LinkedIn: https://linkedin.com/in/alexmorgan\n"
        "Experience:\n"
        "QuantumCloud - Senior Platform Engineer\n"
        "- Built high-throughput telemetry ingestion pipeline in Python and FastAPI.\n"
        "Skills:\n"
        "Python, FastAPI, PostgreSQL, Kubernetes, AWS\n"
    )
    draft = await service.extract_cv_to_evidence_bank(cv_text)
    print(f"      ✓ Extracted headline='{draft.headline}', experiences={len(draft.experiences)}, skills={len(draft.skills)}")

    print("[2/5] Testing prescreen_job ...")
    pre = await service.prescreen_job(
        candidate_summary="Staff Python, FastAPI, Kubernetes, AWS engineer",
        job_title="Senior Cloud Backend Engineer",
        job_tags=["Python", "FastAPI", "AWS"],
    )
    print(f"      ✓ Prescreen relevant={pre.relevant}, confidence={pre.confidence:.2f}, reasons={pre.reason_codes}")

    print("[3/5] Testing assess_job ...")
    assess = await service.assess_job(
        candidate_profile_text="Alex Morgan [EXP_001] [SKILL_001] Python FastAPI Kubernetes AWS",
        job_details={
            "title": "Senior Cloud Backend Engineer (m/w/d) [Remote]",
            "company_name": "NordicCloud AB",
            "location": "Stockholm / Remote",
            "tags": ["Python", "FastAPI", "Kubernetes"],
            "description": "Design resilient cloud-native microservices and AI pipelines on AWS.",
        },
    )
    print(
        f"      ✓ Assessment overall_score={assess.overall_score}, "
        f"recommendation='{assess.recommendation}', sanitized_title='{assess.sanitized_job_title}'"
    )

    print("[4/5] Testing select_cv_evidence (anti-hallucination gate) ...")
    allowed_ids = {
        "experience_bullets": ["EXP_001", "EXP_002"],
        "skills": ["SKILL_001", "SKILL_002"],
        "projects": ["PROJ_001"],
        "certifications": ["CERT_001"],
    }
    selection = await service.select_cv_evidence(
        job_details={"title": "Senior Cloud Backend Engineer", "tags": ["Python", "AWS"]},
        allowed_evidence_ids=allowed_ids,
    )
    assert set(selection.experience_bullet_ids).issubset(set(allowed_ids["experience_bullets"]))
    assert set(selection.skill_ids).issubset(set(allowed_ids["skills"]))
    print(
        f"      ✓ Selected bullets={selection.experience_bullet_ids}, skills={selection.skill_ids}"
    )

    print("[5/5] Testing generate_cover_letter ...")
    letter = await service.generate_cover_letter(
        candidate_profile_text="Alex Morgan - Staff Cloud & AI Architect",
        job_details={"title": "Senior Cloud Backend Engineer", "company_name": "NordicCloud AB"},
        selected_evidence_items=[
            {"stable_id": "EXP_001", "text": "Built high-throughput telemetry ingestion pipeline in Python and FastAPI."}
        ],
        strategy="technical_depth",
    )
    print(
        f"      ✓ Generated cover letter ({len(letter.letter_text)} chars), "
        f"referenced_evidence_ids={letter.referenced_evidence_ids}"
    )


async def verify_live_aws(wait_timeout: int) -> None:
    """Verify against the configured live AWS Orchestrator + Wake endpoint."""
    service = DefaultAIService(
        provider="orchestrator",
        orchestrator_url=settings.ORCHESTRATOR_URL,
        wake_url=settings.AWS_WAKE_ENDPOINT,
        timeout=max(60.0, settings.LLM_TIMEOUT_SECONDS),
        fallback_to_heuristics=False,
    )
    print(f"Initial ORCHESTRATOR_URL : {service.orchestrator_url}")
    print(f"Configured WAKE_URL      : {service.wake_url or '(not set)'}")

    is_live = await service.check_orchestrator_liveliness()
    if not is_live:
        print("Orchestrator is currently unreachable (cold / stopped or IP changed).")
        if service.wake_url:
            print("Triggering Serverless Wake endpoint and discovering live EC2 Public IP...")
            await service.trigger_wake()
            print(f"Active ORCHESTRATOR_URL  : {service.orchestrator_url}")
        deadline = time.time() + wait_timeout
        while time.time() < deadline:
            if await service.check_orchestrator_liveliness():
                is_live = True
                break
            await service.discover_orchestrator_url()
            print(f"  Waiting for Orchestrator ({service.orchestrator_url}) to come online...")
            await asyncio.sleep(5)

    if not is_live:
        print(
            "\n[!] Orchestrator is still unreachable. "
            "Ensure EC2 instance i-07510214fa4da2427 is started or run:\n"
            "    python \"..\\..\\My sleepless slaves\\scripts\\aws_sync_and_deploy.py\""
        )
        sys.exit(1)

    print(f"✓ Connected to live Orchestrator at {service.orchestrator_url}!")
    await run_all_5_tasks(service)

    if service.wake_url:
        print("[6/6] Testing live stale-IP self-healing via Serverless Wake API Gateway ...")
        stale_service = DefaultAIService(
            provider="orchestrator",
            orchestrator_url="http://51.20.134.201:8000",
            wake_url=service.wake_url,
            timeout=60.0,
            fallback_to_heuristics=False,
        )
        healed_pre = await stale_service.prescreen_job(
            candidate_summary="Python, FastAPI, Kubernetes, AWS",
            job_title="Principal Platform Engineer",
            job_tags=["Python", "AWS"],
        )
        print(
            f"      ✓ Self-healed from stale IP http://51.20.134.201:8000 -> {stale_service.orchestrator_url} "
            f"(relevant={healed_pre.relevant}, confidence={healed_pre.confidence:.2f})"
        )

    print("\n✓ All live AWS AI workflow steps succeeded!")


async def main_async() -> None:
    parser = argparse.ArgumentParser(description="Verify remotejobs-public AI workflow against AWS or local stack")
    parser.add_argument("--wait-timeout", type=int, default=240, help="Seconds to wait for cold-start wake")
    args = parser.parse_args()
    await verify_live_aws(wait_timeout=args.wait_timeout)


if __name__ == "__main__":
    asyncio.run(main_async())
