"""
Permanent Test Suite for Project Atlas Phase 1.8 Audit, Arm Design, and Integrity Gate.
"""

import json
from pathlib import Path
import pytest

from atlas.research.release_gate_phase1_8 import run_phase1_8_release_check
from atlas.research.audit_phase1_8 import (
    audit_dataset_inventory,
    run_zero_trust_reconstruction,
    audit_arm_design_and_balance,
    audit_realized_budgets,
    audit_thunix_lineage,
    audit_discovery_validation,
    audit_human_review_and_holdout,
    audit_resource_and_costs
)

DATA_DIR = Path("data/phase1_7")
AUDIT_DIR = Path("audit/phase1_8")

def test_phase1_8_dataset_inventory():
    """Verify all 12 datasets pass row count and cryptographic hash checks."""
    inv = audit_dataset_inventory(DATA_DIR, AUDIT_DIR)
    assert len(inv) == 12
    for filename, info in inv.items():
        assert info["integrity_status"] == "VALID", f"Dataset {filename} integrity check failed: {info}"
        assert info["actual_rows"] == info["expected_rows"]
        assert info["duplicate_rows"] == 0
        assert info["malformed_entries"] == 0
        assert len(info["sha256"]) == 64

def test_phase1_8_zero_trust_reconstruction():
    """Verify zero-trust reconstruction of population, holdout, eligible, and study arms."""
    recon = run_zero_trust_reconstruction(DATA_DIR, AUDIT_DIR)
    assert recon["is_reconstruction_perfect"] is True
    assert recon["population_total"] == 1000
    assert recon["holdout_total"] == 200
    assert recon["eligible_pool_total"] == 800
    assert recon["arm_u_domains"] == 100
    assert recon["arm_d_domains"] == 100
    assert recon["overlaps"]["u_holdout_overlap_count"] == 0
    assert recon["overlaps"]["d_holdout_overlap_count"] == 0
    assert recon["overlaps"]["u_d_overlap_count"] == 0
    assert recon["retrieval_accounting"]["uniform_retrievals"] == 841
    assert recon["retrieval_accounting"]["density_retrievals"] == 1470
    assert recon["discovery_accounting"]["uniform_discoveries"] == 0
    assert recon["discovery_accounting"]["density_discoveries"] == 2

def test_phase1_8_arm_design_audit():
    """Verify arm design is classified as TAIL_SELECTION_VS_REMAINDER_CONTROL."""
    balance = audit_arm_design_and_balance(DATA_DIR, AUDIT_DIR)
    assert balance["design_classification"] == "TAIL_SELECTION_VS_REMAINDER_CONTROL"
    assert balance["category_balance"]["is_category_distribution_identical"] is True
    assert balance["density_metrics_comparison"]["d_raw"]["density_mean"] > balance["density_metrics_comparison"]["d_raw"]["uniform_mean"]

def test_phase1_8_realized_budgets():
    """Verify realized budget forensics and root cause accounting."""
    budgets = audit_realized_budgets(DATA_DIR, AUDIT_DIR)
    assert budgets["protocol_cap_per_domain"] == 15
    assert budgets["uniform_arm"]["realized_retrievals_total"] == 841
    assert budgets["density_arm"]["realized_retrievals_total"] == 1470
    assert budgets["uniform_arm"]["domains_reaching_15_cap"] == 50
    assert budgets["density_arm"]["domains_reaching_15_cap"] == 98

def test_phase1_8_thunix_lineage():
    """Verify thunix.net was in Holdout cohort and deconstruct the script fallback artifact."""
    thunix = audit_thunix_lineage(DATA_DIR, AUDIT_DIR)
    assert thunix["phase1_7_allocation"]["is_in_holdout_cohort"] is True
    assert thunix["phase1_7_allocation"]["is_in_study_arms"] is False
    assert thunix["phase1_7_actual_discoveries"] == ["gnu.org", "tilde.club"]

def test_phase1_8_discovery_validation():
    """Verify raw evidence HTML, hashes, scores, and zero reference contamination."""
    disc = audit_discovery_validation(DATA_DIR, AUDIT_DIR)
    assert disc["total_validated_discoveries"] == 2
    for d in disc["discoveries"]:
        assert d["evidence_file_exists"] is True
        assert len(d["sha256"]) == 64
        assert d["deep_score"] == 55.0
        assert d["human_verdict"] == "CLEAR_ANOMALY"
    assert disc["reference_contamination_check"]["contamination_status"] == "NONE"

def test_phase1_8_release_gate():
    """Verify Phase 1.8 Release Gate passes all 14 criteria."""
    passed, report = run_phase1_8_release_check()
    assert passed is True
    assert report["scientific_release"] == "APPROVED_FOR_PHASE_2"
    assert report["passed_checks_count"] == 14
    assert report["total_checks_count"] == 14
    for check_name, status in report["checks"].items():
        assert status == "PASS", f"Check {check_name} failed: {report['details'].get(check_name)}"
