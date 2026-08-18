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
from atlas.treasure.investigator import investigate_single_candidate, run_adaptive_investigations
from atlas.treasure.prior_art import evaluate_prior_art_status
from atlas.treasure.dossier import publish_treasures, build_treasure_title, determine_time_period
from atlas.treasure.release_gate import run_treasure_release_gate

DATA_DIR = Path("data/treasures")
REPORTS_DIR = Path("reports")

def test_multi_strategy_candidate_generation(tmp_path):
    """Verify 8 strategies generate valid candidate records."""
    out_file = tmp_path / "test_candidates.jsonl"
    candidates = generate_multi_strategy_candidates(limit_domains=10, seed=42, output_file=out_file)

    assert len(candidates) >= 5
    assert out_file.exists()

    strategies_found = set(c.source_strategy for c in candidates)
    assert len(strategies_found) >= 2

    for c in candidates:
        assert c.candidate_id.startswith("TCAND_")
        assert c.domain
        assert c.url.startswith("https://")
        assert 10.0 <= c.discovery_priority <= 100.0
        assert len(c.seen_by_strategies) >= 1

def test_candidate_deduplication_and_strategy_tracking(tmp_path):
    """Verify duplicate paths are merged with multiple strategies recorded."""
    out_file = tmp_path / "test_dedup_candidates.jsonl"
    candidates = generate_multi_strategy_candidates(limit_domains=15, seed=99, output_file=out_file)

    urls = [c.url for c in candidates]
    assert len(urls) == len(set(urls))  # No duplicate URLs

    multi_strat = [c for c in candidates if len(c.seen_by_strategies) > 1]
    assert len(multi_strat) > 0  # Cross-strategy corroboration verified

def test_prior_art_classification_modesty():
    """Verify prior art classifications are accurate and modest."""
    status1, note1 = evaluate_prior_art_status("spacejam.com", "/", "Space Jam", ["retro_styling_elements"])
    assert status1 == PriorArtStatus.WELL_DOCUMENTED

    status2, note2 = evaluate_prior_art_status("uspto.gov", "/web/offices/pac/mpep/", "MPEP", ["pre_css_tables_layout"])
    assert status2 == PriorArtStatus.DOCUMENTED

    status3, note3 = evaluate_prior_art_status("gwern.net", "/doc/rotten.com/library/", "Rotten Mirror", ["pre_css_tables_layout", "orphaned_from_root_navigation"])
    assert status3 == PriorArtStatus.OBSCURE
    assert "Atlas did not identify substantial" in note3

def test_time_period_grouping():
    """Verify accurate historical era assignment."""
    assert "1990–1995" in determine_time_period(1994)
    assert "1996–2000" in determine_time_period(1998)
    assert "2001–2005" in determine_time_period(2003)
    assert "2006–2010" in determine_time_period(2008)
    assert "2011+" in determine_time_period(2018)

def test_dossier_and_feed_generation(tmp_path):
    """Verify markdown dossiers and master feed generation."""
    inv_record = InvestigationRecord(
        investigation_id="INV_TCAND_0001",
        candidate_id="TCAND_0001",
        domain="gwern.net",
        url="https://gwern.net/doc/rotten.com/library/index.html",
        path="/doc/rotten.com/library/index.html",
        category="Personal/independent sites",
        strategy=TreasureStrategy.WEB_ODDITY,
        live_status_code=200,
        live_html_sha256="dd40378445238d5109447905a252675f55fcf88c2c2ba206ae59d2c0c38f2518",
        live_html_bytes=14520,
        live_text_length=4200,
        title="Rotten Library Mirror",
        structural_features=["pre_css_tables_layout", "retro_styling_elements", "orphaned_from_root_navigation"],
        timeline_summary="Continuity across 1999-2024.",
        earliest_year=1999,
        latest_year=2024,
        historical_span_years=25,
        is_linked_from_root=False,
        survival_state=SurvivalState.STILL_ACTIVE,
        prior_art=PriorArtStatus.OBSCURE,
        discovery_difficulty=DiscoveryDifficulty.VERY_HARD,
        treasure_score=85.0,
        decision=TreasureDecision.TREASURE_VALIDATED,
        human_explanation="Atlas discovered an authentic 1990s web preservation library mirror.",
        why_interesting="Preserves table-based layout without modern frontend frameworks.",
        why_search_misses_it="Buried deep in hierarchy without incoming links from homepage.",
        evidence_artifact_path=str(tmp_path / "gwern.net.html"),
        investigated_at_utc="2026-08-18T12:00:00Z"
    )

    out_dir = tmp_path / "treasures_data"
    rep_dir = tmp_path / "treasures_reports"
    treasures, lineages = publish_treasures([inv_record], output_dir=out_dir, reports_dir=rep_dir)

    assert len(treasures) == 1
    assert len(lineages) == 1

    t = treasures[0]
    assert t.treasure_id == "TREASURE_001"
    assert t.treasure_score == 85.0

    dossier_path = rep_dir / "treasures" / "TREASURE_001.md"
    assert dossier_path.exists()
    dossier_text = dossier_path.read_text(encoding="utf-8")
    assert "# TREASURE_001 —" in dossier_text
    assert "## What Atlas Found" in dossier_text
    assert "## Cryptographic Evidence" in dossier_text
    assert t.evidence_sha256 in dossier_text

    feed_path = rep_dir / "TREASURE_FEED.md"
    assert feed_path.exists()
    feed_text = feed_path.read_text(encoding="utf-8")
    assert "Live Archaeological Treasure Feed" in feed_text
    assert "TREASURE_001" in feed_text

def test_treasure_release_gate_runs():
    """Verify release gate function executes."""
    gate = run_treasure_release_gate()
    assert "checks" in gate
    assert gate["total_checks"] == 11
