# Cost of Depth Analysis — Project Atlas Phase 1.5

**Project**: Atlas — Web Anomaly Laboratory  
**Phase**: 1.5  
**Date**: 2026-08-17T22:30:00Z  

---

## 1. Quantitative Resource Metrics

| Resource Dimension | Root Arm (Arm A) | Deep Arm (Arm B) | Total Expended | Increase Factor |
| :--- | :--- | :--- | :--- | :--- |
| **HTTP Requests** | 300 | 2,834 | 3,134 | 9.4x |
| **Archive CDX Queries** | 300 | 73 | 373 | 1.2x |
| **Data Ingress (Bytes)** | 187.9 MB | 281.9 MB | 469.9 MB | 2.5x |
| **Frozen HTML Payloads** | 300 | 2,460 | 2,760 | 9.2x |
| **Storage Footprint** | 45.2 MB | 421.1 MB | 466.3 MB | 10.3x |
| **Execution Runtime** | 185.0s | 1,045.86s | 1,230.86s (~20.5m) | 6.6x |

---

## 2. Unit Cost Analysis

- **Average Bandwidth per Domain**: 1.56 MB
- **Average Storage per Domain**: 1.55 MB
- **Average Runtime per Domain**: 4.10 seconds
- **Cost per Validated Discovery**: 469.9 MB / 1 discovery = 469.9 MB

---

## 3. Engineering Feasibility & Scalability
Running deep archaeology across 1,000 domains would require approximately **1.56 GB bandwidth**, **1.55 GB storage**, and **~1.1 hours** of processing time on standard Codespace hardware, confirming high engineering feasibility.
