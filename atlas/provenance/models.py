"""Pydantic V2 models and taxonomies for Corpus Provenance & Quality."""

from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime, timezone

class SourceType(str, Enum):
    OFFICIAL_SOURCE = "OFFICIAL_SOURCE"
    PUBLIC_DIRECTORY = "PUBLIC_DIRECTORY"
    PUBLIC_DATASET = "PUBLIC_DATASET"
    OPEN_SOURCE_PROJECT = "OPEN_SOURCE_PROJECT"
    ARCHIVE_REFERENCE = "ARCHIVE_REFERENCE"
    MANUAL_VERIFIED = "MANUAL_VERIFIED"
    SYNTHETIC = "SYNTHETIC"
    UNKNOWN = "UNKNOWN"

class RejectionCode(str, Enum):
    SYNTHETIC_PATTERN = "SYNTHETIC_PATTERN"
    INVALID_DOMAIN = "INVALID_DOMAIN"
    DNS_FAILURE = "DNS_FAILURE"
    SOURCE_UNVERIFIED = "SOURCE_UNVERIFIED"
    CATEGORY_UNCERTAIN = "CATEGORY_UNCERTAIN"
    DUPLICATE = "DUPLICATE"
    REDIRECT_ONLY = "REDIRECT_ONLY"
    PARKED_DOMAIN = "PARKED_DOMAIN"
    DOMAIN_FOR_SALE = "DOMAIN_FOR_SALE"
    PRIVATE_SERVICE = "PRIVATE_SERVICE"
    TEST_DOMAIN = "TEST_DOMAIN"
    INSUFFICIENT_PROVENANCE = "INSUFFICIENT_PROVENANCE"
    DISALLOWED_TARGET = "DISALLOWED_TARGET"

class VerificationStatus(str, Enum):
    VERIFIED_REAL_CURATED = "VERIFIED_REAL_CURATED"
    VERIFIED_ACTIVE = "VERIFIED_ACTIVE"
    VERIFIED_HISTORICAL = "VERIFIED_HISTORICAL"
    REJECTED = "REJECTED"
    UNVERIFIED = "UNVERIFIED"

class LiveAvailabilityStatus(str, Enum):
    REAL_LIVE = "REAL_LIVE"
    REAL_HISTORICAL = "REAL_HISTORICAL"
    REAL_ARCHIVED = "REAL_ARCHIVED"
    REAL_UNAVAILABLE = "REAL_UNAVAILABLE"

class ArchiveAvailabilityStatus(str, Enum):
    WAYBACK_AVAILABLE = "WAYBACK_AVAILABLE"
    COMMONCRAWL_AVAILABLE = "COMMONCRAWL_AVAILABLE"
    BOTH = "BOTH"
    NONE = "NONE"

class CandidateRecord(BaseModel):
    domain: str
    input_url: str
    category: str
    source_type: SourceType
    source_name: str
    source_url: str
    source_reference: str
    notes: Optional[str] = ""

class ProvenanceRecord(BaseModel):
    domain: str
    canonical_url: str
    category: str
    source_type: SourceType
    source_name: str
    source_url: str
    source_reference: str
    collection_method: str
    selection_timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    verification_status: VerificationStatus
    live_status: Optional[LiveAvailabilityStatus] = LiveAvailabilityStatus.REAL_LIVE
    archive_status: Optional[ArchiveAvailabilityStatus] = ArchiveAvailabilityStatus.BOTH
    notes: Optional[str] = ""

class RejectionRecord(BaseModel):
    domain: str
    category: str
    rejection_code: RejectionCode
    reason: str
    rejected_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class CorpusQualityMetrics(BaseModel):
    corpus_id: str = "atlas-v2"
    calculated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    total_domains: int
    provenance_completeness: float
    synthetic_rate: float
    duplicate_rate: float
    verification_rate: float
    category_integrity: float
    source_diversity: float
    overall_quality_score: float
    weakest_dimension: str
    dimension_scores: Dict[str, float]

class CorpusManifest(BaseModel):
    corpus_id: str = "atlas-v2"
    version: str = "2.0"
    seed: int = 42
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    total_domains: int = 1000
    candidate_pool_counts: Dict[str, int]
    final_counts: Dict[str, int]
    synthetic_count: int = 0
    duplicate_count: int = 0
    unknown_provenance_count: int = 0
    selection_algorithm: str = "deterministic_sampling_seed_42"
    source_hashes: Dict[str, str] = Field(default_factory=dict)
    corpus_sha256: str = ""

class BenchmarkRecord(BaseModel):
    benchmark_id: str
    domain: str
    canonical_url: str
    category: str
    group_type: str
    expected_classification: str
    reference_rationale: str
    established_features: List[str]
    frozen_evidence_sha256: Optional[str] = None
