"""Candidate Path Prioritization Engine (Retrieval Priority Scoring)."""

from typing import List
from atlas.deep.models import PathCandidate, PathCategory

CATEGORY_PRIORITY_WEIGHTS = {
    PathCategory.ACADEMIC_USER_SPACE: 35.0,
    PathCategory.ARCHIVE_DIRECTORY: 30.0,
    PathCategory.LEGACY_DOCS: 25.0,
    PathCategory.PUBLIC_FILES: 20.0,
    PathCategory.YEAR_PREFIXED: 20.0,
    PathCategory.SOFTWARE_PROJECT: 15.0,
    PathCategory.PERSONAL_BLOG: 15.0,
    PathCategory.GENERAL_DIRECTORY: 5.0
}

def calculate_retrieval_priority(candidate: PathCandidate) -> float:
    """
    Score retrieval priority (0.0 - 100.0) to select top candidate paths for download.
    NOTE: This is strictly a fetch prioritization metric, NOT an anomaly score.
    """
    priority = 0.0

    # 1. Path Category Weight (0 - 35 points)
    priority += CATEGORY_PRIORITY_WEIGHTS.get(candidate.path_category, 5.0)

    # 2. Historical Age Signal (0 - 40 points)
    if candidate.first_observed_year:
        if candidate.first_observed_year <= 1996:
            priority += 40.0
        elif candidate.first_observed_year <= 2000:
            priority += 30.0
        elif candidate.first_observed_year <= 2005:
            priority += 20.0
        elif candidate.first_observed_year <= 2010:
            priority += 10.0

    # 3. Path Brevity & Depth (Shallow paths preferred: 0 - 15 points)
    slash_count = candidate.path.count("/")
    if slash_count <= 2:
        priority += 15.0
    elif slash_count <= 4:
        priority += 10.0

    # 4. Multi-Source Discovery Bonus (0 - 10 points)
    if candidate.discovery_source == "WAYBACK_CDX":
        priority += 10.0

    return min(priority, 100.0)

def rank_and_select_candidates(
    candidates: List[PathCandidate],
    max_retrievals: int = 15
) -> List[PathCandidate]:
    """
    Rank candidate paths by retrieval priority and select top N for targeted download.
    """
    for c in candidates:
        c.retrieval_priority = calculate_retrieval_priority(c)

    # Sort descending by priority
    sorted_candidates = sorted(candidates, key=lambda x: x.retrieval_priority, reverse=True)
    return sorted_candidates[:max_retrievals]
