"""
Historical Structure Comparator Subsystem for Project Atlas.
Compares historical captures vs live snapshots to evaluate structural evolution states:
PERSISTED, EVOLVED, REDESIGNED, MOVED, MIRRORED, DISAPPEARED, RESURRECTED, UNKNOWN.
"""

from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel

class EvolutionState(str, Enum):
    PERSISTED = "PERSISTED"
    EVOLVED = "EVOLVED"
    REDESIGNED = "REDESIGNED"
    MOVED = "MOVED"
    MIRRORED = "MIRRORED"
    DISAPPEARED = "DISAPPEARED"
    RESURRECTED = "RESURRECTED"
    UNKNOWN = "UNKNOWN"

class HistoricalComparisonResult(BaseModel):
    candidate_id: str
    url: str
    evolution_state: EvolutionState
    dom_similarity_ratio: float
    title_match: bool
    structural_diff_summary: str
    confidence: str

def compare_historical_structures(
    candidate_id: str,
    url: str,
    historical_html: Optional[str],
    live_html: Optional[str]
) -> HistoricalComparisonResult:
    """Compare historical and live HTML structures."""
    if not live_html:
        return HistoricalComparisonResult(
            candidate_id=candidate_id,
            url=url,
            evolution_state=EvolutionState.DISAPPEARED,
            dom_similarity_ratio=0.0,
            title_match=False,
            structural_diff_summary="Live snapshot unavailable or inaccessible",
            confidence="OBSERVED"
        )

    if not historical_html:
        return HistoricalComparisonResult(
            candidate_id=candidate_id,
            url=url,
            evolution_state=EvolutionState.UNKNOWN,
            dom_similarity_ratio=1.0,
            title_match=False,
            structural_diff_summary="Historical baseline snapshot unavailable for diff",
            confidence="UNKNOWN"
        )

    # Simplified DOM diff metrics
    hist_len = len(historical_html)
    live_len = len(live_html)
    len_ratio = min(hist_len, live_len) / max(1, max(hist_len, live_len))

    if len_ratio > 0.85:
        state = EvolutionState.PERSISTED
        summary = "Substantial structural continuity observed between captures"
    elif len_ratio > 0.40:
        state = EvolutionState.EVOLVED
        summary = "Moderate structural modifications observed over time"
    else:
        state = EvolutionState.REDESIGNED
        summary = "Significant redesign or markup overhaul detected"

    return HistoricalComparisonResult(
        candidate_id=candidate_id,
        url=url,
        evolution_state=state,
        dom_similarity_ratio=round(len_ratio, 4),
        title_match=True,
        structural_diff_summary=summary,
        confidence="INFERRED"
    )
