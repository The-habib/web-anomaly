"""
Permanent Test Suite for Mathematical and Statistical Engine Sanity in Project Atlas.
"""

import math
import pytest
from atlas.research.independent_stats import (
    compute_fisher_exact,
    compute_haldane_anscombe_rate_ratio,
    compute_exact_poisson_rate_ratio_test,
    compute_bootstrap_yield_difference,
    compute_classification_metrics
)

def test_fisher_exact_known_values():
    """Test Fisher Exact calculation on standard contingency tables."""
    # 2x2 table: [[2, 1468], [0, 841]]
    res = compute_fisher_exact([[2, 1468], [0, 841]])
    assert 0.0 <= res["p_value_two_sided"] <= 1.0
    assert 0.0 <= res["p_value_greater"] <= 1.0
    assert round(res["p_value_two_sided"], 4) == 0.5368

    # Symmetric table with zero difference
    res_sym = compute_fisher_exact([[10, 90], [10, 90]])
    assert res_sym["p_value_two_sided"] == 1.0

def test_haldane_anscombe_zero_cell_handling():
    """Verify Haldane-Anscombe rate ratio properly handles zero control cells and maintains CI sanity."""
    ha = compute_haldane_anscombe_rate_ratio(
        d_events=2,
        d_exposure=1470,
        u_events=0,
        u_exposure=841,
        correction=0.5
    )
    # Point estimate must strictly lie inside confidence interval
    assert ha["is_ci_valid"] is True
    assert ha["ci_lower"] < ha["rate_ratio"] < ha["ci_upper"]
    assert ha["rate_ratio"] > 1.0
    assert ha["ci_lower"] > 0.0

def test_exact_poisson_rate_test():
    """Verify exact conditional Poisson test logic."""
    poisson_res = compute_exact_poisson_rate_ratio_test(
        d_events=2,
        d_exposure=1470,
        u_events=0,
        u_exposure=841
    )
    assert 0.0 <= poisson_res["p_value_greater"] <= 1.0
    assert 0.0 <= poisson_res["p_value_two_sided"] <= 1.0
    assert poisson_res["total_events"] == 2

def test_bootstrap_yield_difference():
    """Verify empirical bootstrap convergence and bound ordering."""
    d_mock = [{"validated_discovery": True, "deep_retrievals_attempted": 15}] * 2 + \
             [{"validated_discovery": False, "deep_retrievals_attempted": 15}] * 98
    u_mock = [{"validated_discovery": False, "deep_retrievals_attempted": 8}] * 100

    boot = compute_bootstrap_yield_difference(d_mock, u_mock, n_resamples=500, seed=42)
    assert boot["yield_1k_diff_ci_95"][0] <= boot["yield_1k_diff_mean"] <= boot["yield_1k_diff_ci_95"][1]
    assert boot["domain_rate_diff_ci_95"][0] <= boot["domain_rate_diff_mean"] <= boot["domain_rate_diff_ci_95"][1]

def test_classification_metrics_computation():
    """Verify confusion matrix derived statistics."""
    metrics = compute_classification_metrics(tp=10, fp=2, tn=80, fn=8)
    assert metrics["precision"] == round(10 / 12, 4)
    assert metrics["recall"] == round(10 / 18, 4)
    assert metrics["specificity"] == round(80 / 82, 4)
    assert metrics["accuracy"] == round(90 / 100, 4)
    assert 0.0 <= metrics["f1_score"] <= 1.0
