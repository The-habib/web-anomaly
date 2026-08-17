# Project Atlas — Formal Correction Notice & Erratum (Phase 1.5)

**Document ID**: `ERRATUM-ATLAS-2026-001`  
**Phase Target**: Phase 1.5 Deep Web Archaeology & Root-vs-Depth Paired Study  
**Audit Phase**: Phase 1.6 Independent Scientific Audit  
**Date**: 2026-08-17T22:42:00Z  
**Classification**: **`AUDIT_VALID_WITH_CORRECTIONS`**  

---

## Executive Erratum Summary

An independent scientific audit of Phase 1.5 machine-readable artifacts (`data/phase1_5/`) conducted in Phase 1.6 revealed multiple reporting and narrative discrepancies between the published Phase 1.5 markdown reports (`reports/PHASE_1_5_*.md`, `ROOT_VS_DEEP_COMPARISON.md`, `DEEP_PATH_DISCOVERY_ANALYSIS.md`, `ARCHIVE_SOURCE_DISAGREEMENT.md`) and the underlying ground-truth datasets.

This notice formally documents all identified discrepancies, explains their operational causes, evaluates their scientific impact, and establishes the definitive reconciled values. **The underlying machine-readable dataset, frozen HTML payloads, and CDX logs remain cryptographically intact and valid.** The core experimental finding—that deep-path expansion uncovers authentic, unmodernized web anomalies completely obscured by modernized root portals (+1 incremental validated discovery with 0 incremental false positives)—remains fully supported by the data.

---

## 1. Itemized Correction Matrix

| Discrepancy ID | Item | Original Published Claim | Reconciled Ground Truth Data | Operational Cause | Scientific Impact |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **ERR-01** | **Validated Discovery Identity** | `cmu.edu` (`/~faculty/`) in Universities category | `thunix.net` (`/~cslug`) in Personal/independent sites category | Narrative carried over hypothetical limitation example from Phase 1.2/1.3 roadmaps rather than referencing the actual machine discovery dossier (`DISCOVERY_thunix_net.md`). | Narrative error only. The actual discovery is `thunix.net/~cslug` (Score 55.0, `CLEAR_ANOMALY`). `cmu.edu` was not in the 300-domain cohort and is marked **`CONTRADICTED`**. |
| **ERR-02** | **Root Candidate Category Distribution** | 1 University (`cmu.edu`), 1 Nonprofit, 1 Corporate FP (`sierratradingpost.com`) | 2 Open-Source (`fltk.org`, `haproxy.org`), 1 Personal (`toastytech.com`) | Fabricated category distribution in Table 1 of `ROOT_VS_DEEP_COMPARISON.md`. | Reporting error. Total candidate count (3 root, 4 deep, 1 incremental) was correct, but category attribution was misstated. |
| **ERR-03** | **Reference Recovery vs Discovery Yield** | "Recovered 4 of 7 reference relics (+33.3% candidate increase)" blended together | 4 of 7 reference relics recovered in isolated benchmark suite; exactly 1 new empirical discovery in 300-domain study | Conflation of known-label reference controls with open-world corpus yield. | Methodological reporting clarity. Reference recoveries and empirical discoveries must never be summed. |
| **ERR-04** | **Candidate Path Volume** | 4,812 candidate paths | 16,174 discovered candidate paths | Author manually constructed an 8-row category subtable that summed to 4,812 instead of reading `path_candidates.jsonl`. | Understated discovery volume. True candidate universe was 16,174 paths across 203 domains. |
| **ERR-05** | **Prioritizer Reduction Metric** | 41.1% bandwidth reduction (`(4,812 - 2,834) / 4,812`) | 82.48% candidate reduction (`(16,174 - 2,834) / 16,174`) | Mathematical formula applied to the erroneous 4,812 subtable total rather than true candidate count. | Understated prioritizer filtering efficiency. |
| **ERR-06** | **Archive Agreement Distribution** | 68 `AGREE`, 5 `WAYBACK_ONLY` across 73 evaluated paths | 73 `WAYBACK_ONLY` (100%) across 73 evaluated pre-2005 paths | Common Crawl index queried was modern snapshot `CC-MAIN-2024-10`, which contained zero captures for pre-2005 academic/personal paths. Narrative table was fabricated. | Common Crawl 2024 monthly index cannot validate pre-2005 URLs. Demonstrates Wayback Machine CDX is indispensable for vintage web archaeology. |
| **ERR-07** | **False Positive Attribution** | Residual FP claimed as `sierratradingpost.com` | 0 Corporate FPs in 300-domain study (`sierratradingpost.com` was not in cohort) | Carried over from Phase 1.4 benchmark evaluation notes into Phase 1.5 FP report. | Corrects false-positive attribution. Corporate cohort yielded 0 candidates and 0 false positives. |

---

## 2. Reconciled Root-vs-Deep Empirical Findings

### A. True Candidate & Discovery Yields (N=300 Domains)
- **Root Arm (Arm A)**: **3 candidates** (`fltk.org`, `haproxy.org`, `toastytech.com`), **0 validated discoveries**.
- **Deep Arm (Arm B)**: **4 candidates** (`fltk.org`, `haproxy.org`, `toastytech.com`, `thunix.net`), **1 validated discovery** (`thunix.net/~cslug`).
- **Incremental Candidates**: **+1** (`thunix.net`).
- **Validated Discoveries**: **+1** (`thunix.net/~cslug`, Score 55.0, unmodernized 1990s table/retro shell relic).
- **Incremental False Positives**: **0** (0.0% false-positive increase).

### B. True Category Distribution
| Domain Category | Domains Attempted | Root Candidates | Deep Candidates | Incremental Candidates | Validated Discoveries | False Positives |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Universities** | 60 | 0 | 0 | 0 | 0 | 0 |
| **Government** | 60 | 0 | 0 | 0 | 0 | 0 |
| **Nonprofits** | 45 | 0 | 0 | 0 | 0 | 0 |
| **Long-running Companies** | 45 | 0 | 0 | 0 | 0 | 0 |
| **Open-source / Projects** | 45 | 2 (`fltk.org`, `haproxy.org`) | 2 (`fltk.org`, `haproxy.org`) | 0 | 0 | 0 |
| **Personal / Independent** | 45 | 1 (`toastytech.com`) | 2 (`toastytech.com`, `thunix.net`) | **+1** (`thunix.net`) | **+1** (`thunix.net/~cslug`) | 0 |
| **TOTAL** | **300** | **3** | **4** | **+1** | **+1** | **0** |

---

## 3. Scientific Usability Verdict

Phase 1.5 remains **SCIENTIFICALLY USABLE** under classification **`AUDIT_VALID_WITH_CORRECTIONS`**. The underlying data collection, network requests, payload storage, and feature scoring were executed with full integrity. All future phases must reference the canonical machine datasets in `audit/phase1_6/` and `data/phase1_5/`.
