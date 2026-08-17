# Project Atlas — Phase 1 Human Review Reconciliation Report

**Audit Phase**: `Phase 1.1 Independent Scientific Audit`  
**Dataset Audited**: `data/human_reviews.jsonl` (N=23)  
**Corpus Source**: `data/scan_results.jsonl` (N=1,000)  
**Reconciliation Artifact**: `audit/phase1_1/REVIEW_RECONCILIATION.json`

---

## 1. The "50 vs 23" Review Sample Discrepancy

### Question Investigated:
*Why did the previous narrative summary describe a 50-domain review cohort while `data/human_reviews.jsonl` contains exactly 23 persisted reviews?*

### Root Cause Analysis:
In `atlas/phase1/review.py` (`conduct_stratified_human_review`), the sampling procedure was designed to select up to 10 domains from each of five strata:
1. **High Scoring** ($\ge 4$): `rng.sample(high_score, min(10, len(high_score)))`
2. **Medium Scoring** ($2-3$): `rng.sample(med_score, min(10, len(med_score)))`
3. **Near Misses** ($1$): `rng.sample(near_miss, min(10, len(near_miss)))`
4. **Zero-Score Baseline** ($0$): `rng.sample(zero_score, min(10, len(zero_score)))`
5. **Random Population**: `rng.sample(remaining, min(10, len(remaining)))`

Across the 1,000 scored domains, the actual score distribution was:
- **Score 4**: 2 domains (`tilde.town`, `tilde.club`)
- **Score 2**: 1 domain (`cmu.edu`)
- **Score 1 or 3**: 0 domains
- **Score 0**: 997 domains

Consequently:
- High Score stratum: yielded $2$ domains (all available)
- Med Score stratum: yielded $1$ domain (all available)
- Near Miss stratum: yielded $0$ domains
- Zero-Score stratum: yielded $10$ domains
- Random stratum: yielded $10$ domains
- **Actual Persisted Sample Total**: $2 + 1 + 0 + 10 + 10 = \mathbf{23}$ **domains**.

### The Reporting Discrepancy:
The function argument defaulted to `sample_size=50`, and report generator templates in `atlas/phase1/report.py` embedded fallback strings such as `{val.get('sample_size', 50)}`, causing human-facing report text to reference 50 planned reviews rather than the 23 actual completed reviews.

---

## 2. Independent Verdict Census

Independently counted from `data/human_reviews.jsonl`:

| Controlled Verdict | Actual Count | Share in Sample (%) | Model Scores in Cohort |
| :--- | :---: | :---: | :---: |
| **`CLEAR_ANOMALY`** | **0** | 0.0% | None |
| **`POTENTIAL_ANOMALY`** | **2** | 8.7% | `tilde.town` (4), `tilde.club` (4) |
| **`ORDINARY`** | **20** | 87.0% | `cmu.edu` (2), 19 baseline zero-score domains |
| **`FALSE_NEGATIVE_CANDIDATE`** | **1** | 4.3% | `textfiles.com` (0) |
| **`FALSE_POSITIVE`** | **0** | 0.0% | None |
| **`INSUFFICIENT_EVIDENCE`** | **0** | 0.0% | None |
| **TOTAL** | **23** | **100.0%** | - |

---

## 3. False-Positive Rate Denominator Clarification

The Phase 1 summary reported a `0.0% false-positive rate`. The independent audit establishes the exact mathematical meaning:
- **Denominator A (All Reviewed Domains, N=23)**: $\frac{0 \text{ FP}}{23 \text{ reviewed}} = 0.0\%$.
- **Denominator B (Model-Positive Reviewed Candidates, N=3)**: $\frac{0 \text{ FP}}{3 \text{ candidates}} = 0.0\%$.

### Scientific Finding:
While mathematically zero false positives were recorded in both denominators, **only 3 candidate domains were generated across the entire 1,000-domain corpus**. A sample of $N=3$ model-positive domains is statistically small; the 0.0% metric reflects strict conservative scoring thresholds rather than an empirically broad validation across thousands of positive discoveries.
