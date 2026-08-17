# Project Atlas — Benchmark v1 Evaluation & Performance Report

**Document**: `reports/BENCHMARK_RESULTS.md`  
**Benchmark Version**: `v1.0` (`data/benchmark_v1/`)  
**Domain Count**: 30 Frozen Reference Domains  
**Evaluation Date**: 2026-08-17T20:30:00Z  

---

## 1. Benchmark Overview & Composition

Benchmark v1 is an independent, versioned validation dataset designed to evaluate the sensitivity, specificity, and calibration of the Atlas scoring engine:

- **Group 1: Ordinary Modern Reference Sites (N=10)**: Standard modern institutional, commercial, and educational portals (`google.com`, `apple.com`, `harvard.edu`, `nasa.gov`, `un.org`, `python.org`, `nytimes.com`, `github.com`, `cloudflare.com`, `bbc.co.uk`). Expected: `ORDINARY`.
- **Group 2: Known Preserved Historical Fossils (N=10)**: Famous or documented living web relics (`spacejam.com`, `toastytech.com`, `zombo.com`, `stallman.org`, `catb.org`, `sdf.org`, `textfiles.com`, etc.). Expected: `POTENTIAL_ANOMALY`.
- **Group 3: Long-Running Technical Infrastructure (N=7)**: Standards bodies and open-source infrastructure with continuous documentation (`ietf.org`, `w3.org`, `kernel.org`, `freebsd.org`, `debian.org`, `sqlite.org`, `curl.se`). Expected: `ORDINARY`.
- **Group 4: Difficult Edge Cases & Gap Tests (N=3)**: Complex hybrid sites with archive gaps or vintage shell roots (`cmu.edu`, `panix.com`, `world.std.com`). Expected: `ORDINARY`.

---

## 2. Evaluation Results & Confusion Matrix

```
                        Predicted Anomaly (Candidate/High)    Predicted Ordinary
Expected Anomaly (10)                 7 (TP)                        3 (FN)
Expected Ordinary (20)                0 (FP)                       20 (TN)
```

### Performance Metrics
| Metric | Value | Interpretation |
| :--- | :--- | :--- |
| **Accuracy** | **90.00%** (27/30) | High overall classification correctness |
| **Precision** | **100.00%** (7/7) | Zero false positive flags on modern infrastructure |
| **Recall / Sensitivity** | **70.00%** (7/10) | Strong detection of prominent fossils |
| **Specificity** | **100.00%** (20/20) | Perfect rejection of non-anomalies |
| **F1 Score** | **82.35%** | Robust harmonic mean of precision & recall |
| **False Positive Rate** | **0.00%** | Zero noise contamination |
| **False Negative Rate** | **30.00%** | Conservative scoring on minimalist text edge cases |

---

## 3. Performance by Benchmark Group

| Benchmark Group | Total Sites | Correct Classifications | Group Accuracy | Mean Anomaly Score |
| :--- | :--- | :--- | :--- | :--- |
| **Ordinary Modern** | 10 | 10 | **100.0%** | 0.00 |
| **Legacy Fossils** | 10 | 7 | **70.0%** | 64.00 |
| **Long-Running Infrastructure** | 7 | 7 | **100.0%** | 0.00 |
| **Edge Cases & Gap Tests** | 3 | 3 | **100.0%** | 0.00 |

---

## 4. Benchmark Cryptographic Manifest

- **CSV File**: `data/benchmark_v1/benchmark_domains.csv` (SHA-256: `955896b010d8a59960ff4a974911d7df4d6ae7161726a798579075ce8d53efbc`)
- **Labels File**: `data/benchmark_v1/labels.jsonl` (SHA-256: `78cb0973a985e5138fc6f2ba4d7dcba0394553258525b6ecf3ee25ebbbdc671d`)
- **Evaluation Report**: `data/benchmark_v1/benchmark_evaluation.json`

To re-run the benchmark validation pipeline at any time:
```bash
python3 -m atlas.cli benchmark run
```
