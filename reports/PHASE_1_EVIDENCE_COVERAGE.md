# Project Atlas — Phase 1 Evidence Coverage & Completeness Audit

**Audit Phase**: `Phase 1.1 Independent Scientific Audit`  
**Dataset Audited**: `experiments/0002/evidence/raw/` (N=1,000)  
**Frozen Manifest**: `experiments/0002/evidence/frozen/frozen_manifest.json`  

---

## 1. Executive Summary

This audit assesses the completeness of raw observational artifacts collected across all 1,000 domains in the Phase 1 seed corpus.

### Coverage Census:
- **Total Domains Inspected**: `1,000`
- **Complete Evidence Dossiers** (Live HTML + Clean Text + CDX Timeline + Bundle JSON): **666 domains (66.6%)**
- **Partial Evidence Dossiers** (Offline / Unresolvable / Dead Domains with Timeline + Bundle JSON): **334 domains (33.4%)**
- **Total Frozen Artifacts**: **3,332 files** (**121.99 MB**)

---

## 2. Artifact Matrix by Category

| Category | Total Domains | Live HTML & Text | CDX Timeline JSON | Complete Dossier Share (%) |
| :--- | :---: | :---: | :---: | :---: |
| **Universities** | 200 | 178 | 200 | 89.0% |
| **Government** | 200 | 148 | 200 | 74.0% |
| **Nonprofits** | 150 | 102 | 150 | 68.0% |
| **Long-running companies** | 150 | 104 | 150 | 69.3% |
| **Open-source projects** | 150 | 88 | 150 | 58.7% |
| **Personal / Independent** | 150 | 46 | 150 | 30.7% |
| **TOTAL** | **1,000** | **666** | **1,000** | **66.6%** |

---

## 3. Cryptographic Hash Audit

- All **3,332 artifact files** listed in `frozen_manifest.json` were re-hashed against disk contents.
- **Match Rate**: **100.0%** (0 corrupted, 0 missing, 0 hash mismatches).
