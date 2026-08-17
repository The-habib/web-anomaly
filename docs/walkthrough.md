# Project Atlas — Laboratory Walkthrough & Operation Guide

**Project Atlas** (internal codename: **Atlas**) is an evidence-based scientific laboratory for discovering, analyzing, scoring, and archiving public web anomalies.

---

## 1. Laboratory Directory Architecture

The repository enforces strict evidence permanence:

```
web-anomaly-lab/
├── findings/                   # Master JSON finding dossiers
│   └── ATLAS-*.json
├── evidence/                   # Permanent, cryptographically hashed artifacts
│   ├── screenshots/            # Playwright full-page renders
│   ├── html/                   # Raw and rendered HTML snapshots
│   ├── json/                   # Serialized evidence dossiers
│   ├── timeline/               # Unified chronological event datasets
│   └── metadata/               # HTTP headers, tech-stack markers, DOM metadata
├── experiments/                # Sequential numbered experiment ledger (0001, 0002...)
├── reports/                    # Standardized Markdown research dossiers
├── scripts/                    # CLI execution and audit scripts
│   ├── run_pipeline.py
│   ├── new_experiment.py
│   └── verify_environment.py
├── data/                       # Target seed corpora
├── logs/                       # Audit logs and daily traces
├── docs/                       # Technical manuals & architecture
├── tests/                      # Comprehensive 7-module test suite
└── atlas/                      # Core Python Laboratory package
    ├── core/                   # config.py, logger.py, models.py
    ├── pipeline/               # 10-stage evidence pipeline & temporal analyzers
    ├── scoring/                # False-positive resistant scoring engine
    ├── experiments/            # Sequential experiment ledger engine
    └── reporting/              # Markdown research report generator
```

---

## 2. Evidence State Model (Phase 0.5)

Project Atlas operates under a 6-tier evidence state model:

| State | Definition | Example |
| :--- | :--- | :--- |
| **`OBSERVED`** | Direct empirical facts recorded from live crawl or archive CDX. | 2004 archive snapshot exists; live status is 200 OK. |
| **`INFERRED`** | Statistically derived deduction or hypothesis. | Site was likely maintained during unobserved intervals. |
| **`CANDIDATE`** | Potential anomaly signal requiring corroborating evidence. | Single failure capture detected between active periods. |
| **`VALIDATED`** | High-confidence anomaly backed by dense, multi-source evidence. | 20+ year persistence with 85%+ yearly coverage. |
| **`DISPROVEN`** | Anomaly hypothesis refuted by empirical evidence. | Claimed resurrection was actually an unobserved crawl gap. |
| **`INSUFFICIENT`**| Sparse or inconclusive evidence; no claim can be made. | 2 isolated captures across 20 years with zero intermediate data. |

---

## 3. CLI Command Reference

### Run Evidence Pipeline
```bash
atlas scan https://target-url.com
```

### Verify Evidence Integrity
Verify SHA-256 hashes of all stored evidence files against actual disk bytes:
```bash
atlas evidence verify
# Or verify a specific finding:
atlas evidence verify ATLAS-20260817-example_com_2026
```

### Manage Experiment Ledger
```bash
# Provision next sequential experiment
atlas experiment new "Investigation of Legacy Academic Subdomains" --hypothesis "Static HTML 3.2 department pages survive on legacy educational servers." --urls https://dept.edu/archive/

# List all experiments
atlas experiment list
```

### List Verified Findings
```bash
atlas findings list
```

### Audit Toolchain Readiness
Run the 4-tier functional audit testing all 25 browser, crawler, parser, diffing, and core subsystems:
```bash
python3 scripts/verify_environment.py
```
