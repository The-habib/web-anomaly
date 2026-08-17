"""Domain data models and schemas for Project Atlas."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

class ArtifactType(str, Enum):
    SCREENSHOT = "screenshot"
    HTML = "html"
    JSON = "json"
    TIMELINE = "timeline"
    METADATA = "metadata"
    WARC = "warc"
    REPORT = "report"

class EvidenceArtifact(BaseModel):
    """Represents a permanent stored piece of digital evidence."""
    artifact_id: str
    artifact_type: ArtifactType
    relative_path: str
    file_name: str
    sha256: str
    size_bytes: int
    created_at: str = Field(default_factory=utc_now_iso)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class TimelineEvent(BaseModel):
    """An event observed at a specific point in time across web archives or live crawl."""
    timestamp: str  # YYYYMMDDhhmmss or ISO format
    datetime_iso: str
    source: str  # 'wayback', 'commoncrawl', 'live'
    status_code: int
    content_length: Optional[int] = None
    mime_type: Optional[str] = None
    digest: Optional[str] = None
    snapshot_url: Optional[str] = None
    notes: Optional[str] = None

class AnomalySignal(BaseModel):
    """A detected anomaly signal with weight and evidence backing."""
    signal_id: str
    name: str
    category: str
    weight: int
    score_awarded: int
    description: str
    evidence_keys: List[str] = Field(default_factory=list)
    confidence: float = 1.0

class Finding(BaseModel):
    """A verified, evidence-backed scientific discovery/finding."""
    finding_id: str
    target_url: str
    canonical_domain: str
    created_at: str = Field(default_factory=utc_now_iso)
    anomaly_score: int
    classification: str
    signals: List[AnomalySignal] = Field(default_factory=list)
    artifacts: List[EvidenceArtifact] = Field(default_factory=list)
    timeline_summary: Dict[str, Any] = Field(default_factory=dict)
    metadata_summary: Dict[str, Any] = Field(default_factory=dict)
    human_summary: str
    machine_summary: Dict[str, Any] = Field(default_factory=dict)
    reproducible_command: str = ""

class ExperimentStatus(str, Enum):
    PROPOSED = "proposed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class Experiment(BaseModel):
    """A numbered scientific experiment ledger entry."""
    experiment_id: str  # e.g., '0001'
    title: str
    hypothesis: str
    status: ExperimentStatus = ExperimentStatus.PROPOSED
    created_at: str = Field(default_factory=utc_now_iso)
    completed_at: Optional[str] = None
    target_urls: List[str] = Field(default_factory=list)
    findings: List[str] = Field(default_factory=list)
    notes: List[str] = Field(default_factory=list)
