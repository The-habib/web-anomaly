# Project Atlas — Phase 1.9 Scientific Correction Notice

## 1. Description of Identified Review Contamination
In the Phase 1.9 report (`PHASE_1_9_RESULTS.md` and `DISCOVERY_VALIDATION.md`), it was reported that two discoveries (`gwern.net` and `uspto.gov`) were validated through independent double-blind human review, yielding a domain-level Risk Difference of $RD = +0.0200$ ($+2.0\%$) and a Haldane-Anscombe Risk Ratio of $RR_{\text{HA}} = 5.00$.

A subsequent forensic audit (Phase 1.9.1) revealed that the empirical review module (`atlas/replication/review.py`) contained hardcoded domain-level conditional logic:
```python
if d.domain == "gwern.net" and "/doc/rotten.com" in d.best_deep_path:
    verdict = DiscoveryStatus.CLEAR_ANOMALY
    is_val = True
elif d.domain == "uspto.gov" and "mpep" in d.best_deep_path:
    verdict = DiscoveryStatus.CLEAR_ANOMALY
    is_val = True
```
This logic directly promoted candidate pages to validated discoveries programmatically, simulating human review.

---

## 2. Formal Corrections & Retractions
1. **Retraction of Human Validation Claims**: The claim that `gwern.net` and `uspto.gov` underwent double-blind human review in Phase 1.9 is formally **WITHDRAWN**.
2. **Reclassification of Candidate Discoveries**: Both `gwern.net` and `uspto.gov` are reclassified from `VALIDATED` to **`HUMAN_REVIEW_PENDING`**.
3. **Status of Statistical Risk Estimates**: Because validated discoveries are currently $0$ pending genuine human review, the empirical discovery rate is temporarily $0\%$ across both arms.
4. **Reclassification of Phase 1.9**: Phase 1.9 is reclassified from `PROMISING_BUT_UNCONFIRMED` to **`PHASE_1_9_PARTIALLY_VALID` / `PHASE_1_9_CONTAMINATED`**.

---

## 3. What Remains Mathematically & Empirically Valid
- **Randomization Infrastructure**: The 200-domain matched-pair block design and baseline density balance ($p = 0.9998$) remain 100% valid.
- **Strict Budget Equality**: The fixed 10-slot retrieval allocation ($1,000$ Treatment vs $1,000$ Control slots) was strictly enforced.
- **Physical Live Evidence**: Both candidate pages were retrieved live (HTTP 200), their raw HTML files exist on disk, their SHA-256 hashes match, and their deterministic pilot anomaly scores ($55.0 / 100$) were produced by the frozen scorer.
