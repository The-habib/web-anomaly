# Project Atlas — System Architecture

This document provides the technical blueprint, component breakdown, and data contracts for the Project Atlas laboratory.

---

## 📐 High-Level Architecture

```
                               ┌───────────────────────────┐
                               │   Atlas CLI / Automation   │
                               │   (atlas scan / scripts)  │
                               └─────────────┬─────────────┘
                                             │
                                             ▼
                               ┌───────────────────────────┐
                               │     Evidence Pipeline     │
                               │     (10-Stage Runner)     │
                               └──────┬─────────────┬──────┘
                                      │             │
              ┌───────────────────────┘             └───────────────────────┐
              ▼                                                             ▼
┌───────────────────────────┐                                 ┌───────────────────────────┐
│     Live Web Ingestion    │                                 │    Temporal Archives      │
│  - Playwright Screenshot  │                                 │  - Wayback Machine CDX    │
│  - HTML & Text Extract    │                                 │  - Common Crawl CDX/WARC  │
│  - Metadata & Headers     │                                 │  - Unified Timeline Fusion│
└─────────────┬─────────────┘                                 └─────────────┬─────────────┘
              │                                                             │
              └───────────────────────┐             ┌───────────────────────┘
                                      │             │
                                      ▼             ▼
                               ┌───────────────────────────┐
                               │    Anomaly Scoring Engine │
                               │ (atlas/scoring/scorer.py) │
                               │  [Config-Driven Weights]  │
                               └─────────────┬─────────────┘
                                             │
                                             ▼
                      ┌─────────────────────────────────────────────┐
                      │             Permanent Storage               │
                      ├──────────────────────┬──────────────────────┤
                      │ evidence/            │ findings/            │
                      │  ├── screenshots/    │  └── ATLAS-*.json    │
                      │  ├── html/           ├──────────────────────┤
                      │  ├── json/           │ reports/             │
                      │  ├── timeline/       │  └── REPORT_*.md     │
                      │  └── metadata/       ├──────────────────────┤
                      │                      │ experiments/         │
                      │                      │  └── 0001, 0002...   │
                      └──────────────────────┴──────────────────────┘
```

---

## 🧩 Core Subsystems

### 1. `atlas.core` (Foundational Primitives)
- **`config.py`**: Central directory constant resolution, timeout settings, and environment detection.
- **`logger.py`**: Multi-channel structured logger writing to console, daily execution logs (`logs/atlas_YYYYMMDD.log`), and structured JSONL audit logs (`logs/audit_YYYYMMDD.jsonl`).
- **`models.py`**: Pydantic schemas enforcing strict typing on `EvidenceArtifact`, `TimelineEvent`, `AnomalySignal`, `Finding`, and `Experiment`.

### 2. `atlas.pipeline` (Evidence Pipeline)
- **`screenshot.py`**: Playwright headless browser manager capturing full-page PNGs with viewport metadata.
- **`html_extractor.py`**: Multi-extractor leveraging `requests`, `BeautifulSoup4`, `trafilatura` for clean text extraction, and `readability-lxml` for document summarization.
- **`wayback_client.py`**: High-speed CDX API client for Wayback Machine timeline reconstruction.
- **`commoncrawl_client.py`**: Multi-index historical snapshot query engine across Common Crawl data repositories.
- **`timeline.py`**: Temporal event fusion, deduplication, chronological sorting, and span computation.
- **`pipeline.py`**: Orchestrator executing the 10-step sequence with failure resilience and cryptographic hashing (SHA-256) of every generated artifact.

### 3. `atlas.scoring` (Anomaly Scoring Engine)
- **`scorer.py`**: Rule evaluation engine that tests for temporal persistence, resurrection gaps, technology fossils, sitemap ghosts, and directory listings against `atlas/config/scoring_rules.json`.

### 4. `atlas.experiments` (Experiment Ledger)
- **`ledger.py`**: Atomic directory provisioning for experiments (`experiments/0001/`), guaranteeing continuous numbering and standard hypothesis/setup/notes/results scaffolding.

### 5. `atlas.reporting` (Markdown Report Generator)
- **`report_generator.py`**: Formats complete finding dossiers into publication-grade Markdown reports containing executive summaries, visual screenshot embeds, signal breakdowns, artifact hash tables, and machine JSON blocks.

---

## 🔒 Data Contracts & Integrity

Every artifact in `evidence/` is governed by the `EvidenceArtifact` schema:
```json
{
  "artifact_id": "art_ss_example_com_20260817",
  "artifact_type": "screenshot",
  "relative_path": "evidence/screenshots/example_com_screenshot.png",
  "file_name": "example_com_screenshot.png",
  "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "size_bytes": 1048576,
  "created_at": "2026-08-17T18:00:00Z",
  "metadata": {}
}
```
