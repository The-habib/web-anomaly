# Project Atlas — Phase 1.8 Resource Accounting & Cost Analysis

**Project**: Atlas Autonomous Research Laboratory  
**Phase**: 1.8 Resource Accounting & Operational Efficiency  
**Date**: 2026-08-18T05:59:00Z  
**Audit Artifact**: `audit/phase1_8/cost_analysis.json`

---

## 1. Resource Ledger Summary

| Operational Metric | Phase 1.7 Observed | Unit / Formulation |
| :--- | :--- | :--- |
| **Total Study Domains** | 200 | 100 Uniform + 100 Density |
| **Total HTTP / Archive Requests** | 2,311 | 841 (U) + 1,470 (D) |
| **Mean Requests per Domain** | 11.56 | 2,311 / 200 |
| **Requests per Validated Discovery** | **1,155.5** | 2,311 / 2 |
| **Total Execution Runtime** | 48.5 seconds | Automated async crawler |
| **Stored Artifact Data** | 28.5 MB | HTML payloads |
| **Direct Cloud / Crawling Cost** | **$0.00** | Open archive APIs / local cache |
| **Cost per Discovery ($USD)** | **$0.00** | Zero marginal monetary cost |

---

## 2. Research Efficiency Analysis

1. **Computational Overhead**: Path density calculation ($d_{\text{raw}}$, $d_{\text{user}}$, etc.) across 1,000 domains took $< 5$ seconds during survey phase.
2. **Retrieval Efficiency**: By concentrating retrievals on domains with verified historical path density, Arm D discovered 2 vintage surfaces within 1,470 requests (1 discovery per 735 requests), whereas Arm U exhausted 841 requests with 0 discoveries.
