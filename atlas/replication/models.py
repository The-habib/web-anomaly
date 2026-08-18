"""
Data Models for Project Atlas Phase 1.9 Controlled Replication Experiment.
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

class Phase19ArmType(str, Enum):
    TREATMENT = "TREATMENT"
    CONTROL = "CONTROL"

class PathOrderStrategy(str, Enum):
    DENSITY_PRIORITIZED = "DENSITY_PRIORITIZED"
    NEUTRAL_RANDOM = "NEUTRAL_RANDOM"

class SlotStatus(str, Enum):
    SUCCESS = "SUCCESS"
    HTTP_ERROR = "HTTP_ERROR"
    TIMEOUT = "TIMEOUT"
    REDIRECT = "REDIRECT"
    EMPTY_RESPONSE = "EMPTY_RESPONSE"
    NON_HTML = "NON_HTML"
    EMPTY_POOL_EXHAUSTED = "EMPTY_POOL_EXHAUSTED"

class AnalysisPopulation(str, Enum):
    INTENT_TO_TREAT = "INTENT_TO_TREAT"
    FULL_EXPOSURE = "FULL_EXPOSURE"
    PER_PROTOCOL = "PER_PROTOCOL"

class DiscoveryStatus(str, Enum):
    CLEAR_ANOMALY = "CLEAR_ANOMALY"
    POTENTIAL_ANOMALY = "POTENTIAL_ANOMALY"
    ORDINARY = "ORDINARY"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"

class PriorArtStatus(str, Enum):
    DOCUMENTED = "DOCUMENTED"
    OBSCURE = "OBSCURE"
    PRIOR_ART_UNCERTAIN = "PRIOR_ART_UNCERTAIN"

class ReplicationVerdict(str, Enum):
    REPLICATED = "REPLICATED"
    PROMISING_BUT_UNCONFIRMED = "PROMISING_BUT_UNCONFIRMED"
    NOT_REPLICATED = "NOT_REPLICATED"
    INCONCLUSIVE = "INCONCLUSIVE"
    DESIGN_FAILURE = "DESIGN_FAILURE"

class Phase19DomainRecord(BaseModel):
    domain: str
    category: str
    canonical_url: str
    d_raw: int
    d_year: float
    d_capture: float
    d_span: int
    d_user: int
    d_legacy: int
    d_diversity: float
    d_content: float
    earliest_observed_year: int
    latest_observed_year: int
    total_captures: int
    density_tier: Optional[str] = "UNSPECIFIED"

class BlockPairRecord(BaseModel):
    block_id: str
    category: str
    treatment_domain: str
    control_domain: str
    treatment_d_raw: int
    control_d_raw: int
    d_raw_delta: int
    random_seed: int

class AssignmentRecord(BaseModel):
    domain: str
    category: str
    block_id: str
    arm: Phase19ArmType
    blinded_arm_label: str
    path_strategy: PathOrderStrategy
    fixed_slot_budget: int = 10
    d_raw: int
    density_tier: Optional[str] = "UNSPECIFIED"

class CandidatePoolRecord(BaseModel):
    domain: str
    category: str
    arm: Phase19ArmType
    total_candidates_found: int
    candidate_paths: List[str]
    has_full_exposure: bool  # len(candidate_paths) >= 10

class RetrievalSlotRecord(BaseModel):
    domain: str
    slot_number: int  # 1 to 10
    arm: Phase19ArmType
    blinded_arm_label: str
    candidate_url: str
    path: str
    path_priority: float
    path_order_rank: int
    status: SlotStatus
    http_status: Optional[int] = None
    html_sha256: Optional[str] = None
    artifact_path: Optional[str] = None
    raw_anomaly_score: float = 0.0
    triggered_rules: List[str] = Field(default_factory=list)

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
    slots_attempted: int
    slots_successful: int
    candidates_available: int
    is_full_exposure: bool
    is_candidate_discovery: bool  # max_deep_score >= 40 and root < 40
    is_validated_discovery: bool  # verified by human review
    discovery_url: Optional[str] = None

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
