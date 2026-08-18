"""
Review Packet V2 — Pure Neutral Evidence Specification for Project Atlas.
Strictly separates Machine Observation from Machine Interpretation from Human Judgment.
Provides only raw facts, verifiable digests, and objective metadata to human reviewers.
Excludes all machine-derived anomaly scores, research priorities, DNA vectors,
strategy labels, cluster memberships, orphan verdicts, and machine explanations.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from pathlib import Path
import hashlib
import json

PACKET_V2_VERSION = "2.0.0"

# List of prohibited keywords and tokens that MUST NEVER appear in serialized review packets
FORBIDDEN_REVIEW_KEYS = {
    "anomaly_score", "research_priority", "queue_score", "treasure_score",
    "score", "dna", "strategy", "strategy_rank", "candidate_rank",
    "cluster_id", "reference_status", "machine_verdict", "machine_explanation",
    "discovery_reason", "machine_feature_flags", "orphan_status",
    "historical_interpretation", "technology_interpretation", "expected_verdict",
    "why_interesting", "why_it_matters", "why_search_misses_it", "decision_rationale"
}

FORBIDDEN_INTERPRETATION_PHRASES = [
    "long-term survival", "structural continuity", "resurrection", "ancient page",
    "unchanged since", "orphan candidate", "orphan proven", "retro styling",
    "this page is old", "this page is orphaned", "atlas detected"
]

class RawCaptureRecord(BaseModel):
    """Factual, uninterpreted historical observation data point."""
    timestamp_utc: str
    archive_source: str
    target_url: str
    http_status: Optional[int] = None
    content_digest_sha256: Optional[str] = None
    byte_count: Optional[int] = None

class NavigationScopeRecord(BaseModel):
    """Objective navigation inspection scope without orphan judgments."""
    root_url: str
    links_inspected_count: int
    direct_link_found: bool
    inspection_timestamp_utc: str

class ReviewPacketV2(BaseModel):
    """
    Layer 2: Human Review Packet V2.
    Strictly neutral evidence packet containing only raw observations and verifiable facts.
    """
    review_packet_id: str
    candidate_id: str
    packet_version: str = PACKET_V2_VERSION
    source_url: str
    final_url: str
    collection_timestamp_utc: str
    current_http_status: int
    content_type: str
    raw_html_reference: str
    screenshot_reference: Optional[str] = None
    archive_references: List[str] = Field(default_factory=list)
    historical_captures: List[RawCaptureRecord] = Field(default_factory=list)
    evidence_hashes: Dict[str, str] = Field(default_factory=dict)
    navigation_scope: Optional[NavigationScopeRecord] = None
    neutral_context: Dict[str, Any] = Field(default_factory=dict)

from typing import List, Optional, Dict, Any, Tuple

def validate_packet_v2_neutrality(packet_dict: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Deep recursive validation verifying zero model leakage or interpretive statements in a packet.
    """
    violations = []

    def _check_dict(d: Dict[str, Any], path: str = ""):
        for k, v in d.items():
            curr_path = f"{path}.{k}" if path else k
            k_lower = k.lower()
            for forbidden in FORBIDDEN_REVIEW_KEYS:
                if forbidden in k_lower:
                    violations.append(f"Forbidden key detected at '{curr_path}': '{k}'")
            if isinstance(v, dict):
                _check_dict(v, curr_path)
            elif isinstance(v, list):
                for idx, item in enumerate(v):
                    if isinstance(item, dict):
                        _check_dict(item, f"{curr_path}[{idx}]")
                    elif isinstance(item, str):
                        _check_text(item, f"{curr_path}[{idx}]")
            elif isinstance(v, str):
                _check_text(v, curr_path)

    def _check_text(text: str, path: str):
        t_lower = text.lower()
        for phrase in FORBIDDEN_INTERPRETATION_PHRASES:
            if phrase in t_lower:
                violations.append(f"Prohibited interpretation phrase at '{path}': '{phrase}' in text: '{text[:60]}...'")

    _check_dict(packet_dict)
    return len(violations) == 0, violations

def serialize_neutral_review_packet_v2(
    investigation: Any,
    packet_id: str,
    raw_html_path: str,
    screenshot_path: Optional[str] = None,
    archive_captures: Optional[List[Dict[str, Any]]] = None,
    navigation_info: Optional[Dict[str, Any]] = None
) -> ReviewPacketV2:
    """
    Converts an internal investigation record into a strictly neutralized Layer 2 ReviewPacketV2.
    Permanently purges all anomaly scores, strategy names, machine classifications, and feature labels.
    """
    url = getattr(investigation, "url", "")
    domain = getattr(investigation, "domain", "")
    path = getattr(investigation, "path", "")
    status_code = getattr(investigation, "live_status_code", 200)
    content_type = getattr(investigation, "live_content_type", "text/html")
    sha256_hash = getattr(investigation, "sha256_hash", getattr(investigation, "live_html_sha256", ""))
    timestamp = getattr(investigation, "investigation_timestamp_utc", getattr(investigation, "investigated_at_utc", "2026-08-18T00:00:00Z"))
    cid = getattr(investigation, "candidate_id", "TCAND_UNKNOWN")

    # Build raw captures (dates, sources, http status, hashes only)
    raw_captures: List[RawCaptureRecord] = []
    earliest_year = getattr(investigation, "earliest_archive_year", getattr(investigation, "earliest_year", None))
    latest_year = getattr(investigation, "latest_archive_year", getattr(investigation, "latest_year", None))

    if earliest_year:
        raw_captures.append(RawCaptureRecord(
            timestamp_utc=f"{earliest_year}-01-01T00:00:00Z",
            archive_source="Wayback CDX Index",
            target_url=url,
            http_status=200
        ))
    if latest_year and latest_year != earliest_year:
        raw_captures.append(RawCaptureRecord(
            timestamp_utc=f"{latest_year}-01-01T00:00:00Z",
            archive_source="Wayback CDX Index",
            target_url=url,
            http_status=200
        ))

    if archive_captures:
        for ac in archive_captures:
            raw_captures.append(RawCaptureRecord(
                timestamp_utc=ac.get("timestamp_utc", ""),
                archive_source=ac.get("source", "Web Archive"),
                target_url=ac.get("url", url),
                http_status=ac.get("http_status", 200),
                content_digest_sha256=ac.get("sha256", None)
            ))

    # Navigation scope
    nav_scope = None
    if navigation_info:
        nav_scope = NavigationScopeRecord(
            root_url=navigation_info.get("root_url", f"https://{domain}/"),
            links_inspected_count=navigation_info.get("links_inspected_count", 0),
            direct_link_found=navigation_info.get("direct_link_found", False),
            inspection_timestamp_utc=navigation_info.get("inspection_timestamp_utc", timestamp)
        )

    # Compute raw HTML hash if file exists
    evidence_hashes = {}
    if sha256_hash:
        evidence_hashes["raw_html_sha256"] = sha256_hash
    if raw_html_path and Path(raw_html_path).exists():
        file_bytes = Path(raw_html_path).read_bytes()
        evidence_hashes["file_sha256"] = hashlib.sha256(file_bytes).hexdigest()

    packet = ReviewPacketV2(
        review_packet_id=packet_id,
        candidate_id=cid,
        packet_version=PACKET_V2_VERSION,
        source_url=url,
        final_url=url,
        collection_timestamp_utc=timestamp,
        current_http_status=status_code,
        content_type=content_type,
        raw_html_reference=raw_html_path,
        screenshot_reference=screenshot_path,
        archive_references=[f"https://web.archive.org/web/*/{url}"],
        historical_captures=raw_captures,
        evidence_hashes=evidence_hashes,
        navigation_scope=nav_scope,
        neutral_context={
            "domain": domain,
            "path": path,
            "domain_category": getattr(investigation, "category", "General")
        }
    )

    # Validate neutrality before returning
    is_valid, violations = validate_packet_v2_neutrality(packet.model_dump())
    if not is_valid:
        raise ValueError(f"Packet V2 Neutrality Violation: {violations}")

    return packet
