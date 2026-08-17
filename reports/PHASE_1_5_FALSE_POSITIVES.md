# Phase 1.5 False Positive Analysis

**Project**: Atlas — Web Anomaly Laboratory  
**Phase**: 1.5  
**Date**: 2026-08-17T22:30:00Z  

---

## 1. False Positive Measurement Across Arms

| Experiment Arm | Evaluated Domains | False Positives Identified | False Positive Rate |
| :--- | :--- | :--- | :--- |
| **Arm A (Root Baseline)** | 300 | 1 | 0.33% (1 / 300) |
| **Arm B (Deep Expansion)** | 300 | 1 | 0.33% (1 / 300) |
| **Incremental Difference** | **0** | **0** | **+0.00%** |

---

## 2. Qualitative Analysis of Residual False Positive

### Domain: `sierratradingpost.com` (Corporate Company Category)
- **Observed Score**: 40.0 (`CANDIDATE_ANOMALY`)
- **Triggered Signals**: `OLD_FIRST_SEEN_YEAR` (1998), `INLINE_STYLES`, table structure remnants in legacy help directory.
- **Root Cause**: An unmodernized terms/privacy policy subpath retained table formatting from an early 2000s redesign.
- **Mitigation Proposal for Future Scorer**: Require technology fossil or academic user-space indicators in addition to basic table formatting for corporate domains.
