# Project Atlas — Benchmark v2 False-Positive Analysis

**Document**: `reports/PHASE_1_4_FALSE_POSITIVE_ANALYSIS.md`  
**Scope**: In-Depth Investigation of Benchmark v2 False Positives  
**Date**: 2026-08-17T21:35:00Z  

---

## 1. False Positive Inventory

In the live Benchmark v2 evaluation, 3 domains received scores $\ge 40.0$ despite being reference ordinary:

| Domain | Observed Score | Classification | Triggered Rules | Failure Class |
| :--- | :--- | :--- | :--- | :--- |
| **`google.com`** | 55.0 | `CANDIDATE_ANOMALY` | `html_tables_layout`, `retro_styling_elements`, `deep_archive_persistence_1996` | `F5_TABLE_OVERDETECTION` |
| **`curl.se`** | 40.0 | `CANDIDATE_ANOMALY` | `html_tables_layout`, `retro_styling_elements` | `F5_TABLE_OVERDETECTION` |
| **`panix.com`** | 70.0 | `CANDIDATE_ANOMALY` | `moderate_stability`, `html_tables_layout`, `retro_styling`, `deep_archive` | `F8_DEEP_PATH` / `F5` |

---

## 2. Root Cause Breakdown

### Case 1: `google.com` (Score: 55.0)
- **Why it fired**: Google's search landing page maintains an ultralight DOM utilizing layout `<table>` elements with inline presentation attributes and has a continuous archive span dating to 1997.
- **Remedy**: Introduce HTML5 `<doctype html>` and responsive viewport checks to distinguish modern minimal single-input applications from 1990s multi-frame documents.

### Case 2: `curl.se` (Score: 40.0)
- **Why it fired**: Daniel Stenberg's cURL project documentation uses hand-crafted, clean HTML with summary tables and retro inline styles without modern JS frameworks.
- **Remedy**: Semantic CSS analysis (CSS grid/flexbox properties vs raw font tags).

### Case 3: `panix.com` (Score: 70.0)
- **Why it fired**: Panix (the oldest commercial ISP in New York) deliberately maintains a retro 1990s dialup shell aesthetic on its landing portal. This is a borderline case where the site exhibits true historical features.
