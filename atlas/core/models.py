"""Domain data models and schemas for Project Atlas (Phase 0.5)."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

class EvidenceState(str, Enum):
    """Scientific classification of evidence backing a finding or signal."""
    OBSERVED = "OBSERVED"          # Direct factual observation from live or archive source
    INFERRED = "INFERRED"          # Statistically derived deduction or hypothesis
    CANDIDATE = "CANDIDATE"        # Potential anomaly requiring corroborating signals
    VALIDATED = "VALIDATED"        # High-confidence anomaly backed by dense, multi-source evidence
    DISPROVEN = "DISPROVEN"        # Anomaly hypothesis refuted by evidence
    INSUFFICIENT = "INSUFFICIENT"  # Sparse or inconclusive evidence; no claim can be made

class ContinuityLevel(str, Enum):
    """Strict classification of temporal archive continuity."""
    HISTORICAL_PRESENCE = "HISTORICAL_PRESENCE"          # Sparse captures (1-2 isolated points over time)
    MULTI_PERIOD_PRESENCE = "MULTI_PERIOD_PRESENCE"      # Multiple eras observed, but with large gaps (> 5 yrs)
    LONG_SPAN_PRESENCE = "LONG_SPAN_PRESENCE"            # >= 15 yr span with moderate coverage (>= 40%)
    HIGH_CAPTURE_CONTINUITY = "HIGH_CAPTURE_CONTINUITY"  # >= 15 yr span with high coverage (>= 65%, gap <= 3.5 yrs)
    CONTINUOUS_PRESENCE = "CONTINUOUS_PRESENCE"          # >= 15 yr span with dense coverage (>= 85%, gap <= 2.0 yrs)

class ArtifactType(str, Enum):
    SCREENSHOT = "screenshot"
    HTML = "html"
    JSON = "json"
    TIMELINE = "timeline"
    METADATA = "metadata"
    WARC = "warc"
    REPORT = "report"

class EvidenceArtifact(BaseModel):
    """Represents a permanent, cryptographically verified piece of digital evidence."""
    artifact_id: str
    artifact_type: ArtifactType
    relative_path: str
    file_name: str
    sha256: str
    size_bytes: int
    created_at: str = Field(default_factory=utc_now_iso)
    source: str = "live"
    collection_method: str = "direct"
    metadata: Dict[str, Any] = Field(default_factory=dict)

class TimelineEvent(BaseModel):
    """An event observed at a specific point in time across web archives or live crawl."""
    timestamp: str  # YYYYMMDDhhmmss format
    datetime_iso: str
    source: str  # 'wayback', 'commoncrawl', 'live'
    status_code: int
    content_length: Optional[int] = None
    mime_type: Optional[str] = None
    digest: Optional[str] = None
    snapshot_url: Optional[str] = None
    notes: Optional[str] = None

class TimelineContinuityMetrics(BaseModel):
    """Rigorous temporal metrics for evaluating web persistence and continuity."""
    first_seen: Optional[str] = None
    last_seen: Optional[str] = None
    earliest_iso: Optional[str] = None
    latest_iso: Optional[str] = None
    years_span: int = 0
    total_captures: int = 0
    unique_years_observed: int = 0
    observed_year_ratio: float = 0.0
    longest_evidence_gap_years: float = 0.0
    average_captures_per_year: float = 0.0
    continuity_level: ContinuityLevel = ContinuityLevel.HISTORICAL_PRESENCE
    continuity_claim: str = "unproven"
    archive_sources: List[str] = Field(default_factory=list)
    has_documented_failures: bool = False
    failure_intervals: List[Dict[str, Any]] = Field(default_factory=list)

class AnomalySignal(BaseModel):
    """A detected anomaly signal with evidence state and confidence backing."""
    signal_id: str
    name: str
    category: str
    weight: int
    score_awarded: int
    evidence_state: EvidenceState = EvidenceState.CANDIDATE
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    description: str
    observed_facts: List[str] = Field(default_factory=list)
    inferences: List[str] = Field(default_factory=list)
    limitations: List[str] = Field(default_factory=list)
    evidence_keys: List[str] = Field(default_factory=list)

class Finding(BaseModel):
    """A verified, evidence-backed scientific discovery/finding dossier."""
    finding_id: str
    target_url: str
    canonical_domain: str
    created_at: str = Field(default_factory=utc_now_iso)
    anomaly_score: int
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    classification: str
    evidence_state: EvidenceState = EvidenceState.CANDIDATE
    signals: List[AnomalySignal] = Field(default_factory=list)
    artifacts: List[EvidenceArtifact] = Field(default_factory=list)
    timeline_summary: Dict[str, Any] = Field(default_factory=dict)
    metadata_summary: Dict[str, Any] = Field(default_factory=dict)
    evidence_state_breakdown: Dict[str, int] = Field(default_factory=dict)
    human_summary: str
    machine_summary: Dict[str, Any] = Field(default_factory=dict)
    reproducible_command: str = ""
    verification_status: str = "unverified"

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

class ArtifactVerificationResult(BaseModel):
    """Result of an integrity check on a single stored artifact."""
    artifact_id: str
    file_name: str
    expected_sha256: str
    calculated_sha256: Optional[str] = None
    size_bytes: int
    status: str  # 'PASS', 'FAIL_MISMATCH', 'MISSING'
    error: Optional[str] = None

class FindingVerificationReport(BaseModel):
    """Comprehensive evidence verification report for a Finding."""
    finding_id: str
    target_url: str
    verified_at: str = Field(default_factory=utc_now_iso)
    total_artifacts: int
    passed_artifacts: int
    failed_artifacts: int
    missing_artifacts: int
    is_valid: bool
    results: List[ArtifactVerificationResult] = Field(default_factory=list)
