# Project Atlas — Phase 1.3 Limitations & Boundary Analysis

**Document**: `reports/PHASE_1_3_LIMITATIONS.md`  
**Classification**: Scientific Transparency & Self-Correction Protocol  
**Phase**: Phase 1.3  

---

## 1. Documented Empirical Limitations

### 1. Root Landing Page Scope
- **Current Architecture**: Live HTTP inspection targets the canonical root landing page (`https://{domain}/`) and follows redirects.
- **Limitation**: Deep legacy subdirectories (e.g. `cmu.edu/~faculty/legacy/`) on institutional domains are not discovered when the root is fully modernized.
- **Future Direction**: Develop an architectural crawler that explores secondary navigation paths while aggregating domain-level scores.

### 2. Upstream Wayback CDX Latency & Rate Limits
- **Current Architecture**: Direct CDX API queries to `https://web.archive.org/cdx/search/cdx`.
- **Limitation**: Periodic upstream HTTP 429 / 503 throttling causes archive observation timeouts (18% in pilot).
- **Mitigation**: Robust multi-archive aggregation (Wayback CDX + Common Crawl indices + local mirror caches) with exponential jitter.

### 3. Minimalist Search Engine Edge Cases
- **Empirical Observation**: Search engine portals that intentionally serve sparse table-based HTML (`google.com`) without external framework wrappers can trigger legacy table heuristics.
- **Future Direction**: Introduce specific semantic tag requirements (`<doctype html>`, Flexbox/Grid CSS properties) to distinguish modern minimalist apps from 1990s table layouts.
