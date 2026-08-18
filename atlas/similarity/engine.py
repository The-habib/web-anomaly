"""
Archaeological Similarity Engine for Project Atlas.
Computes multi-vector structural, technological, platform, and pattern similarity between artifacts.
Emits both a normalized similarity score (0.0 to 1.0) and explicit, evidence-backed similarity reasons.
"""

from enum import Enum
from typing import List, Dict, Any, Tuple, Optional
from pydantic import BaseModel, Field

from atlas.fingerprint.engine import UnifiedFingerprint

class SimilarityReason(str, Enum):
    STRUCTURE_MATCH = "STRUCTURE_MATCH"
    PLATFORM_MATCH = "PLATFORM_MATCH"
    PATH_PATTERN_MATCH = "PATH_PATTERN_MATCH"
    ARCHIVE_PATTERN_MATCH = "ARCHIVE_PATTERN_MATCH"
    TECHNOLOGY_STACK_MATCH = "TECHNOLOGY_STACK_MATCH"
    VISUAL_GEOMETRY_MATCH = "VISUAL_GEOMETRY_MATCH"

class ArtifactComparison(BaseModel):
    artifact_a_id: str
    artifact_b_id: str
    similarity_score: float
    reasons: List[SimilarityReason] = Field(default_factory=list)
    detailed_metrics: Dict[str, Any] = Field(default_factory=dict)
    confidence: str = "OBSERVED"

def compute_artifact_similarity(
    fp_a: UnifiedFingerprint,
    fp_b: UnifiedFingerprint,
    path_a: str = "",
    path_b: str = ""
) -> ArtifactComparison:
    """Compare two unified fingerprints and paths, outputting score and explicit reasons."""
    reasons: List[SimilarityReason] = []
    score_components = []

    # 1. Structure Match
    struct_sim = 0.0
    if fp_a.structure.structural_hash == fp_b.structure.structural_hash:
        struct_sim = 1.0
        reasons.append(SimilarityReason.STRUCTURE_MATCH)
    else:
        # Cosine-like ratio on key counts
        diff_tables = abs(fp_a.structure.table_count - fp_b.structure.table_count)
        diff_nodes = abs(fp_a.structure.total_dom_nodes - fp_b.structure.total_dom_nodes)
        max_nodes = max(1, max(fp_a.structure.total_dom_nodes, fp_b.structure.total_dom_nodes))
        struct_sim = max(0.0, 1.0 - (diff_nodes / max_nodes) - (diff_tables * 0.1))
        if struct_sim > 0.75:
            reasons.append(SimilarityReason.STRUCTURE_MATCH)
    score_components.append(struct_sim * 0.35)

    # 2. Technology & Platform Match
    tech_sim = 0.0
    if fp_a.technology.primary_platform == fp_b.technology.primary_platform and fp_a.technology.primary_platform != "UNKNOWN":
        tech_sim += 0.5
        reasons.append(SimilarityReason.PLATFORM_MATCH)
    if fp_a.technology.technology_hash == fp_b.technology.technology_hash:
        tech_sim = 1.0
        reasons.append(SimilarityReason.TECHNOLOGY_STACK_MATCH)
    score_components.append(tech_sim * 0.25)

    # 3. Visual Geometry Match
    vis_sim = 0.0
    if fp_a.visual.dominant_geometry == fp_b.visual.dominant_geometry:
        vis_sim += 0.6
        reasons.append(SimilarityReason.VISUAL_GEOMETRY_MATCH)
    score_components.append(vis_sim * 0.20)

    # 4. Path Pattern Match
    path_sim = 0.0
    if ("~" in path_a and "~" in path_b) or ("/users/" in path_a and "/users/" in path_b):
        path_sim = 0.9
        reasons.append(SimilarityReason.PATH_PATTERN_MATCH)
    elif path_a.split(".")[-1] == path_b.split(".")[-1] and path_a.split(".")[-1] in ("html", "htm", "txt"):
        path_sim = 0.4
    score_components.append(path_sim * 0.20)

    total_score = round(sum(score_components), 4)

    return ArtifactComparison(
        artifact_a_id=fp_a.fingerprint_id,
        artifact_b_id=fp_b.fingerprint_id,
        similarity_score=min(1.0, total_score),
        reasons=reasons,
        detailed_metrics={
            "structural_similarity": round(struct_sim, 3),
            "technology_similarity": round(tech_sim, 3),
            "visual_similarity": round(vis_sim, 3),
            "path_similarity": round(path_sim, 3)
        },
        confidence="OBSERVED" if total_score > 0.7 else "INFERRED"
    )
