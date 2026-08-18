"""
Unit and Integration Tests for Review Packet V2 Neutrality & Model Leakage Prevention.
Verifies that serialized human review packets contain strictly neutral evidence
and zero internal scores, priorities, DNA vectors, strategy names, or interpretations.
"""

import pytest
from pathlib import Path
from atlas.review.packet_v2 import (
    ReviewPacketV2,
    validate_packet_v2_neutrality,
    serialize_neutral_review_packet_v2,
    FORBIDDEN_REVIEW_KEYS,
    FORBIDDEN_INTERPRETATION_PHRASES
)
from atlas.review.console import load_review_packets_v2

def test_packet_v2_neutrality_clean_packet():
    pkt = ReviewPacketV2(
        review_packet_id="REV_PKT_V2_001",
        candidate_id="TCAND_0001",
        packet_version="2.0.0",
        source_url="https://example.com/archive/doc.html",
        final_url="https://example.com/archive/doc.html",
        collection_timestamp_utc="2026-08-18T00:00:00Z",
        current_http_status=200,
        content_type="text/html",
        raw_html_reference="data/artifacts/doc.html",
        evidence_hashes={"raw_html_sha256": "abc123def456"},
        neutral_context={"domain": "example.com", "path": "/archive/doc.html"}
    )
    is_valid, violations = validate_packet_v2_neutrality(pkt.model_dump())
    assert is_valid is True
    assert len(violations) == 0

def test_packet_v2_neutrality_detects_forbidden_keys():
    bad_dict = {
        "review_packet_id": "REV_PKT_V2_002",
        "candidate_id": "TCAND_0002",
        "anomaly_score": 85.5,
        "strategy": "DEEP_PATH",
        "dna": {"survival": 0.9}
    }
    is_valid, violations = validate_packet_v2_neutrality(bad_dict)
    assert is_valid is False
    assert any("anomaly_score" in v for v in violations)
    assert any("strategy" in v for v in violations)
    assert any("dna" in v for v in violations)

def test_packet_v2_neutrality_detects_prohibited_phrases():
    bad_dict = {
        "review_packet_id": "REV_PKT_V2_003",
        "candidate_id": "TCAND_0003",
        "notes": "Atlas detected long-term survival on this ancient page."
    }
    is_valid, violations = validate_packet_v2_neutrality(bad_dict)
    assert is_valid is False
    assert any("long-term survival" in v for v in violations)
    assert any("ancient page" in v for v in violations)

def test_serialized_run_003_packets_are_100_percent_neutral():
    packets_file = Path("data/treasure_runs/TREASURE_RUN_0003/review_v2/review_packets_v2.jsonl")
    if not packets_file.exists():
        pytest.skip("Review V2 packets file not generated yet")
    
    packets = load_review_packets_v2(packets_file.parent)
    assert len(packets) == 51
    for p in packets:
        is_valid, violations = validate_packet_v2_neutrality(p.model_dump())
        assert is_valid is True, f"Violations found in packet {p.review_packet_id}: {violations}"
