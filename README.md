# Project Atlas — Web Anomaly Research Laboratory

[![Project Atlas](https://img.shields.io/badge/Project-Atlas-blue?style=flat-square)](https://github.com/web-anomaly-lab)
[![Status](https://img.shields.io/badge/Status-Phase%200%20Operational-brightgreen?style=flat-square)](#)
[![Python](https://img.shields.io/badge/Python-3.12-blue?style=flat-square)](https://python.org)
[![Playwright](https://img.shields.io/badge/Playwright-Headless%20Browser-orange?style=flat-square)](https://playwright.dev)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

> **"The public web is not a static document. It is a shifting archaeological landscape of persistent fossils, sudden resurrections, hidden structures, and orphaned survivors."**

**Project Atlas** is an autonomous, evidence-based scientific laboratory built to discover, analyze, score, and archive unusual patterns and phenomena across the public web. Atlas treats web crawlers, Wayback Machine APIs, and Common Crawl dumps as infrastructure to power systematic discovery and reproducible research.

---

## 🔭 Mission & Scientific Philosophy

1. **Evidence-Backed Discoveries**: A web phenomenon is only classified as an anomaly if backed by permanent cryptographic hashes, DOM trees, visual captures, and temporal evidence.
2. **Permanent Archival**: Every investigation permanently stores artifacts in structured formats (`evidence/screenshots/`, `evidence/html/`, `evidence/json/`, `evidence/timeline/`, `evidence/metadata/`).
3. **Reproducibility**: Every discovery report includes the exact CLI command and raw inputs needed to reproduce the finding.
4. **Autonomous Operation**: Standardized pipelines enable autonomous scanning, scoring, and experiment ledger provisioning.

---

## 🏗️ Laboratory Architecture

```
web-anomaly-lab/
├── findings/                   # Permanent JSON records of verified findings
├── evidence/                   # Raw & rendered evidence artifacts
│   ├── screenshots/            # Playwright full-page & viewport captures
│   ├── html/                   # Raw and rendered HTML snapshots
│   ├── json/                   # Serialized evidence dossiers
│   ├── timeline/               # Unified chronological temporal datasets
│   └── metadata/               # HTTP headers, tech-stack, DOM metadata
├── experiments/                # Sequential numbered experiment ledger (0001, 0002...)
├── reports/                    # Publication-grade Markdown research reports
├── scripts/                    # Command-line execution helpers
├── data/                       # Candidate target lists and seed datasets
├── logs/                       # Audit logs and structured execution traces
├── docs/                       # Architectural and technical documentation
└── atlas/                      # Core Python laboratory package
    ├── core/                   # Config, models, structured logger
    ├── pipeline/               # 10-stage evidence collection pipeline
    ├── scoring/                # Config-driven anomaly scoring engine
    ├── experiments/            # Sequential experiment ledger engine
    └── reporting/              # Markdown research report generator
```

---

## 🚀 Quick Start & CLI Usage

### 1. Run the Automated Evidence Pipeline
Analyze any URL across live web, Wayback Machine, and Common Crawl:
```bash
atlas scan https://example.com
```

### 2. Manage the Experiment Ledger
Provision the next sequential experiment in the laboratory ledger:
```bash
# Automatically creates experiments/0001/ with hypothesis.md, setup.md, notes.md, result.md
atlas experiment new "Investigation of Long-Lived Educational Subdomains" --hypothesis "Academic department pages from the late 1990s remain unindexed yet live."
```

List all experiments:
```bash
atlas experiment list
```

### 3. Inspect Findings
Review all verified discoveries recorded by the laboratory:
```bash
atlas findings list
```

### 4. Verify Laboratory Environment
Run the comprehensive self-check auditing all 40 browser, parser, crawler, and diffing tools:
```bash
python3 scripts/verify_environment.py
```

---

## 📊 Anomaly Scoring Model

Atlas uses a config-driven scoring engine (`atlas/config/scoring_rules.json`):

| Signal | Category | Weight | Description |
| :--- | :--- | :---: | :--- |
| **15+ Year Web Persistence** | `temporal` | `+2` | Continuous historical presence across archives and live web >= 15 years |
| **Domain / URL Resurrection** | `temporal` | `+5` | URL disappeared (404/failure >= 2 yrs) and returned with active content |
| **Historical Technology Fossil** | `technological` | `+4` | Legacy markup signatures (Flash, FrontPage, Netscape tags, HTML 3.2) |
| **Low Discoverability** | `graph` | `+4` | Unlinked / orphaned from main navigation while remaining live |
| **Orphaned Surviving Subpage** | `structural` | `+3` | Deep subpage active while parent directory has been retired |
| **Abrupt Structural / Tech Shift** | `evolutionary` | `+3` | Drastic DOM structure, content length, or CMS shift in timeline |
| **Unlisted Sitemap Discovery** | `structural` | `+2` | Valid XML sitemap discovered at non-standard or unlinked path |
| **Robots.txt Historical Discrepancy** | `policy` | `+2` | Anomalous disallows referencing forgotten endpoints |
| **Forgotten Public File / Index** | `content` | `+3` | Open server directory listing or exposed backup |

---

## 📖 Laboratory Documentation

- [ROADMAP.md](ROADMAP.md): Evolutionary roadmap from Phase 0 scaffolding to Phase 2 autonomous discovery.
- [HYPOTHESES.md](HYPOTHESES.md): Active scientific hypotheses regarding web persistence, decay, and anomalies.
- [DISCOVERIES.md](DISCOVERIES.md): Discovery classification taxonomy and evidence requirements.
- [RULES.md](RULES.md): Operating guidelines, ethical scraping limits, and evidence immutability rules.
- [ARCHITECTURE.md](ARCHITECTURE.md): Comprehensive system design, data flow diagrams, and data contracts.
- [CONTRIBUTING.md](CONTRIBUTING.md): Guide for proposing experiments, adding anomaly signals, and writing extensions.
- [CHANGELOG.md](CHANGELOG.md): Version history and milestone tracking.

---

## ⚖️ Ethical Research & Compliance

Project Atlas operates strictly as an observational research laboratory:
- Complies with standard rate-limiting (polite requests with backoff).
- Respects `robots.txt` instructions for live crawling.
- Archives only publicly accessible web data and historical public archives.
- Never bypasses authentication or attempts unauthorized access.

---

**Project Atlas Laboratory** — *Uncovering the archaeology of the open web.*
