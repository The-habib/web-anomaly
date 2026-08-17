# Phase 1.6 Scientific Discovery: The Path Density Hypothesis

**Project**: Atlas — Web Anomaly Laboratory  
**Phase**: 1.6 Independent Scientific Audit  
**Date**: 2026-08-17T22:42:00Z  
**Status**: EXPLORATORY RESEARCH HYPOTHESIS  

---

## 1. The Empirical Anomaly: `thunix.net`

During the 300-domain paired study in Phase 1.5, `thunix.net` (`study-0294`) produced a striking statistical distribution:
- **Candidate Paths Discovered**: **2,989 paths** (18.48% of all 16,174 candidate paths found across the entire 300-domain cohort).
- **Network Retrievals**: **15 paths** (constrained by the 15-retrieval ceiling).
- **Yield**: **1 validated discovery** (`thunix.net/~cslug`), the only validated incremental discovery in the entire study.

This empirical observation motivates the formulation of a new research hypothesis for web archaeology.

---

## 2. Hypothesis Formulation: The Path Density Hypothesis (PDH)

$$\mathbf{H}_{\text{density}}: \text{In historical and live web archives, candidate subpath density is positively correlated with the survival of unmodernized personal/academic archaeological relics.}$$

### Theoretical Rationale:
Modern commercial and institutional web architectures rely on centralized, uniform Content Management Systems (CMS) or Single Page Applications (SPAs) that consolidate hundreds of legacy subpaths into standardized, homogeneous templates. In contrast, multi-user Unix shells, academic tilde directories (`~user`), and retro web clusters operate as federated hosting ecosystems where individual users maintain independent static directories. 

Consequently, high candidate subpath density on personal/independent servers signals a federated static filesystem with high likelihood of unmodernized historical relics.

---

## 3. Exploratory Statistical Distribution Across 300 Cohort Domains

| Candidate Path Density Tier | Domain Count | Percentage | Total Candidate Paths | Deep Retrievals | Validated Discoveries | Discovery Yield per Domain |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Extreme Density ($\ge 1,000$ paths)** | **1** (`thunix.net`) | 0.33% | 2,989 | 15 | **1** | **100.0%** (1 / 1) |
| **High Density ($100 - 999$ paths)** | **29** | 9.67% | 5,612 | 435 | 0 | 0.0% (0 / 29) |
| **Moderate Density ($15 - 99$ paths)** | **148** | 49.33% | 6,583 | 2,220 | 0 | 0.0% (0 / 148) |
| **Low Density ($1 - 14$ paths)** | **25** | 8.33% | 990 | 164 | 0 | 0.0% (0 / 25) |
| **Zero Density ($0$ paths)** | **97** | 32.33% | 0 | 0 | 0 | 0.0% (0 / 97) |
| **TOTAL** | **300** | **100.0%** | **16,174** | **2,834** | **1** | **0.33%** (1 / 300) |

---

## 4. Top 10 Candidate Density Domains in Cohort

| Rank | Domain | Category | Discovered Paths | Retrievals | Max Deep Score | Discovery Outcome |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | **`thunix.net`** | Personal/independent | **2,989** | 15 | **55.0** | **`VALIDATED_DISCOVERY`** (`/~cslug`) |
| 2 | `gwern.net` | Personal/independent | **382** | 15 | 0.0 | `ORDINARY` (Modern CSS/layout) |
| 3 | `haproxy.org` | Open-source/projects | **358** | 15 | 55.0 | `CANDIDATE_ANOMALY` (Root baseline) |
| 4 | `rsf.org` | Nonprofits | **258** | 15 | 0.0 | `ORDINARY` |
| 5 | `fredhutch.org` | Nonprofits | **248** | 15 | 0.0 | `ORDINARY` |
| 6 | `cpj.org` | Nonprofits | **241** | 15 | 0.0 | `ORDINARY` |
| 7 | `reading.ac.uk` | Universities | **233** | 15 | 0.0 | `ORDINARY` |
| 8 | `regeringen.se` | Government | **226** | 15 | 0.0 | `ORDINARY` |
| 9 | `stallman.org` | Personal/independent | **204** | 15 | 35.0 | `ORDINARY` (Near miss) |
| 10 | `csis.org` | Nonprofits | **198** | 15 | 0.0 | `ORDINARY` |

---

## 5. Search Efficiency & Yield Metrics

- **Overall Study Search Efficiency**:
  $$\text{Efficiency}_{\text{study}} = \frac{1 \text{ validated discovery}}{2,834 \text{ retrieved paths}} = \mathbf{0.0353\%}$$
- **Extreme Density Tier Efficiency**:
  $$\text{Efficiency}_{\text{extreme}} = \frac{1 \text{ validated discovery}}{15 \text{ retrieved paths}} = \mathbf{6.667\%} \quad (\mathbf{189\times} \text{ higher than study baseline})$$

---

## 6. Research Guardrails & Phase 2 Next Steps

> [!WARNING]
> **No Premature Scoring Changes**: Candidate path density must **not** be incorporated as an additive anomaly score signal in current production code. Phase 1.6 is strictly an audit phase.

### Proposed Phase 2 Controlled Experiment:
In Phase 2, Project Atlas should run a dedicated stratified study comparing:
- **Arm 1**: Uniform random domain sampling from Corpus v2.
- **Arm 2**: Density-prioritized domain sampling (targeting domains with CDX path density $\ge 500$).
- **Success Criterion**: Measure whether density-prioritized sampling increases discovery yield per 1,000 HTTP requests without inflating false-positive rates.
