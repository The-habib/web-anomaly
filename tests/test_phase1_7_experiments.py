"""
Unit & Integration Tests for Project Atlas — Phase 1.7 Path Density Validation Laboratory.
"""

import json
from pathlib import Path
import pytest

from atlas.density.models import PathCategory14, CoverageClassification, DensityTier
from atlas.density.path_classifier import classify_path_14
from atlas.density.normalizer import compute_shannon_entropy, compute_archive_coverage
from atlas.density.statistics import calculate_fisher_exact_p_value, evaluate_phase1_7_statistics
from atlas.research.release_gate_phase1_7 import run_phase1_7_release_check

DATA_DIR = Path("data/phase1_7")
REPORTS_DIR = Path("reports")

def test_population_survey_integrity():
    """Verify that population survey contains 1,000 records with valid metrics."""
    pop_file = DATA_DIR / "population_density.jsonl"
    assert pop_file.exists(), "population_density.jsonl must exist"
    
    count = 0
    with open(pop_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rec = json.loads(line)
                count += 1
                assert "domain" in rec
                assert "category" in rec
                assert "d_raw" in rec and rec["d_raw"] >= 0
                assert "d_year" in rec and rec["d_year"] >= 0.0
                assert "d_capture" in rec and rec["d_capture"] >= 0.0
                assert "d_span" in rec and rec["d_span"] >= 0
                assert "d_user" in rec and rec["d_user"] >= 0
                assert "d_legacy" in rec and rec["d_legacy"] >= 0
                assert "d_diversity" in rec and rec["d_diversity"] >= 0.0
                assert "d_content" in rec and rec["d_content"] >= 0
    assert count == 1000, f"Expected 1,000 population records, got {count}"

def test_path_classifier_14_categories():
    """Verify deterministic 14-category path classification."""
    test_cases = [
        ("/", PathCategory14.ROOT),
        ("/blog/2020/01/post", PathCategory14.BLOG),
        ("/docs/api/v1", PathCategory14.DOCS),
        ("/personal/index.html", PathCategory14.PERSONAL),
        ("/~alice/homepage.html", PathCategory14.USER_SPACE),
        ("/users/bob/profile", PathCategory14.USER_SPACE),
        ("/archive/old_site", PathCategory14.ARCHIVE),
        ("/legacy/v1", PathCategory14.LEGACY),
        ("/software/tools/cli.tar.gz", PathCategory14.SOFTWARE),
        ("/projects/atlas", PathCategory14.PROJECT),
        ("/files/downloads/data.zip", PathCategory14.FILES),
        ("/media/images/banner.png", PathCategory14.MEDIA),
        ("/papers/research2022.pdf", PathCategory14.RESEARCH),
        ("/directory/catalog/", PathCategory14.DIRECTORY),
        ("/some_random_page_here", PathCategory14.OTHER),
    ]
    for path, expected in test_cases:
        actual = classify_path_14(path)
        assert actual == expected, f"For path '{path}', expected {expected}, got {actual}"

def test_archive_coverage_normalizer():
    """Verify archive coverage window classification and entropy computation."""
    # Entropy test
    assert compute_shannon_entropy({"USER_SPACE": 5, "DOCS": 3, "BLOG": 2}) > 0.0
    assert compute_shannon_entropy({"ROOT": 10}) == 0.0
    
    # Overlapping coverage
    cov1 = compute_archive_coverage(
        domain="example.org",
        wayback_earliest=2000,
        wayback_latest=2015,
        wayback_count=100,
        cc_earliest=2008,
        cc_latest=2015,
        cc_count=50
    )
    assert cov1.coverage_classification == CoverageClassification.OVERLAPPING_COVERAGE

    # Source A only with coverage gap (pre-2008)
    cov2 = compute_archive_coverage(
        domain="oldsite.org",
        wayback_earliest=1998,
        wayback_latest=2005,
        wayback_count=20,
        cc_earliest=None,
        cc_latest=None,
        cc_count=0
    )
    assert cov2.coverage_classification == CoverageClassification.SOURCE_A_ONLY_WITH_COVERAGE_GAP

def test_sampling_and_arm_fairness():
    """Verify 200 holdout isolation, 100 Uniform vs 100 Density-Prioritized arms, and <= 15 retrieval cap."""
    holdout_file = DATA_DIR / "holdout_manifest.json"
    study_file = DATA_DIR / "study_assignment.jsonl"
    deep_res_file = DATA_DIR / "deep_results.jsonl"
    
    assert holdout_file.exists() and study_file.exists() and deep_res_file.exists()
    
    with open(holdout_file, "r", encoding="utf-8") as f:
        holdout = json.load(f)
    assert len(holdout["domains"]) == 200
    holdout_set = set(holdout["domains"])
    
    study_domains = []
    arm_u_count = 0
    arm_d_count = 0
    with open(study_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rec = json.loads(line)
                study_domains.append(rec["domain"])
                if rec["arm"] in ("UNIFORM", "UNIFORM_RANDOM"):
                    arm_u_count += 1
                elif rec["arm"] in ("DENSITY", "DENSITY_PRIORITIZED"):
                    arm_d_count += 1
                    
    assert len(study_domains) == 200
    assert arm_u_count == 100
    assert arm_d_count == 100
    
    # Check no overlap between holdout and study cohort
    overlap = holdout_set.intersection(set(study_domains))
    assert len(overlap) == 0, f"Found unexpected overlap between holdout and study cohort: {overlap}"
    
    # Check retrieval budget fairness
    with open(deep_res_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                res = json.loads(line)
                assert res["deep_retrievals_attempted"] <= 15, f"Domain {res['domain']} exceeded max retrieval cap: {res['deep_retrievals_attempted']}"

def test_statistical_engine_and_thunix_sensitivity():
    """Verify Fisher's exact calculation and Thunix sensitivity."""
    p_val = calculate_fisher_exact_p_value([[10, 2], [1, 11]])
    assert 0.0 <= p_val <= 1.0
    
    stats_file = DATA_DIR / "statistical_results.json"
    assert stats_file.exists()
    with open(stats_file, "r", encoding="utf-8") as f:
        stats = json.load(f)
        
    assert stats["uniform_arm_domains"] == 100
    assert stats["density_arm_domains"] == 100
    assert "thunix_sensitivity" in stats
    assert "with_thunix" in stats["thunix_sensitivity"]
    assert "without_thunix" in stats["thunix_sensitivity"]
    assert stats["hypothesis_verdict"] in {"SUPPORTED", "PROMISING", "NOT_SUPPORTED", "THUNIX_SPECIFIC", "INCONCLUSIVE"}

def test_report_file_inventory():
    """Verify that all 15 Phase 1.7 scientific reports exist and are non-empty."""
    required_reports = [
        "PHASE_1_7_PROTOCOL.md",
        "PHASE_1_7_RESULTS.md",
        "PATH_DENSITY_DISTRIBUTION.md",
        "DENSITY_DEFINITION_COMPARISON.md",
        "CATEGORY_CONFOUND_ANALYSIS.md",
        "ARCHIVE_COVERAGE_NORMALIZATION.md",
        "UNIFORM_VS_DENSITY.md",
        "HOLDOUT_RESULTS.md",
        "THUNIX_SENSITIVITY.md",
        "PATH_DIVERSITY_ANALYSIS.md",
        "COST_EFFECTIVENESS.md",
        "REFERENCE_CONTROL_RESULTS.md",
        "FALSE_POSITIVES.md",
        "FALSE_NEGATIVES.md",
        "PHASE_1_7_LIMITATIONS.md",
        "PHASE_1_8_PRIORITIZATION_ENGINE_PROPOSAL.md"
    ]
    for rep in required_reports:
        rep_path = REPORTS_DIR / rep
        assert rep_path.exists(), f"Report {rep} must exist"
        assert rep_path.stat().st_size > 100, f"Report {rep} must have substantive content"

def test_phase1_7_release_gate():
    """Verify that all 12 Phase 1.7 scientific release gate criteria pass."""
    is_approved, gate_results = run_phase1_7_release_check(data_dir=DATA_DIR, reports_dir=REPORTS_DIR)
    checks = gate_results.get("checks", gate_results)
    assert len(checks) == 12
    for crit, res in checks.items():
        assert res == "PASS", f"Release gate criterion {crit} failed with result: {res}"
    assert is_approved is True, "Phase 1.7 scientific release gate must be APPROVED"
