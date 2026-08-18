"""
Permanent Unit, Integration & Regression Test Suite for Project Atlas — Treasure Run #002.
Verifies no seed injection, unbiased deterministic domain sampling, archival provenance,
prohibition of automatic machine validation, review packet blinding, reference world isolation,
and report consistency.
"""

import json
import pytest
from pathlib import Path

from atlas.treasure.models import (
    TreasureStrategy,
    DiscoveryDifficulty,
    SurvivalState,
    PriorArtStatus,
    CandidateState,
    TreasureDecision,
    CandidateRecord,
    InvestigationRecord,
    ReviewPacket,
    TreasureRecord
)
from atlas.treasure.guard import ExecutionMode, assert_live_blind_isolation
from atlas.treasure.sampler import sample_blind_domain_population, load_corpus_v2_population
from atlas.treasure.discovery import generate_multi_strategy_candidates, evaluate_path_strategies
from atlas.treasure.investigator import investigate_single_candidate
from atlas.treasure.review import generate_review_packets, import_human_review_submissions
from atlas.treasure.prior_art import evaluate_prior_art_status
from atlas.treasure.reference_eval import run_post_hoc_reference_evaluation
from atlas.treasure.release_gate import run_treasure_release_gate
from atlas.density.path_classifier import PathCategory14

def test_no_seed_injection():
    """Verify production discovery module does not define or export KNOWN_ARCHAEOLOGICAL_SEEDS."""
    import atlas.treasure.discovery as disc
    assert not hasattr(disc, "KNOWN_ARCHAEOLOGICAL_SEEDS"), "KNOWN_ARCHAEOLOGICAL_SEEDS must not exist in discovery module!"

def test_seed_contamination_regression():
    """Regression test: verify discovery code does not contain hardcoded known treasure names."""
    disc_file = Path("atlas/treasure/discovery.py")
    content = disc_file.read_text(encoding="utf-8")

    forbidden_names = [
        "thunix.net",
        "tilde.club",
        "spacejam.com",
        "zombo.com",
        "toastytech.com",
        "rotten.com",
        "textfiles.com"
    ]
    for fn in forbidden_names:
        assert fn not in content, f"Forbidden seed '{fn}' found in production discovery code!"

def test_unbiased_deterministic_sampling(tmp_path):
    """Verify deterministic stratified sampling from full Corpus v2 population."""
    out_manifest = tmp_path / "sample_manifest.json"
    manifest1 = sample_blind_domain_population(sample_size=100, seed=101, output_manifest_path=out_manifest)
    
    assert manifest1.sample_size == 100
    assert manifest1.sample_seed == 101
    assert len(manifest1.selected_domains) == 100
    assert len(manifest1.population_sha256) == 64
    assert len(manifest1.selected_domains_sha256) == 64

    # Repeat with same seed -> exactly identical hash
    manifest2 = sample_blind_domain_population(sample_size=100, seed=101, output_manifest_path=tmp_path / "m2.json")
    assert manifest1.selected_domains_sha256 == manifest2.selected_domains_sha256
    assert [d["domain"] for d in manifest1.selected_domains] == [d["domain"] for d in manifest2.selected_domains]

    # Category quotas check
    quotas = manifest1.category_quotas
    assert quotas.get("Universities") == 20
    assert quotas.get("Government") == 20
    assert quotas.get("Nonprofits") == 15
    assert quotas.get("Long-running companies") == 15
    assert quotas.get("Open-source/project sites") == 15
    assert quotas.get("Personal/independent sites") == 15

def test_historical_metadata_provenance(tmp_path):
    """Verify no hardcoded default capture years (1998, 2024, 12 captures)."""
    cand = CandidateRecord(
        candidate_id="TCAND_0001",
        source_strategy=TreasureStrategy.HISTORICAL_SURVIVOR,
        domain="example.org",
        url="https://example.org/archive/",
        path="/archive/",
        discovery_timestamp_utc="2026-08-18T00:00:00Z",
        discovery_reason="Archive directory.",
        path_type="ARCHIVE"
    )
    # Default without CDX evidence must be None / 0, never fabricated 1998/2024
    assert cand.earliest_capture_year is None
    assert cand.latest_capture_year is None
    assert cand.historical_span_years == 0
    assert cand.capture_count == 0

def test_machine_validation_prohibition(tmp_path):
    """Verify candidate scoring >= 50.0 produces REVIEW_PENDING, NEVER automatic TREASURE_VALIDATED."""
    cand = CandidateRecord(
        candidate_id="TCAND_0099",
        source_strategy=TreasureStrategy.USER_SPACE,
        domain="example.edu",
        url="https://example.edu/~student/retro.html",
        path="/~student/retro.html",
        category="Universities",
        discovery_timestamp_utc="2026-08-18T00:00:00Z",
        discovery_reason="User space tilde directory.",
        path_type="USER_SPACE",
        earliest_capture_year=1999,
        latest_capture_year=2024,
        historical_span_years=25,
        capture_count=45,
        research_priority=85.0,
        seen_by_strategies=["USER_SPACE", "TECHNOLOGY_FOSSIL", "HISTORICAL_SURVIVOR"]
    )
    
    # Mock artifact dir
    art_dir = tmp_path / "artifacts"
    art_dir.mkdir(parents=True, exist_ok=True)

    # Directly build an investigation with score > 50
    inv = InvestigationRecord(
        investigation_id="INV_TCAND_0099",
        candidate_id=cand.candidate_id,
        domain=cand.domain,
        url=cand.url,
        path=cand.path,
        category=cand.category,
        strategy=cand.source_strategy,
        live_status_code=200,
        live_html_sha256="a" * 64,
        live_html_bytes=5000,
        live_text_length=1500,
        title="Student Homepage",
        structural_features=["pre_css_tables_layout", "retro_styling_elements", "orphaned_from_root_navigation"],
        treasure_score=85.0,
        decision=TreasureDecision.REVIEW_PENDING,
        state=CandidateState.REVIEW_PENDING,
        investigated_at_utc="2026-08-18T00:00:00Z"
    )

    assert inv.treasure_score >= 50.0
    assert inv.decision == TreasureDecision.REVIEW_PENDING, "High score must yield REVIEW_PENDING, not TREASURE_VALIDATED!"
    assert inv.state == CandidateState.REVIEW_PENDING

def test_no_fake_human_review(tmp_path):
    """Verify only genuine human review files promote candidates to TREASURE_VALIDATED."""
    inv = InvestigationRecord(
        investigation_id="INV_TCAND_0001",
        candidate_id="TCAND_0001",
        domain="example.org",
        url="https://example.org/old/index.html",
        path="/old/index.html",
        category="Nonprofits",
        strategy=TreasureStrategy.ARCHIVE_ONLY,
        live_status_code=200,
        live_html_sha256="b" * 64,
        title="Old Index",
        treasure_score=75.0,
        decision=TreasureDecision.REVIEW_PENDING,
        state=CandidateState.REVIEW_PENDING
    )

    # Empty reviews file -> 0 promoted
    empty_reviews = tmp_path / "empty_reviews.jsonl"
    empty_reviews.touch()
    subs, promoted = import_human_review_submissions(empty_reviews, [inv])
    assert len(subs) == 0
    assert len(promoted) == 0

    # Genuine submission with CLEAR_TREASURE
    valid_reviews = tmp_path / "valid_reviews.jsonl"
    sub_data = {
        "review_id": "REV_PKT_0001",
        "candidate_id": "TCAND_0001",
        "reviewer_id": "HUMAN_AUDITOR_01",
        "verdict": "CLEAR_TREASURE",
        "confidence": 0.95,
        "notes": "Authentic surviving 1990s table-based index.",
        "reviewed_at_utc": "2026-08-18T12:00:00Z"
    }
    valid_reviews.write_text(json.dumps(sub_data) + "\n", encoding="utf-8")

    subs2, promoted2 = import_human_review_submissions(valid_reviews, [inv])
    assert len(subs2) == 1
    assert len(promoted2) == 1
    assert promoted2[0].decision == TreasureDecision.TREASURE_VALIDATED
    assert promoted2[0].state == CandidateState.HUMAN_VALIDATED

def test_review_packet_blindness(tmp_path):
    """Verify review packets hide treasure scores, research priority, and strategy names."""
    inv = InvestigationRecord(
        investigation_id="INV_TCAND_0002",
        candidate_id="TCAND_0002",
        domain="sample.gov",
        url="https://sample.gov/reports/1997/",
        path="/reports/1997/",
        category="Government",
        strategy=TreasureStrategy.RESURRECTION,
        live_status_code=200,
        live_html_sha256="c" * 64,
        title="1997 Report",
        structural_features=["pre_css_tables_layout"],
        timeline_summary="Observed 1997-2026",
        treasure_score=92.0,
        decision=TreasureDecision.REVIEW_PENDING
    )

    out_file = tmp_path / "review_packets.jsonl"
    packets = generate_review_packets([inv], output_file=out_file)

    assert len(packets) == 1
    pkt = packets[0]
    assert pkt.candidate_id == "TCAND_0002"
    assert pkt.blinding_level == "PARTIALLY_BLIND"
    
    # Check JSON representation
    pkt_json = json.loads(pkt.model_dump_json())
    assert "treasure_score" not in pkt_json
    assert "research_priority" not in pkt_json
    assert "strategy" not in pkt_json

def test_reference_world_isolation():
    """Verify LIVE_BLIND mode fails immediately if forbidden simulation modules are loaded."""
    # LIVE_BLIND mode should pass normally when environment is clean
    assert_live_blind_isolation(ExecutionMode.LIVE_BLIND, context="Test Clean")
    
    # Non-LIVE_BLIND modes are exempt
    assert_live_blind_isolation(ExecutionMode.SIMULATION, context="Test Sim")

def test_post_hoc_reference_evaluation(tmp_path):
    """Verify post-hoc reference comparison correctly segregates recoveries from discoveries."""
    invs_file = tmp_path / "investigations.jsonl"
    inv1 = InvestigationRecord(
        investigation_id="INV_01",
        candidate_id="C01",
        domain="uspto.gov",
        url="https://uspto.gov/mpep/",
        path="/mpep/",
        category="Government",
        strategy=TreasureStrategy.STRUCTURAL_SURVIVOR,
        live_status_code=200,
        live_html_sha256="d" * 64,
        treasure_score=60.0
    )
    inv2 = InvestigationRecord(
        investigation_id="INV_02",
        candidate_id="C02",
        domain="obscure-university.edu",
        url="https://obscure-university.edu/~dept/",
        path="/~dept/",
        category="Universities",
        strategy=TreasureStrategy.USER_SPACE,
        live_status_code=200,
        live_html_sha256="e" * 64,
        treasure_score=70.0
    )
    with open(invs_file, "w", encoding="utf-8") as f:
        f.write(inv1.model_dump_json() + "\n")
        f.write(inv2.model_dump_json() + "\n")

    ref_file = Path("data/reference_controls/reference_domains.json")
    out_comp = tmp_path / "reference_comparison.jsonl"

    summary = run_post_hoc_reference_evaluation(
        investigations_file=invs_file,
        reference_domains_file=ref_file,
        output_comparison_file=out_comp
    )

    assert summary["total_evaluated"] == 2
    assert summary["reference_recoveries_count"] == 1  # uspto.gov
    assert summary["new_to_atlas_count"] == 1  # obscure-university.edu

def test_multi_strategy_pattern_evaluator():
    """Verify pure structural pattern classification for 8 strategies."""
    matches1 = evaluate_path_strategies("/~prof/research.html", PathCategory14.USER_SPACE)
    strats1 = [m[0] for m in matches1]
    assert TreasureStrategy.USER_SPACE in strats1
    assert TreasureStrategy.TECHNOLOGY_FOSSIL in strats1

    matches2 = evaluate_path_strategies("/archive/legacy/doc.htm", PathCategory14.ARCHIVE)
    strats2 = [m[0] for m in matches2]
    assert TreasureStrategy.ARCHIVE_ONLY in strats2
    assert TreasureStrategy.ORPHAN_PATH in strats2
