"""
Unit & Reconciliation Tests for Project Atlas — Phase 1.6 Scientific Audit.
"""

import json
from pathlib import Path
import pytest
from atlas.research.release_gate_phase1_6 import run_phase1_6_release_check

AUDIT_DIR = Path("audit/phase1_6")
DATA_DIR = Path("data/phase1_5")
REPORTS_DIR = Path("reports")

def test_dataset_inventory_integrity():
    """Verify that dataset inventory contains all 11 Phase 1.5 files."""
    inv_file = AUDIT_DIR / "dataset_inventory.json"
    assert inv_file.exists(), "dataset_inventory.json must exist"
    with open(inv_file, "r", encoding="utf-8") as f:
        inventory = json.load(f)
    assert len(inventory) == 11
    for path, meta in inventory.items():
        assert Path(path).exists()
        assert meta["size_bytes"] >= 0
        assert len(meta["sha256"]) == 64

def test_root_candidates_reconciliation():
    """Verify exact root candidates list (fltk.org, haproxy.org, toastytech.com)."""
    rc_file = AUDIT_DIR / "root_candidates.jsonl"
    assert rc_file.exists()
    root_cands = []
    with open(rc_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                root_cands.append(json.loads(line))
    assert len(root_cands) == 3
    domains = {c["domain"] for c in root_cands}
    assert domains == {"fltk.org", "haproxy.org", "toastytech.com"}
    for c in root_cands:
        assert c["root_score"] >= 50.0
        assert c["root_classification"] == "CANDIDATE_ANOMALY"

def test_deep_candidates_reconciliation():
    """Verify exact deep candidates list (fltk.org, haproxy.org, toastytech.com, thunix.net)."""
    dc_file = AUDIT_DIR / "deep_candidates.jsonl"
    assert dc_file.exists()
    deep_cands = []
    with open(dc_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                deep_cands.append(json.loads(line))
    assert len(deep_cands) == 4
    domains = {c["domain"] for c in deep_cands}
    assert domains == {"fltk.org", "haproxy.org", "toastytech.com", "thunix.net"}

def test_incremental_candidates_and_discoveries():
    """Verify exact incremental candidate and validated discovery identity (thunix.net/~cslug)."""
    inc_file = AUDIT_DIR / "incremental_candidates.jsonl"
    val_file = AUDIT_DIR / "validated_discoveries.jsonl"
    assert inc_file.exists() and val_file.exists()

    inc_cands = [json.loads(l) for l in open(inc_file, "r", encoding="utf-8") if l.strip()]
    val_discs = [json.loads(l) for l in open(val_file, "r", encoding="utf-8") if l.strip()]

    assert len(inc_cands) == 1
    assert inc_cands[0]["domain"] == "thunix.net"
    assert inc_cands[0]["best_path"] == "/~cslug"
    assert inc_cands[0]["root_score"] == 35.0
    assert inc_cands[0]["deep_score"] == 55.0

    assert len(val_discs) == 1
    assert val_discs[0]["domain"] == "thunix.net"
    assert val_discs[0]["discovery_path"] == "/~cslug"
    assert val_discs[0]["human_verdict"] == "CLEAR_ANOMALY"
    assert Path(val_discs[0]["evidence_artifact"]).exists()

def test_reference_relics_separation():
    """Verify 7 reference relics are isolated from empirical yield."""
    ref_file = AUDIT_DIR / "reference_recoveries.jsonl"
    assert ref_file.exists()
    refs = [json.loads(l) for l in open(ref_file, "r", encoding="utf-8") if l.strip()]
    assert len(refs) == 7

    deep_recovered = [r for r in refs if r["recovery_status"] == "RECOVERED_BY_DEEP"]
    assert len(deep_recovered) == 4
    assert {r["domain"] for r in deep_recovered} == {"spacejam.com", "zombo.com", "catb.org", "textfiles.com"}

    root_recovered = [r for r in refs if r["root_found"]]
    assert len(root_recovered) == 0

def test_resource_accounting_consistency():
    """Verify resource accounting metrics."""
    res_file = AUDIT_DIR / "resource_reconciliation.json"
    assert res_file.exists()
    with open(res_file, "r", encoding="utf-8") as f:
        res = json.load(f)

    assert res["candidate_paths"]["true_canonical_candidate_paths"] == 16174
    assert res["http_requests"]["total_http_requests"] == 3134
    assert res["raw_artifacts"]["frozen_html_payloads_total"] == 2760
    assert res["retrieval_cap_distribution"]["domains_at_cap"] == 178
    assert res["retrieval_cap_distribution"]["domains_below_cap"] == 25
    assert res["retrieval_cap_distribution"]["domains_with_zero_retrievals"] == 97

def test_prioritizer_blindness():
    """Verify candidate prioritizer is blind to anomaly score and ground truth labels."""
    from atlas.deep.prioritizer import calculate_retrieval_priority
    from atlas.deep.models import PathCandidate, PathCategory

    cand = PathCandidate(
        domain="example.org",
        candidate_url="https://example.org/~user/",
        path="/~user/",
        path_category=PathCategory.ACADEMIC_USER_SPACE,
        discovery_source="WAYBACK_CDX",
        first_observed_year=1995,
        last_observed_year=2026,
        capture_count=10
    )
    score = calculate_retrieval_priority(cand)
    assert 0.0 <= score <= 100.0
    # Academic user space (35) + <=1996 (40) + slash_count <=2 (15) + WAYBACK_CDX (10) = 100.0
    assert score == 100.0

def test_release_gate_passes():
    """Verify full Phase 1.6 release gate audit returns APPROVED."""
    passed, report = run_phase1_6_release_check()
    assert passed is True
    assert report["scientific_release"] == "APPROVED"
    assert report["audit_classification"] == "AUDIT_VALID_WITH_CORRECTIONS"
    assert all(status == "PASS" for status in report["checks"].values())
