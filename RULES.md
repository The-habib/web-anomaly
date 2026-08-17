# Project Atlas — Laboratory Operating Rules & Ethical Standards

This document establishes the mandatory operational, scientific, and ethical guidelines governing all autonomous actions, pipelines, and human contributions within Project Atlas.

---

## ⚖️ 1. Ethical & Legal Principles

1. **Observational Science Only**: Atlas investigates only publicly accessible web data and historical public archives (Wayback Machine, Common Crawl).
2. **No Authentication Bypass**: Never attempt to bypass authentication, crack credentials, exploit vulnerabilities, or access private endpoints.
3. **Strict Respect for Robots Directives**: Live crawlers must obey `robots.txt` disallow rules and `Crawl-delay` directives during active web crawling.
4. **Polite Request Throttling**:
   - Limit concurrent connections to any individual target domain to `<= 2`.
   - Implement exponential backoff when encountering HTTP 429 (Too Many Requests) or HTTP 503.
   - Include clear User-Agent headers with contact/research identification:
     `ProjectAtlas/0.1.0 (+https://github.com/web-anomaly-lab; research@atlas.lab)`

---

## 🔒 2. Scientific Integrity & Evidence Immutability

1. **No Data Fabrication**: Never synthesize, fabricate, or hallucinate findings, timestamps, or HTML markup.
2. **Permanent Cryptographic Verification**: Every piece of collected evidence (screenshot, HTML, JSON, WARC) must be hashed (SHA-256) upon collection and recorded in metadata.
3. **Zero Deletion Policy**: Never delete or overwrite previous experimental evidence unless explicitly purging corrupted test artifacts from `cache/`.
4. **Atomic Experiment Ledger**: Every experiment must have a unique sequential number (`experiments/0001/`, `experiments/0002/`) and contain:
   - `hypothesis.md`
   - `setup.md`
   - `notes.md`
   - `result.md`
   - `evidence/` directory

---

## 🛠️ 3. Software Architecture & Code Standards

1. **Modular Architecture**: All pipeline components must be isolated into single-responsibility Python modules under `atlas/`.
2. **Config-Driven Logic**: Anomaly scores, rate limits, and timeouts must be defined in JSON/Python configuration files, never hardcoded in logic loops.
3. **Structured Logging**: All actions, durations, statuses, and error traces must be logged to `logs/` via `atlas.core.logger`.
4. **Git Hygiene**:
   - Commit frequently with atomic, descriptive messages (`feat: ...`, `fix: ...`, `docs: ...`, `test: ...`).
   - Never commit API keys, personal credentials, or large binary dumps outside of designated evidence paths.
