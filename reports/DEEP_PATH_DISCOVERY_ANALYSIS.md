# Deep Path Discovery Analysis — Project Atlas Phase 1.5

**Project**: Atlas — Web Anomaly Laboratory  
**Phase**: 1.5  
**Date**: 2026-08-17T22:30:00Z  

---

## 1. Candidate Path Taxonomy Breakdown

During the 300-domain study, **4,812 candidate paths** were extracted across Wayback CDX and live HTML links, classified into 8 functional categories:

| Path Category | Pattern | Candidates Discovered | Selected for Retrieval | Relic Discovery Yield |
| :--- | :--- | :--- | :--- | :--- |
| **Academic User Space** | `~user/`, `/~[name]` | 412 | 185 | **High (Primary Yield)** |
| **Archive Directory** | `/old/`, `/archive/`, `/history/` | 684 | 310 | Medium |
| **Legacy Docs** | `/doc/`, `/man/`, `/rfc/` | 520 | 240 | Medium |
| **Public Files** | `/pub/`, `/files/`, `/downloads/` | 890 | 410 | Low (often modern mirrors) |
| **Year-Prefixed** | `/1995/`, `/1998/`, `/2000/` | 145 | 95 | **High (Vintage promotional)** |
| **Software Project** | `/projects/`, `/src/` | 630 | 280 | Low |
| **Personal / Blog** | `/personal/`, `/people/` | 510 | 220 | Low |
| **General Directory** | subpaths | 1,021 | 420 | Very Low |

---

## 2. Priority Scorer Performance

The candidate prioritizer successfully prioritized:
1. Academic user spaces with earliest observation dates ≤ 1996.
2. Direct `/archive/` and `/old/` directory paths.
3. Shallow directory trees (depth ≤ 2) over sprawling subtrees.

This reduced required network retrievals from 4,812 potential paths down to 2,834 targeted requests (a 41.1% bandwidth savings).
