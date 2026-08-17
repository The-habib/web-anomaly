# Project Atlas — Benchmark v2 Empirical Results Report

**Document**: `reports/BENCHMARK_V2_RESULTS.md`  
**Benchmark Version**: `v2.0-live` (`data/benchmark_v2/`)  
**Domain Count**: 30 Frozen Reference Domains  
**Mode**: `LIVE` (Real Public HTTP & Wayback CDX Queries)  
**Evaluation Timestamp**: 2026-08-17T20:50:15Z  

---

## 1. Empirical Confusion Matrix

```
                        Predicted Anomaly (Candidate/High)    Predicted Ordinary
Reference Anomaly (10)                2 (TP)                        8 (FN)
Reference Ordinary (20)               3 (FP)                       17 (TN)
```

---

## 2. Empirical Performance Metrics

| Metric | Empirical Value | Interpretation |
| :--- | :--- | :--- |
| **Accuracy** | **63.33%** (19 / 30) | Honest empirical classification accuracy on live web |
| **Precision** | **40.00%** (2 / 5) | 2 of 5 predicted anomalies were confirmed historical relics |
| **Recall / Sensitivity** | **20.00%** (2 / 10) | Identifies prominent unmodernized relics (`stallman.org`, `toastytech.com`) |
| **Specificity** | **85.00%** (17 / 20) | Correctly identifies 17 of 20 modern/infrastructure portals |
| **F1 Score** | **26.67%** | True empirical harmonic mean |
| **False Positive Rate** | **15.00%** (3 / 20) | Minimalist table layouts on search engines (`google.com`) |
| **False Negative Rate** | **80.00%** (8 / 10) | Redirects and plain ASCII archives scored under threshold |

---

## 3. Detailed Per-Domain Evaluation

### True Positives (Detected Relics)
1. **`stallman.org`**: Score 55.0 (`CANDIDATE_ANOMALY`) — Retro markup, unmodernized HTML layout, deep Wayback continuity.
2. **`toastytech.com`**: Score 55.0 (`CANDIDATE_ANOMALY`) — Preserved table-based layout and retro styling.

### False Positives (Over-Scored Modern)
1. **`google.com`**: Score 55.0 (`CANDIDATE_ANOMALY`) — Minimalist search landing page with table elements and 1997 archive origin.
2. **`panix.com`**: Score 55.0 (`CANDIDATE_ANOMALY`) — Dialup ISP text root directory with retro markup.
3. **`world.std.com`**: Score 55.0 (`CANDIDATE_ANOMALY`) — Dialup ISP legacy shell directory.

### False Negatives (Under-Scored Relics)
- `spacejam.com`, `zombo.com`, `catb.org`, `sdf.org`, `textfiles.com`, `wiby.me`, `frogfind.com`, `68k.news`: Scored 0.0 – 35.0 due to modern HTTPS wrappers, redirect chains, or pure ASCII layout without table tags.
