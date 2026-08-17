# Project Atlas — Phase 1 Research Limitations

**Date**: 2026-08-17  
**Experiment**: Phase 1 Blind Seed-Corpus Discovery (N=1,000)  

---

## 1. Observational Scope Limitations

1. **Seed Corpus Stratification**: The 1,000-domain seed corpus was stratified across 6 equal/near-equal institutional and independent categories. This is designed for balanced archaeological sensitivity and does not represent the real-world commercial traffic distribution of the web.
2. **First-Pass Landing Page Scope**: Phase 1 collected evidence from the root landing page (canonical URL) of each domain. Deep subdirectories and unlinked subpages were not exhaustively spidered during this initial pass.
3. **Third-Party CDX Index Latency**: The Wayback Machine and Common Crawl index APIs have variable crawl coverage. Unobserved intervals were conservatively treated as `INSUFFICIENT` rather than domain disappearance.

---

## 2. Measurement & Calibration Caveats

1. **Confidence Score Calibration**: The reported confidence metric is an internal heuristic based on evidence density and multi-source corroboration, not a calibrated statistical probability.
2. **Sample Validation**: Human review was performed on a 50-domain stratified sample; broad precision/recall extrapolation must be stated as sample estimates rather than global ground-truth constants.
