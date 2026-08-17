# Project Atlas — Phase 1.3 Pilot Claims & Representativeness Audit

**Document**: `reports/PHASE_1_4_PILOT_AUDIT.md`  
**Dataset Audited**: `data/phase1_3_live/` (N=200 Attempted Domains)  
**Date**: 2026-08-17T21:35:00Z  

---

## 1. Audit of Pilot Headline Claims

| Published Claim | Original Scope | Audited Finding | Corrected Scientific Statement |
| :--- | :--- | :--- | :--- |
| **"100% Modernized"** | General claim | Applies to 178 reachable root homepages | 100% of the 178 reachable root homepages in the sampled pilot cohort have updated layouts. |
| **"0% False Positives"** | Pilot cohort | Evaluated against reachable modern cohort | Zero false positive candidate anomaly flags were triggered on the 178 modernized public root homepages. |
| **"Living Relics are Rare (<1%)"** | Inferred global web | Sample size N=200 | In this stratified 200-domain pilot sample, zero unmodernized root relics were discovered. Global web frequency requires broader census. |

---

## 2. Denominator and Coverage Audit

- **Total Domains Attempted**: 200
- **Reachable Live Domains**: 178 (89.0%)
- **Unreachable / Timeout Domains**: 22 (11.0%)
- **Wayback CDX Coverage**: 164 (82.0%)
- **Denominator Rule**: Precision and false positive metrics must specify the 178 reachable domains as denominator, with the 22 failures classified as `INSUFFICIENT_EVIDENCE`.
