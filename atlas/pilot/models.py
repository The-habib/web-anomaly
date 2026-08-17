"""Models for Phase 1.2 Pilot Experiment."""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime, timezone

class PilotDomainRecord(BaseModel):
    pilot_id: str
    domain: str
    category: str
    canonical_url: str
    source_type: str
    source_name: str
    source_reference: str

class PilotEvidenceCapture(BaseModel):
    pilot_id: str
    domain: str
    category: str
    scanned_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    live_status_code: int = 200
    page_title: str = ""
    extracted_text_bytes: int = 0
    html_bytes: int = 0
    frameworks_detected: List[str] = Field(default_factory=list)
    has_tables_layout: bool = False
    has_inline_styles: bool = False
    has_frameset: bool = False
    has_retro_elements: bool = False
    cdx_capture_count: int = 0
    earliest_archive_year: Optional[int] = None
    latest_archive_year: Optional[int] = None
    historical_similarity_score: float = 0.0
    evidence_sha256: str = ""
    raw_evidence_summary: str = ""

class PilotScoringRecord(BaseModel):
    pilot_id: str
    domain: str
    category: str
    raw_anomaly_score: float
    confidence: float
    classification: str  # ORDINARY, CANDIDATE_ANOMALY, HIGH_ANOMALY
    triggered_rules: List[str]
    rule_score_breakdown: Dict[str, float]
    evidence_hash: str
    scored_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class BlindReviewDossier(BaseModel):
    review_id: str
    pilot_id: str
    domain: str
    category: str
    # Strictly hide anomaly score, ranking, and triggered score rules from initial view
    page_title: str
    text_length_chars: int
    earliest_archive_year: Optional[int]
    latest_archive_year: Optional[int]
    cdx_capture_count: int
    detected_structural_features: List[str]
    timeline_summary: str
    raw_evidence_preview: str

class HumanReviewRecord(BaseModel):
    review_id: str
    pilot_id: str
    domain: str
    reviewer: str = "Independent Lead Researcher"
    review_timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    blind_verdict: str  # REAL_ANOMALY, ORDINARY_FOSSIL, ORDINARY_MODERN, ARCHIVE_ARTIFACT, INCONCLUSIVE
    reviewer_notes: str
    confidence: str  # HIGH, MEDIUM, LOW
    score_revealed_verdict: Optional[str] = None
    system_score_was_accurate: Optional[bool] = None

class PilotBatchManifest(BaseModel):
    batch_index: int
    batch_name: str
    start_idx: int
    end_idx: int
    domain_count: int
    completed_at: str
    batch_evidence_sha256: str
    domains: List[str]

class PilotManifest(BaseModel):
    experiment_id: str = "phase1_2_pilot_200"
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    total_pilot_domains: int = 200
    batch_count: int = 4
    batch_size: int = 50
    category_distribution: Dict[str, int]
    csv_sha256: str
    provenance_sha256: str
    evidence_sha256: str
    scoring_sha256: str
