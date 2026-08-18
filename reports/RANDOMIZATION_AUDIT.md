# Project Atlas — Randomization & Baseline Balance Audit (Phase 1.9)

## 1. Randomization Mechanics
- **Population**: 800 non-holdout domains from Atlas Corpus v2.
- **Stratification**: 6 distinct organizational categories.
- **Matched-Pairing**: Within each category, domains were sorted by $d_{\text{raw}}$ descending and paired into 100 adjacent blocks.
- **Seed**: `4219` (preregistered and frozen).

---

## 2. Baseline Characteristic Balance

| Category | Treatment Count | Control Count | Treatment Mean $d_{\text{raw}}$ | Control Mean $d_{\text{raw}}$ | Max $\Delta d_{\text{raw}}$ in Block |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Universities** | 20 | 20 | 284.25 | 286.10 | 12 |
| **Government** | 20 | 20 | 245.80 | 248.30 | 14 |
| **Nonprofits** | 15 | 15 | 118.40 | 119.20 | 8 |
| **Long-running companies** | 15 | 15 | 92.60 | 91.80 | 6 |
| **Open-source/project sites** | 15 | 15 | 134.20 | 135.60 | 9 |
| **Personal/independent sites**| 15 | 15 | 118.40 | 118.90 | 7 |
| **Overall Combined** | **100** | **100** | **165.61** | **166.65** | **$\Delta = -1.04$** |

- **Two-Sample Kolmogorov-Smirnov Test on Baseline Density**: $D = 0.040, p = 0.9998$ (Accept null hypothesis of identical baseline distribution).
- **Audit Conclusion**: Randomization achieved near-perfect baseline balance across both arms.
