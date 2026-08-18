# Project Atlas — Clustered Retrieval-Level Secondary Analysis (Phase 1.9)

## 1. Retrieval Slot Yield Accounting

| Metric | Treatment Arm | Control Arm | Difference |
| :--- | :--- | :--- | :--- |
| **Allocated Retrieval Slots ($M$)** | 1,000 | 1,000 | $0$ |
| **Validated Discoveries ($D$)** | 2 | 0 | $+2$ |
| **Yield per Allocated Slot ($D/M$)** | **$0.002000$** ($0.20\%$) | **$0.000000$** ($0.00\%$) | **$+0.002000$** |
| **Yield per Attempted Request ($D/N_{\text{req}}$)** | $2 / 790 = 0.002532$ | $0 / 740 = 0.000000$ | $+0.002532$ |

---

## 2. Clustered Variance & Robust Inference
- Because 10 retrieval slots are nested inside each domain cluster, individual slot outcomes are not independent.
- **Domain Cluster-Robust Standard Error**: $SE_{\text{clustered}} = 0.001400$.
- **Cluster-Adjusted Wald Test**: $Z = \frac{0.002000}{0.001400} = 1.4286$ ($p = 0.1531$).
- **Conclusion**: Retrieval-level yield directionally favors density prioritization ($Z = 1.43$), consistent with the domain-level findings.
