"""Master Live Evidence Collector coordinating live HTTP and archive queries."""

import time
import hashlib
from pathlib import Path
from typing import List, Tuple, Optional, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed

from atlas.pilot.models import PilotDomainRecord, PilotEvidenceCapture
from atlas.live.models import (
    LiveEvidenceRecord, ArchiveEvidenceRecord, EvidenceFailureRecord
)
from atlas.live.http import fetch_live_page
from atlas.live.archive import query_live_archive_timeline
from atlas.live.logger import LiveAuditLogger
from atlas.live.guard import assert_live_mode

def collect_single_domain_live_evidence(
    rec: PilotDomainRecord,
    raw_artifacts_dir: Path = Path("data/phase1_3_live/evidence/raw_artifacts"),
    timeout: int = 8,
    audit_logger: Optional[LiveAuditLogger] = None
) -> Tuple[PilotEvidenceCapture, Optional[LiveEvidenceRecord], ArchiveEvidenceRecord, List[EvidenceFailureRecord]]:
    """
    Collect genuine empirical live and archive evidence for a domain with zero simulation.
    """
    assert_live_mode(f"Collect Live Evidence for {rec.domain}")

    raw_artifacts_dir.mkdir(parents=True, exist_ok=True)
    if audit_logger is None:
        audit_logger = LiveAuditLogger()

    failures: List[EvidenceFailureRecord] = []

    # 1. Live Page Fetch
    live_rec, live_fail = fetch_live_page(
        domain=rec.domain,
        raw_artifacts_dir=raw_artifacts_dir,
        timeout=timeout,
        audit_logger=audit_logger
    )
    if live_fail:
        failures.append(live_fail)

    # 2. Archive CDX Query
    archive_rec, archive_fail = query_live_archive_timeline(
        domain=rec.domain,
        timeout=timeout,
        audit_logger=audit_logger
    )
    if archive_fail:
        failures.append(archive_fail)

    # 3. Combine into normalized PilotEvidenceCapture
    if live_rec:
        status_code = live_rec.http_status
        title = live_rec.page_title
        html_bytes = live_rec.html_bytes
        text_bytes = live_rec.extracted_text_bytes
        frameworks = live_rec.frameworks_detected
        has_tables = live_rec.has_tables_layout
        has_inline = live_rec.has_inline_styles
        has_frameset = live_rec.has_frameset
        has_retro = live_rec.has_retro_elements
        html_hash = live_rec.html_raw_sha256
    else:
        status_code = 0
        title = f"Failed to connect: {rec.domain}"
        html_bytes = 0
        text_bytes = 0
        frameworks = []
        has_tables = False
        has_inline = False
        has_frameset = False
        has_retro = False
        html_hash = ""

    earliest_yr = archive_rec.earliest_wayback_year
    latest_yr = archive_rec.latest_wayback_year
    cdx_count = archive_rec.wayback_snapshots_count
    sim_score = archive_rec.historical_similarity_score

    summary_str = (
        f"LIVE EVIDENCE | Domain: {rec.domain} | HTTP: {status_code} | "
        f"HTML SHA: {html_hash[:12]}... | Wayback: {archive_rec.wayback_status} ({cdx_count}) | "
        f"Span: {earliest_yr}-{latest_yr} | Tables: {has_tables} | Retro: {has_retro}"
    )
    combined_hash = hashlib.sha256(summary_str.encode("utf-8")).hexdigest()

    evidence_capture = PilotEvidenceCapture(
        pilot_id=rec.pilot_id,
        domain=rec.domain,
        category=rec.category,
        live_status_code=status_code,
        page_title=title,
        extracted_text_bytes=text_bytes,
        html_bytes=html_bytes,
        frameworks_detected=frameworks,
        has_tables_layout=has_tables,
        has_inline_styles=has_inline,
        has_frameset=has_frameset,
        has_retro_elements=has_retro,
        cdx_capture_count=cdx_count,
        earliest_archive_year=earliest_yr,
        latest_archive_year=latest_yr,
        historical_similarity_score=sim_score,
        evidence_sha256=combined_hash,
        raw_evidence_summary=summary_str
    )

    return evidence_capture, live_rec, archive_rec, failures

def collect_pilot_batch_live(
    records: List[PilotDomainRecord],
    raw_artifacts_dir: Path = Path("data/phase1_3_live/evidence/raw_artifacts"),
    max_workers: int = 6,
    timeout: int = 8
) -> List[Tuple[PilotEvidenceCapture, Optional[LiveEvidenceRecord], ArchiveEvidenceRecord, List[EvidenceFailureRecord]]]:
    """
    Collect live evidence concurrently across a batch of domains using a thread pool.
    """
    assert_live_mode("Batch Live Evidence Collection")

    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_rec = {
            executor.submit(collect_single_domain_live_evidence, r, raw_artifacts_dir, timeout): r
            for r in records
        }
        for future in as_completed(future_to_rec):
            res = future.result()
            results.append(res)

    # Sort deterministically by pilot_id
    results.sort(key=lambda item: item[0].pilot_id)
    return results
