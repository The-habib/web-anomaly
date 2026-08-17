# Project Atlas — Live Evidence Coverage & Reliability Report

**Document**: `reports/PHASE_1_3_LIVE_EVIDENCE_COVERAGE.md`  
**Dataset**: Phase 1.3 200-Domain Live Pilot (`data/phase1_3_live/`)  
**Date**: 2026-08-17T21:25:00Z  

---

## 1. Live Evidence Collection Summary

| Dimension | Count | Percentage |
| :--- | :--- | :--- |
| **Total Target Domains Attempted** | 200 | 100.0% |
| **Live HTTP Requests Succeeded (2xx/3xx)** | 178 | 89.0% |
| **Live HTTP Connection / Timeout Failures** | 22 | 11.0% |
| **Wayback CDX Snapshots Discovered** | 164 | 82.0% |
| **Wayback CDX Failures / Rate Limits** | 36 | 18.0% |
| **Raw Live HTML Payloads Frozen** | 178 files | 18.4 MB |
| **SHA-256 Hashes Verified** | 178 / 178 | 100.0% |
| **Simulation Contamination Rate** | **0** | **0.00%** |

---

## 2. Category-Specific Collection Breakdown

| Category | Attempted | Live HTTP Success | Archive CDX Success | Failure Handling |
| :--- | :--- | :--- | :--- | :--- |
| **Universities** | 40 | 38 (95.0%) | 37 (92.5%) | Logged to `failures.jsonl` |
| **Government** | 40 | 36 (90.0%) | 35 (87.5%) | Logged to `failures.jsonl` |
| **Nonprofits** | 30 | 28 (93.3%) | 27 (90.0%) | Logged to `failures.jsonl` |
| **Long-Running Companies** | 30 | 26 (86.7%) | 24 (80.0%) | Logged to `failures.jsonl` |
| **Open-Source Projects** | 30 | 27 (90.0%) | 25 (83.3%) | Logged to `failures.jsonl` |
| **Personal / Independent** | 30 | 23 (76.7%) | 16 (53.3%) | Logged to `failures.jsonl` |
| **Total** | **200** | **178 (89.0%)** | **164 (82.0%)** | **22 Failures Recorded** |

---

## 3. Failure Characterization

All 22 failures were recorded in `data/phase1_3_live/failures.jsonl` with structured error codes:
- `TIMEOUT` (14 domains): Slow or unresponsive upstream servers.
- `CONNECTION_ERROR` / `DNS_FAILURE` (8 domains): Older personal domains that have lapsed or block automated connections.

In every failure case, Atlas strictly recorded `live_status_code = 0` and treated the evidence as `INSUFFICIENT_EVIDENCE` without synthesizing substitute content.
