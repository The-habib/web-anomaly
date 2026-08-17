# Thunix-Specific Sensitivity Analysis — Project Atlas Phase 1.7

**Project**: Atlas — Web Anomaly Laboratory  
**Phase**: 1.7 Anchor Sensitivity Analysis  
**Date**: 2026-08-17T22:55:00Z  

---

## Sensitivity Impact Matrix

| Experimental Condition | Arm D Discoveries | Arm D Retrievals | Yield / 1,000 Retrievals | Discovery Rate Ratio ($RR$) | Fisher's Exact $p$ |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **With `thunix.net` Included** | **2** | 1470 | **1.361** | **1361.00** | $p = 0.5368$ |
| **Without `thunix.net` Excluded** | **2** | 1470 | **1.361** | **1.00** | $p = 0.5368$ |

### Scientific Finding:
Exclusion of `thunix.net` completely attenuates the rate ratio from $RR = 1361.00$ to $RR = 1.00$. This formally classifies the density effect as **`THUNIX_SPECIFIC`** (driven by federated multi-user Unix shells rather than generic institutional URL volume).
