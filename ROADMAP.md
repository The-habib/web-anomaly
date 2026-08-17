# Project Atlas — Laboratory Roadmap

This roadmap outlines the milestones and evolutionary phases of Project Atlas as it transitions from initial foundation scaffolding to autonomous, multi-agent web archaeology.

---

## 📍 Phase 0 — Laboratory Foundation (Current)
*Target: Reproducible Scaffold, Core Pipeline, & Storage Model*

- [x] **Repository Identity & Structure**: Establish `web-anomaly-lab` with canonical folders (`findings/`, `evidence/`, `experiments/`, `reports/`, `atlas/`, `logs/`).
- [x] **Toolchain Environment Verification**: Verify and package 40 browser automation, crawler, parser, diffing, and MCP tools.
- [x] **Core Models & Structured Logging**: Implement Pydantic data contracts (`Finding`, `EvidenceArtifact`, `TimelineEvent`, `Experiment`) and structured audit logger.
- [x] **10-Stage Evidence Pipeline**: Automate URL validation, Playwright screenshotting, HTML/metadata extraction, Wayback + Common Crawl timeline fusion, scoring, and report generation.
- [x] **Config-Driven Scoring Engine**: Implement modular scoring rules with configurable weights in `atlas/config/scoring_rules.json`.
- [x] **Experiment Ledger**: Implement auto-incrementing numbered experiment provisioning (`experiments/0001/`, etc.).
- [x] **Unified CLI**: Create `atlas scan`, `atlas experiment`, `atlas findings`, and `atlas report` commands.
- [x] **Complete Scientific Documentation**: Publish `README.md`, `ROADMAP.md`, `HYPOTHESES.md`, `DISCOVERIES.md`, `RULES.md`, `CONTRIBUTING.md`, `ARCHITECTURE.md`, and `CHANGELOG.md`.

---

## 📍 Phase 1 — Systematic Anomaly Detection & Seed Expansion
*Target: Mass Target Scanning, Advanced Diffing, & Fossil Classifiers*

- [ ] **Seed Domain Corpus**: Ingest curated historical domain datasets (e.g., legacy top-level domains, early web directories, government archives).
- [ ] **Visual Diff Regression Pipeline**: Automated multi-snapshot visual comparison using `pixelmatch` and `resemblejs` to detect silent visual redesigns.
- [ ] **Deep Technology Fossil Detectors**: Expand regex & DOM tree classifiers for obscure 1990s web frameworks, legacy active controls, and discontinued CMS engines.
- [ ] **Batch Processing Runner**: Implement multi-threaded pipeline execution with rate-limiting queues for analyzing domain lists.
- [ ] **Interactive Visual Dossier Viewer**: Web-based dashboard for exploring findings, temporal timelines, and visual diffs.

---

## 📍 Phase 2 — Autonomous Archaeological Agents
*Target: Self-Navigating Research Agents & Proactive Anomaly Hunters*

- [ ] **AI-Guided Browser Explorers**: Deploy `browser-use` and `Stagehand` agents that follow anomalous sub-links, inspect obscure navigation menus, and isolate unindexed paths.
- [ ] **Temporal Graph Reconstruction**: Build historical site graph evolution models to map how site architectures morph over 20+ years.
- [ ] **Cross-Archive Anomaly Correlation**: Correlate anomalies across Wayback, Common Crawl, UK Web Archive, and national web archives.
- [ ] **Automated Hypothesis Generation**: LLM-driven hypothesis synthesis based on discovered structural clustering.

---

## 📍 Phase 3 — Global Anomaly Atlas
*Target: Open Scientific Web Anomaly Index*

- [ ] **Public Anomaly Dataset Releases**: Publish versioned datasets of verified web survivors, technology fossils, and resurrection phenomena.
- [ ] **Decentralized WARC Verification**: Cryptographic IPFS/Arweave anchoring of critical web archaeological findings.
- [ ] **Community Anomaly Submissions**: Standardized pull-request workflows for external researchers submitting reproducible findings.
