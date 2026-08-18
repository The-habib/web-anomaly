"""
Archaeological Family Tree Subsystem for Project Atlas.
Builds platform genealogies and mirror trees using explicit relation confidence qualifiers.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class FamilyTreeNode(BaseModel):
    node_id: str
    entity_name: str
    relation_to_parent: Optional[str] = None  # OBSERVED_RELATION, INFERRED_RELATION, POSSIBLE_RELATION
    evidence_notes: str
    children: List['FamilyTreeNode'] = Field(default_factory=list)

class PlatformFamilyTree(BaseModel):
    tree_id: str
    platform_name: str
    root_node: FamilyTreeNode
    total_nodes: int
    created_at_utc: str

def build_platform_family_tree(
    platform_name: str,
    root_domain: str,
    child_artifacts: List[Dict[str, Any]],
    timestamp_utc: str
) -> PlatformFamilyTree:
    """Build a hierarchical genealogical family tree for a platform community."""
    children_nodes = []
    for art in child_artifacts:
        children_nodes.append(FamilyTreeNode(
            node_id=art.get("candidate_id", art.get("url", "UNKNOWN")),
            entity_name=art.get("url", "UNKNOWN"),
            relation_to_parent="OBSERVED_RELATION" if "~" in art.get("path", "") else "INFERRED_RELATION",
            evidence_notes=f"Member of platform community {platform_name} on {art.get('domain')}",
            children=[]
        ))

    root = FamilyTreeNode(
        node_id=f"PLAT-{platform_name.upper()}",
        entity_name=f"{platform_name} Root ({root_domain})",
        relation_to_parent=None,
        evidence_notes=f"Foundational platform host for {len(child_artifacts)} observed artifacts",
        children=children_nodes
    )

    return PlatformFamilyTree(
        tree_id=f"TREE-{platform_name.upper()}",
        platform_name=platform_name,
        root_node=root,
        total_nodes=1 + len(children_nodes),
        created_at_utc=timestamp_utc
    )
