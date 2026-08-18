"""
Graph Export Subsystem for Project Atlas — Knowledge Graph.
Exports knowledge graph topologies to Cytoscape JSON, GraphML, and Mermaid diagrams.
"""

import json
from typing import Dict, Any, List
from atlas.knowledge.graph import KnowledgeGraph

def export_to_cytoscape_json(graph: KnowledgeGraph) -> Dict[str, Any]:
    """Export graph into Cytoscape.js compatible JSON structure."""
    elements = []

    # Nodes
    for ent in graph.entities.values():
        elements.append({
            "data": {
                "id": ent.entity_id,
                "label": ent.name,
                "type": ent.entity_type.value,
                "status": ent.status,
                **ent.attributes
            }
        })

    # Edges
    for edge in graph.edges.values():
        elements.append({
            "data": {
                "id": edge.edge_id,
                "source": edge.source_entity_id,
                "target": edge.target_entity_id,
                "label": edge.relation_type.value,
                "confidence": edge.confidence.value,
                "method": edge.method
            }
        })

    return {"elements": elements}

def export_to_mermaid_markdown(graph: KnowledgeGraph, max_nodes: int = 50) -> str:
    """Generate Mermaid flowchart markdown for visualization."""
    lines = ["```mermaid", "graph TD"]
    count = 0

    for ent in list(graph.entities.values())[:max_nodes]:
        safe_name = ent.name.replace('"', "'")
        lines.append(f'    {ent.entity_id}["{ent.entity_type.value}: {safe_name}"]')

    for edge in list(graph.edges.values())[:max_nodes * 2]:
        if edge.source_entity_id in graph.entities and edge.target_entity_id in graph.entities:
            lines.append(f'    {edge.source_entity_id} -->|{edge.relation_type.value}| {edge.target_entity_id}')

    lines.append("```")
    return "\n".join(lines)
