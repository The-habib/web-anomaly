"""
Storage Subsystem for Project Atlas — Knowledge Graph.
Handles JSONL persistence, atomic writes, and loading for graph entities and relationships.
"""

import json
from pathlib import Path
from typing import Tuple, List, Optional
from atlas.knowledge.entities import EntityRecord
from atlas.knowledge.relations import GraphEdge
from atlas.knowledge.graph import KnowledgeGraph

SCHEMA_VERSION = "1.0.0"

def save_knowledge_graph(
    graph: KnowledgeGraph,
    output_dir: Path,
    entities_filename: str = "entities.jsonl",
    relations_filename: str = "relationships.jsonl"
) -> Tuple[Path, Path]:
    """Persist graph entities and edges to JSONL files."""
    output_dir.mkdir(parents=True, exist_ok=True)
    ent_path = output_dir / entities_filename
    rel_path = output_dir / relations_filename

    with open(ent_path, "w", encoding="utf-8") as f:
        for ent in graph.entities.values():
            data = ent.model_dump()
            data["schema_version"] = SCHEMA_VERSION
            f.write(json.dumps(data) + "\n")

    with open(rel_path, "w", encoding="utf-8") as f:
        for edge in graph.edges.values():
            data = edge.model_dump()
            data["schema_version"] = SCHEMA_VERSION
            f.write(json.dumps(data) + "\n")

    return ent_path, rel_path

def load_knowledge_graph(
    entities_path: Path,
    relations_path: Path
) -> KnowledgeGraph:
    """Load a KnowledgeGraph instance from entities and relationships JSONL files."""
    graph = KnowledgeGraph()

    if entities_path.exists():
        with open(entities_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                data = json.loads(line)
                data.pop("schema_version", None)
                entity = EntityRecord(**data)
                graph.add_entity(entity)

    if relations_path.exists():
        with open(relations_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                data = json.loads(line)
                data.pop("schema_version", None)
                edge = GraphEdge(**data)
                # Only add if endpoints exist
                if edge.source_entity_id in graph.entities and edge.target_entity_id in graph.entities:
                    graph.add_edge(edge)

    return graph
