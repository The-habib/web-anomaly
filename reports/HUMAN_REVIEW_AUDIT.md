# Project Atlas — Phase 1.8 Human Review Protocol & Blindness Audit

**Project**: Atlas Autonomous Research Laboratory  
**Phase**: 1.8 Review Protocol Forensics & Blindness Classification  
**Date**: 2026-08-18T05:59:00Z  
**Audit Artifact**: `audit/phase1_8/human_review_audit.json`

---

## 1. Executive Summary

Phase 1.8 audited the stratified human review dataset (`data/phase1_7/human_reviews.jsonl`, $N=30$ dossiers) to evaluate the integrity and degree of reviewer blinding.

### Key Audit Finding:
- **Blindness Classification**: **`PARTIALLY_BLIND`**
- **Arm Labels**: Reviewers were presented with randomized study labels (`STUDY_A` vs `STUDY_B`). Explicit arm names (`UNIFORM` / `DENSITY_PRIORITIZED`) were stripped from the review dossiers.
- **Structural Leakage**: Because dossiers contained full target URLs (e.g. `/~cslug`, `/software/halifax/`), domain expertise and URL path semantics could allow knowledgeable reviewers to infer whether a domain belonged to a high-density institutional repository or personal shell community.

---

## 2. Review Protocol Quantitative Summary

- **Total Review Dossiers**: 30 (covering all candidates scoring $\ge 40$, sampled near misses $20 \le \text{score} < 40$, and sampled ordinary controls $< 20$).
- **Verdict Distribution**:
  - `CLEAR_ANOMALY`: 7 dossiers (2 incremental deep discoveries + 5 root relics)
  - `POTENTIAL_ANOMALY`: 4 dossiers
  - `ORDINARY`: 19 dossiers
- **Incremental False Positives**: **0** (0 modern commercial or corporate sites misclassified as vintage anomalies).
