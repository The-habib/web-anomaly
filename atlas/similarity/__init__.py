"""
Project Atlas — Archaeological Similarity Subsystem.
"""

from atlas.similarity.engine import (
    SimilarityReason,
    ArtifactComparison,
    compute_artifact_similarity
)
from atlas.similarity.clustering import (
    ArchaeologicalCluster,
    cluster_archaeological_candidates
)
from atlas.similarity.family_tree import (
    FamilyTreeNode,
    PlatformFamilyTree,
    build_platform_family_tree
)
