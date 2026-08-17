"""Automated Integrity Test Suite for Project Atlas Phase 1.5."""

import json
import pytest
from pathlib import Path

from atlas.deep.config import DeepExperimentConfig
from atlas.deep.models import PathCandidate, PathCategory, DeepEvidenceCapture
from atlas.deep.sampler import sample_study_cohort
from atlas.deep.prioritizer import calculate_retrieval_priority
from atlas.deep.cross_archive import evaluate_archive_agreement, ArchiveAgreementState
from atlas.deep.runner import score_deep_evidence_as_pilot
from atlas.live.guard import assert_no_simulation, set_experiment_mode, SimulationContaminationError

def test_study_sampler_distribution(tmp_path):
    config = DeepExperimentConfig(output_dir=tmp_path)
    records, csv_p, csv_sha = sample_study_cohort(config)

    assert len(records) == 300
    assert csv_p.exists()
    assert len(csv_sha) == 64

    cat_counts = {}
    for r in records:
        cat_counts[r.category] = cat_counts.get(r.category, 0) + 1

    assert cat_counts["Universities"] == 60
    assert cat_counts["Government"] == 60
    assert cat_counts["Nonprofits"] == 45
    assert cat_counts["Long-running companies"] == 45
    assert cat_counts["Open-source/project sites"] == 45
    assert cat_counts["Personal/independent sites"] == 45

def test_simulation_blocked_in_live_mode():
    set_experiment_mode("LIVE")
    from atlas.simulation.generator import generate_synthetic_evidence_profile
    from atlas.pilot.models import PilotDomainRecord

    rec = PilotDomainRecord(
        pilot_id="p15-test-01",
        domain="example.edu",
        category="Universities",
        canonical_url="https://example.edu",
        source_type="curated",
        source_name="Test",
        source_reference="Ref"
    )
    with pytest.raises(SimulationContaminationError):
        generate_synthetic_evidence_profile(rec)

def test_retrieval_priority_scoring():
    c1 = PathCandidate(
        domain="cmu.edu",
        candidate_url="https://cmu.edu/~faculty/legacy/",
        path="/~faculty/legacy/",
        path_category=PathCategory.ACADEMIC_USER_SPACE,
        discovery_source="WAYBACK_CDX",
        first_observed_year=1995,
        last_observed_year=2026,
        capture_count=100
    )
    c2 = PathCandidate(
        domain="cmu.edu",
        candidate_url="https://cmu.edu/news/recent/",
        path="/news/recent/",
        path_category=PathCategory.GENERAL_DIRECTORY,
        discovery_source="ROOT_PAGE_LINK",
        first_observed_year=2024,
        last_observed_year=2026,
        capture_count=5
    )

    p1 = calculate_retrieval_priority(c1)
    p2 = calculate_retrieval_priority(c2)

    assert p1 > p2
    assert p1 >= 80.0
    assert p2 <= 30.0

def test_cross_archive_agreement_classification():
    rec_agree = evaluate_archive_agreement("test.edu", "https://test.edu/old", 50, 1996, 20, 2024)
    assert rec_agree.agreement_state == ArchiveAgreementState.AGREE

    rec_wb = evaluate_archive_agreement("test.edu", "https://test.edu/old", 50, 1996, 0, None)
    assert rec_wb.agreement_state == ArchiveAgreementState.WAYBACK_ONLY

    rec_cc = evaluate_archive_agreement("test.edu", "https://test.edu/old", 0, None, 20, 2024)
    assert rec_cc.agreement_state == ArchiveAgreementState.COMMONCRAWL_ONLY

def test_paired_dataset_1_to_1_reconciliation():
    data_dir = Path("data/phase1_5")
    assert (data_dir / "study_domains.csv").exists()
    assert (data_dir / "root_results.jsonl").exists()
    assert (data_dir / "deep_results.jsonl").exists()

    with open(data_dir / "root_results.jsonl", "r") as f:
        root_lines = [line for line in f if line.strip()]
    with open(data_dir / "deep_results.jsonl", "r") as f:
        deep_lines = [line for line in f if line.strip()]

    assert len(root_lines) == 300
    assert len(deep_lines) == 300

def test_deterministic_score_replay_on_deep_evidence():
    sample_ev = DeepEvidenceCapture(
        study_id="study-0001",
        domain="sample-uni.edu",
        target_url="https://sample-uni.edu/~legacy/",
        is_root=False,
        path="/~legacy/",
        path_category=PathCategory.ACADEMIC_USER_SPACE,
        live_status_code=200,
        page_title="Legacy Faculty Archive",
        extracted_text_bytes=1500,
        html_bytes=4500,
        frameworks_detected=[],
        has_tables_layout=True,
        has_inline_styles=True,
        has_frameset=False,
        has_retro_elements=True,
        has_ascii_layout=False,
        cdx_capture_count=1000,
        earliest_archive_year=1995,
        latest_archive_year=2026,
        historical_similarity_score=0.75,
        evidence_sha256="abc12345"
    )

    s1, c1, r1 = score_deep_evidence_as_pilot(sample_ev)
    s2, c2, r2 = score_deep_evidence_as_pilot(sample_ev)

    assert s1 == s2
    assert c1 == c2 == "CANDIDATE_ANOMALY"
    assert r1 == r2
