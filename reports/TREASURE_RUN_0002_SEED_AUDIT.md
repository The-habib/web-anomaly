# Project Atlas — Treasure Run #002 Seed & Contamination Forensic Audit
## Comprehensive Repository Audit & Decontamination Catalog

**Date**: 2026-08-18  
**Experiment**: `TREASURE_RUN_0002`  
**Status**: Pre-Implementation Forensic Clearance  
**Auditor**: Project Atlas Archaeological Governance Engine  

---

## Executive Summary

To ensure **Treasure Run #002** satisfies the strict **No-Seed Policy** and operates under **Blind Discovery** without hard-coded answers, fabricated history, or automatic validation, a complete codebase scan was conducted across all files.

### Audit Category Summary

| Classification | Description | Status / Action |
| :--- | :--- | :--- |
| **PRODUCTION_CONTAMINATION** | Hard-coded seeds, hint paths, fabricated capture years, or automatic validation in `atlas/treasure/`. | **Immediate Complete Removal / Refactoring in Run #002.** |
| **PRODUCTION_RISK** | Logic in `atlas/treasure/` requiring runtime mode isolation. | **Guarded under LIVE_BLIND mode assertions.** |
| **TEST_ONLY** | Unit test fixtures and mock candidates in `tests/`. | **Maintained in isolated test suite.** |
| **SIMULATION_ONLY** | Synthetic simulations from prior benchmark phases. | **Blocked from LIVE_BLIND import via runtime guards.** |
| **REFERENCE_ONLY** | Historical benchmarks and reference controls. | **Quarantined to post-hoc evaluation only.** |
| **DOCUMENTATION** | Scientific reports, historical hypotheses, and docs. | **Maintained for historical research continuity.** |
| **HISTORICAL_ARCHIVAL** | Frozen run outputs and legacy corpus provenance. | **Preserved in historical storage.** |

---

## Production Contamination Breakdown & Remediation Plan

### 1. `atlas/treasure/discovery.py`
- **Contamination**: `KNOWN_ARCHAEOLOGICAL_SEEDS` contained 10 hard-coded domains (`gwern.net`, `uspto.gov`, `gnu.org`, `tilde.club`, `thunix.net`, `toastytech.com`, `mit.edu`, `stanford.edu`, `cern.ch`, `textfiles.com`) with `hint_paths`.
- **Contamination**: Injected seed paths into domain candidate lists during candidate generation.
- **Contamination**: Hardcoded domain match for `"rotten.com"` under `WEB_ODDITY`.
- **Contamination**: Hardcoded default historical span (`1998-2024`, 26 years, 12 captures).
- **Contamination**: Sliced domain pool before shuffling (`domains_pool[:limit_domains]`).
- **Remediation**:
  1. Remove `KNOWN_ARCHAEOLOGICAL_SEEDS` entirely.
  2. Remove hint path injection.
  3. Replace domain slicing with deterministic full-population stratified sampling from Atlas Corpus v2 (`seed=101`).
  4. Query live CDX API for authentic timestamps and years; set `None`/`0` if unavailable without fabricated defaults.
  5. Remove all domain-specific strategy matches.

### 2. `atlas/treasure/investigator.py`
- **Contamination**: Hardcoded automatic promotion: `if score >= 50.0 and deep_ev.live_status_code == 200: decision = TreasureDecision.TREASURE_VALIDATED`.
- **Contamination**: Hardcoded domain-specific prior art rules for `"rotten.com"`, `"halifax"`, `"mpep"`.
- **Remediation**:
  1. Strictly prohibit machine validation. Candidates with score >= 50 are assigned `CandidateState.REVIEW_PENDING` and nominated to `potential_treasures.jsonl`.
  2. Only imported genuine human review submissions can transition a candidate to `HUMAN_VALIDATED` / `TREASURE_VALIDATED`.
  3. Remove all domain-specific prior art rules.

### 3. `atlas/treasure/prior_art.py`
- **Contamination**: Hardcoded lists `WELL_KNOWN_SITES` and `DOCUMENTED_ARCHIVES`.
- **Remediation**: Refactor into generic structural obscurity assessment and quarantine known landmark matching strictly to post-hoc reference evaluation.

---

## Quarantined Reference World Setup

Reference domains are strictly separated from production discovery and saved in:
- `data/reference_controls/reference_domains.json`
- `data/reference_controls/reference_comparison.jsonl`

These files are evaluated **only after** blind discovery and investigations are frozen.

---

## Certification

All identified `PRODUCTION_CONTAMINATION` and `PRODUCTION_RISK` items in the production discovery pathway are scheduled for immediate elimination in Treasure Run #002.
