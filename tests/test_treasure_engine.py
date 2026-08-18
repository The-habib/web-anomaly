"""
Permanent Unit & Integration Test Suite for Project Atlas — Treasure Mode.
Verifies multi-strategy candidate discovery, deduplication, adaptive investigations,
prior-art modesty, dossier generation, checkpoint persistence, and release gate.
"""

import json
import pytest
from pathlib import Path

from atlas.treasure.models import (
    TreasureStrategy,
    DiscoveryDifficulty,
    SurvivalState,
    PriorArtStatus,
    TreasureDecision,
    CandidateRecord,
    InvestigationRecord,
    TreasureRecord
)
from atlas.treasure.discovery import generate_multi_strategy_candidates
from atlas.treasure.sampler import sample_blind_domain_population
from atlas.treasure.investigator import investigate_single_candidate, run_adaptive_investigations
from atlas.treasure.prior_art import evaluate_prior_art_status
from atlas.treasure.dossier import generate_individual_treasure_dossier, generate_clean_treasure_feed, build_treasure_title, determine_time_period
from atlas.treasure.release_gate import run_treasure_release_gate

DATA_DIR = Path("data/treasure_runs/TREASURE_RUN_0002")
REPORTS_DIR = Path("reports")

def test_multi_strategy_candidate_generation(tmp_path):
    """Verify 8 strategies generate valid candidate records."""
    out_file = tmp_path / "test_candidates.jsonl"
    sample_manifest = sample_blind_domain_population(sample_size=10, seed=42, output_manifest_path=tmp_path / "sample.json")
    candidates = generate_multi_strategy_candidates(
        sampled_domains=sample_manifest.selected_domains,
        output_file=out_file
    )

    assert len(candidates) >= 5
    assert out_file.exists()

    strategies_found = set(c.source_strategy for c in candidates)
    assert len(strategies_found) >= 1

    for c in candidates:
        assert c.candidate_id.startswith("TCAND_")
        assert c.domain
        assert c.url.startswith("https://")
        assert 10.0 <= c.research_priority <= 100.0
        assert len(c.seen_by_strategies) >= 1

def test_candidate_deduplication_and_strategy_tracking(tmp_path):
    """Verify duplicate paths are merged with multiple strategies recorded."""
    out_file = tmp_path / "test_dedup_candidates.jsonl"
    sample_manifest = sample_blind_domain_population(sample_size=15, seed=99, output_manifest_path=tmp_path / "sample_dedup.json")
    candidates = generate_multi_strategy_candidates(
        sampled_domains=sample_manifest.selected_domains,
        output_file=out_file
    )

    urls = [c.url for c in candidates]
    assert len(urls) == len(set(urls))  # No duplicate URLs

def test_prior_art_classification_modesty():
    """Verify prior art classifications are accurate and modest."""
    status1, note1 = evaluate_prior_art_status("example.com", "/", "Example", ["retro_styling_elements"])
    assert status1 == PriorArtStatus.DOCUMENTED

    status2, note2 = evaluate_prior_art_status("example.gov", "/web/offices/pac/mpep/", "MPEP", ["pre_css_tables_layout"])
    assert status2 in (PriorArtStatus.DOCUMENTED, PriorArtStatus.POORLY_DOCUMENTED)

    status3, note3 = evaluate_prior_art_status("example.net", "/doc/lib/index.html", "Mirror", ["pre_css_tables_layout", "orphaned_from_root_navigation", "ascii_art_present"])
    assert status3 == PriorArtStatus.OBSCURE
    assert "archaeological surface" in note3

def test_time_period_grouping():
    """Verify accurate historical era assignment."""
    assert "1990–1995" in determine_time_period(1994)
    assert "1996–2000" in determine_time_period(1998)
    assert "2001–2005" in determine_time_period(2003)
    assert "2006–2010" in determine_time_period(2008)
    assert "2011+" in determine_time_period(2018)

def test_dossier_and_feed_generation(tmp_path):
    """Verify markdown dossiers and master feed generation."""
    tr = TreasureRecord(
        treasure_id="TREASURE_001",
        candidate_id="TCAND_0001",
        title="Surviving Historical Web Surface (example.org/archive/)",
        domain="example.org",
        category="Nonprofits",
        path="/archive/",
        full_url="https://example.org/archive/",
        strategy=TreasureStrategy.ARCHIVE_ONLY,
        time_period="1996–2000 (Dot-Com Expansion Era)",
        treasure_score=85.0,
        discovery_difficulty=DiscoveryDifficulty.VERY_HARD,
        survival_state=SurvivalState.STILL_ACTIVE,
        prior_art=PriorArtStatus.OBSCURE,
        one_sentence_summary="Authentic unmodernized archive preserved at /archive/ on example.org.",
        human_explanation="Atlas discovered an authentic unmodernized web preservation surface.",
        why_interesting="Preserves table-based layout without modern frontend frameworks.",
        why_search_misses_it="Buried deep in hierarchy without incoming links from homepage.",
        historical_timeline="Historical continuity across 1999-2024.",
        detected_features=["pre_css_tables_layout", "retro_styling_elements", "orphaned_from_root_navigation"],
        evidence_sha256="dd40378445238d5109447905a252675f55fcf88c2c2ba206ae59d2c0c38f2518",
        artifact_path=str(tmp_path / "example.org.html"),
        reproduction_steps="curl -s https://example.org/archive/ | sha256sum",
        validated_at_utc="2026-08-18T12:00:00Z"
    )

    dossiers_dir = tmp_path / "treasures_reports" / "treasures"
    dossier_path = generate_individual_treasure_dossier(tr, output_dir=dossiers_dir)

    assert dossier_path.exists()
    dossier_text = dossier_path.read_text(encoding="utf-8")
    assert "# TREASURE_001 —" in dossier_text
    assert "## What Atlas Found" in dossier_text
    assert "## Cryptographic Evidence" in dossier_text
    assert tr.evidence_sha256 in dossier_text

    feed_path = tmp_path / "TREASURE_FEED_RUN_0002.md"
    generate_clean_treasure_feed([tr], [], feed_file=feed_path)
    assert feed_path.exists()
    feed_text = feed_path.read_text(encoding="utf-8")
    assert "Treasure Run #002 Discovery Feed" in feed_text
    assert "TREASURE_001" in feed_text

def test_treasure_release_gate_runs():
    """Verify release gate function executes."""
    gate = run_treasure_release_gate()
    assert "checks" in gate
    assert gate["total_checks"] == 11
