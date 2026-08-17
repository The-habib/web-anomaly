# Project Atlas — Benchmark v2 Independent Reconciliation Report

**Document**: `reports/PHASE_1_4_BENCHMARK_RECONCILIATION.md`  
**Auditor**: Independent Scientific Program (`scripts/audit_benchmark_v2_independently.py`)  
**Scope**: 30-Domain Reference Benchmark v2  
**Date**: 2026-08-17T21:35:00Z  

---

## 1. Independent Confusion Matrix

```
                        Predicted Anomaly (Candidate/High)    Predicted Ordinary
Reference Anomaly (10)                3 (TP)                        7 (FN)
Reference Ordinary (20)               3 (FP)                       17 (TN)
```

---

## 2. Independent Performance Metrics

| Metric | Independent Ground Truth | 95% Confidence Interval | Interpretation |
| :--- | :--- | :--- | :--- |
| **Accuracy** | **66.67%** (20 / 30) | [47.2%, 82.7%] | Overall correct classifications |
| **Precision** | **50.00%** (3 / 6) | [11.8%, 88.2%] | 3 of 6 predicted anomalies are true historical relics |
| **Recall / Sensitivity** | **30.00%** (3 / 10) | [6.7%, 65.2%] | Successfully detects 3 of 10 known relics |
| **Specificity** | **85.00%** (17 / 20) | [62.1%, 96.8%] | Correctly rejects 17 of 20 ordinary sites |
| **F1 Score** | **37.50%** | N/A | Harmonic mean of precision & recall |
| **False Positive Rate** | **15.00%** (3 / 20) | [3.2%, 37.9%] | Minimalist table layouts (`google.com`, `curl.se`, `panix.com`) |
| **False Negative Rate** | **70.00%** (7 / 10) | [34.8%, 93.3%] | Redirects & plain ASCII archives |

---

## 3. Case-by-Case Domain Reconciliation Table

| Benchmark ID | Domain | Reference Label | Live Score | Predicted Class | Result Classification | Triggered Rules Summary |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `bench-v2-0001` | `google.com` | `REFERENCE_ORDINARY` | 55.0 | `CANDIDATE_ANOMALY` | **FALSE_POSITIVE** | `html_tables_layout`, `retro_styling_elements`, `deep_archive` |
| `bench-v2-0002` | `apple.com` | `REFERENCE_ORDINARY` | 15.0 | `ORDINARY` | **TRUE_NEGATIVE** | `deep_archive_persistence_1996` |
| `bench-v2-0003` | `harvard.edu` | `REFERENCE_ORDINARY` | 0.0 | `ORDINARY` | **TRUE_NEGATIVE** | Modern CMS / Responsive Framework |
| `bench-v2-0004` | `nasa.gov` | `REFERENCE_ORDINARY` | 0.0 | `ORDINARY` | **TRUE_NEGATIVE** | Modern CMS / Responsive Framework |
| `bench-v2-0005` | `un.org` | `REFERENCE_ORDINARY` | 0.0 | `ORDINARY` | **TRUE_NEGATIVE** | Modern CMS / Responsive Framework |
| `bench-v2-0006` | `python.org` | `REFERENCE_ORDINARY` | 0.0 | `ORDINARY` | **TRUE_NEGATIVE** | Modern CMS / Responsive Framework |
| `bench-v2-0007` | `nytimes.com` | `REFERENCE_ORDINARY` | 0.0 | `ORDINARY` | **TRUE_NEGATIVE** | Modern CMS / Responsive Framework |
| `bench-v2-0008` | `github.com` | `REFERENCE_ORDINARY` | 0.0 | `ORDINARY` | **TRUE_NEGATIVE** | Modern SPA Architecture |
| `bench-v2-0009` | `cloudflare.com` | `REFERENCE_ORDINARY` | 0.0 | `ORDINARY` | **TRUE_NEGATIVE** | Modern Responsive Framework |
| `bench-v2-0010` | `bbc.co.uk` | `REFERENCE_ORDINARY` | 0.0 | `ORDINARY` | **TRUE_NEGATIVE** | Modern Responsive Portal |
| `bench-v2-0011` | `spacejam.com` | `REFERENCE_ANOMALY` | 0.0 | `ORDINARY` | **FALSE_NEGATIVE** | Root redirects to modern Warner Bros portal |
| `bench-v2-0012` | `toastytech.com`| `REFERENCE_ANOMALY` | 70.0 | `CANDIDATE_ANOMALY` | **TRUE_POSITIVE** | `moderate_stability`, `html_tables_layout`, `retro_styling` |
| `bench-v2-0013` | `zombo.com` | `REFERENCE_ANOMALY` | 0.0 | `ORDINARY` | **FALSE_NEGATIVE** | HTML5 audio wrapper lacks table tags |
| `bench-v2-0014` | `stallman.org` | `REFERENCE_ANOMALY` | 50.0 | `CANDIDATE_ANOMALY` | **TRUE_POSITIVE** | `moderate_stability`, `retro_styling`, `deep_archive` |
| `bench-v2-0015` | `catb.org` | `REFERENCE_ANOMALY` | 20.0 | `ORDINARY` | **FALSE_NEGATIVE** | Plain ASCII layout scored under threshold |
| `bench-v2-0016` | `sdf.org` | `REFERENCE_ANOMALY` | 55.0 | `CANDIDATE_ANOMALY` | **TRUE_POSITIVE** | `html_tables_layout`, `retro_styling`, `deep_archive` |
| `bench-v2-0017` | `textfiles.com` | `REFERENCE_ANOMALY` | 0.0 | `ORDINARY` | **FALSE_NEGATIVE** | Upstream timeout during live scan |
| `bench-v2-0018` | `wiby.me` | `REFERENCE_ANOMALY` | 0.0 | `ORDINARY` | **FALSE_NEGATIVE** | Minimal modern search engine format |
| `bench-v2-0019` | `frogfind.com` | `REFERENCE_ANOMALY` | 20.0 | `ORDINARY` | **FALSE_NEGATIVE** | Retro styling (+20) scored below threshold |
| `bench-v2-0020` | `68k.news` | `REFERENCE_ANOMALY` | 20.0 | `ORDINARY` | **FALSE_NEGATIVE** | Retro styling (+20) scored below threshold |
| `bench-v2-0021` | `ietf.org` | `REFERENCE_ORDINARY` | 15.0 | `ORDINARY` | **TRUE_NEGATIVE** | `deep_archive_persistence_1996` |
| `bench-v2-0022` | `w3.org` | `REFERENCE_ORDINARY` | 15.0 | `ORDINARY` | **TRUE_NEGATIVE** | `deep_archive_persistence_1996` |
| `bench-v2-0023` | `kernel.org` | `REFERENCE_ORDINARY` | 0.0 | `ORDINARY` | **TRUE_NEGATIVE** | Modern responsive mirror structure |
| `bench-v2-0024` | `freebsd.org` | `REFERENCE_ORDINARY` | 0.0 | `ORDINARY` | **TRUE_NEGATIVE** | Modernized responsive portal |
| `bench-v2-0025` | `debian.org` | `REFERENCE_ORDINARY` | 15.0 | `ORDINARY` | **TRUE_NEGATIVE** | `deep_archive_persistence_1996` |
| `bench-v2-0026` | `sqlite.org` | `REFERENCE_ORDINARY` | 0.0 | `ORDINARY` | **TRUE_NEGATIVE** | Modern clean static documentation |
| `bench-v2-0027` | `curl.se` | `REFERENCE_ORDINARY` | 40.0 | `CANDIDATE_ANOMALY` | **FALSE_POSITIVE** | `html_tables_layout`, `retro_styling_elements` |
| `bench-v2-0028` | `cmu.edu` | `REFERENCE_ORDINARY` | 15.0 | `ORDINARY` | **TRUE_NEGATIVE** | `deep_archive_persistence_1996` |
| `bench-v2-0029` | `panix.com` | `REFERENCE_ORDINARY` | 70.0 | `CANDIDATE_ANOMALY` | **FALSE_POSITIVE** | `moderate_stability`, `html_tables_layout`, `retro_styling` |
| `bench-v2-0030` | `world.std.com` | `REFERENCE_ORDINARY` | 30.0 | `ORDINARY` | **TRUE_NEGATIVE** | Vintage dialup ISP scored under 40.0 |
