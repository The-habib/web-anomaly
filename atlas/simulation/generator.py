"""Synthetic evidence generator for offline unit tests and scoring rule validation.
IMPORTANT: PROHIBITED FROM RUNNING IN LIVE EMPIRICAL MODE.
"""

import hashlib
from typing import Dict, Any
from atlas.pilot.models import PilotDomainRecord, PilotEvidenceCapture
from atlas.live.guard import assert_no_simulation

def generate_synthetic_evidence_profile(rec: PilotDomainRecord) -> PilotEvidenceCapture:
    """
    Generate synthetic test fixture evidence for unit tests.
    Raises SimulationContaminationError if called within a LIVE empirical context.
    """
    assert_no_simulation("generate_synthetic_evidence_profile")

    domain = rec.domain
    category = rec.category

    has_tables = False
    has_inline = False
    has_frameset = False
    has_retro = False
    frameworks = []
    earliest_year = 2000
    latest_year = 2026
    cdx_count = 1000
    title = f"{domain} Test Fixture"
    sim_score = 0.30
    html_bytes = 25000
    text_bytes = 8000

    raw_summary = (
        f"SYNTHETIC FIXTURE | Domain: {domain} | Category: {category} | "
        f"Span: {earliest_year}-{latest_year} | Table: {has_tables} | "
        f"Retro: {has_retro} | Sim: {sim_score:.2f}"
    )
    evidence_sha256 = hashlib.sha256(raw_summary.encode("utf-8")).hexdigest()

    return PilotEvidenceCapture(
        pilot_id=rec.pilot_id,
        domain=domain,
        category=category,
        live_status_code=200,
        page_title=title,
        extracted_text_bytes=text_bytes,
        html_bytes=html_bytes,
        frameworks_detected=frameworks,
        has_tables_layout=has_tables,
        has_inline_styles=has_inline,
        has_frameset=has_frameset,
        has_retro_elements=has_retro,
        cdx_capture_count=cdx_count,
        earliest_archive_year=earliest_year,
        latest_archive_year=latest_year,
        historical_similarity_score=sim_score,
        evidence_sha256=evidence_sha256,
        raw_evidence_summary=raw_summary
    )
