"""
Data Models for Project Atlas — Treasure Mode Subsystem.
Defines schemas for multi-strategy candidate discovery, adaptive investigations,
review packets, human review submissions, lineages, sample manifests, and checkpoints.
"""

from enum import Enum
from typing import List, Optional, Dict, Any
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

class CandidateState(str, Enum):
    DISCOVERED = "DISCOVERED"
    CANDIDATE = "CANDIDATE"
    EVIDENCE_PENDING = "EVIDENCE_PENDING"
    EVIDENCE_COMPLETE = "EVIDENCE_COMPLETE"
    REVIEW_PENDING = "REVIEW_PENDING"
    HUMAN_VALIDATED = "HUMAN_VALIDATED"
    REJECTED = "REJECTED"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    ORDINARY = "ORDINARY"
    FALSE_POSITIVE = "FALSE_POSITIVE"

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
    state: CandidateState = CandidateState.DISCOVERED

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
    category: str
    strategy: TreasureStrategy
    live_status_code: int
    live_html_sha256: str
    live_html_bytes: int = 0
    live_text_length: int = 0
    title: str = ""
    structural_features: List[str] = Field(default_factory=list)
    timeline_summary: str = ""
    earliest_year: Optional[int] = None
    latest_year: Optional[int] = None
    capture_count: int = 0
    historical_span_years: int = 0
    is_linked_from_root: bool = False
    orphan_likelihood: float = 0.0
    survival_state: SurvivalState = SurvivalState.STILL_ACTIVE
    prior_art: PriorArtStatus = PriorArtStatus.OBSCURE
    discovery_difficulty: DiscoveryDifficulty = DiscoveryDifficulty.MODERATE
    treasure_score: float = 0.0
    decision: TreasureDecision = TreasureDecision.REVIEW_PENDING
    state: CandidateState = CandidateState.EVIDENCE_COMPLETE
    human_explanation: str = ""
    why_interesting: str = ""
    why_search_misses_it: str = ""
    evidence_artifact_path: Optional[str] = None
    investigated_at_utc: str = ""

class ReviewPacket(BaseModel):
    review_id: str
    candidate_id: str
    url: str
    domain: str
    path: str
    blinding_level: str = "PARTIALLY_BLIND"
    live_status_code: int
    features_observed: List[str]
    orphan_status: str
    timeline_observed: str
    evidence_sha256: str
    artifact_path: str
    neutral_summary: str

class HumanReviewSubmission(BaseModel):
    review_id: str
    candidate_id: str
    reviewer_id: str
    verdict: str  # CLEAR_TREASURE, POTENTIAL_TREASURE, ORDINARY, INSUFFICIENT_EVIDENCE
    confidence: float
    notes: str
    reviewed_at_utc: str

class SampleManifest(BaseModel):
    run_id: str
    corpus_version: str
    sample_seed: int
    sample_size: int
    category_quotas: Dict[str, int]
    population_sha256: str
    selected_domains_sha256: str
    selected_domains: List[Dict[str, str]]
    created_at_utc: str

class TreasureRecord(BaseModel):
    treasure_id: str
    candidate_id: str
    title: str
    domain: str
    category: str
    path: str
    full_url: str
    strategy: TreasureStrategy
    time_period: str
    treasure_score: float
    discovery_difficulty: DiscoveryDifficulty
    survival_state: SurvivalState
    prior_art: PriorArtStatus
    one_sentence_summary: str
    human_explanation: str
    why_interesting: str
    why_search_misses_it: str
    historical_timeline: str
    detected_features: List[str]
    evidence_sha256: str
    artifact_path: str
    reproduction_steps: str
    validated_at_utc: str

class TreasureLineageRecord(BaseModel):
    treasure_id: str
    candidate_id: str
    strategy: TreasureStrategy
    domain: str
    url: str
    discovery_path: str
    discovery_timestamp_utc: str
    retrieval_sequence: List[str] = Field(default_factory=list)
    live_status_code: int
    live_sha256: str
    historical_archive_sources: List[str] = Field(default_factory=list)
    quality_score: float
    difficulty: DiscoveryDifficulty
    prior_art_status: PriorArtStatus
    decision: TreasureDecision
    artifact_hash: str

class RunCheckpoint(BaseModel):
    run_id: str
    seed: int
    start_time_utc: str
    batch_id: str = "batch-001"
    completed_candidate_ids: List[str] = Field(default_factory=list)
    pending_candidate_ids: List[str] = Field(default_factory=list)
    investigated_count: int = 0
    validated_treasure_ids: List[str] = Field(default_factory=list)
    potential_treasure_ids: List[str] = Field(default_factory=list)
    dismissed_count: int = 0
    false_positive_count: int = 0
    is_completed: bool = False
