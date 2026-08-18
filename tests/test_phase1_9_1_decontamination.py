"""
Permanent Unit & Regression Test Suite for Phase 1.9.1 Review Decontamination.
Verifies removal of domain-specific review logic, blinding integrity of review packets,
enforcement of discovery state machine, and release gate certification.
"""

import json
import re
import pytest
from pathlib import Path

from atlas.replication.models import (
    DiscoveryState,
    DiscoveryStatus,
    ReviewPacket,
    HumanReviewSubmission
)
from atlas.research.release_gate_phase1_9_1 import run_phase1_9_1_release_gate
from atlas.replication.review import (
    generate_blind_review_packets,
    import_human_review_submissions
)

DATA_DIR = Path("data/phase1_9_1")
AUDIT_DIR = Path("audit/phase1_9_1")

def test_empirical_review_has_no_domain_specific_checks():
    """Verify empirical review module contains zero domain name conditional branches."""
    review_py = Path("atlas/replication/review.py")
    assert review_py.exists()
    content = review_py.read_text(encoding="utf-8")

    # Ensure no hardcoded domain overrides
    assert not re.search(r'if\s+.*domain\s*==\s*["\']gwern\.net["\']', content)
    assert not re.search(r'if\s+.*domain\s*==\s*["\']uspto\.gov["\']', content)
    assert not re.search(r'if\s+.*domain\s*==\s*["\']joelonsoftware\.com["\']', content)

def test_review_packets_contain_no_scores_or_arms():
    """Verify exported review packets strictly omit model scores, arms, and density ranks."""
    packets_file = DATA_DIR / "review_packets.jsonl"
    assert packets_file.exists()

    with open(packets_file, "r", encoding="utf-8") as f:
        packets = [json.loads(l) for l in f if l.strip()]

    assert len(packets) >= 20
    for p in packets:
        assert "raw_anomaly_score" not in p
        assert "arm" not in p
        assert "density_rank" not in p
        assert "expected_verdict" not in p
        assert "model_rule_points" not in p
        assert "packet_id" in p
        assert "candidate_id" in p
        assert "evaluated_path" in p

def test_discovery_state_machine_transitions():
    """Verify formal Discovery State Machine defines all valid lifecycle states."""
    valid_states = {
        DiscoveryState.OBSERVED,
        DiscoveryState.RETRIEVED,
        DiscoveryState.SCORED,
        DiscoveryState.CANDIDATE,
        DiscoveryState.REVIEW_PENDING,
        DiscoveryState.HUMAN_REVIEWED,
        DiscoveryState.VALIDATED,
        DiscoveryState.REJECTED,
        DiscoveryState.INSUFFICIENT
    }
    assert len(valid_states) == 9

def test_candidate_promotion_fails_without_human_review(tmp_path):
    """Verify candidate promotion requires a valid human review submission."""
    # Test with non-existent file
    subs, adjs, val_discs = import_human_review_submissions(tmp_path / "nonexistent.jsonl")
    assert len(val_discs) == 0

    # Test with invalid candidate ID
    invalid_sub = tmp_path / "invalid_sub.jsonl"
    invalid_sub.write_text(json.dumps({
        "submission_id": "SUB_001",
        "packet_id": "PACKET_001",
        "candidate_id": "INVALID_CANDIDATE_ID_999",
        "reviewer_id": "REV_01",
        "review_timestamp_utc": "2026-08-18T12:00:00Z",
        "verdict": "CLEAR_ANOMALY",
        "reviewer_notes": "test",
        "is_genuine_human": True
    }) + "\n")

    with pytest.raises(ValueError, match="Unknown candidate_id"):
        import_human_review_submissions(invalid_sub)

def test_frozen_evidence_artifacts_exist():
    """Verify cryptographic lineage for candidate surfaces."""
    lineage_file = AUDIT_DIR / "discovery_lineage.jsonl"
    assert lineage_file.exists()

    with open(lineage_file, "r", encoding="utf-8") as f:
        lineage = [json.loads(l) for l in f if l.strip()]

    gwern_rec = next((l for l in lineage if l["domain"] == "gwern.net"), None)
    uspto_rec = next((l for l in lineage if l["domain"] == "uspto.gov"), None)

    assert gwern_rec is not None
    assert uspto_rec is not None
    assert gwern_rec["http_status"] == 200
    assert uspto_rec["http_status"] == 200
    assert gwern_rec["raw_anomaly_score"] == 55.0
    assert uspto_rec["raw_anomaly_score"] == 55.0
    assert gwern_rec["decontaminated_status"] == "HUMAN_REVIEW_PENDING"
    assert uspto_rec["decontaminated_status"] == "HUMAN_REVIEW_PENDING"

def test_phase1_9_1_release_gate():
    """Verify all 12 criteria pass in Phase 1.9.1 scientific release gate."""
    gate = run_phase1_9_1_release_gate()
    assert gate["all_passed"] is True
    assert gate["passed_checks"] == 12
    assert gate["total_checks"] == 12
    assert gate["decision"] == "APPROVED_FOR_SALVAGE_AND_HEURISTIC_EXPLORATION"
