"""
Core Graph Engine for Project Atlas — Knowledge Graph Subsystem.
Provides in-memory node and edge indexing, neighbor traversals, multi-hop pathfinding,
subgraph extraction, and relationship filtering.
"""

from typing import Dict, List, Set, Optional, Tuple, Any
from atlas.knowledge.entities import EntityRecord, EntityType
from atlas.knowledge.relations import GraphEdge, RelationType, RelationConfidence

class KnowledgeGraph:
    """Archaeological Knowledge Graph for Project Atlas."""

    def __init__(self):
        self.entities: Dict[str, EntityRecord] = {}
        self.edges: Dict[str, GraphEdge] = {}
        # Adjacency indexes: source -> {relation: [edge_ids]}
        self.out_edges: Dict[str, List[str]] = {}
        # Inward indexes: target -> {relation: [edge_ids]}
        self.in_edges: Dict[str, List[str]] = {}

    def add_entity(self, entity: EntityRecord) -> None:
        """Add or update an entity node in the graph."""
        self.entities[entity.entity_id] = entity
        if entity.entity_id not in self.out_edges:
            self.out_edges[entity.entity_id] = []
        if entity.entity_id not in self.in_edges:
            self.in_edges[entity.entity_id] = []

    def add_edge(self, edge: GraphEdge) -> None:
        """Add an edge to the graph after validating endpoint existence."""
        if edge.source_entity_id not in self.entities:
            raise KeyError(f"Source entity '{edge.source_entity_id}' does not exist in graph.")
        if edge.target_entity_id not in self.entities:
            raise KeyError(f"Target entity '{edge.target_entity_id}' does not exist in graph.")

        self.edges[edge.edge_id] = edge
        if edge.edge_id not in self.out_edges[edge.source_entity_id]:
            self.out_edges[edge.source_entity_id].append(edge.edge_id)
        if edge.edge_id not in self.in_edges[edge.target_entity_id]:
            self.in_edges[edge.target_entity_id].append(edge.edge_id)

    def get_entity(self, entity_id: str) -> Optional[EntityRecord]:
        return self.entities.get(entity_id)

    def get_edge(self, edge_id: str) -> Optional[GraphEdge]:
        return self.edges.get(edge_id)

    def get_outgoing_edges(self, entity_id: str, relation_type: Optional[RelationType] = None) -> List[GraphEdge]:
        edge_ids = self.out_edges.get(entity_id, [])
        results = [self.edges[eid] for eid in edge_ids if eid in self.edges]
        if relation_type:
            results = [e for e in results if e.relation_type == relation_type]
        return results

    def get_incoming_edges(self, entity_id: str, relation_type: Optional[RelationType] = None) -> List[GraphEdge]:
        edge_ids = self.in_edges.get(entity_id, [])
        results = [self.edges[eid] for eid in edge_ids if eid in self.edges]
        if relation_type:
            results = [e for e in results if e.relation_type == relation_type]
        return results

    def get_neighbors(self, entity_id: str, relation_type: Optional[RelationType] = None) -> List[EntityRecord]:
        """Return all adjacent entities reachable via outgoing edges."""
        edges = self.get_outgoing_edges(entity_id, relation_type)
        return [self.entities[e.target_entity_id] for e in edges if e.target_entity_id in self.entities]

    def find_subgraph(self, root_entity_id: str, max_depth: int = 2) -> Tuple[List[EntityRecord], List[GraphEdge]]:
        """Extract an ego-subgraph centered around root_entity_id up to max_depth."""
        visited_nodes: Set[str] = set()
        collected_edges: Set[str] = set()
        queue: List[Tuple[str, int]] = [(root_entity_id, 0)]

        while queue:
            curr_id, depth = queue.pop(0)
            if curr_id in visited_nodes or curr_id not in self.entities:
                continue
            visited_nodes.add(curr_id)

            if depth < max_depth:
                out_e = self.out_edges.get(curr_id, [])
                for eid in out_e:
                    edge = self.edges.get(eid)
                    if edge:
                        collected_edges.add(eid)
                        if edge.target_entity_id not in visited_nodes:
                            queue.append((edge.target_entity_id, depth + 1))
                in_e = self.in_edges.get(curr_id, [])
                for eid in in_e:
                    edge = self.edges.get(eid)
                    if edge:
                        collected_edges.add(eid)
                        if edge.source_entity_id not in visited_nodes:
                            queue.append((edge.source_entity_id, depth + 1))

        nodes = [self.entities[nid] for nid in visited_nodes]
        edges = [self.edges[eid] for eid in collected_edges]
        return nodes, edges
