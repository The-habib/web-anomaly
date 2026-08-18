"""
Prior-Art & Obscurity Assessment Engine for Project Atlas — Treasure Mode.
Evaluates public web and archive documentation levels without overclaiming novelty.
"""

from typing import Tuple, List
from atlas.treasure.models import PriorArtStatus

WELL_KNOWN_SITES = ["spacejam.com", "zombo.com", "catb.org", "toastytech.com"]
DOCUMENTED_ARCHIVES = ["uspto.gov", "gnu.org", "textfiles.com", "w3.org", "ietf.org"]

def evaluate_prior_art_status(
    domain: str,
    path: str,
    title: str,
    structural_signals: List[str]
) -> Tuple[PriorArtStatus, str]:
    """
    Classify prior-art documentation level for an investigated archaeological candidate.
    """
    dom_lower = domain.lower()
    path_lower = path.lower()

    if any(ws in dom_lower for ws in WELL_KNOWN_SITES) and (path == "/" or not path):
        return (
            PriorArtStatus.WELL_DOCUMENTED,
            "Widely recognized early web cultural landmark with substantial external public documentation."
        )

    if any(da in dom_lower for da in DOCUMENTED_ARCHIVES) and ("manual" in path_lower or "mpep" in path_lower or "rfc" in path_lower):
        return (
            PriorArtStatus.DOCUMENTED,
            "Documented official organizational or technical repository preserving legacy publication formatting."
        )

    if "rotten.com" in path_lower or "halifax" in path_lower or "~" in path_lower:
        return (
            PriorArtStatus.OBSCURE,
            "Atlas did not identify substantial contemporary search visibility or mainstream index references for this specific nested path."
        )

    if len(structural_signals) >= 3 and "orphaned_from_root_navigation" in structural_signals:
        return (
            PriorArtStatus.OBSCURE,
            "Buried unlinked archaeological surface with low public search discoverability."
        )

    return (
        PriorArtStatus.POORLY_DOCUMENTED,
        "Surviving subpath with limited modern search engine indexing."
    )
