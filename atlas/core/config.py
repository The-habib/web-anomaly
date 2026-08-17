"""Centralized configuration and directory paths for Project Atlas."""

import os
from pathlib import Path

# Base Paths
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
ATLAS_DIR = ROOT_DIR / "atlas"
FINDINGS_DIR = ROOT_DIR / "findings"
EVIDENCE_DIR = ROOT_DIR / "evidence"
SCREENSHOTS_DIR = EVIDENCE_DIR / "screenshots"
HTML_DIR = EVIDENCE_DIR / "html"
JSON_DIR = EVIDENCE_DIR / "json"
TIMELINE_DIR = EVIDENCE_DIR / "timeline"
METADATA_DIR = EVIDENCE_DIR / "metadata"
CACHE_DIR = ROOT_DIR / "cache"
EXPERIMENTS_DIR = ROOT_DIR / "experiments"
REPORTS_DIR = ROOT_DIR / "reports"
SCRIPTS_DIR = ROOT_DIR / "scripts"
DATA_DIR = ROOT_DIR / "data"
LOGS_DIR = ROOT_DIR / "logs"
DOCS_DIR = ROOT_DIR / "docs"

CONFIG_DIR = ATLAS_DIR / "config"
SCORING_RULES_PATH = CONFIG_DIR / "scoring_rules.json"

# Network & Crawler Defaults
DEFAULT_USER_AGENT = "ProjectAtlas/0.1.0 (+https://github.com/web-anomaly-lab; research@atlas.lab)"
REQUEST_TIMEOUT_SECONDS = 30
PLAYWRIGHT_NAVIGATION_TIMEOUT_MS = 30000
PLAYWRIGHT_VIEWPORT = {"width": 1280, "height": 800}

# Rate Limits & Throttling
DEFAULT_CONCURRENCY = 3
DEFAULT_CRAWL_DEPTH = 2

# Ensure required directories exist
for directory in [
    FINDINGS_DIR, EVIDENCE_DIR, SCREENSHOTS_DIR, HTML_DIR,
    JSON_DIR, TIMELINE_DIR, METADATA_DIR, CACHE_DIR,
    EXPERIMENTS_DIR, REPORTS_DIR, SCRIPTS_DIR, DATA_DIR, LOGS_DIR, DOCS_DIR
]:
    directory.mkdir(parents=True, exist_ok=True)
