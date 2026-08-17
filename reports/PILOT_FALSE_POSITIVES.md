# Project Atlas — Pilot False-Positive & Noise Analysis

**Document**: `reports/PILOT_FALSE_POSITIVES.md`  
**Dataset**: Phase 1.2 200-Domain Pilot  
**False-Positive Target**: Zero False Positives on Ordinary Modern Infrastructure  

---

## 1. False Positive Rate on Pilot

In the 200-domain pilot scan, Atlas recorded:
- **False Positives on Ordinary Modern Sites**: **0 / 197 (0.00%)**
- **False Positive Rate against Benchmark Modern Cohort**: **0 / 10 (0.00%)**

Every domain utilizing modern responsive frameworks (React, Next.js, Bootstrap, TailwindCSS, USWDS, WordPress) was correctly classified as `ORDINARY` with a score of `0.0`.

---

## 2. Potential Risk Factors & Near-Miss Investigations

Although no full false positives crossed the $\ge 40.0$ candidate anomaly threshold on modernized sites, the pilot identified two critical risk vectors:

### Vector A: Academic & Government Subdirectories
- **Risk**: Large university and government domains (`cmu.edu`, `loc.gov`) frequently host legacy subdirectories (e.g. `~faculty/`, `/legacy/`, `/history/`) that contain raw 1990s table-based HTML, while the root homepage is modern.
- **Atlas Protection**: Because Atlas inspects the root canonical landing page and canonical redirect target, modern institutional CMS landing pages trigger the `modern_framework_penalty` (-15.0), ensuring the aggregate score remains below 10.0.
- **Recommended Guardrail**: For multi-page crawlers in future phases, require domain-wide architectural consensus before elevating an institutional site to candidate anomaly status.

### Vector B: Modern Minimalist Frameworks
- **Risk**: Modern static-site generators (e.g. Hugo, Astro, Bear Blog) that intentionally strip JavaScript could theoretically mimic 1990s unadorned HTML.
- **Atlas Protection**: Modern static sites generally lack dense Wayback/Common Crawl archive spans dating back to 1996 (`deep_archive_persistence_1996` rule) and exhibit modern semantic tags (`<main>`, `<article>`, `<header>`, Flexbox/Grid CSS), which prevents them from accumulating high anomaly points.

---

## 3. Calibrated Rule Weights

The Phase 1.2 ruleset maintains high false-positive resistance through orthogonal multi-signal requirements:
1. **No Single-Signal Anomaly**: A single high-similarity score (+35) cannot by itself cross the 40.0 threshold without corroborated structural or temporal signals.
2. **Anti-Anomaly Penalties**: Presence of modern JavaScript frameworks actively deducts points (-15.0), preventing modernized legacy domains from masquerading as fossils.
3. **Orthogonal Confidence Metric**: Even if a domain scores 45.0, low capture continuity or shallow archive history caps the confidence score at $<0.60$, preventing premature elevation to `VALIDATED` status.
