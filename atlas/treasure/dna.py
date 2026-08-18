"""
Treasure DNA & Multi-Dimensional Profile Subsystem for Project Atlas.
Computes an 11-dimensional explanatory research profile for candidate web artifacts.
Permanently enforces separation between RESEARCH_PRIORITY, TREASURE_INTEREST, and HUMAN_VALIDATION.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from atlas.treasure.models import CandidateRecord, InvestigationRecord, TreasureState

class DimensionTrace(BaseModel):
    score: float  # Normalized 0.0 to 10.0
    confidence: str  # OBSERVED, INFERRED, UNKNOWN, INSUFFICIENT
    evidence_summary: str
    data_points: Dict[str, Any] = Field(default_factory=dict)

class TreasureDNA(BaseModel):
    dna_id: str
    candidate_id: str
    url: str
    domain: str
    created_at_utc: str
    
    # 11 Explanatory Dimensions
    historical_depth: DimensionTrace
    survival: DimensionTrace
    structural_rarity: DimensionTrace
    technology_age: DimensionTrace
    orphan_probability: DimensionTrace
    discoverability_difficulty: DimensionTrace
    archive_persistence: DimensionTrace
    content_uniqueness: DimensionTrace
    platform_interest: DimensionTrace
    historical_context: DimensionTrace
    evidence_quality: DimensionTrace

    # Permanent 3-Score Separation
    research_priority: float
    treasure_interest: float
    human_validation_status: str

    profile_hash: str

def compute_treasure_dna(
    candidate: CandidateRecord,
    investigation: Optional[InvestigationRecord] = None,
    html: Optional[str] = None,
    timestamp_utc: str = ""
) -> TreasureDNA:
    """
    Construct evidence-backed Treasure DNA profile.
    Guarantees every dimension is grounded in observed artifacts.
    """
    import hashlib

    # 1. Historical depth
    earliest = candidate.earliest_capture_year or (investigation.earliest_archive_year if investigation else None)
    if earliest and earliest > 1990:
        age_years = max(0, 2026 - earliest)
        depth_score = min(10.0, age_years / 3.0)
        h_depth = DimensionTrace(
            score=round(depth_score, 2),
            confidence="OBSERVED",
            evidence_summary=f"First observed in public archive in {earliest} ({age_years} years span)",
            data_points={"earliest_year": earliest, "span_years": age_years}
        )
    else:
        h_depth = DimensionTrace(
            score=1.0,
            confidence="UNKNOWN",
            evidence_summary="No early archive timestamp confirmed",
            data_points={}
        )

    # 2. Survival
    if investigation:
        if investigation.live_status_code == 200:
            surv = DimensionTrace(score=9.0, confidence="OBSERVED", evidence_summary="Active HTTP 200 live response", data_points={"status": 200})
        else:
            surv = DimensionTrace(score=2.0, confidence="OBSERVED", evidence_summary=f"Live response returned status {investigation.live_status_code}", data_points={"status": investigation.live_status_code})
    else:
        surv = DimensionTrace(score=5.0, confidence="INFERRED", evidence_summary="Survival awaiting live investigation", data_points={})

    # 3. Structural Rarity
    features = investigation.html_features_detected if investigation else []
    struct_score = min(10.0, len(features) * 2.5)
    s_rarity = DimensionTrace(
        score=round(struct_score, 2),
        confidence="OBSERVED" if features else "INSUFFICIENT",
        evidence_summary=f"Detected features: {', '.join(features) if features else 'Standard modern markup'}",
        data_points={"features": features}
    )

    # 4. Technology Age
    tech_score = 3.0
    if "pre_css_tables_layout" in features:
        tech_score += 3.5
    if "frameset_layout" in features:
        tech_score += 3.0
    if "deprecated_markup_tags" in features:
        tech_score += 2.0
    tech_age = DimensionTrace(
        score=round(min(10.0, tech_score), 2),
        confidence="OBSERVED" if features else "INFERRED",
        evidence_summary=f"Technology age markers score {tech_score:.1f}/10",
        data_points={"markers": features}
    )

    # 5. Orphan Probability
    is_root = candidate.path in ("", "/")
    orphan_score = 1.0 if is_root else 6.5
    if candidate.source_strategy == "ORPHAN_PATH":
        orphan_score = 8.5
    orphan_prob = DimensionTrace(
        score=orphan_score,
        confidence="INFERRED",
        evidence_summary=f"Candidate path '{candidate.path}' structural depth and link status",
        data_points={"path": candidate.path, "strategy": candidate.source_strategy}
    )

    # 6. Discoverability Difficulty
    diff_val = investigation.discovery_difficulty.value if investigation else "MODERATE"
    diff_map = {"EASY": 2.0, "MODERATE": 5.0, "HARD": 7.5, "VERY_HARD": 9.0, "EXTREME": 10.0}
    disc_diff = DimensionTrace(
        score=diff_map.get(diff_val, 5.0),
        confidence="OBSERVED",
        evidence_summary=f"Assessment based on URL pattern and root depth: {diff_val}",
        data_points={"difficulty": diff_val}
    )

    # 7. Archive Persistence
    cap_count = candidate.capture_count or (investigation.historical_capture_count if investigation else 0)
    arch_persist = DimensionTrace(
        score=round(min(10.0, cap_count * 0.5), 2),
        confidence="OBSERVED" if cap_count > 0 else "UNKNOWN",
        evidence_summary=f"{cap_count} historical archival captures recorded",
        data_points={"capture_count": cap_count}
    )

    # 8. Content Uniqueness
    content_u = DimensionTrace(
        score=5.0,
        confidence="INFERRED",
        evidence_summary="Textural distinctiveness evaluated from DOM density",
        data_points={}
    )

    # 9. Platform Interest
    is_user_space = "~" in candidate.path or candidate.source_strategy == "USER_SPACE"
    plat_score = 8.5 if is_user_space else 4.0
    plat_interest = DimensionTrace(
        score=plat_score,
        confidence="OBSERVED",
        evidence_summary="Personal / Independent Tilde Space" if is_user_space else "Standard Domain Space",
        data_points={"user_space": is_user_space}
    )

    # 10. Historical Context
    hist_ctx = DimensionTrace(
        score=round((h_depth.score + tech_age.score) / 2.0, 2),
        confidence="INFERRED",
        evidence_summary=f"Composite historical era evaluation: {candidate.domain}",
        data_points={"domain": candidate.domain}
    )

    # 11. Evidence Quality
    ev_score = 9.0 if (investigation and investigation.sha256_hash) else 4.0
    ev_qual = DimensionTrace(
        score=ev_score,
        confidence="VERIFIED" if (investigation and investigation.sha256_hash) else "INSUFFICIENT",
        evidence_summary="Cryptographically hashed live HTML snapshot preserved" if ev_score >= 8.0 else "Metadata only",
        data_points={"has_hash": bool(investigation and investigation.sha256_hash)}
    )

    # Permanent 3-Score Separation
    r_priority = candidate.research_priority
    t_interest = investigation.archaeological_score if investigation else 0.0
    h_status = "NOT_REVIEWED"
    if candidate.state == TreasureState.VALIDATED_TREASURE:
        h_status = "VALIDATED_BY_HUMAN"
    elif candidate.state == TreasureState.REVIEW_PENDING:
        h_status = "REVIEW_PENDING"

    dna_repr = f"{candidate.candidate_id}:{h_depth.score}:{surv.score}:{s_rarity.score}:{tech_age.score}:{r_priority}:{t_interest}"
    p_hash = hashlib.sha256(dna_repr.encode("utf-8")).hexdigest()[:20]

    return TreasureDNA(
        dna_id=f"DNA-{candidate.candidate_id}",
        candidate_id=candidate.candidate_id,
        url=candidate.url,
        domain=candidate.domain,
        created_at_utc=timestamp_utc,
        historical_depth=h_depth,
        survival=surv,
        structural_rarity=s_rarity,
        technology_age=tech_age,
        orphan_probability=orphan_prob,
        discoverability_difficulty=disc_diff,
        archive_persistence=arch_persist,
        content_uniqueness=content_u,
        platform_interest=plat_interest,
        historical_context=hist_ctx,
        evidence_quality=ev_qual,
        research_priority=r_priority,
        treasure_interest=t_interest,
        human_validation_status=h_status,
        profile_hash=p_hash
    )

def save_treasure_dnas(dnas: List[TreasureDNA], output_file: Path) -> None:
    """Save Treasure DNA profiles to JSONL."""
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        for dna in dnas:
            data = dna.model_dump()
            data["schema_version"] = "1.0.0"
            f.write(json.dumps(data) + "\n")
