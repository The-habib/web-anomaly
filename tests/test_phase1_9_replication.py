"""
Permanent Unit & Integration Test Suite for Phase 1.9 Controlled Replication.
Verifies matched-pair randomization balance, budget equality, domain-level statistics,
double-blind review, holdout isolation, and scientific release gate.
"""

import json
import pytest
from pathlib import Path

from atlas.replication.release_gate_phase1_9 import run_phase1_9_release_gate
from atlas.replication.statistics import (
    compute_newcombe_risk_difference_ci,
    compute_haldane_anscombe_rr
)

DATA_DIR = Path("data/phase1_9")
AUDIT_DIR = Path("audit/phase1_9")

def test_phase1_9_sample_and_matched_pair_balance():
    """Verify 200 domains, 100 matched pairs, and balanced baseline density."""
    pop_file = DATA_DIR / "population.jsonl"
    blocks_file = DATA_DIR / "blocks.jsonl"
    assignments_file = DATA_DIR / "assignments.jsonl"

    assert pop_file.exists()
    assert blocks_file.exists()
    assert assignments_file.exists()

    with open(pop_file, "r", encoding="utf-8") as f:
        pop = [json.loads(l) for l in f if l.strip()]
    with open(blocks_file, "r", encoding="utf-8") as f:
        blocks = [json.loads(l) for l in f if l.strip()]
    with open(assignments_file, "r", encoding="utf-8") as f:
        assignments = [json.loads(l) for l in f if l.strip()]

    assert len(pop) == 200
    assert len(blocks) == 100
    assert len(assignments) == 200

    t_assignments = [a for a in assignments if a["arm"] == "TREATMENT"]
    c_assignments = [a for a in assignments if a["arm"] == "CONTROL"]
    assert len(t_assignments) == 100
    assert len(c_assignments) == 100

    t_mean_d = sum(a["d_raw"] for a in t_assignments) / len(t_assignments)
    c_mean_d = sum(a["d_raw"] for a in c_assignments) / len(c_assignments)
    assert abs(t_mean_d - c_mean_d) < 5.0

def test_phase1_9_budget_and_slot_equality():
    """Verify strictly equal 10-slot retrieval budgets across both arms."""
    slots_file = DATA_DIR / "retrieval_slots.jsonl"
    assert slots_file.exists()

    with open(slots_file, "r", encoding="utf-8") as f:
        slots = [json.loads(l) for l in f if l.strip()]

    assert len(slots) == 2000
    t_slots = [s for s in slots if s["arm"] == "TREATMENT"]
    c_slots = [s for s in slots if s["arm"] == "CONTROL"]

    assert len(t_slots) == 1000
    assert len(c_slots) == 1000

def test_phase1_9_candidate_pool_independence():
    """Verify candidate pools are built for all 200 domains."""
    pools_file = DATA_DIR / "candidate_pools.jsonl"
    assert pools_file.exists()

    with open(pools_file, "r", encoding="utf-8") as f:
        pools = [json.loads(l) for l in f if l.strip()]

    assert len(pools) == 200
    for p in pools:
        assert "domain" in p
        assert "total_candidates_found" in p
        assert "has_full_exposure" in p

def test_phase1_9_blind_review_and_discoveries():
    """Verify blinded review dossiers and discovery validation."""
    rev_file = DATA_DIR / "human_reviews.jsonl"
    disc_file = DATA_DIR / "discoveries.jsonl"

    assert rev_file.exists()
    assert disc_file.exists()

    with open(rev_file, "r", encoding="utf-8") as f:
        revs = [json.loads(l) for l in f if l.strip()]
    with open(disc_file, "r", encoding="utf-8") as f:
        discs = [json.loads(l) for l in f if l.strip()]

    assert len(revs) >= 20
    assert len(discs) == 2

    # Discoveries in Phase 1.9 must belong to Treatment arm
    for d in discs:
        assert d["arm"] == "TREATMENT"
        assert d["anomaly_score"] >= 50.0

def test_phase1_9_domain_level_statistics_sanity():
    """Verify mathematical sanity of domain-level statistical estimators."""
    stats_file = DATA_DIR / "statistics.json"
    assert stats_file.exists()

    with open(stats_file, "r", encoding="utf-8") as f:
        st = json.load(f)

    assert st["primary_unit_of_analysis"] == "DOMAIN"
    assert st["verdict"] == "PROMISING_BUT_UNCONFIRMED"

    dom_stats = st["domain_level_primary"]
    assert dom_stats["treatment_discoveries"] == 2
    assert dom_stats["control_discoveries"] == 0
    assert dom_stats["risk_difference"] == 0.0200
    assert 0.0 <= dom_stats["fisher_exact_p_value_two_sided"] <= 1.0

    # Risk Difference Newcombe test
    rd, rd_low, rd_high = compute_newcombe_risk_difference_ci(2, 100, 0, 100)
    assert rd == 0.0200
    assert rd_low < 0.0 < rd_high  # CI crosses zero at N=200

    # Haldane-Anscombe test
    rr_ha, rr_low, rr_high = compute_haldane_anscombe_rr(2, 100, 0, 100)
    assert rr_ha == 5.0000

def test_phase1_9_holdout_isolation():
    """Verify 200 holdout domains are isolated."""
    holdout_file = DATA_DIR / "holdout.jsonl"
    assert holdout_file.exists()

    with open(holdout_file, "r", encoding="utf-8") as f:
        h = [json.loads(l) for l in f if l.strip()]

    assert len(h) == 200
    for hr in h:
        assert hr["cohort"] == "HOLDOUT_BASELINE"

def test_phase1_9_release_gate():
    """Verify all 14 criteria pass in Phase 1.9 release gate."""
    gate = run_phase1_9_release_gate()
    assert gate["all_passed"] is True
    assert gate["passed_checks"] == 14
    assert gate["total_checks"] == 14
    assert gate["decision"] == "APPROVED_FOR_PHASE_2_HEURISTIC_EXPLORATION"
