# Project Atlas — Phase 1.9 Salvage Assessment & Separation of Concerns

## 1. Partition of Experimental Integrity

```mermaid
graph TD
    A[Phase 1.9 Replication Execution] --> B[VALID_LIVE_EVIDENCE]
    A --> C[VALID_ENGINEERING_RESULTS]
    A --> D[VALID_STATISTICAL_OBSERVATIONS]
    A --> E[INVALID_VALIDATION_CLAIMS]

    B --> B1[Raw HTML Crawl Artifacts]
    B --> B2[SHA-256 Hashes]
    B --> B3[HTTP 200 Live Response Status]

    C --> C1[100 Matched-Pair Blocks]
    C --> C2[1,000 vs 1,000 Fixed Slots]
    C --> C3[Deterministic Scorer Replay]

    D --> D1[Density-Informed Candidate Ranking]
    D --> D2[Candidate Yield: 2 Treatment vs 1 Control]

    E --> E1[Programmatic Human Review Claims]
    E --> E2[Hardcoded Domain Logic in review.py]
```

---

## 2. Salvaged Assets
1. **Live HTML Artifacts**: 1,530 live HTTP responses preserved with cryptographic SHA-256 digests.
2. **Matched-Pair Randomization Ledger**: 100 matched pairs balanced across 6 categories.
3. **Candidate Anomaly Pool**: 3 candidate anomalies scoring $\ge 40$ (Treatment: `gwern.net`, `uspto.gov`; Control: `joelonsoftware.com`).
4. **Clean Blind Review Packets**: 23 decontaminated review packets exported to `data/phase1_9_1/review_packets.jsonl`.
