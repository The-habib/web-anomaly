# Category Confound Analysis — Project Atlas Phase 1.7

**Project**: Atlas — Web Anomaly Laboratory  
**Phase**: 1.7 Confound Isolation  
**Date**: 2026-08-17T22:55:00Z  

---

## 1. Category vs Density Distribution

Institutional and academic domains (Universities, Government) naturally possess high candidate URL volume due to multi-departmental size rather than vintage unmodernized status.

| Category | Mean $D_{\text{raw}}$ | Median $D_{\text{raw}}$ | P95 $D_{\text{raw}}$ | Archaeological Yield | Confound Risk |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Universities** | 85.4 | 52.0 | 240.0 | 0.0% | **High (Large modern CMS size)** |
| **Government** | 72.1 | 44.0 | 195.0 | 0.0% | **High (Large administrative portals)** |
| **Nonprofits** | 48.2 | 28.0 | 180.0 | 0.0% | Medium |
| **Companies** | 35.6 | 18.0 | 120.0 | 0.0% | Low |
| **Open-source / Projects** | 22.4 | 14.0 | 95.0 | 0.0% | Low |
| **Personal / Independent** | 18.2 | 8.0 | 382.0 (`thunix`) | **2.2%** | **Low (Federated user static files)** |

*Conclusion*: Generic URL volume on institutional domains is confounded with organizational scale. User-space density ($D_{\text{user}}$) on personal/independent servers is the true predictive feature.
