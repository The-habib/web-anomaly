# Project Atlas — Phase 1.8 Holdout Cohort & Generalization Audit

**Project**: Atlas Autonomous Research Laboratory  
**Phase**: 1.8 Holdout Isolation & Functionality Audit  
**Date**: 2026-08-18T05:59:00Z  
**Audit Artifact**: `audit/phase1_8/holdout_audit.json`

---

## 1. Executive Summary

Phase 1.7 reserved a **200-domain Holdout Cohort** from Corpus v2 to validate generalization.

This audit evaluates:
1. **Holdout Isolation**: Did any holdout domains leak into experimental treatment or control arms?
2. **Holdout Role**: Did the holdout function as a formal replication trial or an observational baseline?

---

## 2. Holdout Isolation Verification

- **Total Holdout Domains**: 200 domains (recorded in `data/phase1_7/holdout_manifest.json`, Seed=42).
- **Stratification**: 40 Universities, 40 Government, 30 Nonprofits, 30 Companies, 30 Open-source, 30 Personal.
- **Overlap Audit**:
  - Overlap with Arm U ($N=100$): **0 domains (0.0%)**
  - Overlap with Arm D ($N=100$): **0 domains (0.0%)**
  - Overlap with Eligible Pool ($N=800$): **0 domains (0.0%)**
- **Conclusion**: Holdout isolation was **$100\%$ preserved**.

---

## 3. Holdout Functionality & Generalization Analysis

In Phase 1.7, the holdout cohort was scanned observationally:
- **Domains Evaluated**: 200 total (including 40 density-prioritized holdout domains).
- **Discoveries Found**: **0**
- **Yield**: $0.000$ per 1,000 retrievals.

### Functional Classification:
We classify the holdout function as **`OBSERVATIONAL_BASELINE`** / **`EXPLORATORY_CHECK`**.

### Scientific Note:
Because a full parallel randomized trial (Arm U vs Arm D) was not executed on the holdout cohort, the holdout outcome does **not** constitute a formal experimental replication. Instead, it provides empirical evidence that authentic vintage web surfaces are extremely rare ($< 0.5\%$) in broad uncurated distributions.
