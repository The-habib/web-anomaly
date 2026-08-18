"""
Relationship Model for Project Atlas — Knowledge Graph Subsystem.
Defines 18 standardized archaeological relationships, edge schemas, evidence provenance,
and confidence qualifiers (OBSERVED, INFERRED, POSSIBLE).
"""

import uuid
from enum import Enum
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

class RelationType(str, Enum):
    HOSTS = "HOSTS"
    CONTAINS = "CONTAINS"
    REDIRECTS_TO = "REDIRECTS_TO"
    ARCHIVED_AS = "ARCHIVED_AS"
    CAPTURED_BY = "CAPTURED_BY"
    DISCOVERED_BY = "DISCOVERED_BY"
    DISCOVERED_DURING = "DISCOVERED_DURING"
    SIMILAR_TO = "SIMILAR_TO"
    STRUCTURALLY_SIMILAR = "STRUCTURALLY_SIMILAR"
    TECHNOLOGICALLY_SIMILAR = "TECHNOLOGICALLY_SIMILAR"
    SAME_PLATFORM = "SAME_PLATFORM"
    SAME_PATH_PATTERN = "SAME_PATH_PATTERN"
    SAME_ARCHIVE_PATTERN = "SAME_ARCHIVE_PATTERN"
    REVIEWED_AS = "REVIEWED_AS"
    REFERENCES = "REFERENCES"
    MIRRORS = "MIRRORS"
    POSSIBLE_MIRROR_OF = "POSSIBLE_MIRROR_OF"
    POSSIBLE_DESCENDANT_OF = "POSSIBLE_DESCENDANT_OF"

class RelationConfidence(str, Enum):
    OBSERVED = "OBSERVED"
    INFERRED = "INFERRED"
    POSSIBLE = "POSSIBLE"

class GraphEdge(BaseModel):
    edge_id: str
    source_entity_id: str
    target_entity_id: str
    relation_type: RelationType
    evidence_ids: List[str] = Field(default_factory=list)
    created_at_utc: str
    method: str
    confidence: RelationConfidence = RelationConfidence.OBSERVED
    status: str = "ACTIVE"
    attributes: Dict[str, Any] = Field(default_factory=dict)

def generate_edge_id(source_id: str, relation: RelationType, target_id: str) -> str:
    """Generate a deterministic edge ID."""
    key = f"{source_id}:{relation.value}:{target_id}"
    short_hash = uuid.uuid5(uuid.NAMESPACE_URL, key).hex[:10].upper()
    return f"EDGE-{short_hash}"
