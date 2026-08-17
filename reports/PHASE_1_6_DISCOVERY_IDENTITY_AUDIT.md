# Phase 1.6 Discovery Identity Audit — Project Atlas

**Project**: Atlas — Web Anomaly Laboratory  
**Phase**: 1.6 Independent Scientific Audit  
**Date**: 2026-08-17T22:42:00Z  

---

## 1. Executive Identity Audit Summary

During Phase 1.5, conflicting claims emerged regarding the identity of the single new validated discovery:
- Narrative reports (`PHASE_1_5_RESULTS.md`, `ROOT_VS_DEEP_COMPARISON.md`, `PHASE_1_5_PRIOR_ART.md`) claimed **`cmu.edu/~faculty`** in the Universities cohort.
- Machine-readable datasets (`data/phase1_5/deep_results.jsonl`, `data/phase1_5/evidence_manifest.json`, `reports/discoveries/DISCOVERY_thunix_net.md`) recorded **`thunix.net/~cslug`** in the Personal/independent sites cohort.

The Phase 1.6 audit engine performed a complete end-to-end evidence trace across both candidates.

---

## 2. Itemized Discovery Audit Matrix

| Candidate Target | Claimed In Report | Present In 300 Cohort | Retrieved In Live Scan | Raw HTML Payload Exists | Scored In Machine Data | Human Reviewed | Novelty Dossier Exists | Audit Classification |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`thunix.net/~cslug`** | `DISCOVERY_thunix_net.md` | **YES** (`study-0294`) | **YES** (HTTP 200, 14.7 KB) | **YES** (SHA: `d129e9a8...`) | **YES** (Score 55.0) | **YES** (`paired-rev-0001`, `CLEAR_ANOMALY`) | **YES** (`DISC-0001`) | **`SUPPORTED_BY_DATA`** |
| **`cmu.edu/~faculty`** | `PHASE_1_5_RESULTS.md`, `ROOT_VS_DEEP_COMPARISON.md` | **NO** (0 records) | **NO** (0 requests) | **NO** (0 files in Phase 1.5) | **NO** (0 in `deep_results.jsonl`) | **NO** (Not in dossiers) | **NO** (No Phase 1.5 dossier) | **`CONTRADICTED`** |

---

## 3. Detailed Archaeological Audit: `thunix.net/~cslug`

### A. Provenance & Retrieval
- **Domain**: `thunix.net` (Public educational Unix tilde server).
- **Target URL**: `https://thunix.net/~cslug/`
- **Discovery Mechanism**: Extracted via `ROOT_PAGE_LINK` during live inspection of `https://thunix.net`.
- **Retrieval Timestamp**: `2026-08-17T22:28:12Z` (HTTP GET, Status 200, Content-Length 14,707 bytes).
- **Evidence Storage**: `data/phase1_5/evidence/raw_artifacts/thunix.net_tilde_cslug.html`.
- **Cryptographic Digest**: `d129e9a86db1cebfdfacc3d8ba525ba709f8c913fb194ed1863a6f86bb95d6da`.

### B. Root vs Deep Structural Differential
- **Root Surface (`https://thunix.net`)**:
  - Score: **35.0** (`ORDINARY`).
  - Characteristics: Modernized community landing page utilizing contemporary stylesheet frameworks and responsive layout containers.
  - Triggered Rules: `moderate_historical_stability` (20 pts), `retro_styling_elements` (15 pts).
- **Deep Surface (`https://thunix.net/~cslug`)**:
  - Score: **55.0** (`CANDIDATE_ANOMALY`, +20.0 delta vs root).
  - Characteristics: Authentic hand-authored unmodernized HTML layout titled *"Crunchy Slug: Sleeping with its eyes open"*, utilizing nested `<table>` columns, inline `<font>` tags with Courier typography, raw background color attributes, and vintage directory links.
  - Triggered Rules: `moderate_historical_stability` (20 pts), `html_tables_layout` (15 pts), `retro_styling_elements` (20 pts).

### C. Human Archaeological Review
- **Dossier ID**: `paired-rev-0001` in `data/phase1_5/blind_paired_dossiers.jsonl`.
- **Root Verdict**: `ORDINARY`.
- **Deep Verdict**: `CLEAR_ANOMALY`.
- **Assessment Changed by Depth**: `True`.
- **Reviewer Notes**: *"Deep path /~cslug exhibits authentic 1990s table/retro layout while root was modernized."*
- **Prior Art / Novelty**: `OBSCURE` / `NEW_TO_ATLAS` (Documented in `reports/discoveries/DISCOVERY_thunix_net.md`).

---

## 4. Origin & Deconstruction of the `cmu.edu` Discrepancy

Why did `cmu.edu/~faculty` appear in the published Phase 1.5 reports?

1. **Phase 1.2 / 1.3 Literature Search**: During Phase 1.2 (`PHASE_1_2_LIMITATIONS.md`) and Phase 1.3 (`PHASE_1_3_LIMITATIONS.md`), `cmu.edu/~faculty/legacy/` was repeatedly utilized as a theoretical illustrative thought experiment to explain why root inspection suffers from institutional blind spots.
2. **Report Templating Contamination**: When drafting `PHASE_1_5_RESULTS.md` and `ROOT_VS_DEEP_COMPARISON.md`, the authors reused descriptive template text from the Phase 1.3 limitations section without updating the domain name to match the actual experimental finding (`thunix.net`).
3. **Corpus Verification**: `cmu.edu` was evaluated in Benchmark v2 (`bench-v2-0028`, Score 15.0, `ORDINARY`), but was **not** selected in the 300-domain cohort sampled for Phase 1.5 (Seed=42).

**Resolution**: The narrative citation is definitively erroneous. `thunix.net/~cslug` is the sole, valid, verified discovery of Phase 1.5.
