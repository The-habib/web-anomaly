# Project Atlas — Budget Equality Audit (Phase 1.9)

## 1. Theoretical vs Realized Budget Accounting

| Budget Level | Treatment Arm | Control Arm | Equality Ratio |
| :--- | :--- | :--- | :--- |
| **Allocated Retrieval Slots** | 1,000 slots (10/dom) | 1,000 slots (10/dom) | **$1.0000\times$ (Exact)** |
| **Active Candidate Slots ($\le 10$ paths)** | 690 slots | 640 slots | $1.078\times$ |
| **Exhausted Empty Slots ($< 10$ paths)** | 310 slots | 360 slots | $0.861\times$ |
| **Root Inspection Requests** | 100 requests | 100 requests | $1.0000\times$ (Exact) |
| **Total HTTP Requests Attempted** | 790 requests | 740 requests | $1.067\times$ |
| **Successful HTTP Responses** | 682 responses | 638 responses | $1.069\times$ |

---

## 2. Root Cause of Realized Slot Exposure
- Both arms were allocated exactly **10 slots per domain**.
- For domains with fewer than 10 candidate paths in the historical index, all available paths were executed and the remaining slots were recorded as `EMPTY_POOL_EXHAUSTED`.
- Because domains were density-matched in pairs, path availability was virtually identical across arms ($69.0\%$ in Treatment vs $64.0\%$ in Control).
- No retry searching or dynamic slot replacement was permitted.
