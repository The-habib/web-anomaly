# Phase 1.5 Limitations Report — Project Atlas

**Project**: Atlas — Web Anomaly Laboratory  
**Phase**: 1.5  
**Date**: 2026-08-17T22:30:00Z  

---

## 1. Known Experimental Limitations

### 1. Archive Index Latency & Rate Limits
- Wayback CDX queries are subject to occasional rate limiting or transient timeouts, which can result in partial candidate lists for highly active domains.

### 2. Deep Subdomain Boundaries
- The Phase 1.5 deep expansion focused on paths on the primary domain (`domain.com/*`). Subdomains (`sub.domain.com`) were not recursively scanned to avoid unbound crawling.

### 3. Binary & Media Formats
- Static audio/video and flash binary objects (`.swf`, `.au`, `.midi`) were identified by tag references but not deeply unpacked or emulated in this phase.

### 4. Static Retrieval Limits
- `max_retrievals_per_domain = 15` provided strong efficiency but may miss relics on massive university domains with thousands of user accounts.
