"""Formal Web Anomaly Research Failure Taxonomy (Phase 1.4)."""

from enum import Enum
from typing import Dict, Any
from pydantic import BaseModel

class FailureCategory(str, Enum):
    F1_ROOT_SCOPE = "F1_ROOT_SCOPE"                   # Relic exists in deep subpath (~user/), root is modernized
    F2_REDIRECT_WRAPPER = "F2_REDIRECT_WRAPPER"       # Preserved relic enclosed in modern iframe/CMS wrapper
    F3_ASCII_LAYOUT = "F3_ASCII_LAYOUT"               # Pure plain-text/ASCII layout lacking HTML table markers
    F4_ARCHIVE_COVERAGE = "F4_ARCHIVE_COVERAGE"       # Archive API timeout or sparse CDX index gap
    F5_TABLE_OVERDETECTION = "F5_TABLE_OVERDETECTION" # Modern minimalist page using layout tables (e.g. google.com)
    F6_DYNAMIC_CONTENT = "F6_DYNAMIC_CONTENT"         # Client-side JavaScript rendering obscures legacy DOM
    F7_CANONICALIZATION = "F7_CANONICALIZATION"       # HTTP/HTTPS redirect loop or alternate domain canonical
    F8_DEEP_PATH = "F8_DEEP_PATH"                     # Academic or ISP user shell directories
    F9_OTHER = "F9_OTHER"                             # Unclassified transient network or DNS issue

class FailureClassificationRecord(BaseModel):
    domain: str
    category: FailureCategory
    error_type: str  # 'FALSE_POSITIVE', 'FALSE_NEGATIVE', 'COLLECTION_FAILURE'
    description: str
    observed_score: float
    recommended_remedy: str
