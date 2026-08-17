# Root vs Deep Comparison Report — Project Atlas Phase 1.5

**Project**: Atlas — Web Anomaly Laboratory  
**Phase**: 1.5  
**Date**: 2026-08-17T22:30:00Z  

---

## 1. Paired Statistical Overview

| Domain Category | Domains Attempted | Root Candidates | Deep Candidates | Incremental Candidates | Validated Discoveries |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Universities** | 60 | 1 | 2 | **+1** | **+1** (`cmu.edu/~faculty`) |
| **Government** | 60 | 0 | 0 | 0 | 0 |
| **Nonprofits** | 45 | 1 | 1 | 0 | 0 |
| **Companies** | 45 | 1 | 1 | 0 | 0 (FP) |
| **Open-Source** | 45 | 0 | 0 | 0 | 0 |
| **Personal / Indep** | 45 | 0 | 0 | 0 | 0 |
| **TOTAL** | **300** | **3** | **4** | **+1** | **+1** |

---

## 2. Qualitative Discovery Analysis: The Root Blind Spot

### Example: `cmu.edu` (Carnegie Mellon University)
- **Root Baseline (Arm A)**: Modern Next.js/CMS university portal. Score = 0.0 (ORDINARY).
- **Deep Expansion (Arm B)**: Historical CDX index discovered `/~faculty/legacy/` active since 1995.
- **Evidence**: Raw HTML contains 1990s table layouts, `<font>` styling, raw FTP links, and complete absence of modern CSS frameworks.
- **Deep Score**: **55.0** (`CANDIDATE_ANOMALY`).
- **Human Review**: Confirmed as an authentic, unmodernized academic user-space relic preserved intact.

---

## 3. False-Positive Trade-off
- **Root Arm False Positives**: 1 (Corporate site with legacy table remnants).
- **Deep Arm False Positives**: 1.
- **Incremental False Positives**: **0**.
- **Conclusion**: Deep historical index exploration did not introduce additional false positives into the pipeline.
