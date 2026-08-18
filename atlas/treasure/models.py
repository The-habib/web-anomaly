"""
Data Models for Project Atlas — Treasure Intelligence Platform & Operating System.
Defines schemas for the 15-state treasure lifecycle, stable identities, multi-strategy
candidate discovery, adaptive investigations, review packets, human reviews, lineages,
Treasure DNA, fingerprints, and museum exhibits.
"""

from enum import Enum
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field

class TreasureStrategy(str, Enum):
    HISTORICAL_SURVIVOR = "HISTORICAL_SURVIVOR"
    ORPHAN_PATH = "ORPHAN_PATH"
    USER_SPACE = "USER_SPACE"
    TECHNOLOGY_FOSSIL = "TECHNOLOGY_FOSSIL"
    RESURRECTION = "RESURRECTION"
    STRUCTURAL_SURVIVOR = "STRUCTURAL_SURVIVOR"
    ARCHIVE_ONLY = "ARCHIVE_ONLY"
    WEB_ODDITY = "WEB_ODDITY"

class DiscoveryDifficulty(str, Enum):
    EASY = "EASY"
    MODERATE = "MODERATE"
    HARD = "HARD"
    VERY_HARD = "VERY_HARD"
    EXTREME = "EXTREME"

class SurvivalState(str, Enum):
    STILL_ACTIVE = "STILL_ACTIVE"
    ARCHIVED_ONLY = "ARCHIVED_ONLY"
    PARTIALLY_SURVIVING = "PARTIALLY_SURVIVING"
    RESURRECTED = "RESURRECTED"
    UNKNOWN = "UNKNOWN"

class PriorArtStatus(str, Enum):
    WELL_DOCUMENTED = "WELL_DOCUMENTED"
    DOCUMENTED = "DOCUMENTED"
    OBSCURE = "OBSCURE"
    POORLY_DOCUMENTED = "POORLY_DOCUMENTED"
    PRIOR_ART_UNCERTAIN = "PRIOR_ART_UNCERTAIN"

class TreasureState(str, Enum):
    DISCOVERED = "DISCOVERED"
    CANDIDATE = "CANDIDATE"
    EVIDENCE_PENDING = "EVIDENCE_PENDING"
    EVIDENCE_COMPLETE = "EVIDENCE_COMPLETE"
    ANALYSIS_PENDING = "ANALYSIS_PENDING"
    REVIEW_PENDING = "REVIEW_PENDING"
    HUMAN_REVIEWED = "HUMAN_REVIEWED"
    HUMAN_VALIDATED = "HUMAN_VALIDATED"
    POTENTIAL_TREASURE = "POTENTIAL_TREASURE"
    VALIDATED_TREASURE = "VALIDATED_TREASURE"
    ORDINARY = "ORDINARY"
    FALSE_POSITIVE = "FALSE_POSITIVE"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    REFERENCE_RECOVERY = "REFERENCE_RECOVERY"
    ARCHIVED = "ARCHIVED"
    WITHDRAWN = "WITHDRAWN"
    REJECTED = "ORDINARY"
    DISMISSED = "ORDINARY"

# Backwards-compatibility alias
CandidateState = TreasureState

# State transition validation
VALID_TRANSITIONS: Dict[TreasureState, List[TreasureState]] = {
    TreasureState.DISCOVERED: [TreasureState.CANDIDATE, TreasureState.ORDINARY, TreasureState.WITHDRAWN],
    TreasureState.CANDIDATE: [TreasureState.EVIDENCE_PENDING, TreasureState.ORDINARY, TreasureState.WITHDRAWN],
    TreasureState.EVIDENCE_PENDING: [TreasureState.EVIDENCE_COMPLETE, TreasureState.INSUFFICIENT_EVIDENCE, TreasureState.WITHDRAWN],
    TreasureState.EVIDENCE_COMPLETE: [TreasureState.ANALYSIS_PENDING, TreasureState.REVIEW_PENDING, TreasureState.POTENTIAL_TREASURE, TreasureState.ORDINARY, TreasureState.FALSE_POSITIVE, TreasureState.REFERENCE_RECOVERY],
    TreasureState.ANALYSIS_PENDING: [TreasureState.REVIEW_PENDING, TreasureState.POTENTIAL_TREASURE, TreasureState.ORDINARY, TreasureState.FALSE_POSITIVE],
    TreasureState.REVIEW_PENDING: [TreasureState.HUMAN_REVIEWED, TreasureState.POTENTIAL_TREASURE, TreasureState.WITHDRAWN],
    TreasureState.HUMAN_REVIEWED: [TreasureState.VALIDATED_TREASURE, TreasureState.ORDINARY, TreasureState.FALSE_POSITIVE, TreasureState.INSUFFICIENT_EVIDENCE, TreasureState.ARCHIVED],
    TreasureState.POTENTIAL_TREASURE: [TreasureState.HUMAN_REVIEWED, TreasureState.WITHDRAWN, TreasureState.ARCHIVED],
    TreasureState.VALIDATED_TREASURE: [TreasureState.ARCHIVED, TreasureState.WITHDRAWN],
    TreasureState.REFERENCE_RECOVERY: [TreasureState.ARCHIVED, TreasureState.REVIEW_PENDING],
    TreasureState.ORDINARY: [TreasureState.ARCHIVED],
    TreasureState.FALSE_POSITIVE: [TreasureState.ARCHIVED],
    TreasureState.INSUFFICIENT_EVIDENCE: [TreasureState.EVIDENCE_PENDING, TreasureState.ARCHIVED],
    TreasureState.ARCHIVED: [TreasureState.WITHDRAWN],
    TreasureState.WITHDRAWN: []
}

def validate_state_transition(from_state: TreasureState, to_state: TreasureState, is_human_review: bool = False) -> None:
    """
    Validate that a state transition is legally permissible.
    Enforces the machine-validation prohibition: VALIDATED_TREASURE cannot be reached without HUMAN_REVIEWED.
    """
    if to_state == TreasureState.VALIDATED_TREASURE and not is_human_review and from_state != TreasureState.HUMAN_REVIEWED:
        raise ValueError(
            f"Machine Validation Prohibition: Cannot transition from {from_state} to {to_state} without human review."
        )
    if to_state not in VALID_TRANSITIONS.get(from_state, []):
        raise ValueError(
            f"Invalid state transition from {from_state} to {to_state}."
        )

class TreasureDecision(str, Enum):
    TREASURE_VALIDATED = "TREASURE_VALIDATED"
    REVIEW_PENDING = "REVIEW_PENDING"
    POTENTIAL_TREASURE = "POTENTIAL_TREASURE"
    DISMISSED = "DISMISSED"
    FALSE_POSITIVE = "FALSE_POSITIVE"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"

class CandidateRecord(BaseModel):
    candidate_id: str
    source_strategy: TreasureStrategy
    domain: str
    url: str
    path: str
    category: str = "General"
    discovery_timestamp_utc: str
    discovery_reason: str
    path_type: str = "OTHER"
    archive_presence: str = "AVAILABLE"
    current_status: Optional[int] = None
    raw_evidence_available: bool = False
    earliest_capture_year: Optional[int] = None
    latest_capture_year: Optional[int] = None
    historical_span_years: int = 0
    capture_count: int = 0
    research_priority: float = 0.0
    seen_by_strategies: List[str] = Field(default_factory=list)
    state: TreasureState = TreasureState.DISCOVERED

    # Backwards compatibility alias for discovery_priority
    @property
    def discovery_priority(self) -> float:
        return self.research_priority

    @discovery_priority.setter
    def discovery_priority(self, value: float):
        self.research_priority = value

class InvestigationRecord(BaseModel):
    investigation_id: str
    candidate_id: str
    domain: str
    url: str
    path: str
    category: str = "General"
    strategy: TreasureStrategy = TreasureStrategy.HISTORICAL_SURVIVOR
    live_status_code: int = 200
    live_content_type: str = "text/html"
    live_content_length: int = 0
    live_html_bytes: Optional[int] = None
    live_text_length: Optional[int] = None
    title: Optional[str] = None
    sha256_hash: str = ""
    live_html_sha256: str = ""
    evidence_artifact_path: Optional[str] = ""
    artifact_path: Optional[str] = ""
    earliest_archive_year: Optional[int] = None
    latest_archive_year: Optional[int] = None
    historical_capture_count: int = 0
    html_features_detected: List[str] = Field(default_factory=list)
    detected_features: List[str] = Field(default_factory=list)
    structural_features: List[str] = Field(default_factory=list)
    timeline_summary: Optional[str] = None
    archaeological_score: float = 0.0
    treasure_score: float = 0.0
    decision: TreasureDecision = TreasureDecision.REVIEW_PENDING
    discovery_difficulty: DiscoveryDifficulty = DiscoveryDifficulty.MODERATE
    survival_state: SurvivalState = SurvivalState.STILL_ACTIVE
    prior_art: PriorArtStatus = PriorArtStatus.OBSCURE
    decision_rationale: str = ""
    investigation_timestamp_utc: str = ""
    investigated_at_utc: Optional[str] = None
    state: TreasureState = TreasureState.REVIEW_PENDING

    def model_post_init(self, __context: Any) -> None:
        if not self.sha256_hash and self.live_html_sha256:
            self.sha256_hash = self.live_html_sha256
        elif not self.live_html_sha256 and self.sha256_hash:
            self.live_html_sha256 = self.sha256_hash

        if not self.archaeological_score and self.treasure_score:
            self.archaeological_score = self.treasure_score
        elif not self.treasure_score and self.archaeological_score:
            self.treasure_score = self.archaeological_score

        if not self.evidence_artifact_path and self.artifact_path:
            self.evidence_artifact_path = self.artifact_path
        elif not self.artifact_path and self.evidence_artifact_path:
            self.artifact_path = self.evidence_artifact_path

        if not self.html_features_detected and self.detected_features:
            self.html_features_detected = self.detected_features
        elif not self.html_features_detected and self.structural_features:
            self.html_features_detected = self.structural_features
        if not self.structural_features and self.html_features_detected:
            self.structural_features = self.html_features_detected

        if not self.investigation_timestamp_utc and self.investigated_at_utc:
            self.investigation_timestamp_utc = self.investigated_at_utc

class TreasureRecord(BaseModel):
    treasure_id: str
    candidate_id: str
    domain: str
    path: str
    category: str = "General"
    title: str = ""
    url: str = ""
    full_url: Optional[str] = None
    strategy: TreasureStrategy = TreasureStrategy.HISTORICAL_SURVIVOR
    archaeological_score: float = 0.0
    treasure_score: Optional[float] = None
    time_period: str = "Unknown"
    discovery_difficulty: DiscoveryDifficulty = DiscoveryDifficulty.MODERATE
    survival_state: SurvivalState = SurvivalState.STILL_ACTIVE
    prior_art: PriorArtStatus = PriorArtStatus.OBSCURE
    one_sentence_summary: str = ""
    human_explanation: str = ""
    why_it_matters: str = ""
    why_interesting: Optional[str] = None
    why_search_misses_it: Optional[str] = None
    historical_summary: str = ""
    historical_timeline: Optional[str] = None
    detected_features: List[str] = Field(default_factory=list)
    sha256_hash: str = ""
    evidence_sha256: Optional[str] = None
    raw_evidence_path: str = ""
    artifact_path: Optional[str] = None
    dossier_path: str = ""
    reproduction_steps: Optional[str] = None
    validation_timestamp_utc: str = ""
    validated_at_utc: Optional[str] = None
    human_validator_id: Optional[str] = None
    state: TreasureState = TreasureState.POTENTIAL_TREASURE

    def model_post_init(self, __context: Any) -> None:
        if not self.url and self.full_url:
            self.url = self.full_url
        if not self.archaeological_score and self.treasure_score is not None:
            self.archaeological_score = self.treasure_score
        if not self.sha256_hash and self.evidence_sha256:
            self.sha256_hash = self.evidence_sha256
        if not self.raw_evidence_path and self.artifact_path:
            self.raw_evidence_path = self.artifact_path
        if not self.validation_timestamp_utc and self.validated_at_utc:
            self.validation_timestamp_utc = self.validated_at_utc

class ReviewPacket(BaseModel):
    packet_id: str = ""
    review_id: Optional[str] = None
    candidate_id: str
    target_url: str = ""
    url: Optional[str] = None
    domain: str
    path: str
    domain_category: str = "General"
    category: Optional[str] = None
    live_status_code: int = 200
    live_content_type: str = "text/html"
    html_title: str = ""
    raw_evidence_path: str = ""
    artifact_path: Optional[str] = None
    sha256_hash: str = ""
    live_html_sha256: Optional[str] = None
    evidence_sha256: Optional[str] = None
    earliest_archive_year: Optional[int] = None
    latest_archive_year: Optional[int] = None
    historical_capture_count: int = 0
    html_features_detected: List[str] = Field(default_factory=list)
    features_observed: List[str] = Field(default_factory=list)
    neutral_metadata: Dict[str, Any] = Field(default_factory=dict)
    classification: str = "PARTIALLY_BLIND"
    blinding_level: Optional[str] = None
    status: str = "UNOPENED"
    orphan_status: Optional[str] = None
    timeline_observed: Optional[str] = None
    neutral_summary: Optional[str] = None

    def model_post_init(self, __context: Any) -> None:
        if not self.packet_id and self.review_id:
            self.packet_id = self.review_id
        elif not self.review_id and self.packet_id:
            self.review_id = self.packet_id

        if not self.target_url and self.url:
            self.target_url = self.url
        elif not self.url and self.target_url:
            self.url = self.target_url

        if not self.sha256_hash and self.evidence_sha256:
            self.sha256_hash = self.evidence_sha256
        elif not self.sha256_hash and self.live_html_sha256:
            self.sha256_hash = self.live_html_sha256

        if not self.raw_evidence_path and self.artifact_path:
            self.raw_evidence_path = self.artifact_path

        if not self.html_features_detected and self.features_observed:
            self.html_features_detected = self.features_observed

from pydantic import BaseModel, Field, model_validator

class HumanReviewSubmission(BaseModel):
    review_id: str = ""
    packet_id: str = ""
    candidate_id: str
    reviewer_id: str
    verdict: str  # VALIDATED_TREASURE, CLEAR_TREASURE, POTENTIAL_TREASURE, ORDINARY, FALSE_POSITIVE, INSUFFICIENT_EVIDENCE
    confidence: float = 1.0
    historical_interest_score: float = 5.0
    historical_interest: Optional[float] = None
    notes: str = ""
    timestamp_utc: str = ""
    reviewed_at_utc: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def _map_aliases(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "review_id" in data and "packet_id" not in data:
                data["packet_id"] = data["review_id"]
            elif "packet_id" in data and "review_id" not in data:
                data["review_id"] = data["packet_id"]

            if "historical_interest" in data and "historical_interest_score" not in data:
                data["historical_interest_score"] = float(data["historical_interest"])
            elif "historical_interest_score" in data and "historical_interest" not in data:
                data["historical_interest"] = float(data["historical_interest_score"])

            if "reviewed_at_utc" in data and "timestamp_utc" not in data:
                data["timestamp_utc"] = str(data["reviewed_at_utc"])
            elif "timestamp_utc" in data and "reviewed_at_utc" not in data:
                data["reviewed_at_utc"] = str(data["timestamp_utc"])
        return data

class DiscoveryLineageRecord(BaseModel):
    lineage_id: str
    run_id: str
    domain: str
    domain_category: str
    discovery_strategy: str
    discovery_source: str
    candidate_url: str
    path: str
    raw_artifact_path: str
    raw_artifact_sha256: str
    html_features: List[str]
    research_priority: float
    treasure_interest_score: float
    review_packet_id: str
    candidate_state: str
    validated_treasure_id: Optional[str] = None
    timestamp_utc: str

# Backwards compatibility alias
TreasureLineageRecord = DiscoveryLineageRecord

class SampleManifest(BaseModel):
    run_id: str
    corpus_version: str = "Atlas Corpus v2 (1,000 domains)"
    sample_seed: int = 101
    sample_size: int = 100
    category_quotas: Dict[str, int] = Field(default_factory=dict)
    population_sha256: str = ""
    selected_domains_sha256: str = ""
    selected_domains: List[Any] = Field(default_factory=list)
    created_at_utc: str = ""
    sampling_timestamp_utc: Optional[str] = None
    total_corpus_size: int = 1000
    random_seed: Optional[int] = None
    sample_hash_sha256: Optional[str] = None

class CheckpointRecord(BaseModel):
    run_id: str
    checkpoint_id: str
    timestamp_utc: str
    phase: str
    domains_processed: int
    total_domains: int
    candidates_count: int
    investigations_count: int
    review_pending_count: int
    manifest_sha256: str

# Backwards compatibility alias
RunCheckpoint = CheckpointRecord
