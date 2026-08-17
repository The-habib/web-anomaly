# Project Atlas — Benchmark v1 vs Benchmark v2 Audit Report

**Document**: `reports/PHASE_1_3_BENCHMARK_AUDIT.md`  
**Scope**: Methodological Decontamination of Validation Benchmarks  
**Date**: 2026-08-17T21:25:00Z  

---

## 1. Decontamination Summary

Under Phase 1.3:
1. **Benchmark v1 (`data/benchmark_v1/`)**: Officially reclassified as a **synthetic unit regression benchmark**. It verified that scoring code paths execute without exception, but did not measure real-world detection capabilities.
2. **Benchmark v2 (`data/benchmark_v2/`)**: Built as a **genuine empirical validation benchmark** utilizing live HTTP requests, live Wayback CDX queries, and blinded private reference labels.

---

## 2. Benchmark Architecture Comparison

| Dimension | Benchmark v1 (Phase 1.2) | Benchmark v2 (Phase 1.3) |
| :--- | :--- | :--- |
| **Evidence Source** | `_generate_realistic_domain_evidence()` | Live HTTP (`requests`) & Wayback CDX API |
| **Artifact Freezing** | None | 30 Raw HTML payloads saved with SHA-256 |
| **Label Blinding** | Labels in `labels.jsonl` | Labels in `labels_private.jsonl` (blinded from scorer) |
| **Scoring Input** | Mock properties | Extracted DOM & Wayback metadata |
| **Reported Accuracy** | 90.0% (Simulated) | **63.33% (True Empirical)** |
| **Reported Precision**| 100.0% (Simulated) | **40.00% (True Empirical)** |
| **Reported Recall**   | 70.0% (Simulated) | **20.00% (True Empirical)** |
| **Reported Specificity**| 100.0% (Simulated) | **85.00% (True Empirical)** |

---

## 3. Analysis of Empirical Performance Drop

The drop from simulated 90% accuracy to empirical 63.33% accuracy is a **vital scientific milestone**:
1. **Real-World Complexity**: On the live web, `google.com` serves a minimal HTML layout with nested tables and has deep archive presence dating to 1997. This scored 55.0 points (a false positive candidate anomaly), exposing an over-reliance on table layout heuristics.
2. **Living Preservation Challenges**: Preserved legacy sites like `spacejam.com` now redirect to modern Warner Bros landing pages or embed legacy content in dynamic wrappers, causing the root scanner to see modern CMS markup (false negative).
3. **Actionable Engineering Direction**: Benchmark v2 provides the first **honest, empirical baseline** upon which real detector improvements can be measured in future research.
