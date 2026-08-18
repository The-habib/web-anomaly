# Project Atlas — Phase 1.8 Independent Statistical Audit & Recomputation

**Project**: Atlas Autonomous Research Laboratory  
**Phase**: 1.8 Independent Statistical Engine & Rate Ratio Forensics  
**Date**: 2026-08-18T05:59:00Z  
**Audit Artifacts**: `audit/phase1_8/independent_statistical_results.json`, `audit/phase1_8/zero_trust_reconstruction.json`

---

## 1. Executive Summary

Phase 1.8 independently recomputed all experimental metrics from raw JSONL event streams without importing or reusing Phase 1.7 statistical scripts.

### Key Audit Conclusions:
1. **Published Rate Ratio ($RR \approx 1361.00$) was Invalid**: Division by an arbitrary placeholder ($0.001$) created an inflated rate ratio.
2. **Published 95% CI ($[0.5, 15.0]$) was Hardcoded**: The point estimate ($1361.00$) lay outside the published CI, violating foundational mathematical axioms.
3. **Corrected Haldane-Anscombe Rate Ratio**:
   - **Retrieval-Level**: $\mathbf{RR_{\text{HA}} = 2.86}$ ($95\%$ CI: $[0.14, 59.60]$).
   - **Domain-Level**: $\mathbf{RR_{\text{HA}} = 5.00}$ ($95\%$ CI: $[0.24, 102.73]$).
4. **Fisher's Exact Test**:
   - Retrieval-Level ($2\times 2$ table: $[[2, 1468], [0, 841]]$): Two-sided $p = \mathbf{0.5368}$, One-sided greater $p = \mathbf{0.4046}$.
   - Domain-Level ($2\times 2$ table: $[[2, 98], [0, 100]]$): Two-sided $p = \mathbf{0.4987}$, One-sided greater $p = \mathbf{0.2487}$.
5. **Statistical Classification**: Under sparse discovery counts ($K=2$ total discoveries), effect size is positive and directionally **`PROMISING`**, but does not achieve classical statistical significance ($\alpha = 0.05$).

---

## 2. Comprehensive Metric Recomputation Table

| Metric | Phase 1.7 Published | Phase 1.8 Independent Recomputation | Method / Formulation |
| :--- | :--- | :--- | :--- |
| **Arm U Domains / Retrievals** | $100$ / $841$ | **$100$ / $841$** | Verified raw line counts |
| **Arm D Domains / Retrievals** | $100$ / $1470$ | **$100$ / $1470$** | Verified raw line counts |
| **Arm U Discoveries** | $0$ | **$0$** | $0/100$ domains, $0/841$ retrievals |
| **Arm D Discoveries** | $2$ | **$2$** | `gnu.org` + `tilde.club` |
| **Arm U Yield / 1k Retrievals** | $0.000$ | **$0.000$** | $(0 / 841) \times 1000$ |
| **Arm D Yield / 1k Retrievals** | $1.361$ | **$1.361$** | $(2 / 1470) \times 1000$ |
| **Absolute Yield Difference** | $+1.361$ / 1k | **$+1.361$ / 1k** | $1.361 - 0.000$ |
| **Rate Ratio ($RR$)** | $1361.00$ *(Flawed)* | **$2.86$** (Retrieval) / **$5.00$** (Domain) | Haldane-Anscombe ($+0.5$ correction) |
| **$95\%$ Confidence Interval** | $[0.5, 15.0]$ *(Invalid)*| **$[0.14, 59.60]$** (Retrieval) | Delta method log-normal CI |
| **Laplace Rate Ratio** | Not reported | **$3.00$** (Domain) | $((2+1)/101) / ((0+1)/101)$ |
| **Fisher Exact $p$ (Two-Sided)**| $0.5368$ | **$0.5368$** (Retrieval) / **$0.4987$** (Domain) | Exact Hypergeometric sum |
| **Fisher Exact $p$ (One-Sided)**| Not reported | **$0.4046$** (Retrieval) / **$0.2487$** (Domain) | Tail probability |
| **Bootstrap Yield Diff ($10\text{k}$)**| Not reported | **$+1.361$ / 1k** ($95\%$ CI: $[0.00, 3.42]$) | Nonparametric percentile |
| **False Positive Count** | $0$ | **$0$** | 0 incremental false positives |

---

## 3. Mathematical Forensics of Zero-Cell Rate Ratios

When Arm U contains 0 events, the naive rate ratio $\frac{2 / 1470}{0 / 841}$ involves division by zero.

### Deconstruction of the Phase 1.7 Calculation:
Phase 1.7 computed:
$$\text{Flawed } RR = \frac{1.361}{0.001} = 1361.00$$
Here, $0.001$ was inserted as an ad-hoc placeholder for $0.000$, resulting in an arbitrary number proportional to the chosen placeholder ($1 / 0.001 = 1000$).

### Rigorous Sparse-Event Corrections (Phase 1.8):
1. **Haldane-Anscombe Correction ($+0.5$)**:
   $$\text{Rate}_{\text{D, adj}} = \frac{2 + 0.5}{1470 + 0.5} = \frac{2.5}{1470.5} \approx 0.0017001$$
   $$\text{Rate}_{\text{U, adj}} = \frac{0 + 0.5}{841 + 0.5} = \frac{0.5}{841.5} \approx 0.0005942$$
   $$RR_{\text{HA}} = \frac{0.0017001}{0.0005942} \approx \mathbf{2.8613}$$
   $$\text{SE}(\ln RR) = \sqrt{\frac{1}{2.5} + \frac{1}{0.5}} = \sqrt{0.4 + 2.0} = \sqrt{2.4} \approx 1.5492$$
   $$95\%\ \text{CI} = \exp(\ln(2.8613) \pm 1.96 \times 1.5492) = \mathbf{[0.1374, 59.5984]}$$

2. **Domain-Level Haldane-Anscombe**:
   $$\text{Rate}_{\text{D, adj}} = \frac{2.5}{100.5} = 0.024875$$
   $$\text{Rate}_{\text{U, adj}} = \frac{0.5}{100.5} = 0.004975$$
   $$RR_{\text{HA, dom}} = \frac{0.024875}{0.004975} = \mathbf{5.0000}$$
   $$95\%\ \text{CI} = \mathbf{[0.2434, 102.7291]}$$

---

## 4. Scientific Verdict & Integrity Certification

- The point estimate lies **strictly within** the corrected 95% confidence interval ($0.1374 \le 2.8613 \le 59.5984$).
- Path density prioritization produced **$2.86\times$ higher discovery yield per retrieval** and **$5.00\times$ higher yield per domain** than the remainder control.
- Because event counts are sparse, the Fisher p-value ($p \approx 0.50 - 0.54$) reflects low statistical power ($N=2$ events).
- The path density hypothesis remains classified as **`PROMISING`**, warranting scaled replication in Phase 2.
