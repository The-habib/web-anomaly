"""
Prior-Art & Obscurity Assessment Engine for Project Atlas — Treasure Mode.
Evaluates public web and archive documentation levels using structural signals
and path discoverability metrics without domain hardcoding.
"""

from typing import Tuple, List
from atlas.treasure.models import PriorArtStatus

def evaluate_prior_art_status(
    domain: str,
    path: str,
    title: str,
    structural_signals: List[str]
) -> Tuple[PriorArtStatus, str]:
    """
    Classify prior-art documentation level for an investigated archaeological candidate
    based on objective structural discoverability.
    """
    path_depth = path.strip("/").count("/") + 1
    is_orphan = "orphaned_from_root_navigation" in structural_signals

    if is_orphan and path_depth >= 2 and len(structural_signals) >= 3:
        return (
            PriorArtStatus.OBSCURE,
            "Deeply nested and orphaned archaeological surface with low public search discoverability."
        )

    if is_orphan or path_depth >= 2:
        return (
            PriorArtStatus.POORLY_DOCUMENTED,
            "Surviving subpath with limited modern search engine indexing or discoverability."
        )

    if path == "/" or not path:
        return (
            PriorArtStatus.DOCUMENTED,
            "Root domain surface accessible via standard search indexing."
        )

    return (
        PriorArtStatus.DOCUMENTED,
        "Public subpath indexed across standard public directories."
    )
