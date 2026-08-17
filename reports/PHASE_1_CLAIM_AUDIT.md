# Project Atlas — Phase 1 Claim-by-Claim Scientific Audit

**Audit Phase**: `Phase 1.1 Independent Scientific Audit`  
**Date**: 2026-08-17  

---

## 1. Executive Summary

This document evaluates every major claim made in the Phase 1 documentation against underlying raw evidence, independent recomputations, and verified statistical calculations.

---

## 2. Claim-by-Claim Evaluation Matrix

| # | Major Claim in Phase 1 Report | Evidence Source | Reproducible? | Supported? | Overstated? | Audit Status | Audit Notes / Technical Correction |
|---|---|---|:---:|:---:|:---:|:---:|---|
| **C1** | *"1,000 public domains processed blindly."* | `data/seed_corpus.csv`, `experiments/0002/evidence/raw/` | Yes | Partially | Yes | **PARTIALLY_SUPPORTED** | 901 domains were real curated domains; 99 were procedurally generated synthetic pattern domains (`corp-001.com`, etc.) used to fill quotas. |
| **C2** | *"Blind evidence collection before scoring."* | `atlas/phase1/collector.py`, timestamps | Yes | Yes | No | **SUPPORTED** | Confirmed: All live HTML and CDX timelines were written to disk and frozen with SHA-256 manifests before scoring ran. |
| **C3** | *"Evidence frozen with SHA-256 manifests."* | `frozen_manifest.json` | Yes | Yes | No | **SUPPORTED** | 3,332 artifact files (121.99 MB) 100% matched their SHA-256 digests. |
| **C4** | *"3 Candidates discovered (Score $\ge 2$)."* | `data/findings.jsonl`, `data/scan_results.jsonl` | Yes | Yes | No | **SUPPORTED** | `tilde.town` (4), `tilde.club` (4), `cmu.edu` (2). Replayed 1000/1000 identically. |
| **C5** | *"Stratified sample of 50 domains reviewed."* | `data/human_reviews.jsonl` | No | No | Yes | **CONTRADICTED** | Only **23 domains** were persisted in `data/human_reviews.jsonl`. Sampling quota yielded $2+1+0+10+10=23$. |
| **C6** | *"0.0% sample false-positive rate."* | `data/human_reviews.jsonl` | Yes | Partially | Yes | **PARTIALLY_SUPPORTED** | Mathematically 0 FPs in review cohort, but model-positive candidate sample was only $N=3$. Needs clear denominator qualification. |
| **C7** | *"0.88 (High) Confidence in discovery."* | `atlas/scoring/scorer.py` | Yes | Partially | Yes | **PARTIALLY_SUPPORTED** | Internal evidence heuristic score, not a statistically calibrated probability. Must be stated as heuristic. |
| **C8** | *"Strong positive correlation ($r = 0.82$)."* | Report text | No | No | Yes | **UNSUPPORTED** | Calculated on a tiny candidate subset without formal statistical significance testing. Withdrawn from formal claims. |
| **C9** | *"tilde.town & tilde.club exhibit active `<marquee>` fossils."* | `rendered.html` | Yes | Yes | No | **SUPPORTED** | Verified: Active `<marquee>` tags render live dynamic server uptime and member links. Valid `POTENTIAL_ANOMALY`. |
| **C10** | *"cmu.edu 29-year footprint back to 1997."* | `timeline.json` | Yes | Partially | Yes | **PARTIALLY_SUPPORTED** | Calendar span is 29 years, but unobserved gap is 24 years (only 7 unique years). 404 in 2000 was misclassified as resurrection. |

---

## 3. Overall Claim Summary

- **Total Claims Audited**: 10
- **Supported**: 4 (40.0%)
- **Partially Supported (Requires Qualification)**: 4 (40.0%)
- **Contradicted (Discrepancy Found)**: 1 (10.0%)
- **Unsupported (Withdrawn)**: 1 (10.0%)
