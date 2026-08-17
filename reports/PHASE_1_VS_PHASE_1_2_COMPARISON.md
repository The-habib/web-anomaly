# Project Atlas — Comparative Analysis: Phase 1 vs Phase 1.2

**Document**: `reports/PHASE_1_VS_PHASE_1_2_COMPARISON.md`  
**Scope**: Historical Baseline Comparison across Methodology, Provenance, Integrity & Scientific Rigor  

---

## 1. Direct Head-to-Head Comparison Matrix

| Scientific Dimension | Phase 1 (Baseline Experiment) | Phase 1.1 (Audit Reconciliation) | Phase 1.2 (Validated System) |
| :--- | :--- | :--- | :--- |
| **Corpus Provenance** | None recorded | Reconstructed census (901 real, 99 synthetic) | **100% Curated Provenance across 1,000 domains** |
| **Synthetic Quota Fillers** | 99 domains present (`univ-001.edu`, etc.) | Identified & documented | **Strictly 0 (Zero Tolerance Guardrails)** |
| **Verification Level** | None | Post-hoc classification | **100% Verified Real Entities (`atlas/provenance/`)** |
| **Corpus Quality Score** | Uncalculated | 0.825 (Compromised by synthetics) | **1.000 (Perfect Multi-Dimensional Score)** |
| **Benchmark Separation** | No benchmark dataset | No benchmark dataset | **Independent 30-domain Benchmark v1 (`data/benchmark_v1/`)** |
| **Human Review Protocol**| 23 reviews (unblinded, score visible) | Reconciled 23 reviews (50 planned) | **20 Blind Reviews (Strict Score-Hiding Engine)** |
| **Operational Gating** | Unchecked 1,000-domain execution | Retrospective verification | **200-Domain Checkpointed Pilot Gate (4 Batches)** |
| **Reproducibility** | Partially reproducible scoring replay | Deterministic scoring replay verified | **Full SHA-256 Manifests for Corpus, Pilot & Benchmark** |

---

## 2. Key Methodological Lessons & Evolutions

### 1. From Quota Satisfaction to Provenance Verification
- **Phase 1 Mistake**: When curated registries yielded fewer than 200 candidates for certain categories, procedural generators were allowed to inject synthetic fillers (`univ-001.edu`, `company-042.com`) to reach the round quota of 1,000.
- **Phase 1.2 Resolution**: Candidate pools were comprehensively expanded with real-world entities (326 Univ, 203 Gov, 160 Nonprofits, 157 Companies, 152 FOSS, 151 Independent). If any candidate fails verification, it is rejected and logged without synthetic padding.

### 2. From Unblinded Scoring to Blind Review Dossiers
- **Phase 1 Mistake**: Reviewers were shown the calculated anomaly score and triggered rules, introducing confirmation bias.
- **Phase 1.2 Resolution**: Human review dossiers (`data/phase1_2_pilot/blind_review_dossiers.jsonl`) explicitly hide anomaly scores, ranks, and rule triggers. Reviewers judge raw structural and timeline evidence independently before system scores are revealed.

### 3. Separation of Discovery and Regression Benchmarks
- **Phase 1 Mistake**: The discovery corpus and test cases were intertwined, making it impossible to evaluate scoring sensitivity on known ground truth without contaminating discovery data.
- **Phase 1.2 Resolution**: `data/corpus_v2/` is strictly unlabeled and used solely for open exploration; `data/benchmark_v1/` is versioned, labeled, and used solely for regression and sensitivity measurement.

---

## 3. Historical Preservation Policy

In accordance with strict scientific auditing principles:
- The original Phase 1 experiment artifacts in `experiments/0002/` and `data/seed_corpus.csv` remain unaltered as permanent historical evidence.
- Phase 1.1 audit reports (`reports/PHASE_1_1_AUDIT.md`, `reports/PHASE_1_CORRECTION_NOTICE.md`) document the baseline audit trajectory.
- Phase 1.2 provides the scientifically sound foundation for all future research.
