# Project Atlas — Phase 1.8 Methodological & Statistical Limitations

**Project**: Atlas Autonomous Research Laboratory  
**Phase**: 1.8 Comprehensive Limitations Disclosure  
**Date**: 2026-08-18T05:59:00Z  

---

## 1. Statistical Limitations

1. **Sparse Event Counts**:
   - Total validated discoveries in Phase 1.7 was $K=2$ (both in Arm D, 0 in Arm U).
   - While the rate ratio is directionally positive ($RR_{\text{HA}} = 2.86$), the 95% confidence interval is broad ($[0.14, 59.60]$), and Fisher's exact test ($p \approx 0.50 - 0.54$) does not reach statistical significance ($\alpha = 0.05$).
2. **Zero-Cell Reliance**:
   - Zero events in the control arm necessitates continuity corrections (Haldane-Anscombe, Laplace) or exact Poisson models, which introduce sensitivity to the chosen prior.

---

## 2. Methodological & Sampling Limitations

1. **Remainder Control Design**:
   - Arm U was drawn from the remainder after extracting the top density tail for Arm D, rather than an independent unconstrained draw.
2. **Realized Budget Confound**:
   - Arm D executed $1.75\times$ more retrievals than Arm U ($1,470$ vs $841$) because path-sparse domains in Arm U exhausted candidate pools before reaching the 15-retrieval cap.
3. **Partial Reviewer Blinding**:
   - Reviewers saw blinded study labels, but full URL paths were visible, allowing expert deduction of domain archetype.

---

## 3. Road to Phase 2

These limitations do not invalidate the Phase 1.7 findings, but they establish strict requirements for Phase 2:
- Scaled randomized block trials ($N \ge 2,500$ domains).
- Fixed-effort retrieval quotas (enforcing identical query counts per domain).
- Fully anonymized URL paths in human review dossiers.
