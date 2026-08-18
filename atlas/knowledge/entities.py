"""
Entity Model for Project Atlas — Knowledge Graph Subsystem.
Defines 16 standardized archaeological entity types with stable, URL-independent identities,
creation provenance, timestamps, and metadata schemas.
"""

import uuid
from enum import Enum
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

class EntityType(str, Enum):
    DOMAIN = "DOMAIN"
    HOST = "HOST"
    PATH = "PATH"
    PAGE = "PAGE"
    CAPTURE = "CAPTURE"
    ARTIFACT = "ARTIFACT"
    CANDIDATE = "CANDIDATE"
    TREASURE = "TREASURE"
    REVIEW = "REVIEW"
    STRATEGY = "STRATEGY"
    TECHNOLOGY = "TECHNOLOGY"
    PLATFORM = "PLATFORM"
    ARCHIVE_SOURCE = "ARCHIVE_SOURCE"
    RUN = "RUN"
    DISCOVERY_EVENT = "DISCOVERY_EVENT"
    REPORT = "REPORT"

class EntityRecord(BaseModel):
    entity_id: str
    entity_type: EntityType
    name: str
    canonical_uri: Optional[str] = None
    created_at_utc: str
    source_run_id: str
    provenance_source: str
    status: str = "ACTIVE"
    attributes: Dict[str, Any] = Field(default_factory=dict)
    evidence_ids: List[str] = Field(default_factory=list)

def generate_entity_id(entity_type: EntityType, unique_key: str) -> str:
    """
    Generate a deterministic, stable entity ID based on type and unique key.
    Example: ENT-DOMAIN-1a2b3c4d, TREASURE-000001, TCAND-000001
    """
    prefix_map = {
        EntityType.DOMAIN: "ENT-DOM",
        EntityType.HOST: "ENT-HST",
        EntityType.PATH: "ENT-PTH",
        EntityType.PAGE: "ENT-PAG",
        EntityType.CAPTURE: "ENT-CAP",
        EntityType.ARTIFACT: "ENT-ART",
        EntityType.CANDIDATE: "TCAND",
        EntityType.TREASURE: "TREASURE",
        EntityType.REVIEW: "ENT-REV",
        EntityType.STRATEGY: "ENT-STR",
        EntityType.TECHNOLOGY: "ENT-TEC",
        EntityType.PLATFORM: "ENT-PLT",
        EntityType.ARCHIVE_SOURCE: "ENT-SRC",
        EntityType.RUN: "ENT-RUN",
        EntityType.DISCOVERY_EVENT: "ENT-EVT",
        EntityType.REPORT: "ENT-RPT"
    }
    prefix = prefix_map.get(entity_type, "ENT-UNK")
    if entity_type in (EntityType.TREASURE, EntityType.CANDIDATE):
        # Format as numeric padded ID if int convertible, else hash
        if unique_key.isdigit():
            return f"{prefix}-{int(unique_key):06d}"
    
    clean_key = unique_key.strip().lower()
    short_hash = uuid.uuid5(uuid.NAMESPACE_URL, f"{prefix}:{clean_key}").hex[:8].upper()
    return f"{prefix}-{short_hash}"
