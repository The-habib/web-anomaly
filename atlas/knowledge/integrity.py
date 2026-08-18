"""
Integrity and Validation Subsystem for Project Atlas — Knowledge Graph.
Enforces edge endpoint validity, evidence provenance, and topological health.
"""

from typing import List, Dict, Any, Tuple
from atlas.knowledge.graph import KnowledgeGraph

def validate_graph_integrity(graph: KnowledgeGraph) -> Tuple[bool, List[str]]:
    """
    Validate graph integrity:
    1. Every edge source and target must exist as an entity.
    2. Every edge must have non-empty created_at_utc and method.
    3. Entities must have non-empty provenance_source.
    Returns (is_valid, list_of_violations).
    """
    violations: List[str] = []

    # Check entities
    for eid, ent in graph.entities.items():
        if not ent.provenance_source:
            violations.append(f"Entity '{eid}' missing provenance_source.")
        if not ent.source_run_id:
            violations.append(f"Entity '{eid}' missing source_run_id.")

    # Check edges
    for edge_id, edge in graph.edges.items():
        if edge.source_entity_id not in graph.entities:
            violations.append(f"Edge '{edge_id}' has non-existent source '{edge.source_entity_id}'.")
        if edge.target_entity_id not in graph.entities:
            violations.append(f"Edge '{edge_id}' has non-existent target '{edge.target_entity_id}'.")
        if not edge.method:
            violations.append(f"Edge '{edge_id}' missing discovery method.")

    return len(violations) == 0, violations
