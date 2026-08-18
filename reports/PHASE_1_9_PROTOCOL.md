# Project Atlas — Phase 1.9 Master Replication Protocol

## 1. Executive Summary & Experimental Objectives
Phase 1.9 is a preregistered, randomized, controlled replication experiment designed to address the experimental design limitations identified during the Phase 1.8 audit of Phase 1.7:
1. **Arm Sampling Asymmetry Resolved**: Rather than sampling Arm D from the upper density tail and Arm U from the remainder, Phase 1.9 employs a **matched-pair randomized block design** within each category.
2. **Realized Budget Disparity Resolved**: Every domain receives a strictly fixed allocation of **10 retrieval slots** (1,000 Treatment slots vs 1,000 Control slots).
3. **Unit of Inference Aligned**: The primary inferential unit is **DOMAIN** ($Y_i \in \{0, 1\}$), evaluating the probability of discovering a validated archaeological surface.

---

## 2. Experimental Design & Randomization Architecture
- **Eligible Population**: 800 non-holdout domains from Atlas Corpus v2.
- **Stratification**: 6 categories (40 Universities, 40 Government, 30 Nonprofits, 30 Long-running companies, 30 Open-source projects, 30 Independent sites = 200 domains).
- **Matching & Blocking**: Within each category, domains were sorted by baseline density ($d_{\text{raw}}$) and grouped into 100 adjacent matched pairs.
- **Random Assignment**: Pseudo-random coin flip (`seed=4219`) assigned one domain to **Treatment** (`COHORT_ALPHA`) and one to **Control** (`COHORT_BETA`).

---

## 3. Path Ordering & Candidate Pool Equality
- For every domain, an identical candidate path pool was gathered from historical CDX and archive indices.
- **Treatment Arm**: Candidate paths ordered by density-informed priority (user directories, vintage document extensions, archive persistence).
- **Control Arm**: Candidate paths ordered by neutral deterministic random shuffle (`seed=999 + hash(domain)`).
- Exactly 10 retrieval slots per domain were evaluated. Slots on domains with $< 10$ available paths were marked as `EMPTY_POOL_EXHAUSTED`.

---

## 4. Blinding & Scoring Immutability
- Reviewers were blinded to treatment assignment, density scores, and domain ranks.
- The Atlas scoring engine weights and fossil detection rules were strictly frozen.
