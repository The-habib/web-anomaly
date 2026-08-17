# Archive Source Disagreement Report — Project Atlas Phase 1.5

**Project**: Atlas — Web Anomaly Laboratory  
**Phase**: 1.5  
**Date**: 2026-08-17T22:30:00Z  

---

## 1. Multi-Archive Coverage Comparison (Wayback vs Common Crawl)

Phase 1.5 evaluated **73 historical deep paths** across both Internet Archive Wayback Machine and Common Crawl CDX indices.

| Archive Agreement State | Count | Percentage | Research Interpretation |
| :--- | :--- | :--- | :--- |
| **`AGREE`** | 68 | 93.15% | Both archives confirm multi-year historical presence. |
| **`WAYBACK_ONLY`** | 5 | 6.85% | Observed in Wayback (1995–2002) but absent from Common Crawl index. |
| **`COMMONCRAWL_ONLY`** | 0 | 0.00% | No deep paths were uniquely in Common Crawl. |
| **`CONFLICTING`** | 0 | 0.00% | No contradictory status code records found. |

---

## 2. Root Cause of Wayback-Only Records

All 5 `WAYBACK_ONLY` paths represented early academic homepages (`/~faculty/`, `/~dept/`) created prior to Common Crawl's establishment (post-2007). 

This demonstrates that **Wayback Machine CDX queries remain indispensable for pre-2005 archaeological discovery**, while Common Crawl serves as an effective modern cross-validation layer.
