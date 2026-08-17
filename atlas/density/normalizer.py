"""
Archive Coverage Normalizer & Protocol-Aware URL Canonicalizer for Phase 1.7.
"""

import math
from typing import Dict, List, Optional, Tuple
from atlas.density.models import ArchiveCoverageRecord, CoverageClassification

def normalize_historical_url(url: str) -> str:
    """Normalize URL string, collapsing protocol/case while preserving path identity."""
    cleaned = url.strip()
    if cleaned.startswith("http://"):
        cleaned = "https://" + cleaned[7:]
    elif not cleaned.startswith("https://"):
        cleaned = "https://" + cleaned

    # Strip fragments
    if "#" in cleaned:
        cleaned = cleaned.split("#", 1)[0]

    # Strip session tracking queries
    if "?" in cleaned:
        base, query = cleaned.split("?", 1)
        # Retain query unless pure session ID
        if any(tok in query.lower() for tok in ("jsessionid", "phpsessid", "sid=", "utm_")):
            cleaned = base
    return cleaned

def compute_archive_coverage(
    domain: str,
    wayback_earliest: Optional[int],
    wayback_latest: Optional[int],
    wayback_count: int,
    cc_earliest: Optional[int],
    cc_latest: Optional[int],
    cc_count: int
) -> ArchiveCoverageRecord:
    """
    Compute archive coverage window and classify agreement without gap conflation.
    """
    wb_years = set(range(wayback_earliest, wayback_latest + 1)) if (wayback_earliest and wayback_latest) else set()
    cc_years = set(range(cc_earliest, cc_latest + 1)) if (cc_earliest and cc_latest) else set()
    overlap = sorted(list(wb_years.intersection(cc_years)))

    if wayback_count > 0 and cc_count > 0 and len(overlap) > 0:
        classification = CoverageClassification.OVERLAPPING_COVERAGE
        summary = f"Overlapping temporal presence across {len(overlap)} years ({min(overlap)}-{max(overlap)})."
    elif wayback_count > 0 and cc_count == 0 and wayback_latest and wayback_latest < 2008:
        classification = CoverageClassification.SOURCE_A_ONLY_WITH_COVERAGE_GAP
        summary = f"Wayback-only captures observed in pre-Common Crawl era ({wayback_earliest}-{wayback_latest}). Not a source conflict."
    elif wayback_count > 0 and cc_count == 0:
        classification = CoverageClassification.TRUE_DISAGREEMENT
        summary = f"Captured in Wayback ({wayback_count} snapshots) but omitted in contemporary Common Crawl indexing."
    elif wayback_count == 0 and cc_count > 0:
        classification = CoverageClassification.TRUE_DISAGREEMENT
        summary = f"Captured in Common Crawl ({cc_count} snapshots) but absent from Wayback CDX."
    else:
        classification = CoverageClassification.INSUFFICIENT
        summary = "No archive records found in either source."

    return ArchiveCoverageRecord(
        domain=domain,
        wayback_earliest_year=wayback_earliest,
        wayback_latest_year=wayback_latest,
        wayback_capture_count=wayback_count,
        commoncrawl_earliest_year=cc_earliest,
        commoncrawl_latest_year=cc_latest,
        commoncrawl_capture_count=cc_count,
        overlapping_years=overlap,
        coverage_classification=classification,
        coverage_summary=summary
    )

def compute_shannon_entropy(counts: Dict[str, int]) -> float:
    """Calculate Shannon entropy for a categorical frequency dictionary."""
    total = sum(counts.values())
    if total <= 1:
        return 0.0
    entropy = 0.0
    for cnt in counts.values():
        if cnt > 0:
            p = cnt / total
            entropy -= p * math.log(p)
    return round(entropy, 4)
