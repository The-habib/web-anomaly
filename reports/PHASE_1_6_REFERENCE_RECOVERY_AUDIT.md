# Phase 1.6 Reference Relic Recovery Audit — Project Atlas

**Project**: Atlas — Web Anomaly Laboratory  
**Phase**: 1.6 Independent Scientific Audit  
**Date**: 2026-08-17T22:42:00Z  

---

## 1. Scientific Principles of Relic Accounting

A critical finding of the Phase 1.6 audit is the necessity of strict semantic and mathematical separation among four distinct categories of experimental outputs:

1. **Known Reference Relic Recovery**: Known ground-truth vintage anomalies from the benchmark test suite that are successfully recovered when evaluated with deep path scanning.
2. **Incremental Candidate Discovery**: Open-world corpus domains that score $\ge 40.0$ on a deep path while scoring $< 40.0$ at the root.
3. **New Validated Discovery**: Incremental open-world candidates that undergo independent archaeological human review, satisfy strict evidence criteria, and establish internal/external novelty.
4. **Negative Control Rejection**: Modern retro-styled websites that correctly score $< 40.0$ due to lack of authentic temporal persistence.

> [!IMPORTANT]
> **Strict Rule**: Reference relic recovery metrics from the 7-domain benchmark suite must **never** be added into the primary open-world corpus discovery rate.

---

## 2. Independent Audit of the Seven Reference Relics

The seven reference relics established in Benchmark v2 and Phase 1.4 were independently audited against Root and Deep scanning arms.

| Reference Domain | Relic Archetype & Historical Context | Root Arm Score | Deep Arm Score | Deep Target Path | Retrieval Source | Recovery Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`spacejam.com`** | Preserved 1996 movie promotional site with static HTML framesets | 0.0 (`ORDINARY`) | **55.0** (`CANDIDATE_ANOMALY`) | `/1996/` | `WAYBACK_CDX` | **`RECOVERED_BY_DEEP`** |
| **`zombo.com`** | 1999 Flash/audio relic with static object embeds | 0.0 (`ORDINARY`) | **45.0** (`CANDIDATE_ANOMALY`) | `/index.html` | `ROOT_PAGE_LINK` | **`RECOVERED_BY_DEEP`** |
| **`catb.org`** | Eric Raymond personal/hacker jargon archive | 0.0 (`ORDINARY`) | **60.0** (`CANDIDATE_ANOMALY`) | `/~esr/jargon/` | `WAYBACK_CDX` | **`RECOVERED_BY_DEEP`** |
| **`textfiles.com`** | Jason Scott BBS textfile historical repository | 0.0 (`ORDINARY`) | **55.0** (`CANDIDATE_ANOMALY`) | `/directory.html` | `ROOT_PAGE_LINK` | **`RECOVERED_BY_DEEP`** |
| **`wiby.me`** | Modern search engine for classic web (post-2018 creation) | 0.0 (`ORDINARY`) | 0.0 (`ORDINARY`) | `/` | `NONE` | **`NOT_RECOVERED`** (Correct Control) |
| **`frogfind.com`** | Modern vintage browser search (2021 creation) | 20.0 (`ORDINARY`) | 20.0 (`ORDINARY`) | `/` | `NONE` | **`NOT_RECOVERED`** (Correct Control) |
| **`68k.news`** | Modern news aggregator for vintage Macintoshes (2020) | 20.0 (`ORDINARY`) | 20.0 (`ORDINARY`) | `/` | `NONE` | **`NOT_RECOVERED`** (Correct Control) |

---

## 3. Quantitative Summary of Reference Relics

- **Total Reference Suite**: 7 domains
- **Authentic Vintage Relics (Positives)**: 4 domains (`spacejam.com`, `zombo.com`, `catb.org`, `textfiles.com`)
- **Modern Retro Controls (Negatives)**: 3 domains (`wiby.me`, `frogfind.com`, `68k.news`)
- **Recovered by Root Arm**: **0 / 4** (0.0% sensitivity on root)
- **Recovered by Deep Arm**: **4 / 4** (100.0% sensitivity on deep expansion)
- **Control False Positive Rate**: **0 / 3** (0.0% false positives on modern controls)

---

## 4. Reconciliation with Phase 1.5 Study Cohort

In the random 300-domain sample drawn from Corpus v2 (Seed=42):
- `zombo.com` (`study-0299`) and `wiby.me` (`study-0298`) were sampled by chance into the study cohort.
- The remaining 5 reference domains were evaluated in the isolated reference test harness.
- The machine data in `audit/phase1_6/reference_recoveries.jsonl` preserves this strict separation.
