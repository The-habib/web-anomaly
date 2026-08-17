# Phase 1.6 Future Research Hypotheses & Architectural Proposals

**Project**: Atlas — Web Anomaly Laboratory  
**Phase**: 1.6 Independent Scientific Audit  
**Date**: 2026-08-17T22:42:00Z  
**Scope**: Prospective Research Proposals (**NO PRODUCTION SCORING CHANGES**)  

---

## 1. Principles of Hypothesis Preservation

In accordance with scientific audit standards, Phase 1.6 introduces **zero** modifications to scoring algorithms, feature weights, anomaly thresholds, or crawler parameters. All architectural improvements and new detection signals identified during the audit are formally cataloged below for consideration in Phase 2.

---

## 2. Catalog of Proposed Hypotheses & Experimental Designs

### Hypothesis 1: Path Density-Stratified Sampling
- **Hypothesis**: Stratifying domain selection by historical CDX candidate density ($\ge 500$ URLs) will increase deep discovery yield by at least $5\times$ compared to uniform random sampling.
- **Proposed Protocol**: Evaluate 100 high-density domains vs 100 uniform random domains across identical category quotas.
- **Target Metric**: Validated discoveries per 1,000 HTTP requests.

### Hypothesis 2: Technology Fossil Conjunctive Rule Formulation
- **Hypothesis**: Requiring conjunctive presence of structural fossils (e.g. `nested_tables` + `inline_font_face` + `raw_bgcolor_attributes`) eliminates false positives on unmodernized corporate privacy policies while preserving 100% recall on authentic vintage user spaces.
- **Proposed Scoring Modification**: Formulate a composite rule `vintage_layout_stack` requiring $\ge 3$ distinct pre-CSS visual layout markers.

### Hypothesis 3: Multi-Archive Temporal Index Partitioning
- **Hypothesis**: Internet Archive Wayback Machine CDX API is optimal for pre-2005 archaeology, while Common Crawl index APIs are optimal for 2008–present cross-validation.
- **Proposed Protocol**: Automatically route pre-2005 historical path verification strictly through Wayback CDX, and post-2008 paths through Common Crawl columnar indexes, reducing unnecessary zero-yield queries by ~90%.

### Hypothesis 4: Fully Anonymized Single-Surface Blind Review Protocol
- **Hypothesis**: Presenting single isolated HTML visual captures with hostname and URL strings blinded will eliminate reviewer confirmation bias arising from deep subpath visibility.
- **Proposed Architecture**: Anonymize domain headers, blur logo text, and present root and deep surfaces in an interleaved, randomized review queue.

### Hypothesis 5: Subdomain Discovery vs Deep-Path Expansion Comparison
- **Hypothesis**: For institutional domains (universities and governments), legacy subdomains (e.g. `cs.cmu.edu`, `history.ufl.edu`) contain higher relic density than root-attached subpaths (e.g. `cmu.edu/~faculty`).
- **Proposed Protocol**: Run a 3-arm paired study (Root Baseline vs Deep Path Expansion vs Subdomain Enumeration) on 100 university domains.
