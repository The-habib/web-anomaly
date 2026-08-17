# Project Atlas — Benchmark v2 Empirical Results Report

**Document**: `reports/BENCHMARK_V2_RESULTS.md`  
**Benchmark Version**: `v2.0-live` (`data/benchmark_v2/`)  
**Domain Count**: 30 Frozen Reference Domains  
**Mode**: `LIVE` (Real Public HTTP & Wayback CDX Queries)  
**Evaluation Status**: Reconciled & Audited (Phase 1.4)  

---

## 1. Empirical Confusion Matrix

```
                        Predicted Anomaly (Candidate/High)    Predicted Ordinary
Reference Anomaly (10)                3 (TP)                        7 (FN)
Reference Ordinary (20)               3 (FP)                       17 (TN)
```

---

## 2. Empirical Performance Metrics

| Metric | Empirical Value | Interpretation |
| :--- | :--- | :--- |
| **Accuracy** | **66.67%** (20 / 30) | Honest empirical classification accuracy on live web |
| **Precision** | **50.00%** (3 / 6) | 3 of 6 predicted anomalies were confirmed historical relics |
| **Recall / Sensitivity** | **30.00%** (3 / 10) | Identifies prominent unmodernized relics (`toastytech.com`, `stallman.org`, `sdf.org`) |
| **Specificity** | **85.00%** (17 / 20) | Correctly identifies 17 of 20 modern/infrastructure portals |
| **F1 Score** | **37.50%** | True empirical harmonic mean |
| **False Positive Rate** | **15.00%** (3 / 20) | Minimalist table layouts on search engines (`google.com`, `curl.se`, `panix.com`) |
| **False Negative Rate** | **70.00%** (7 / 10) | Redirects and plain ASCII archives scored under threshold |

---

## 3. Detailed Per-Domain Evaluation

### True Positives (Detected Relics)
1. **`toastytech.com`**: Score 70.0 (`CANDIDATE_ANOMALY`) — Preserved table-based layout and retro styling.
2. **`stallman.org`**: Score 50.0 (`CANDIDATE_ANOMALY`) — Retro markup, unmodernized HTML layout, deep Wayback continuity.
3. **`sdf.org`**: Score 55.0 (`CANDIDATE_ANOMALY`) — Preserved table layout, retro elements, and 1996 archive presence.

### False Positives (Over-Scored Modern)
1. **`google.com`**: Score 55.0 (`CANDIDATE_ANOMALY`) — Minimalist search landing page with table elements and 1997 archive origin.
2. **`curl.se`**: Score 40.0 (`CANDIDATE_ANOMALY`) — Clean static documentation using table layout and retro elements.
3. **`panix.com`**: Score 70.0 (`CANDIDATE_ANOMALY`) — Oldest NY commercial ISP with vintage shell roots.

### False Negatives (Under-Scored Relics)
- `spacejam.com`, `zombo.com`, `catb.org`, `textfiles.com`, `wiby.me`, `frogfind.com`, `68k.news`: Scored 0.0 – 20.0 due to modern HTTPS wrappers, redirect chains, or pure ASCII layout without table tags.
