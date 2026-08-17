# Project Atlas — Formal Correction Notice (Phase 1.3 Benchmark Reconciliation)

**Document**: `reports/PHASE_1_3_CORRECTION_NOTICE.md`  
**Issued By**: Independent Scientific Audit Team (Phase 1.4)  
**Date**: 2026-08-17T21:35:00Z  
**Classification**: Formal Scientific Reclassification  

---

## 1. Statement of Correction

During the Phase 1.4 audit, an internal discrepancy was identified between `reports/BENCHMARK_V2_RESULTS.md` and the machine-readable dataset `data/benchmark_v2/evaluation.json`.

The investigation proved that:
1. The empirical live benchmark run produced **Accuracy: 66.67% (20/30), Precision: 50.00% (3/6), Recall: 30.00% (3/10), Specificity: 85.00% (17/20)**.
2. A subsequent automated test suite run executed in simulation mode and accidentally mutated `evaluation.json` and `predictions.jsonl` with an all-zero synthetic profile output (`Accuracy: 66.67%, Precision: 100%, Recall: 0%`).
3. The live dataset files in `data/benchmark_v2/` have been restored, reconciled, independently audited via `scripts/audit_benchmark_v2_independently.py`, and locked against test mutation via `tmp_path` test sandboxing.

---

## 2. Reconciled Metrics Summary

| Metric | Previously Stated in Report | Overwritten Test Artifact | Corrected Reconciled Ground Truth |
| :--- | :--- | :--- | :--- |
| **True Positives (TP)** | 2 | 0 | **3** (`toastytech.com`, `stallman.org`, `sdf.org`) |
| **True Negatives (TN)** | 17 | 20 | **17** |
| **False Positives (FP)**| 3 | 0 | **3** (`google.com`, `curl.se`, `panix.com`) |
| **False Negatives (FN)**| 8 | 10 | **7** |
| **Accuracy** | 63.33% | 66.67% | **66.67%** (20 / 30) |
| **Precision** | 40.00% | 100.00% | **50.00%** (3 / 6) |
| **Recall** | 20.00% | 0.00% | **30.00%** (3 / 10) |
| **Specificity** | 85.00% | 100.00% | **85.00%** (17 / 20) |
| **F1 Score** | 26.67% | 0.00% | **37.50%** |

---

## 3. Scope of Valid Findings

- **Corpus v2 (1,000 domains)**: Verified 100% real-world provenance with zero synthetics.
- **Phase 1.3 Live Pilot (200 domains)**: Verified genuine HTTP and Wayback CDX queries with 178 frozen HTML payloads.
- **Benchmark v2 (30 domains)**: Verified live evidence evaluation with blinded private reference labels.
