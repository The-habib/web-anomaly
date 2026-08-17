"""Pydantic V2 Models for Phase 1.5 Deep Web Archaeology."""

from enum import Enum
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

class PathCategory(str, Enum):
    ACADEMIC_USER_SPACE = "academic_user_space"  # /~user/, ~user/
    LEGACY_DOCS = "legacy_docs"                  # doc/, docs/, man/, rfc/
    ARCHIVE_DIRECTORY = "archive_directory"      # archive/, archives/, old/, history/, retro/
    PUBLIC_FILES = "public_files"                # pub/, public/, files/, downloads/
    SOFTWARE_PROJECT = "software_project"        # projects/, src/, repo/
    PERSONAL_BLOG = "personal_blog"              # personal/, members/, users/, blog/
    YEAR_PREFIXED = "year_prefixed"              # 1990/, 1995/, 1998/, 1999/, 2000/
    GENERAL_DIRECTORY = "general_directory"      # other subdirectories

class ArchiveAgreementState(str, Enum):
    AGREE = "AGREE"
    WAYBACK_ONLY = "WAYBACK_ONLY"
    COMMONCRAWL_ONLY = "COMMONCRAWL_ONLY"
    CONFLICTING = "CONFLICTING"
    INSUFFICIENT = "INSUFFICIENT"

class NoveltyClass(str, Enum):
    WELL_DOCUMENTED = "WELL_DOCUMENTED"
    DOCUMENTED = "DOCUMENTED"
    OBSCURE = "OBSCURE"
    POORLY_DOCUMENTED = "POORLY_DOCUMENTED"
    PRIOR_ART_UNCERTAIN = "PRIOR_ART_UNCERTAIN"

class StudyDomainRecord(BaseModel):
    study_id: str
    domain: str
    category: str
    canonical_url: str
    source_type: str
    source_name: str
    source_reference: str

class PathCandidate(BaseModel):
    domain: str
    candidate_url: str
    path: str
    path_category: PathCategory
    discovery_source: str  # 'WAYBACK_CDX', 'COMMON_CRAWL', 'ROOT_PAGE_LINK', 'SITEMAP'
    first_observed_year: Optional[int] = None
    last_observed_year: Optional[int] = None
    capture_count: int = 1
    retrieval_priority: float = 0.0

class DeepEvidenceCapture(BaseModel):
    study_id: str
    domain: str
    target_url: str
    is_root: bool
    path: str
    path_category: Optional[PathCategory] = None
    live_status_code: int
    page_title: str
    extracted_text_bytes: int
    html_bytes: int
    frameworks_detected: List[str] = Field(default_factory=list)
    has_tables_layout: bool = False
    has_inline_styles: bool = False
    has_frameset: bool = False
    has_retro_elements: bool = False
    has_ascii_layout: bool = False
    cdx_capture_count: int = 0
    earliest_archive_year: Optional[int] = None
    latest_archive_year: Optional[int] = None
    historical_similarity_score: float = 0.0
    evidence_sha256: str
    raw_artifact_path: Optional[str] = None
    archive_source: str = "WAYBACK_AND_COMMONCRAWL"

class PairedDomainResult(BaseModel):
    study_id: str
    domain: str
    category: str
    # Arm A: Root
    root_score: float
    root_classification: str
    root_triggered_rules: List[str] = Field(default_factory=list)
    root_status_code: int = 0
    # Arm B: Deep
    deep_candidates_found: int = 0
    deep_retrievals_attempted: int = 0
    deep_max_score: float = 0.0
    deep_best_path: Optional[str] = None
    deep_classification: str = "ORDINARY"
    deep_triggered_rules: List[str] = Field(default_factory=list)
    # Comparison
    is_incremental_candidate: bool = False
    is_new_validated_discovery: bool = False
    is_incremental_false_positive: bool = False
    recovered_false_negative: bool = False
    novelty: Optional[NoveltyClass] = None

class CrossArchiveDisagreementRecord(BaseModel):
    domain: str
    path_url: str
    wayback_capture_count: int
    wayback_earliest_year: Optional[int] = None
    commoncrawl_capture_count: int
    commoncrawl_earliest_year: Optional[int] = None
    agreement_state: ArchiveAgreementState
    disagreement_summary: str

class ResourceCostMetrics(BaseModel):
    total_http_requests_root: int = 0
    total_http_requests_deep: int = 0
    total_archive_cdx_queries_root: int = 0
    total_archive_cdx_queries_deep: int = 0
    total_bytes_downloaded_root: int = 0
    total_bytes_downloaded_deep: int = 0
    total_runtime_seconds: float = 0.0
    storage_footprint_bytes: int = 0
    cost_per_domain_bytes: float = 0.0
    cost_per_validated_discovery_bytes: float = 0.0
