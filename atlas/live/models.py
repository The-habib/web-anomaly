"""Formal evidence data contracts with strict provenance for Project Atlas Phase 1.3."""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime, timezone

class LiveEvidenceRecord(BaseModel):
    """Cryptographically verified empirical evidence collected from a live website."""
    domain: str
    requested_url: str
    final_url: str
    redirect_chain: List[str] = Field(default_factory=list)
    http_status: int
    content_type: str = ""
    collected_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    collection_duration_ms: float = 0.0
    page_title: str = ""
    html_raw_sha256: str = ""
    html_bytes: int = 0
    extracted_text_bytes: int = 0
    raw_artifact_path: str = ""
    frameworks_detected: List[str] = Field(default_factory=list)
    has_tables_layout: bool = False
    has_inline_styles: bool = False
    has_frameset: bool = False
    has_retro_elements: bool = False
    collection_method: str = "LIVE_HTTP_REQUEST"
    provenance_verified: bool = True

class ArchiveEvidenceRecord(BaseModel):
    """Cryptographically verified empirical evidence collected from public web archives."""
    domain: str
    target_url: str
    query_timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    wayback_status: str = "NOT_QUERIED"  # 'SUCCESS', 'WAYBACK_UNAVAILABLE', 'NO_ARCHIVE_OBSERVATION', 'ERROR'
    wayback_snapshots_count: int = 0
    earliest_wayback_timestamp: Optional[str] = None
    latest_wayback_timestamp: Optional[str] = None
    earliest_wayback_year: Optional[int] = None
    latest_wayback_year: Optional[int] = None
    commoncrawl_status: str = "NOT_QUERIED"  # 'SUCCESS', 'COMMONCRAWL_UNAVAILABLE', 'NO_RECORDS', 'ERROR'
    commoncrawl_records_count: int = 0
    historical_similarity_score: float = 0.0
    raw_archive_summary: str = ""
    archive_query_duration_ms: float = 0.0
    provenance_verified: bool = True

class EvidenceFailureRecord(BaseModel):
    """Explicit structured failure record. Forbids silent fallback to simulation."""
    domain: str
    target_url: str
    stage: str  # 'LIVE_HTTP', 'WAYBACK_CDX', 'COMMONCRAWL_CDX', 'RENDER_SCREENSHOT'
    error_code: str  # 'TIMEOUT', 'CONNECTION_REFUSED', 'HTTP_5XX', 'HTTP_4XX', 'RATE_LIMITED', 'DNS_FAILURE'
    error_message: str
    failed_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    fallback_action: str = "RECORD_FAILURE_AS_INSUFFICIENT_EVIDENCE"

class CollectionAuditLogEntry(BaseModel):
    """Structured audit log entry written to logs/phase1_3/."""
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    domain: str
    source: str  # 'LIVE_HTTP', 'WAYBACK_CDX', 'COMMONCRAWL_CDX'
    operation: str
    status: str  # 'SUCCESS', 'FAILURE', 'TIMEOUT', 'RATE_LIMITED'
    duration_ms: float
    bytes_received: int
    artifact_hash: Optional[str] = None
    error: Optional[str] = None
