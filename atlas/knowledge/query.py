"""
Archaeological Query Engine for Project Atlas — Knowledge Graph Subsystem.
Supports domain, platform, structural similarity, and multi-strategy discovery queries.
"""

from typing import List, Dict, Any, Optional, Tuple
from atlas.knowledge.graph import KnowledgeGraph
from atlas.knowledge.entities import EntityRecord, EntityType
from atlas.knowledge.relations import RelationType, GraphEdge

class GraphQueryEngine:
    """High-level archaeological queries over the knowledge graph."""

    def __init__(self, graph: KnowledgeGraph):
        self.graph = graph

    def find_entities_by_type(self, entity_type: EntityType) -> List[EntityRecord]:
        return [e for e in self.graph.entities.values() if e.entity_type == entity_type]

    def find_treasures_by_platform(self, platform_name: str) -> List[EntityRecord]:
        """Find treasures or candidates connected to a specific platform."""
        matches = []
        for ent in self.graph.entities.values():
            if ent.entity_type in (EntityType.TREASURE, EntityType.CANDIDATE):
                edges = self.graph.get_outgoing_edges(ent.entity_id, RelationType.SAME_PLATFORM)
                for edge in edges:
                    target = self.graph.get_entity(edge.target_entity_id)
                    if target and platform_name.lower() in target.name.lower():
                        matches.append(ent)
                        break
        return matches

    def find_structurally_similar(self, entity_id: str) -> List[Tuple[EntityRecord, GraphEdge]]:
        """Find all nodes structurally similar to entity_id."""
        results = []
        out_edges = self.graph.get_outgoing_edges(entity_id, RelationType.STRUCTURALLY_SIMILAR)
        for e in out_edges:
            target = self.graph.get_entity(e.target_entity_id)
            if target:
                results.append((target, e))
        return results

    def find_orphaned_paths(self, domain_name: Optional[str] = None) -> List[EntityRecord]:
        """Find path entities categorized as orphaned or not linked from root."""
        orphans = []
        for ent in self.graph.entities.values():
            if ent.entity_type == EntityType.PATH:
                if ent.attributes.get("orphan_candidate", False):
                    if not domain_name or ent.attributes.get("domain") == domain_name:
                        orphans.append(ent)
        return orphans

    def find_multi_strategy_candidates(self) -> List[EntityRecord]:
        """Find candidates discovered by more than one independent strategy."""
        candidates = []
        for ent in self.graph.entities.values():
            if ent.entity_type == EntityType.CANDIDATE:
                strategies = ent.attributes.get("seen_by_strategies", [])
                if len(strategies) > 1:
                    candidates.append(ent)
        return candidates
