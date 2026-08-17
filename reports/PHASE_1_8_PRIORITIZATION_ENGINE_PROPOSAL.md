# Phase 1.8 Architectural Proposal: Multi-User Platform & User-Space Prioritization Engine

**Project**: Atlas — Web Anomaly Laboratory  
**Phase**: 1.8 Prospective Architecture Proposal  
**Date**: 2026-08-17T22:55:00Z  

---

## Future Prioritization Architecture

Based on Phase 1.7 findings:
1. **Target User-Space Density ($D_{\text{user}}$)**: Prioritize domains with $\ge 50$ `~user` subpaths over generic institutional size.
2. **Adaptive Retrieval Budgets**: Scale retrieval ceilings dynamically for federated multi-user domains.
3. **Multi-Archive Partitioning**: Route pre-2005 queries to Wayback CDX and post-2008 queries to Common Crawl.
