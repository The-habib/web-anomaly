# Project Atlas — Phase 1.2 Limitations, Edge Cases & Future Roadmap

**Document**: `reports/PHASE_1_2_LIMITATIONS.md`  
**Classification**: Scientific Transparency & Self-Correction Protocol  
**Phase**: Phase 1.2  

---

## 1. Documented Limitations of Phase 1.2

While Phase 1.2 successfully eliminates synthetic data and establishes full provenance, the following scientific and technical limitations remain:

### 1. Root Canonical Scope
- **Current Behavior**: The pilot and corpus pipelines currently evaluate the root landing page (`https://{domain}/`) and follow canonical redirects.
- **Limitation**: Historic relics embedded in deep subdirectories (e.g. `cmu.edu/~faculty/retro_page.html`) on otherwise modern institutional domains are masked by the modern root portal.
- **Future Resolution**: Implement an exploratory multi-depth spider that samples secondary paths while preserving domain-level aggregation.

### 2. Live Network Rate Limits & Archive Dependency
- **Current Behavior**: Timeline continuity relies heavily on CDX indices from the Internet Archive Wayback Machine and Common Crawl.
- **Limitation**: Temporary archive upstream rate limits (HTTP 429 / 503) can artificially inflate the longest observed evidence gap if retry backoff is exhausted.
- **Mitigation**: The Atlas pipeline incorporates multi-provider fallback (Wayback CDX + Common Crawl CDX indices) with exponential jittered backoff.

### 3. Under-Scoring of Minimalist ASCII / Audio Artifacts
- **Current Behavior**: As documented in `reports/PILOT_FALSE_NEGATIVES.md`, pure ASCII preformatted text archives (`catb.org`) and audio loop relics (`zombo.com`) score 35.0, narrowly missing the 40.0 anomaly threshold.
- **Future Resolution**: Add specialized rules for ASCII-dominated DOM hierarchies and legacy media transition markers.

---

## 2. Edge Case Inventory

| Edge Case Type | Representative Domain | Observed Behavior | Atlas Handling |
| :--- | :--- | :--- | :--- |
| **Institutional Subdomain Wildcards** | `golem.ph.utexas.edu` | High-depth academic subdomains | Normalized and verified as independent research entities. |
| **Archival Gap without Failure** | `cmu.edu` | 3-year gap in historical CDX indexing | Classified as `LONG_SPAN_PRESENCE` rather than true downtime resurrection. |
| **Hybrid Dialup Shell Roots** | `world.std.com`, `panix.com` | Vintage text directories behind modern HTTPS | Scored accurately with low false positive footprint. |
| **Historic Preserved Relics** | `spacejam.com`, `toastytech.com` | Frameset and HTML3.2 table layouts | Correctly detected as High / Candidate Anomalies. |

---

## 3. Strict Hard-Stop Directive

In accordance with Phase 1.2 guidelines:
- **HARD STOP CONDITION**: Project Atlas will **NOT** automatically begin Phase 2.
- The repository, test suites, provenance database, pilot evidence, and benchmark evaluation are frozen in a clean, reproducible state awaiting user directives.
