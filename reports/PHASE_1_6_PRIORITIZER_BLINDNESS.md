# Phase 1.6 Prioritizer Blindness Audit — Project Atlas

**Project**: Atlas — Web Anomaly Laboratory  
**Phase**: 1.6 Independent Scientific Audit  
**Date**: 2026-08-17T22:42:00Z  
**Classification**: **`FULLY_BLIND_TO_GROUND_TRUTH_AND_SCORES`**  

---

## 1. Objective & Scope of Prioritizer Audit

In paired experimental designs, if the candidate selection or prioritization engine has access to anomaly scores, ground-truth labels, or target domain names, the experiment suffers from selection bias.

The Phase 1.6 audit conducted a line-by-line inspection of `atlas/deep/prioritizer.py` to establish whether candidate path prioritization maintained absolute blindness to experimental outcomes.

---

## 2. Feature & Weight Breakdown of `calculate_retrieval_priority`

The prioritizer computes an integer/float priority score ($0.0 - 100.0$) using four input dimensions:

| Component | Source Feature | Maximum Points | Implementation Verification | Blindness Audit |
| :--- | :--- | :--- | :--- | :--- |
| **1. Structural Category** | Regex pattern matching on path string (`PathCategory`) | 35.0 pts | `CATEGORY_PRIORITY_WEIGHTS`: `ACADEMIC_USER_SPACE` (35), `ARCHIVE_DIRECTORY` (30), `LEGACY_DOCS` (25), `PUBLIC_FILES` (20), `YEAR_PREFIXED` (20), `SOFTWARE_PROJECT` (15), `PERSONAL_BLOG` (15), `GENERAL_DIRECTORY` (5) | **PASS** (Pure structural regex on URL string) |
| **2. Historical Age** | CDX earliest observation timestamp | 40.0 pts | $\le 1996$ (+40), $\le 2000$ (+30), $\le 2005$ (+20), $\le 2010$ (+10) | **PASS** (Public historical CDX metadata) |
| **3. Path Depth** | Count of forward slashes (`/`) in path | 15.0 pts | $\le 2$ slashes (+15), $\le 4$ slashes (+10) | **PASS** (Shallow URL heuristic) |
| **4. Archive Source** | Discovery source tag | 10.0 pts | `WAYBACK_CDX` (+10) | **PASS** (Source indicator) |

---

## 3. Negative Assertion Verification

Line-by-line static analysis of `atlas/deep/prioritizer.py` confirms that the prioritizer:
- **DOES NOT** access or calculate anomaly scores.
- **DOES NOT** access ground-truth reference labels (`spacejam.com`, `zombo.com`, etc.).
- **DOES NOT** access human reviewer verdicts or notes.
- **DOES NOT** inspect or parse HTML content prior to selection.
- **DOES NOT** contain hardcoded domain lists or whitelist rules.

---

## 4. Prioritizer Efficiency & Reduction Audit

| Metric | Machine Reconciled Ground Truth | Narrative Report Claim | Audit Variance |
| :--- | :--- | :--- | :--- |
| **Raw Candidate Paths Discovered** | **16,174** | 4,812 | -11,362 (Report undercounted) |
| **Selected Paths for Retrieval** | **2,834** | 2,834 | Exact Match |
| **Candidate Filtering Reduction** | **82.48%** | 41.1% | +41.38% (Prioritizer was more selective than claimed) |

$$\text{True Filtering Efficiency} = \frac{16,174 - 2,834}{16,174} = \mathbf{82.48\%}$$

---

## 5. Audit Verdict

The candidate prioritizer operated with complete scientific blindness. Its selection criteria were based entirely on publicly observable pre-fetch metadata (URL structure and CDX first-seen dates). The experiment was completely free of prioritizer selection bias.
