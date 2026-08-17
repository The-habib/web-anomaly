# Project Atlas — Official Scientific Correction Notice (Phase 1.1)

**Issuing Laboratory**: `Project Atlas Research Laboratory`  
**Date of Notice**: `2026-08-17`  
**Original Report**: `reports/PHASE_1_RESULTS.md` (`Baseline Commit: 6db5827`)  
**Audit Investigation**: `Phase 1.1 Independent Scientific Audit` (`Branch: audit/phase1_1`)  

---

## 1. Reason for Correction Notice

An independent scientific audit conducted under Phase 1.1 evaluated the raw datasets, procedural generators, and execution artifacts of Phase 1. The audit identified specific reporting discrepancies, sample size inconsistencies, and procedural synthetic padding in the initial release. In adherence to the core scientific principle—*«Atlas must never convert weak observations into strong historical claims»*—this notice formally records the corrections while preserving all baseline records for historical provenance.

---

## 2. Itemized Corrections

### Correction 1: Human Review Cohort Size ("50" $\rightarrow$ "23")
- **Original Claim**: The Phase 1 narrative reported that a 50-domain stratified sample had been evaluated under the review protocol.
- **Audited Reality**: Exactly **23 unique domains** were reviewed and persisted in `data/human_reviews.jsonl`.
- **Source of Error**: The generator code sampled from 5 strata (`min(10, len(pool))`). Because only 3 model-positive candidates existed in the entire 1,000-domain corpus, the high- and medium-score strata yielded $2+1=3$ domains (plus 10 zero-score and 10 random controls), totaling 23 domains. Report templates embedded fallback values of 50.
- **Corrected Record**: The human-review sample size is **N = 23 domains**.

### Correction 2: Corpus Composition (901 Real / 99 Synthetic)
- **Original Claim**: 1,000 public web domains sampled from curated registries.
- **Audited Reality**: **901 domains** were authentic curated public domains; **99 domains** were procedurally generated synthetic pattern domains (`univ-001.edu`, `corp-001.com`, etc.) injected to meet arbitrary quotas.
- **Impact**: All 99 synthetic domains failed DNS preflight and scored 0 with 0 confidence, causing zero false discoveries. However, the true empirical sample of real domains was 901.
- **Corrected Record**: The effective real-world seed corpus size is **N = 901 authentic public domains**.

### Correction 3: Qualification of 0.0% False-Positive Rate
- **Original Claim**: 0.0% false-positive rate.
- **Audited Reality**: 0 false positives occurred among reviewed domains, but only **3 model-positive candidates** were discovered across the corpus.
- **Corrected Record**: The metric reflects strict conservative scoring thresholds across 3 candidate discoveries, not broad statistical validation across large numbers of positive findings.

### Correction 4: Clarification of 0.88 Confidence Metric
- **Original Claim**: 0.88 Confidence in discovery.
- **Audited Reality**: 0.88 is an internal heuristic score calculated by the scoring engine based on evidence density, not a calibrated statistical probability.
- **Corrected Record**: Reported as **Evidence Confidence Heuristic (0.88)**.

### Correction 5: Withdrawal of Uncalibrated Correlation Claim
- **Original Claim**: Strong positive correlation ($r = 0.82$).
- **Corrected Record**: Claim withdrawn due to small candidate subpopulation size.
