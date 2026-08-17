# Project Atlas — Discovery Taxonomy & Findings Ledger

This document defines what constitutes a verified scientific discovery within Project Atlas, the classification taxonomy, and the master findings ledger.

---

## 🏛️ Definition of a Discovery

In Project Atlas, an observation is officially designated as a **Discovery** if and only if:
1. It is backed by cryptographic hashes (SHA-256) of collected raw HTML, rendered screenshots, and structured evidence.
2. It satisfies at least one verifiable anomaly condition (e.g., >= 15 years persistence, structural resurrection, legacy technology fossil).
3. It achieves an Anomaly Score >= 4 based on the scoring ruleset (`atlas/config/scoring_rules.json`).
4. The evidence is completely reproducible using the automated pipeline.

---

## 🏷️ Anomaly Classification Taxonomy

| Tier | Classification | Score Range | Description |
| :--- | :--- | :---: | :--- |
| **Tier-1** | **Major Web Anomaly** | `Score >= 8` | Rare, multi-signal anomaly (e.g., 20+ year survivor with legacy Flash/HTML 3.2 markup and resurrection history). |
| **Tier-2** | **Significant Historical Anomaly** | `5 <= Score <= 7` | Substantial archaeological or structural anomaly (e.g., active unlinked sitemap or surviving orphaned department archive). |
| **Tier-3** | **Minor Temporal / Structural Anomaly** | `2 <= Score <= 4` | Measurable historical footprint or minor robots.txt discrepancy. |
| **Baseline**| **Standard Web Surface** | `Score < 2` | Standard modern commercial or dynamic web page with typical lifecycle. |

---

## 📋 Master Findings Ledger

| Finding ID | Target URL | Score | Classification | Discovery Date | Report Dossier |
| :--- | :--- | :---: | :--- | :---: | :--- |
| `ATLAS-20260817-example_com_2026` | `https://example.com` | `7` | Tier-2 Significant Historical Anomaly | 2026-08-17 | [REPORT_ATLAS-20260817-example_com_2026.md](reports/REPORT_ATLAS-20260817-example_com_2026.md) |

---

## 🔍 Validation Protocol

Before any finding is added to this ledger:
1. Verify screenshot in `evidence/screenshots/`.
2. Check temporal timeline consistency in `evidence/timeline/`.
3. Validate HTML hash integrity against `evidence/html/`.
4. Confirm reproduction command runs cleanly via `atlas scan <URL>`.
