# Phase 1.5 False Negative Analysis

**Project**: Atlas — Web Anomaly Laboratory  
**Phase**: 1.5  
**Date**: 2026-08-17T22:30:00Z  

---

## 1. Characterizing Residual False Negatives

Despite significant discovery gains (+57.1% reference relic recovery), several residual false-negative patterns remain:

### 1. Plain ASCII / Raw Text Repositories
- **Pattern**: Sites structured as plain `.txt` files or `<pre>` tags without HTML tables or retro tags (`textfiles.com`, text RFC mirrors).
- **Current Scorer Behavior**: `AnomalyScorer` awards points for tables and retro HTML tags, but awards 0 points for pure ASCII layout.
- **Proposed Future Feature**: `ASCII_PLAIN_TEXT_LAYOUT` (+25.0 points) when body text is predominantly wrapped in `<pre>` or unstyled monospace.

### 2. Deep Subdomain Partitioning
- **Pattern**: Relics hosted on historical third-level subdomains (`www-retro.mit.edu`, `archive.kernel.org`) rather than subpaths of the primary domain.
- **Current Scorer Behavior**: Phase 1.5 operates on the apex/canonical domain name.
- **Proposed Future Feature**: Subdomain enumeration layer using `subfinder` / `assetfinder`.
