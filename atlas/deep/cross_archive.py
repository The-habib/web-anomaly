"""Cross-Source Archive Comparison Engine (Wayback vs Common Crawl)."""

import requests
from typing import Tuple, Optional
from atlas.deep.models import CrossArchiveDisagreementRecord, ArchiveAgreementState

def query_common_crawl_index(url: str, timeout: int = 5) -> Tuple[int, Optional[int]]:
    """
    Query Common Crawl index API for URL observations.
    Returns (capture_count, earliest_year).
    """
    cc_index_url = f"https://index.commoncrawl.org/CC-MAIN-2024-10-index?url={url}&output=json"
    try:
        resp = requests.get(
            cc_index_url,
            headers={"User-Agent": "ProjectAtlas-DeepArchaeology/1.5"},
            timeout=timeout
        )
        if resp.status_code == 200:
            lines = [l for l in resp.text.strip().split("\n") if l.strip()]
            if lines:
                return len(lines), 2024
    except Exception:
        pass
    return 0, None

def evaluate_archive_agreement(
    domain: str,
    path_url: str,
    wayback_count: int,
    wayback_earliest: Optional[int],
    commoncrawl_count: int,
    commoncrawl_earliest: Optional[int]
) -> CrossArchiveDisagreementRecord:
    """
    Compare multi-archive coverage and classify agreement status.
    """
    if wayback_count > 0 and commoncrawl_count > 0:
        state = ArchiveAgreementState.AGREE
        summary = f"Both archives confirm presence ({wayback_count} WB, {commoncrawl_count} CC captures)."
    elif wayback_count > 0 and commoncrawl_count == 0:
        state = ArchiveAgreementState.WAYBACK_ONLY
        summary = f"Captured in Wayback ({wayback_count} snapshots) but absent from Common Crawl index."
    elif wayback_count == 0 and commoncrawl_count > 0:
        state = ArchiveAgreementState.COMMONCRAWL_ONLY
        summary = f"Captured in Common Crawl ({commoncrawl_count} snapshots) but absent from Wayback CDX."
    else:
        state = ArchiveAgreementState.INSUFFICIENT
        summary = "No archive records found in either Wayback or Common Crawl."

    return CrossArchiveDisagreementRecord(
        domain=domain,
        path_url=path_url,
        wayback_capture_count=wayback_count,
        wayback_earliest_year=wayback_earliest,
        commoncrawl_capture_count=commoncrawl_count,
        commoncrawl_earliest_year=commoncrawl_earliest,
        agreement_state=state,
        disagreement_summary=summary
    )
