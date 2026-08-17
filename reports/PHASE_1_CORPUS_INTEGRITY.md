# Project Atlas — Phase 1 Corpus Integrity & Provenance Audit

**Audit Phase**: `Phase 1.1 Independent Scientific Audit`  
**Dataset Audited**: `data/seed_corpus.csv` (N=1,000)  
**Date**: 2026-08-17  
**Provenance Lineage**: Documented in `data/corpus_provenance.jsonl`

---

## 1. Executive Summary

A comprehensive 100% census audit was conducted on all **1,000 domains** in `data/seed_corpus.csv`. The audit cross-referenced each domain against curated public registries, the procedural generation algorithm in `atlas/phase1/corpus.py`, and public DNS records.

### Headline Integrity Statistics:
- **Total Corpus Rows**: `1,000`
- **Unique Domains**: `1,000` (100.0%)
- **Verified Real Curated Domains**: `901` (**90.1%**)
- **Confirmed Synthetic Pattern Domains**: `99` (**9.9%**)
- **Duplicate Records**: `0`
- **Unknown Origin**: `0`

---

## 2. Provenance Distribution by Category

| Category | Claimed Quota | Real Curated Domains | Synthetic Domains | Real Share (%) |
| :--- | :---: | :---: | :---: | :---: |
| **Universities** | 200 | 200 | 0 | 100.0% |
| **Government** | 200 | 184 | 16 | 92.0% |
| **Nonprofits** | 150 | 128 | 22 | 85.3% |
| **Long-running companies** | 150 | 132 | 18 | 88.0% |
| **Open-source/project sites** | 150 | 133 | 17 | 88.7% |
| **Personal/independent sites** | 150 | 124 | 26 | 82.7% |
| **TOTAL** | **1,000** | **901** | **99** | **90.1%** |

---

## 3. Root Cause of Synthetic Domain Generation

In `atlas/phase1/corpus.py`, when curated candidate pools contained fewer entries than the category quota, the generator procedural loop (`lines 207–226`) synthesized pattern domains:
- `univ-NNN.edu` / `college-NNN.ac.uk`
- `dept-NNN.gov` / `agency-NNN.gov.uk`
- `foundation-NNN.org` / `institute-NNN.org`
- `corp-NNN.com` / `industries-NNN.co.uk`
- `project-NNN.org` / `foss-NNN.net`
- `tilde-user-NNN.org` / `personal-site-NNN.net`

### Experimental Impact:
1. **Preflight Behavior**: All 99 synthetic pattern domains failed live DNS preflight resolution (`DNS_FAILURE` or `CONNECTION_ERROR`), contributing to the observed preflight drop rate (671 / 1,000 passed).
2. **Scoring Isolation**: None of the 99 synthetic domains triggered candidate anomaly scores (all scored 0 with 0 confidence), meaning synthetic data did not leak into the discovered candidate set.
3. **Scientific Implication**: While harmless to anomaly discovery, synthetic placeholders artificially inflated the nominal corpus size from 901 real domains to 1,000 rows. Future phases must draw strictly from verified real-world seed lists without procedural padding.
