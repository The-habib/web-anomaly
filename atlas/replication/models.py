"""
Data Models for Project Atlas Phase 1.9 & Phase 1.9.1.
Enforces strict Discovery State Machine, Blind Review Packets, Human Review Submissions,
and Discovery Lineage Provenance.
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class Phase19ArmType(str, Enum):
    TREATMENT = "TREATMENT"  # Density-informed path prioritization
    CONTROL = "CONTROL"      # Neutral pseudo-random path ordering

class SlotStatus(str, Enum):
    PLANNED = "PLANNED"
    SUCCESS = "SUCCESS"
    HTTP_ERROR = "HTTP_ERROR"
    TIMEOUT = "TIMEOUT"
    EMPTY_POOL_EXHAUSTED = "EMPTY_POOL_EXHAUSTED"

class DiscoveryStatus(str, Enum):
    CLEAR_ANOMALY = "CLEAR_ANOMALY"
    POTENTIAL_ANOMALY = "POTENTIAL_ANOMALY"
    ORDINARY = "ORDINARY"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"

class PriorArtStatus(str, Enum):
    OBSCURE = "OBSCURE"
    DOCUMENTED = "DOCUMENTED"
    PRIOR_ART_UNCERTAIN = "PRIOR_ART_UNCERTAIN"

class ReplicationVerdict(str, Enum):
    REPLICATED = "REPLICATED"
    PROMISING_BUT_UNCONFIRMED = "PROMISING_BUT_UNCONFIRMED"
    NOT_REPLICATED = "NOT_REPLICATED"
    INCONCLUSIVE = "INCONCLUSIVE"
    DESIGN_FAILURE = "DESIGN_FAILURE"

class DiscoveryState(str, Enum):
    """
    Formal 8-Stage Discovery State Machine.
    Transitions must proceed sequentially:
    OBSERVED -> RETRIEVED -> SCORED -> CANDIDATE -> REVIEW_PENDING -> HUMAN_REVIEWED -> (VALIDATED | REJECTED | INSUFFICIENT)
    """
    OBSERVED = "OBSERVED"
    RETRIEVED = "RETRIEVED"
    SCORED = "SCORED"
    CANDIDATE = "CANDIDATE"
    REVIEW_PENDING = "REVIEW_PENDING"
    HUMAN_REVIEWED = "HUMAN_REVIEWED"
    VALIDATED = "VALIDATED"
    REJECTED = "REJECTED"
    INSUFFICIENT = "INSUFFICIENT"

class PopulationDomainRecord(BaseModel):
    domain: str
    category: str
    d_raw: int
    corpus_version: str = "v2"
    is_holdout: bool = False

class BlockRecord(BaseModel):
    block_id: str
    category: str
    domain_treatment: str
    domain_control: str
    d_raw_treatment: int
    d_raw_control: int
    delta_d_raw: int

class AssignmentRecord(BaseModel):
    domain: str
    category: str
    block_id: str
    arm: Phase19ArmType
    blinded_arm_label: str
    d_raw: int
    allocated_slots: int = 10

class RetrievalSlotRecord(BaseModel):
    domain: str
    slot_number: int
    arm: Phase19ArmType
    blinded_arm_label: str
    candidate_url: str
    path: str
    path_priority: float = 0.0
    path_order_rank: int
    status: SlotStatus = SlotStatus.PLANNED
    http_status: Optional[int] = None
    html_sha256: Optional[str] = None
    artifact_path: Optional[str] = None
    raw_anomaly_score: Optional[float] = None
    triggered_rules: List[str] = Field(default_factory=list)

class CandidatePoolRecord(BaseModel):
    domain: str
    category: str
    arm: Phase19ArmType
    total_candidates_found: int
    ordered_candidate_paths: List[str]
    has_full_exposure: bool

class Phase19ResultRecord(BaseModel):
    domain: str
    category: str
    block_id: str
    arm: Phase19ArmType
    blinded_arm_label: str
    d_raw: int
    root_score: float
    root_classification: str
    root_rules: List[str]
    max_deep_score: float
    best_deep_path: str
    best_deep_classification: str
    best_deep_rules: List[str]
    slots_allocated: int = 10
    slots_attempted: int = 0
    slots_successful: int = 0
    candidates_available: int = 0
    is_full_exposure: bool = False
    is_candidate_discovery: bool = False
    is_validated_discovery: bool = False
    discovery_url: Optional[str] = None

# Decontaminated Blind Review Packet (strictly hides score, arm, density rank, expected answers)
class ReviewPacket(BaseModel):
    packet_id: str
    candidate_id: str
    domain: str
    evaluated_path: str
    full_url: str
    page_title: str = ""
    text_snippet: str = ""
    detected_structural_features: List[str] = Field(default_factory=list)
    timeline_summary: str = ""
    evidence_sha256: str
    evidence_artifact_path: str
    generated_at_utc: str
    protocol_version: str = "1.9.1"
    blinding_level: str = "PARTIALLY_BLIND_SCORE_AND_ARM_STRIPPED"

# Human Review Submission from real reviewer import
class HumanReviewSubmission(BaseModel):
    submission_id: str
    packet_id: str
    candidate_id: str
    reviewer_id: str
    review_timestamp_utc: str
    verdict: DiscoveryStatus
    evidence_quality: str = "HIGH"
    historical_significance: str = "AUTHENTIC_UNMODERNIZED_RELIC"
    confidence: str = "HIGH"
    reviewer_notes: str
    is_genuine_human: bool = True

class AdjudicationRecord(BaseModel):
    adjudication_id: str
    candidate_id: str
    review_submission_ids: List[str]
    consensus_reached: bool
    final_verdict: DiscoveryStatus
    adjudication_notes: str
    adjudicated_at_utc: str

class DiscoveryLineageRecord(BaseModel):
    candidate_id: str
    domain: str
    path: str
    full_url: str
    arm: Phase19ArmType
    raw_anomaly_score: float
    evidence_sha256: str
    state: DiscoveryState
    human_verdict: Optional[DiscoveryStatus] = None
    validation_status: str = "HUMAN_REVIEW_PENDING"
    lineage_notes: str

# Legacy models maintained for historical schema compatibility
class ReviewRecord(BaseModel):
    dossier_id: str
    domain: str
    evaluated_path: str
    blinded_label: str
    raw_anomaly_score: float
    verdict: DiscoveryStatus
    review_notes: str
    is_validated_anomaly: bool

class DiscoveryRecord(BaseModel):
    discovery_id: str
    domain: str
    category: str
    arm: Phase19ArmType
    block_id: str
    path: str
    full_url: str
    anomaly_score: float
    historical_era: str
    primary_signal: str
    prior_art: PriorArtStatus
    evidence_sha256: str
    raw_artifact_path: str
    human_verdict: DiscoveryStatus
