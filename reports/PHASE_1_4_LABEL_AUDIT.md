# Project Atlas — Benchmark v2 Label Provenance & Bias Audit

**Document**: `reports/PHASE_1_4_LABEL_AUDIT.md`  
**Dataset Audited**: `data/benchmark_v2/labels_private.jsonl` (N=30)  
**Date**: 2026-08-17T21:35:00Z  

---

## 1. Audit of Label Attribution & Provenance

During the Phase 1.3 benchmark construction, the label metadata recorded:
```json
"labeling_method": "INDEPENDENT_EXPERT_PANEL"
```

### Audit Findings:
1. **No External Multi-Rater Delphi Panel**: The 30 reference labels were assigned directly by the Project Atlas lead research engineers based on established public web history and domain documentation.
2. **Provenance Reclassification**: To maintain scientific integrity, the label methodology is formally reclassified from `"INDEPENDENT_EXPERT_PANEL"` to:
   $$\mathbf{LABELING\text{ }METHOD: \text{ REFERENCE\_RETROSPECTIVE\_CURATION}}$$
   $$\mathbf{CONFIDENCE: \text{ REFERENCE\_MEDIUM\_CONFIDENCE}}$$

---

## 2. Description & Selection Bias Audit

- **Anomaly Cohort (10 domains)**: Selected predominantly from famous living web artifacts (`spacejam.com`, `toastytech.com`, `zombo.com`, `stallman.org`, `catb.org`, `sdf.org`, `textfiles.com`).
- **Scientific Implication**: The benchmark measures the detector's capability to recognize **known anomaly archetypes** rather than discovering uncharacterized anomalies in the open wild.
- **Ordinary Cohorts (20 domains)**: Represent diverse, well-maintained institutional, commercial, and technical infrastructure portals.

---

## 3. Label Independence Safeguards

- Labels are stored in `data/benchmark_v2/labels_private.jsonl`.
- The live feature extractor and scoring engine (`AnomalyScorer`) never load or inspect this file during execution.
- Evaluation metrics are computed strictly post-scoring in an independent join stage.
