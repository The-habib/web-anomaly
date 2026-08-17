"""
Pydantic Models for Phase 1.7 Path Density Laboratory.
"""

from enum import Enum
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

class PathCategory14(str, Enum):
    ROOT = "ROOT"
    BLOG = "BLOG"
    DOCS = "DOCS"
    PERSONAL = "PERSONAL"
    USER_SPACE = "USER_SPACE"
    ARCHIVE = "ARCHIVE"
    LEGACY = "LEGACY"
    SOFTWARE = "SOFTWARE"
    PROJECT = "PROJECT"
    FILES = "FILES"
    MEDIA = "MEDIA"
    RESEARCH = "RESEARCH"
    DIRECTORY = "DIRECTORY"
    OTHER = "OTHER"

class CoverageClassification(str, Enum):
    OVERLAPPING_COVERAGE = "OVERLAPPING_COVERAGE"
    SOURCE_A_ONLY_WITH_COVERAGE_GAP = "SOURCE_A_ONLY_WITH_COVERAGE_GAP"
    TRUE_DISAGREEMENT = "TRUE_DISAGREEMENT"
    INSUFFICIENT = "INSUFFICIENT"

class DensityTier(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    EXTREME = "EXTREME"

class ArmType(str, Enum):
    UNIFORM = "UNIFORM"
    DENSITY_PRIORITIZED = "DENSITY_PRIORITIZED"

class PopulationDensityRecord(BaseModel):
    domain: str
    category: str
    canonical_url: str
    index_source: str = "WAYBACK_CDX"
    d_raw: int = Field(description="Unique historical URLs count")
    d_year: float = Field(description="Unique paths / observed years")
    d_capture: float = Field(description="Unique paths / total capture observations")
    d_span: int = Field(description="Span in years (latest - earliest)")
    d_user: int = Field(description="Count of user-space paths")
    d_legacy: int = Field(description="Count of legacy/archive paths")
    d_diversity: float = Field(description="Shannon entropy of path type distribution")
    d_content: int = Field(description="Unique content digest count")
    earliest_observed_year: Optional[int] = None
    latest_observed_year: Optional[int] = None
    total_captures: int = 0
    path_distribution: Dict[str, int] = Field(default_factory=dict)
    density_tier: Optional[DensityTier] = None

class ArchiveCoverageRecord(BaseModel):
    domain: str
    wayback_earliest_year: Optional[int] = None
    wayback_latest_year: Optional[int] = None
    wayback_capture_count: int = 0
    commoncrawl_earliest_year: Optional[int] = None
    commoncrawl_latest_year: Optional[int] = None
    commoncrawl_capture_count: int = 0
    overlapping_years: List[int] = Field(default_factory=list)
    coverage_classification: CoverageClassification
    coverage_summary: str

class DomainFeatureRecord(BaseModel):
    domain: str
    category: str
    observed_web_history_span: int
    public_url_volume: int
    subdomain_count_proxy: int = 1
    section_count_proxy: int = 1
    is_multi_user_platform: bool = False

class StudyAssignmentRecord(BaseModel):
    study_id: str
    domain: str
    category: str
    arm: ArmType
    blinded_arm_label: str  # e.g. "STUDY_A" or "STUDY_B"
    d_raw: int
    density_tier: DensityTier
    is_holdout: bool = False

class DensityStatisticalResults(BaseModel):
    experiment_id: str = "phase1_7_density_validation"
    primary_metric: str = "validated_discoveries_per_1000_retrievals"
    uniform_arm_domains: int
    uniform_arm_retrievals: int
    uniform_arm_candidates: int
    uniform_arm_discoveries: int
    uniform_arm_fp: int
    uniform_yield_per_1000_retrievals: float
    uniform_yield_per_100_domains: float
    density_arm_domains: int
    density_arm_retrievals: int
    density_arm_candidates: int
    density_arm_discoveries: int
    density_arm_fp: int
    density_yield_per_1000_retrievals: float
    density_yield_per_100_domains: float
    rate_ratio: float
    rate_ratio_ci_95: List[float]
    absolute_risk_difference: float
    fishers_exact_p_value: float
    statistical_significance: bool
    hypothesis_verdict: str
    thunix_sensitivity: Dict[str, Any] = Field(default_factory=dict)
    category_breakdown: Dict[str, Any] = Field(default_factory=dict)
    holdout_validation: Dict[str, Any] = Field(default_factory=dict)
