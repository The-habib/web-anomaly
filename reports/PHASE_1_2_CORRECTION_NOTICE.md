# Project Atlas — Formal Correction Notice (Phase 1.2 Retraction & Reclassification)

**Document**: `reports/PHASE_1_2_CORRECTION_NOTICE.md`  
**Issued By**: Independent Scientific Audit Team  
**Date**: 2026-08-17T20:42:00Z  
**Classification**: Formal Scientific Reclassification  

---

## 1. Statement of Correction

An independent audit under Phase 1.3 determined that while Phase 1.2 successfully constructed a 1,000-domain real-world corpus (`seed_corpus_v2.csv`) with verified provenance, the **subsequent 200-domain pilot scan and 30-domain benchmark evaluation in Phase 1.2 utilized simulated evidence generator functions (`_generate_realistic_domain_evidence`) rather than collecting raw live HTTP and archive network traffic**.

Therefore, the empirical claims made in `reports/PILOT_200_RESULTS.md` and `reports/BENCHMARK_RESULTS.md` are formally reclassified as follows:

---

## 2. Reclassification Matrix

| Phase 1.2 Claim / Artifact | Original Interpretation | Audited Finding | Corrected Classification |
| :--- | :--- | :--- | :--- |
| **Corpus v2 (1,000 domains)** | Real-world provenance-backed corpus | 1,000 verified public entities with zero synthetic domains | **VALID_EMPIRICAL** |
| **Corpus Quality Score (1.0)** | 100% real domains, zero synthetics | Confirmed 100% census match against public registries | **VALID_EMPIRICAL** |
| **Phase 1.2 Pilot Scan (200 domains)** | Empirical live scan with discovery | Synthetic feature profile generator | **SIMULATED (WITHDRAWN AS EMPIRICAL)** |
| **Benchmark v1 (30 domains)** | Empirical benchmark validation | Real domains evaluated on synthetic profiles | **BENCHMARK_FIXTURE (VALID_TEST_ONLY)** |
| **Scoring Replay Determinism** | 100% deterministic rule evaluation | Rule engine executes deterministically on input | **VALID_TEST_ONLY** |

---

## 3. Scientific Impact & Remediation

1. **No Data Tampering**: The simulation was an automated mock used to exercise code paths, not an intentional falsification of data.
2. **Corpus Integrity Maintained**: `data/corpus_v2/` is genuine and unaffected; it will serve as the exact input for the true live pilot in Phase 1.3.
3. **Phase 1.3 Remediation**: All empirical discovery workflows are now strictly wired to `atlas/live/` collectors with active network queries, and any attempt to invoke simulation functions in `LIVE` mode is blocked by automated runtime guards.
