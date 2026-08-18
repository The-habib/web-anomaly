# Project Atlas — Phase 1.9 Replication Results & Executive Synthesis

## 1. Key Experimental Outcomes

| Metric | Treatment Arm (`DENSITY_PRIORITIZED`) | Control Arm (`NEUTRAL_RANDOM`) | Disparity / Difference |
| :--- | :--- | :--- | :--- |
| **Randomized Domains ($N$)** | 100 domains | 100 domains | $1.00\times$ (Balanced) |
| **Baseline Mean Density ($d_{\text{raw}}$)** | $165.61$ | $166.65$ | $\Delta = -1.04$ ($p = 0.96$) |
| **Theoretical Retrieval Slots** | 1,000 slots | 1,000 slots | $1.0000\times$ (Exact Equality) |
| **Actual HTTP Requests Attempted** | 790 requests | 740 requests | $1.067\times$ |
| **Candidate Discoveries ($\ge 40$)** | 2 domains | 1 domain | $+1$ domain |
| **Validated Discoveries** | **2 domains** ($2.0\%$) | **0 domains** ($0.0\%$) | **$\mathbf{+2.0\%}$** |
| **Domain-Level Risk Difference ($RD$)** | **$+0.0200$** ($95\%\text{ CI: } [-0.0197, +0.0700]$) | — | — |
| **Haldane-Anscombe Risk Ratio ($RR_{\text{HA}}$)** | **$5.00$** ($95\%\text{ CI: } [0.24, 102.84]$) | — | — |
| **Two-Sided Fisher's Exact $p$-value** | **$p = 0.4975$** (One-sided $p = 0.2487$) | — | — |
| **Final Preregistered Classification** | **`PROMISING_BUT_UNCONFIRMED`** | — | Direction Replicated |

---

## 2. Synthesis of Findings
1. **Directional Replication**: Under strictly equal 10-slot retrieval budgets and matched baseline density, path-density prioritization successfully surfaced 2 authentic unmodernized archaeological discoveries in Treatment (`gwern.net` Rotten.com web mirror and `uspto.gov` MPEP 8th Edition table repository) versus 0 in Control.
2. **Statistical Power**: Because the total event count was small ($N_{\text{events}} = 2$), the domain-level Fisher exact test yielded $p = 0.4975$, and the 95% CI on Risk Difference crossed zero.
3. **Methodological Validity**: Zero protocol violations occurred: budget equality was exactly $1.0000\times$, candidate pools were identical, scoring was immutable, and review was double-blind.
