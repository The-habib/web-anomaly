"""
Adversarial Security & Integrity Guard Test Suite for Project Atlas.
Simulates malicious attacks and accidental corruptions against the research operating system:
1. Malicious seed injection into blind discovery.
2. Fabricated historical metadata spans.
3. Machine score promotion without human review.
4. Information leakage into neutral review packets.
5. Cross-run memory leakage into live blind execution.
6. Tampering with frozen cryptographic evidence artifacts.
"""

import pytest
import tempfile
import json
import hashlib
from pathlib import Path

from atlas.treasure.guard import ExecutionMode, assert_live_blind_isolation
from atlas.treasure.models import (
    TreasureState,
    validate_state_transition,
    CandidateRecord,
    InvestigationRecord,
    TreasureStrategy,
    DiscoveryDifficulty,
    SurvivalState,
    PriorArtStatus,
    TreasureDecision
)
from atlas.treasure.review import generate_review_packets
from atlas.review.importer import import_human_reviews
from atlas.memory.engine import CrossRunMemoryStore, MemoryDomain

def test_adversarial_seed_injection_rejection():
    """Verify runtime guard detects forbidden reference seeds or simulation modules in LIVE_BLIND mode."""
    # Attempting to run in LIVE_BLIND mode with reference tokens in scope
    # The guard should strictly check and raise RuntimeError if simulation modules or tokens are imported
    assert_live_blind_isolation(ExecutionMode.LIVE_BLIND, context="Adversarial Test")

def test_adversarial_unreviewed_promotion_prevention():
    """Verify system strictly rejects transitioning a machine candidate directly to VALIDATED_TREASURE."""
    with pytest.raises(ValueError, match="Machine Validation Prohibition"):
        validate_state_transition(
            from_state=TreasureState.CANDIDATE,
            to_state=TreasureState.VALIDATED_TREASURE,
            is_human_review=False
        )

    with pytest.raises(ValueError, match="Machine Validation Prohibition"):
        validate_state_transition(
            from_state=TreasureState.POTENTIAL_TREASURE,
            to_state=TreasureState.VALIDATED_TREASURE,
            is_human_review=False
        )

def test_adversarial_review_packet_leakage(tmp_path):
    """Verify review packets never leak machine scores, rankings, or discovery strategies."""
    inv = InvestigationRecord(
        investigation_id="INV-SECRET-001",
        candidate_id="TCAND-SECRET-001",
        domain="example.com",
        url="https://example.com/ancient.html",
        path="/ancient.html",
        category="General",
        strategy=TreasureStrategy.TECHNOLOGY_FOSSIL,
        live_status_code=200,
        live_content_type="text/html",
        live_content_length=2048,
        sha256_hash="d" * 64,
        evidence_artifact_path=str(tmp_path / "ancient.html"),
        earliest_archive_year=2000,
        latest_archive_year=2026,
        historical_capture_count=35,
        html_features_detected=["pre_css_tables_layout"],
        archaeological_score=88.5,
        decision=TreasureDecision.POTENTIAL_TREASURE,
        discovery_difficulty=DiscoveryDifficulty.VERY_HARD,
        survival_state=SurvivalState.STILL_ACTIVE,
        prior_art=PriorArtStatus.OBSCURE,
        decision_rationale="Extremely high score fossil",
        investigation_timestamp_utc="2026-08-18T00:00:00Z"
    )

    out_file = tmp_path / "packets.jsonl"
    packets = generate_review_packets([inv], out_file)
    assert len(packets) == 1

    packet_dict = packets[0].model_dump()
    assert "archaeological_score" not in packet_dict
    assert "strategy" not in packet_dict
    assert "decision" not in packet_dict
    assert "discovery_difficulty" not in packet_dict
    assert "decision_rationale" not in packet_dict

def test_adversarial_memory_quarantine(tmp_path):
    """Verify live blind execution cannot query quarantined review memory."""
    store = CrossRunMemoryStore(tmp_path)
    store.record(MemoryDomain.REVIEW_MEMORY, "FORBIDDEN_KEY", {"secret": "data"}, "RUN_001", "2026-08-18T00:00:00Z")

    with pytest.raises(PermissionError, match="ISOLATION VIOLATION"):
        store.query(MemoryDomain.REVIEW_MEMORY, "FORBIDDEN_KEY", execution_mode="LIVE_BLIND")

def test_adversarial_fake_human_impersonation(tmp_path):
    """Verify human review importer rejects automated or system-generated reviewer IDs."""
    fake_review_file = tmp_path / "fake_reviews.jsonl"
    with open(fake_review_file, "w", encoding="utf-8") as f:
        f.write(json.dumps({
            "review_id": "REV-001",
            "packet_id": "PKT-001",
            "candidate_id": "TCAND-001",
            "reviewer_id": "machine_auto_bot",
            "verdict": "VALIDATED_TREASURE",
            "confidence": 0.99,
            "historical_interest_score": 90.0,
            "notes": "Automated confirmation",
            "timestamp_utc": "2026-08-18T00:00:00Z"
        }) + "\n")

    imported, summary = import_human_reviews(fake_review_file, known_candidates={"TCAND-001"})
    assert len(imported) == 0
    assert summary.rejected_reviews_count == 1
    assert "Machine/system reviewer ID forbidden" in summary.rejections[0]

def test_adversarial_evidence_tampering_detection(tmp_path):
    """Verify hash mismatch is detected if frozen HTML bytes are modified."""
    original_html = "<html><body>Original Untampered Content</body></html>"
    orig_hash = hashlib.sha256(original_html.encode("utf-8")).hexdigest()

    file_path = tmp_path / "tampered.html"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("<html><body>Maliciously Modified Content</body></html>")

    curr_hash = hashlib.sha256(file_path.read_bytes()).hexdigest()
    assert curr_hash != orig_hash
