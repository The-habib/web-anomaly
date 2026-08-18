"""
Independent Statistical Engine for Project Atlas Phase 1.8.
Zero-trust mathematical computation of confusion matrices, rate ratios,
exact Fisher tests, sparse-event corrections, and bootstrap confidence intervals.
"""

import math
import random
from typing import Dict, List, Tuple, Any, Optional

def log_factorial(n: int) -> float:
    """Compute ln(n!)."""
    if n < 0:
        raise ValueError("Factorial undefined for negative numbers.")
    if n <= 1:
        return 0.0
    return sum(math.log(i) for i in range(2, n + 1))

def log_hypergeometric_prob(x: int, k: int, m: int, total: int) -> float:
    """
    Log-probability of drawing x successes in sample of size m from population of size total with k total successes.
    k: row 1 sum (a + b)
    m: col 1 sum (a + c)
    total: table sum (a + b + c + d)
    """
    return (
        log_factorial(k) - log_factorial(x) - log_factorial(k - x) +
        log_factorial(total - k) - log_factorial(m - x) - log_factorial(total - k - (m - x)) -
        (log_factorial(total) - log_factorial(m) - log_factorial(total - m))
    )

def compute_fisher_exact(table: List[List[int]]) -> Dict[str, float]:
    """
    Compute one-sided (greater), one-sided (less), and two-sided Fisher's exact test p-values.
    table = [[a, b], [c, d]]
    """
    a, b = table[0]
    c, d = table[1]
    n = a + b + c + d
    k = a + b  # row 1 sum
    m = a + c  # col 1 sum

    min_x = max(0, k + m - n)
    max_x = min(k, m)

    # Observed probability
    obs_log_prob = log_hypergeometric_prob(a, k, m, n)
    obs_prob = math.exp(obs_log_prob)

    p_greater = 0.0
    p_less = 0.0
    p_two_tailed = 0.0

    for x in range(min_x, max_x + 1):
        log_p_x = log_hypergeometric_prob(x, k, m, n)
        p_x = math.exp(log_p_x)
        if x >= a:
            p_greater += p_x
        if x <= a:
            p_less += p_x
        if p_x <= obs_prob + 1e-12:
            p_two_tailed += p_x

    return {
        "p_value_two_sided": min(1.0, max(0.0, p_two_tailed)),
        "p_value_greater": min(1.0, max(0.0, p_greater)),
        "p_value_less": min(1.0, max(0.0, p_less)),
        "observed_table_prob": obs_prob
    }

def compute_haldane_anscombe_rate_ratio(
    d_events: int,
    d_exposure: float,
    u_events: int,
    u_exposure: float,
    correction: float = 0.5,
    confidence_level: float = 0.95
) -> Dict[str, Any]:
    """
    Compute rate ratio with Haldane-Anscombe continuity correction for zero cells.
    """
    d_rate_adj = (d_events + correction) / (d_exposure + correction)
    u_rate_adj = (u_events + correction) / (u_exposure + correction)
    rr = d_rate_adj / u_rate_adj

    # Standard error of ln(RR) using delta method with corrected cell counts
    # SE(ln(RR)) ≈ sqrt(1/(d_events + c) + 1/(u_events + c))
    se_ln_rr = math.sqrt((1.0 / (d_events + correction)) + (1.0 / (u_events + correction)))
    z = 1.959963984540054  # 95% CI standard normal quantile
    if confidence_level == 0.99:
        z = 2.5758293035489004
    elif confidence_level == 0.90:
        z = 1.6448536269514722

    ci_lower = math.exp(math.log(rr) - z * se_ln_rr)
    ci_upper = math.exp(math.log(rr) + z * se_ln_rr)

    # Sanity check: point estimate must strictly lie inside CI
    is_ci_valid = (ci_lower <= rr <= ci_upper) and (ci_lower > 0)

    return {
        "rate_ratio": round(rr, 4),
        "ci_lower": round(ci_lower, 4),
        "ci_upper": round(ci_upper, 4),
        "ci_95": [round(ci_lower, 4), round(ci_upper, 4)],
        "se_ln_rr": round(se_ln_rr, 4),
        "d_rate_adjusted": round(d_rate_adj, 6),
        "u_rate_adjusted": round(u_rate_adj, 6),
        "correction_applied": correction,
        "is_ci_valid": is_ci_valid
    }

def compute_exact_poisson_rate_ratio_test(
    d_events: int,
    d_exposure: float,
    u_events: int,
    u_exposure: float
) -> Dict[str, Any]:
    """
    Exact conditional Poisson rate test (binomial model on exposure ratio).
    Under H0 (rates equal), the number of events in D given total events K follows Binomial(K, pi0),
    where pi0 = d_exposure / (d_exposure + u_exposure).
    """
    total_events = d_events + u_events
    if total_events == 0:
        return {
            "p_value_one_sided": 1.0,
            "p_value_two_sided": 1.0,
            "exposure_ratio": round(d_exposure / max(u_exposure, 1e-9), 4),
            "expected_proportion": 0.5
        }

    pi0 = d_exposure / (d_exposure + u_exposure)

    # Binomial probability P(X = x | K, pi0)
    def binom_pmf(x: int, n: int, p: float) -> float:
        if x < 0 or x > n:
            return 0.0
        log_prob = log_factorial(n) - log_factorial(x) - log_factorial(n - x) + x * math.log(p) + (n - x) * math.log(1.0 - p)
        return math.exp(log_prob)

    obs_p = binom_pmf(d_events, total_events, pi0)
    p_greater = sum(binom_pmf(x, total_events, pi0) for x in range(d_events, total_events + 1))
    p_two_sided = sum(binom_pmf(x, total_events, pi0) for x in range(0, total_events + 1) if binom_pmf(x, total_events, pi0) <= obs_p + 1e-12)

    return {
        "p_value_greater": round(min(1.0, p_greater), 4),
        "p_value_two_sided": round(min(1.0, p_two_sided), 4),
        "exposure_proportion_pi0": round(pi0, 4),
        "total_events": total_events
    }

def compute_bootstrap_yield_difference(
    d_results: List[Dict[str, Any]],
    u_results: List[Dict[str, Any]],
    n_resamples: int = 10000,
    seed: int = 42
) -> Dict[str, Any]:
    """
    Empirical bootstrap for discovery yield difference (per 1,000 retrievals) and domain discovery rates.
    """
    rng = random.Random(seed)
    n_d = len(d_results)
    n_u = len(u_results)

    yield_diffs = []
    domain_rate_diffs = []

    for _ in range(n_resamples):
        sample_d = [rng.choice(d_results) for _ in range(n_d)]
        sample_u = [rng.choice(u_results) for _ in range(n_u)]

        d_disc = sum(1 for r in sample_d if r.get("validated_discovery", False))
        u_disc = sum(1 for r in sample_u if r.get("validated_discovery", False))

        d_ret = sum(r.get("deep_retrievals_attempted", 0) for r in sample_d)
        u_ret = sum(r.get("deep_retrievals_attempted", 0) for r in sample_u)

        d_yield_1k = (d_disc / max(d_ret, 1)) * 1000.0
        u_yield_1k = (u_disc / max(u_ret, 1)) * 1000.0
        yield_diffs.append(d_yield_1k - u_yield_1k)

        d_dom_rate = (d_disc / n_d) * 100.0
        u_dom_rate = (u_disc / n_u) * 100.0
        domain_rate_diffs.append(d_dom_rate - u_dom_rate)

    yield_diffs.sort()
    domain_rate_diffs.sort()

    lower_idx = int(0.025 * n_resamples)
    upper_idx = int(0.975 * n_resamples)

    return {
        "n_resamples": n_resamples,
        "yield_1k_diff_mean": round(float(sum(yield_diffs) / n_resamples), 4),
        "yield_1k_diff_ci_95": [round(yield_diffs[lower_idx], 4), round(yield_diffs[upper_idx], 4)],
        "domain_rate_diff_mean": round(float(sum(domain_rate_diffs) / n_resamples), 4),
        "domain_rate_diff_ci_95": [round(domain_rate_diffs[lower_idx], 4), round(domain_rate_diffs[upper_idx], 4)]
    }

def compute_classification_metrics(tp: int, fp: int, tn: int, fn: int) -> Dict[str, Any]:
    """Compute confusion matrix and performance statistics."""
    total = tp + fp + tn + fn
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0
    accuracy = (tp + tn) / total if total > 0 else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    return {
        "TP": tp,
        "FP": fp,
        "TN": tn,
        "FN": fn,
        "total": total,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "specificity": round(specificity, 4),
        "accuracy": round(accuracy, 4),
        "f1_score": round(f1, 4)
    }
