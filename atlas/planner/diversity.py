"""
Diversity Controller Subsystem for Project Atlas.
Tracks candidate diversity across domain categories, platform signatures, path patterns, and eras.
"""

from typing import List, Dict, Any
from pydantic import BaseModel, Field

class DiversityAudit(BaseModel):
    category_distribution: Dict[str, int]
    strategy_distribution: Dict[str, int]
    platform_distribution: Dict[str, int]
    diversity_index: float  # Normalized 0.0 to 1.0
    recommendations: List[str]

def audit_candidate_diversity(candidates: List[Dict[str, Any]]) -> DiversityAudit:
    """Analyze diversity metrics across candidate pool."""
    categories: Dict[str, int] = {}
    strategies: Dict[str, int] = {}
    platforms: Dict[str, int] = {}

    for c in candidates:
        cat = c.get("category", c.get("domain_category", "General"))
        strat = c.get("source_strategy", "UNKNOWN")
        path = c.get("path", "")
        
        categories[cat] = categories.get(cat, 0) + 1
        strategies[strat] = strategies.get(strat, 0) + 1

        if "~" in path:
            plat = "TILDE_SPACE"
        elif ".edu" in c.get("domain", ""):
            plat = "ACADEMIC_SERVER"
        elif ".gov" in c.get("domain", ""):
            plat = "GOV_ARCHIVE"
        else:
            plat = "INDEPENDENT_WEB"
        platforms[plat] = platforms.get(plat, 0) + 1

    total = max(1, len(candidates))
    unique_cats = len(categories)
    unique_strats = len(strategies)

    div_idx = round(min(1.0, (unique_cats / 6.0) * 0.5 + (unique_strats / 8.0) * 0.5), 3)

    recs = []
    if categories.get("Universities", 0) > total * 0.4:
        recs.append("University candidates overrepresented; expand independent and open-source sites.")
    if strategies.get("USER_SPACE", 0) > total * 0.4:
        recs.append("User-space candidates overrepresented; prioritize technology fossils and government document trees.")

    return DiversityAudit(
        category_distribution=categories,
        strategy_distribution=strategies,
        platform_distribution=platforms,
        diversity_index=div_idx,
        recommendations=recs
    )
