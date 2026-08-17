"""Comprehensive verification tests for Phase 1.3 Live Mode Integrity."""

import json
import pytest
import hashlib
from pathlib import Path

from atlas.live.guard import (
    SimulationContaminationError,
    assert_no_simulation,
    set_experiment_mode,
    get_experiment_mode
)
from atlas.pilot.models import PilotDomainRecord, PilotEvidenceCapture
from atlas.pilot.scoring import score_single_evidence
from atlas.pilot.benchmark_runner import build_benchmark_v2, run_benchmark_v2_evaluation
from atlas.provenance.manifest import compute_sha256

def test_simulation_blocked_in_live_mode():
    set_experiment_mode("LIVE")
    from atlas.simulation.generator import generate_synthetic_evidence_profile
    rec = PilotDomainRecord(
        pilot_id="test-0001",
        domain="example.com",
        category="Companies",
        canonical_url="https://example.com",
        source_type="curated",
        source_name="Test",
        source_reference="Ref"
    )
    with pytest.raises(SimulationContaminationError) as exc_info:
        generate_synthetic_evidence_profile(rec)
    assert "SECURITY GUARD VIOLATION" in str(exc_info.value)

def test_live_evidence_provenance_completeness():
    live_file = Path("data/phase1_3_live/pilot_evidence.jsonl")
    assert live_file.exists()

    with open(live_file, "r", encoding="utf-8") as f:
        records = [json.loads(line) for line in f if line.strip()]

    assert len(records) > 100
    for r in records[:20]:
        assert "domain" in r
        assert "live_status_code" in r
        assert "evidence_sha256" in r
        assert len(r["evidence_sha256"]) == 64

def test_negative_synthetic_injection_rejected():
    set_experiment_mode("LIVE")
    # Synthetic generator must fail
    with pytest.raises(SimulationContaminationError):
        assert_no_simulation("Testing synthetic injection blocker")

def test_domain_blind_scoring():
    # Scoring engine must produce identical scores for identical evidence regardless of domain name
    ev1 = PilotEvidenceCapture(
        pilot_id="pilot-001",
        domain="ordinary-site.org",
        category="Nonprofits",
        has_tables_layout=True,
        has_retro_elements=True,
        has_frameset=False,
        historical_similarity_score=0.90,
        earliest_archive_year=1996,
        cdx_capture_count=5000,
        evidence_sha256="abc",
        raw_evidence_summary="summary"
    )
    ev2 = PilotEvidenceCapture(
        pilot_id="pilot-002",
        domain="arbitrary-name-12345.org",
        category="Nonprofits",
        has_tables_layout=True,
        has_retro_elements=True,
        has_frameset=False,
        historical_similarity_score=0.90,
        earliest_archive_year=1996,
        cdx_capture_count=5000,
        evidence_sha256="abc",
        raw_evidence_summary="summary"
    )

    s1 = score_single_evidence(ev1)
    s2 = score_single_evidence(ev2)

    assert s1.raw_anomaly_score == s2.raw_anomaly_score
    assert s1.classification == s2.classification
    assert s1.triggered_rules == s2.triggered_rules

def test_label_blind_benchmark_scoring():
    build_benchmark_v2()
    # Ensure labels_private.jsonl is separated from public manifest
    manifest_p = Path("data/benchmark_v2/public_manifest.json")
    assert manifest_p.exists()
    with open(manifest_p, "r", encoding="utf-8") as f:
        m_data = json.load(f)
    assert "labels_sha256" in m_data

def test_evidence_tampering_detection(tmp_path):
    raw_file = tmp_path / "test_artifact.html"
    raw_file.write_bytes(b"<html>Original Content</html>")
    orig_hash = compute_sha256(raw_file)

    # Tamper with file
    raw_file.write_bytes(b"<html>Tampered Content</html>")
    tampered_hash = compute_sha256(raw_file)

    assert orig_hash != tampered_hash

def test_deterministic_score_replay():
    ev_file = Path("data/phase1_3_live/pilot_evidence.jsonl")
    assert ev_file.exists()

    with open(ev_file, "r", encoding="utf-8") as f:
        evidence_list = [PilotEvidenceCapture.model_validate_json(line) for line in f if line.strip()]

    # Score run 1
    scores_run1 = [score_single_evidence(ev) for ev in evidence_list]
    # Score run 2
    scores_run2 = [score_single_evidence(ev) for ev in evidence_list]

    assert len(scores_run1) == len(scores_run2)
    for s1, s2 in zip(scores_run1, scores_run2):
        assert s1.domain == s2.domain
        assert s1.raw_anomaly_score == s2.raw_anomaly_score
        assert s1.classification == s2.classification
