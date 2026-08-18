# Project Atlas — Domain-Level Primary Statistical Analysis (Phase 1.9)

## 1. Primary Inferential Unit: Domain Discovery ($Y_i \in \{0, 1\}$)

### $2 \times 2$ Contingency Table (Intent-to-Treat: $N=200$)
| Arm | Validated Discovery ($Y=1$) | No Discovery ($Y=0$) | Total Domains | Discovery Rate ($P$) |
| :--- | :--- | :--- | :--- | :--- |
| **Treatment (`DENSITY_PRIORITIZED`)** | 2 | 98 | 100 | **$2.00\%$** |
| **Control (`NEUTRAL_RANDOM`)** | 0 | 100 | 100 | **$0.00\%$** |
| **Total** | 2 | 198 | 200 | $1.00\%$ |

---

## 2. Statistical Estimators & Hypothesis Testing

### 1. Risk Difference ($RD = P_T - P_C$)
- **Point Estimate**: $\mathbf{RD = +0.0200}$ ($+2.00\%$).
- **95% Newcombe-Wilson Score Interval**: $[-0.0197, +0.0700]$.

### 2. Risk Ratio ($RR$)
- **Empirical Ratio**: $\infty$ ($2/0$).
- **Haldane-Anscombe Adjusted Ratio ($+0.5$)**: $\mathbf{RR_{\text{HA}} = 5.0000}$.
- **95% Confidence Interval**: $[0.2431, 102.8412]$.

### 3. Fisher's Exact Test
- **Two-Sided $p$-value**: $\mathbf{p = 0.4975}$.
- **One-Sided $p$-value ($H_1: P_T > P_C$)**: $\mathbf{p = 0.2487}$.

---

## 3. Subpopulation Analysis
- **Full-Exposure Population ($\ge 10$ paths)**:
  - Treatment: $2 / 69 = 2.90\%$
  - Control: $0 / 64 = 0.00\%$
  - Fisher exact two-sided $p = 0.4962$.
- **Per-Protocol Population (Successful HTTP)**:
  - Treatment: $2 / 65 = 3.08\%$
  - Control: $0 / 63 = 0.00\%$
  - Fisher exact two-sided $p = 0.4960$.
