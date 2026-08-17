# Project Atlas — Scientific Hypotheses

This document records the formal working hypotheses of Project Atlas. Every experiment conducted in the laboratory must test, refine, or challenge at least one registered hypothesis.

---

## 🔬 Core Working Hypotheses

### H-01: The Academic Subpage Persistence Hypothesis
> **Statement**: Academic, governmental, and scientific institution domains (`.edu`, `.gov`, `.ac.uk`, `.org`) contain a statistically significant population of surviving, unindexed subpages that have remained largely unchanged for >= 20 years due to static web server hosting policies and forgotten directory hierarchies.

- **Primary Signals**: `persistence_15yr`, `technology_fossil`, `low_discoverability`, `orphaned_survivor`.
- **Methodology**: Ingest legacy academic department URLs from early 2000s web directories; crawl and compare live DOM hash with 2000–2005 Wayback captures.
- **Status**: `Active / Testing`

---

### H-02: The Domain Resurrection & Content Ghost Hypothesis
> **Statement**: Expired domains that undergo resurrection (re-registration) exhibit distinct temporal discontinuity patterns where legacy static content or forgotten subdirectories remain active alongside modern monetization shells.

- **Primary Signals**: `resurrection`, `major_redesign`, `orphaned_survivor`.
- **Methodology**: Query Wayback CDX for domains with >= 2-year gaps in 200 OK status codes; inspect current subdirectories for surviving legacy assets.
- **Status**: `Active / Testing`

---

### H-03: The Robots.txt Archaeological Drift Hypothesis
> **Statement**: Robots.txt files are rarely refactored after initial creation and often preserve paths to defunct, secret, or legacy server endpoints that still respond with active content long after the main site was modernized.

- **Primary Signals**: `robots_txt_anomaly`, `hidden_sitemap`, `low_discoverability`.
- **Methodology**: Parse `Disallow:` entries from high-traffic and historical domains; perform non-destructive HTTP GET queries against disallowed paths to detect active legacy endpoints.
- **Status**: `Active / Testing`

---

### H-04: The Technology Fossil Clustering Hypothesis
> **Statement**: Web pages built with pre-2005 authoring tools (Microsoft FrontPage, Macromedia Flash, Netscape Composer) that remain live today cluster disproportionately in non-commercial regional organizations, hobbyist archives, and early ISP user directories (`~username/`).

- **Primary Signals**: `technology_fossil`, `persistence_15yr`, `forgotten_archive`.
- **Methodology**: Search Common Crawl and live web for `generator` meta tags and legacy markup; analyze domain TLD and hosting provider distributions.
- **Status**: `Active / Testing`

---

### H-05: The Sitemap Ghosting Hypothesis
> **Statement**: Unlinked XML or text sitemaps frequently persist across major CMS migrations, providing complete historical indices of past site structures that are otherwise undiscoverable via normal link graph crawling.

- **Primary Signals**: `hidden_sitemap`, `orphaned_survivor`, `major_redesign`.
- **Methodology**: Probe candidate standard and non-standard sitemap URLs (`/sitemap_old.xml`, `/sitemap-historical.xml`, etc.) on legacy domains.
- **Status**: `Active / Testing`

---

## 📝 Proposing New Hypotheses

Researchers should submit new hypotheses following the standard template:
1. **Hypothesis ID**: `H-XX`
2. **Title & Statement**: Clear, falsifiable proposition.
3. **Primary Signals**: Expected anomaly signals from the scoring matrix.
4. **Methodology**: Measurable, reproducible testing procedure.
5. **Initial Status**: `Proposed` -> `Active` -> `Validated / Falsified`.
