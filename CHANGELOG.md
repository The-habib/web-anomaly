# Changelog

All notable changes to Project Atlas will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.1.0] - 2026-08-17 (Phase 0 Foundation)

### Added
- Initial establishment of **Project Atlas** (codename: *Atlas*) as an autonomous web anomaly research laboratory.
- Canonical laboratory directory structure: `findings/`, `evidence/` (with subdirectories for `screenshots/`, `html/`, `json/`, `timeline/`, `metadata/`), `experiments/`, `reports/`, `scripts/`, `data/`, `logs/`, `docs/`, and `atlas/`.
- Full integration of 40 Browser, Web Crawling, HTML Parsing, Visual Diffing, Network Inspection, and MCP tools.
- Core data models in `atlas.core.models` (`Finding`, `EvidenceArtifact`, `TimelineEvent`, `AnomalySignal`, `Experiment`).
- Structured audit and performance logging system in `atlas.core.logger`.
- Config-driven Anomaly Scoring Engine in `atlas.scoring.scorer` and `atlas/config/scoring_rules.json`.
- 10-stage automated Evidence Pipeline (`atlas.pipeline.pipeline`) integrating Playwright screenshots, HTML & Trafilatura text extraction, Wayback Machine CDX API, and Common Crawl index queries.
- Numbered Experiment Ledger manager (`atlas.experiments.ledger`) for sequential provisioning (`experiments/0001/`, etc.).
- Automated Markdown research report generator (`atlas.reporting.report_generator`).
- Unified Command Line Interface `atlas` (`atlas scan`, `atlas experiment`, `atlas findings`, `atlas report`).
- Complete documentation suite: `README.md`, `ROADMAP.md`, `HYPOTHESES.md`, `DISCOVERIES.md`, `RULES.md`, `CONTRIBUTING.md`, `ARCHITECTURE.md`, and `CHANGELOG.md`.
- Automated test suite covering models, scoring logic, experiment provisioning, and pipeline operations.
