# Project Atlas — Resource Accounting & Execution Costs (Phase 1.9)

## 1. Execution Footprint

| Resource Metric | Treatment Arm | Control Arm | Combined Total |
| :--- | :--- | :--- | :--- |
| **Domains Evaluated** | 100 | 100 | 200 |
| **Retrieval Slots Allocated** | 1,000 | 1,000 | 2,000 |
| **Root HTTP Requests** | 100 | 100 | 200 |
| **Deep HTTP Requests Attempted** | 690 | 640 | 1,330 |
| **Total HTTP Network Requests** | 790 | 740 | 1,530 |
| **Total Data Transferred (Bytes)** | 14.8 MB | 13.9 MB | 28.7 MB |
| **Execution Runtime (Concurrent Pool)**| — | — | **147.17 seconds** (~2.5 min) |
| **Average Cost per Domain** | — | — | 7.65 requests / 143 KB |

- **Efficiency Conclusion**: The 20-worker thread pool reduced replication runtime from ~20 minutes to under 2.5 minutes while maintaining strict request throttling and error handling.
